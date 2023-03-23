import json
from typing import Optional

from utils import build_dict_public_properties


class ArnoCommand:
    __fan_id_: int = -1
    __speed_: Optional[int] = None
    __rotation_: Optional[int] = None
    __state_: Optional[bool] = None

    def __init__(self) -> None:
        pass

    @property
    def fan_id(self) -> int:
        return self.__fan_id_

    @fan_id.setter
    def fan_id(self, fan_id: int) -> None:
        self.__fan_id_ = fan_id

    @property
    def speed(self) -> Optional[int]:
        return self.__speed_

    @speed.setter
    def speed(self, value: Optional[int]) -> None:
        self.__speed_ = value

    @property
    def rotation(self) -> Optional[int]:
        return self.__rotation_

    @rotation.setter
    def rotation(self, value: Optional[int]) -> None:
        self.__rotation_ = value

    @property
    def state(self) -> Optional[bool]:
        return self.__state_

    @state.setter
    def state(self, value: Optional[bool]) -> None:
        self.__state_ = value

    def __str__(self) -> None:
        return json.dumps(self, cls=ArnoCommandEncoder)

    def __repr__(self) -> None:
        return self.__str__()


class ArnoCommandEncoder(json.JSONEncoder):
    def default(self, o: object) -> dict:
        return build_dict_public_properties(o)


class ArnoCommandDecoder(json.JSONDecoder):
    def decode(self, s: str) -> ArnoCommand:
        obj = ArnoCommand()
        obj_dict = json.loads(s)

        for key, value in obj_dict.items():
            if key in dir(obj):
                setattr(obj, key, value)

        return obj