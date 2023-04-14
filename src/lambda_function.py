# -*- coding: utf-8 -*-

# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# SPDX-License-Identifier: LicenseRef-.amazon.com.-AmznSL-1.0
# Licensed under the Amazon Software License (the "License")
# You may not use this file except in
# compliance with the License. A copy of the License is located at http://aws.amazon.com/asl/
#
# This file is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, express or implied. See the License for the specific
# language governing permissions and limitations under the License.

import json
import logging
from traceback import format_exc

from alexa.exceptions import HandleCommandException
from alexa.models import AlexaResponse, ArnoFanDiscoveryResponse
from clients import SqsClient
from commands import ArnoCommand
from models import ArnoResponse, ArnoResponseDecoder

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

HOME_QUEUE = "https://sqs.us-east-1.amazonaws.com/559001708083/HomeSQS"
ALEXA_QUEUE = "https://sqs.us-east-1.amazonaws.com/559001708083/AlexaQueue"

supported_capabilities = ArnoFanDiscoveryResponse.supported_capabilities()


def sqs_helper(command: ArnoCommand) -> ArnoResponse:
    sqs = SqsClient()

    post_home_queue_message(sqs, command)
    return fetch_alexa_queue_message(sqs)


def post_home_queue_message(sqs: SqsClient, command: ArnoCommand) -> None:
    sqs.send_message(
        sql_url=HOME_QUEUE,
        message=str(command)
    )


def fetch_alexa_queue_message(sqs: SqsClient) -> ArnoResponse:
    messages = sqs.fetch_messages(sqs_url=ALEXA_QUEUE)
    message_received = messages["Messages"][0]
    message_receipt_handler = message_received["ReceiptHandle"]

    sqs.delete_message(sqs_url=ALEXA_QUEUE,
                       receipt_handle=message_receipt_handler)

    message_body = message_received["Body"]

    return json.loads(
        message_body,
        cls=ArnoResponseDecoder
    )


def handle_command(namespace: str, name: str, request: dict) -> AlexaResponse:
    endpoint_id = request['directive']['endpoint']['endpointId']
    correlation_token = request['directive']['header']['correlationToken']
    power_state_value = None

    alexa_response = AlexaResponse()

    try:
        if namespace == "Alexa.PowerController":
            # The directive to TurnOff or TurnOn the light bulb.
            power_state_value = 'OFF' if name == 'TurnOff' else 'ON'

            alexa_response = handle_power_command(
                namespace=namespace,
                name=supported_capabilities[namespace]["supported"][0]["name"],
                endpoint_id=endpoint_id,
                correlation_token=correlation_token,
                power_state_value=power_state_value
            )

        elif namespace == "Alexa.ToggleController":
            instance = request["directive"]["header"].get(
                "instance", 
                supported_capabilities[namespace].get("instance")
            )
            toggle_state_value = 'OFF' if name == 'TurnOff' else 'ON'

            if instance == "Fan.Oscillate":
                alexa_response = handle_toggle_command(
                    namespace=namespace,
                    name=supported_capabilities[namespace]["supported"][0]["name"],
                    instance=instance,
                    endpoint_id=endpoint_id,
                    correlation_token=correlation_token,
                    toggle_state_value=toggle_state_value
                )

        elif namespace == "Alexa.PercentageController" and name == "SetPercentage":
            percentage_value = request["directive"]["payload"]["percentage"]

            alexa_response = handle_percentage_command(
                namespace=namespace,
                name=supported_capabilities[namespace]["supported"][0]["name"],
                endpoint_id=endpoint_id,
                correlation_token=correlation_token,
                percentage_value=percentage_value
            )

    except HandleCommandException as ex:  # pylint: disable = bare-except
        alexa_response = AlexaResponse(
            name="ErrorResponse",
            payload={
                "type": "ENDPOINT_UNREACHABLE",
                "message": f"[{namespace}.{name}] -> {ex.message}"
            }
        )

    except Exception as ex:
        raise ex

    return alexa_response


def handle_power_command(
    namespace: str,
    name: str,
    endpoint_id: int,
    power_state_value: str,
    correlation_token: str
) -> AlexaResponse:
    command = ArnoCommand()

    command.fan_id = int(endpoint_id)
    command.state = power_state_value == "ON"

    response = sqs_helper(command=command)

    if response.success:
        alexa_response = AlexaResponse(
            correlation_token=correlation_token,
            endpoint_id=endpoint_id,
        )

        alexa_response.add_context_property(
            namespace=namespace,
            name=name,
            value="ON" if response.response_message["state"]
            else "OFF"
        )

        return alexa_response

    raise HandleCommandException(message=response.response_message)


def handle_percentage_command(
    namespace: str,
    name: str,
    endpoint_id: str,
    percentage_value: int,
    correlation_token: str
) -> AlexaResponse:
    command = ArnoCommand()

    command.fan_id = endpoint_id
    command.speed = percentage_value
    command.state = True if percentage_value > 0 else False

    response = sqs_helper(command=command)

    if response.success:
        alexa_response = AlexaResponse(
            correlation_token=correlation_token,
            endpoint_id=endpoint_id
        )

        alexa_response.add_context_property(
            namespace=namespace,
            name=name,
            value=response.response_message["speed"]
        )

        return alexa_response

    raise HandleCommandException(message=response.response_message)


def handle_toggle_command(
        namespace: str,
        name: str,
        instance: str,
        endpoint_id: str,
        toggle_state_value: str,
        correlation_token: str
) -> AlexaResponse:
    command = ArnoCommand()

    command.fan_id = endpoint_id
    command.rotation_direction = 1 if toggle_state_value == "ON" else 0
    command.state = True

    response = sqs_helper(command=command)

    if response.success:
        alexa_response = AlexaResponse(
            correlation_token=correlation_token,
            endpoint_id=endpoint_id
        )

        alexa_response.add_context_property(
            namespace=namespace,
            name=name,
            instance=instance,
            value="ON" if response.response_message["rotation_direction"] else "OFF"
        )

        return alexa_response

    raise HandleCommandException(message=response.response_message)


def lambda_handler(request, context):
    try:
        # Dump the request for logging - check the CloudWatch logs.
        print('lambda_handler request  -----')
        print(json.dumps(request))

        if context is not None:
            print('lambda_handler context  -----')
            print(context)

        # Validate the request is an Alexa smart home directive.
        if 'directive' not in request:
            alexa_response = AlexaResponse(
                name='ErrorResponse',
                payload={
                    'type': 'INVALID_DIRECTIVE',
                    'message': 'Missing key: directive, Is the request a valid Alexa Directive?'
                }
            )
            return send_response(alexa_response.get())

        # Check the payload version.
        payload_version = request['directive']['header']['payloadVersion']
        if payload_version != '3':
            alexa_response = AlexaResponse(
                name='ErrorResponse',
                payload={'type': 'INTERNAL_ERROR',
                         'message': 'This skill only supports Smart Home API version 3'})
            return send_response(alexa_response.get())

        # Crack open the request to see the request.
        name = request['directive']['header']['name']
        namespace = request['directive']['header']['namespace']

        # Handle the incoming request from Alexa based on the namespace.
        if namespace == 'Alexa.Authorization':
            if name == 'AcceptGrant':
                # Note: This example code accepts any grant request.
                # In your implementation,
                # invoke Login With Amazon with the grant code to get access and refresh tokens.
                grant_code = request['directive']['payload']['grant']['code']
                grantee_token = request['directive']['payload']['grantee']['token']

                auth_response = AlexaResponse(
                    namespace='Alexa.Authorization', 
                    name='AcceptGrant.Response'
                )
                
                return send_response(auth_response.get())

        if namespace == 'Alexa.Discovery' and name == 'Discover':
            fan_1 = ArnoFanDiscoveryResponse(friendly_name="Ventilador 0", endpoint_id=0)
            fan_4 = ArnoFanDiscoveryResponse(friendly_name="Ventilador 4", endpoint_id=4)

            return send_response((fan_1 + fan_4).get())
        
        if namespace == "Alexa" and name == "ReportState":
            endpoint_id = request['directive']['endpoint']['endpointId']
            correlation_token = request['directive']['header']['correlationToken']

            command = ArnoCommand()

            command.state_report = True
            command.fan_id = endpoint_id

            response = sqs_helper(command=command)

            if response.success:

                alexa_response = AlexaResponse(
                    correlation_token=correlation_token,
                    endpoint_id=endpoint_id,
                    name="StateReport"
                )

                capability_to_value_map = {
                    "Alexa.PowerController": "ON" if response.response_message["state"] else "OFF",
                    "Alexa.PercentageController": response.response_message["speed"],
                    "Alexa.ToggleController": "ON" \
                        if response.response_message["rotation_direction"] \
                            else "OFF",
                }

                for key, value in capability_to_value_map.items():
                    if(supported_capabilities[key].get("instance")):
                        alexa_response.add_context_property(
                            namespace=key,
                            name=supported_capabilities[key]["supported"][0]["name"],
                            value=value,
                            instance=supported_capabilities[key].get("instance")
                        )

                        continue
                    alexa_response.add_context_property(
                        namespace=key,
                        name=supported_capabilities[key]["supported"][0]["name"],
                        value=value
                    )

                return send_response(alexa_response.get())

            return send_response(AlexaResponse(
                    name="ErrorResponse",
                    payload={
                        "type": "ENDPOINT_UNREACHABLE",
                        "message": response.response_message
                    }).get()
            )

        if supported_capabilities.get(namespace, None):
            return send_response(
                handle_command(
                    namespace=namespace,
                    name=name,
                    request=request
                ).get()
            )

        return send_response(AlexaResponse(
                name="ErrorResponse",
                payload={
                    "type": "INVALID_DIRECTIVE",
                    "message": "COMMAND INVALID"
                }
            ).get()
        )
    
    except Exception as ex:  # pylint: disable = broad-exception-caught
        return send_response(AlexaResponse(
                name="ErrorResponse",
                payload={
                    "type": "INTERNAL_ERROR",
                    "message": f"COMMAND INVALID => {ex}\nStack:{format_exc()}"
                }
            ).get()
        )


def send_response(response):
    print('lambda_handler response -----')
    print(json.dumps(response))
    return response


if __name__ == "__main__":
    TEST = {
  "directive": {
    "header": {
      "namespace": "Alexa.Discovery",
      "name": "Discover",
      "messageId": "Unique identifier, preferably a version 4 UUID",
      "payloadVersion": "3"
    },
    "payload": {
      "scope": {
        "type": "BearerToken",
        "token": "OAuth2.0 bearer token"
      }
    }
  }
}


    TEST_CONTEXT = ""

    lambda_handler(TEST, TEST_CONTEXT)
