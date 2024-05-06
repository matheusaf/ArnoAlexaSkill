import asyncio
import json
import logging as lg
from datetime import datetime
from threading import Event
from traceback import format_exc

import aiohttp as req

from clients import HttpClient, SqsClient
from commands import ArnoCommand, ArnoCommandDecoder
from models import ArnoResponse

HOME_QUEUE = "XXXXXXXXXXXXXXXXXXXXXX"
ALEXA_QUEUE = "XXXXXXXXXXXXXXXXXXXXXX"
BACKEND_BASE_URL = "XXXXXXXXXXXXXXXXXXXXXX"

MAX_ITEMS_STACK = 15

TIME_INTERVAL_SEC = 0

CUR_TIMEZONE_NAME = "XXXXXXXXXXXXXXXXXXXXXX"

root_log = lg.getLogger("root")

file_logger = lg.FileHandler(
    filename=f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log", encoding="utf-8"
)
file_logger.setLevel(lg.DEBUG)
file_logger.setFormatter(
    lg.Formatter(
        "(%(asctime)s)[%(levelname)s:%(name)s] %(module)s.%(filename)s.%(funcName)s => | %(message)s |" # noqa
    )
)
file_logger.addFilter(lg.Filter(name="root"))

stdout_logger = lg.StreamHandler()
stdout_logger.setLevel(lg.WARNING)

root_log.setLevel(lg.DEBUG)
root_log.addHandler(file_logger)
root_log.addHandler(stdout_logger)

response_stack = []


def handle_response_stack(sqs_client: SqsClient, max_tries=5, interval=1) -> None:
    while len(response_stack) > 0:
        cur_try = 0
        top_item = response_stack.pop(-1)
        exit_flag = Event()
        while cur_try < max_tries and not exit_flag.wait(interval * cur_try):
            try:
                post_alexa_queue_message(sqs_client, str(top_item))
                return
            except Exception as ex:  # pylint: disable = broad-except
                cur_try += 1
                lg.log(
                    lg.ERROR,
                    "exception %s caught when posting message to alexa queue (try %d of %d)\nstack%s", # noqa
                    ex,
                    cur_try + 1,
                    max_tries,
                    format_exc()
                )


def post_alexa_queue_message(sqs_client: SqsClient, message: str) -> None:
    sqs_client.send_message(ALEXA_QUEUE, message)


async def main() -> None:
    while True:
        try:
            sqs_client = SqsClient()

            messages = sqs_client.fetch_messages(HOME_QUEUE)

            message_received = messages["Messages"][0]

            message_receipt_handle = message_received["ReceiptHandle"]

            message_body = message_received["Body"]

            lg.log(
                lg.INFO, "message %s received with body %s",
                message_receipt_handle,
                message_body
            )

            sqs_client.delete_message(HOME_QUEUE, message_receipt_handle)

            lg.log(
                lg.INFO, "message %s deleted",
                message_receipt_handle
            )

            async with req.ClientSession() as session:
                http_client = HttpClient(session)

                lg.log(lg.INFO, "calling API with %s", message_body)

                command: ArnoCommand = json.loads(
                    message_body,
                    cls=ArnoCommandDecoder
                )

                response = await http_client.patch(
                    f"{BACKEND_BASE_URL}/{command.fan_id}",
                    body=str(command)
                )

                response.raise_for_status()

                lg.log(
                    lg.INFO,
                    "[%d] -> %s {%s}",
                    response.status,
                    response.url,
                    await response.text()
                )

                response_body = await response.json()

                arno_response = ArnoResponse(
                    status_code=response.status,
                    response_message=response_body,
                    success=response.ok
                )

                try:
                    post_alexa_queue_message(sqs_client, str(arno_response))
                except Exception as ex:  # pylint: disable = broad-except
                    if len(response_stack) > 5:
                        response_stack.pop(0)
                        response_stack.append(arno_response)
                        raise ex
                    handle_response_stack(sqs_client)

        except Exception as ex:  # pylint: disable = broad-except
            lg.log(lg.ERROR, "exception %ex caught\nstack%s", ex, format_exc())

    # fan_id: int
    # speed: int
    # rotation_direction: RotationDirection
    # state: bool

asyncio.run(main())
