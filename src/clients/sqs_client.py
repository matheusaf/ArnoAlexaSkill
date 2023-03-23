from typing import List

import boto3 as b3


class SqsClient:
    __slots__ = [
        "__sqs_client_"
    ]

    __sqs_client_: object

    def __init__(self) -> None:
        self.__sqs_client_ = b3.client("sqs")

    # ["device_id", "command", "repeat"]

    def fetch_messages(self,
                       sqs_url: str,
                       max_number_of_messages=1,
                       wait_time_seconds=20,
                       attributes_list: List[str] = []) -> object:
        message_attribute_names = []
        if attributes_list is not None and len(attributes_list) > 0:
            message_attribute_names.append("All")
        return self.__sqs_client_.receive_message(
            QueueUrl=sqs_url,
            WaitTimeSeconds=wait_time_seconds,
            MaxNumberOfMessages=max_number_of_messages,
            MessageAttributeNames=message_attribute_names,
            AttributeNames=attributes_list
        )

    def send_message(self, sql_url: str, message: object, delay_seconds=0) -> None:
        self.__sqs_client_.send_message(
            QueueUrl=sql_url,
            DelaySeconds=delay_seconds,
            MessageBody=message
        )

    def delete_message(self, sqs_url: str, receipt_handle: str) -> None:
        self.__sqs_client_.delete_message(
            QueueUrl=sqs_url,
            ReceiptHandle=receipt_handle
        )
