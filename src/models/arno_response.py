import json

from utils import build_dict_public_properties


class ArnoResponse:
    __slots__ = [
        "__status_code_",
        "__response_message_",
        "__success_"
    ]

    __status_code_: int
    __response_message_: dict
    __success_: bool

    def __init__(
        self, 
        status_code: int = -1, 
        response_message: dict = {}, 
        success: bool = False
    ) -> None:
        self.__status_code_ = status_code
        self.__success_ = success
        self.__response_message_ = response_message

    @property
    def status_code(self) -> int:
        return self.__status_code_

    @status_code.setter
    def status_code(self, value: int) -> None:
        self.__status_code_ = value

    @property
    def response_message(self) -> dict:
        return self.__response_message_

    @response_message.setter
    def response_message(self, value: dict) -> None:
        self.__response_message_ = value

    @property
    def success(self) -> bool:
        return self.__success_

    @success.setter
    def success(self, value: bool) -> None:
        self.__success_ = value

    def __str__(self) -> str:
        return json.dumps(self, cls=ArnoResponseEncoder)

    def __repr__(self) -> str:
        return self.__str__()


class ArnoResponseEncoder(json.JSONEncoder):
    def default(self, o: object) -> dict:
        return build_dict_public_properties(o)


class ArnoResponseDecoder(json.JSONDecoder):
    def decode(self, s: str) -> ArnoResponse:
        obj = ArnoResponse()
        obj_dict = json.loads(s)

        for key, value in obj_dict.items():
            if key in dir(obj):
                setattr(obj, key, value)

        return obj
