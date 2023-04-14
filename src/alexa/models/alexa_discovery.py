from typing import List

from alexa.models.alexa_response import AlexaResponse


class AlexaDiscoveryResponse(AlexaResponse):
    __slots__ = [
        "__capabilities_"
    ]

    __capabilities_: List[dict]

    def __init__(self, namespace="Alexa.Discovery", name="Discover.Response") -> None:
        super().__init__(namespace=namespace, name=name)
        self.__capabilities_ = []

    @property
    def capabilities(self) -> List[dict]:
        return [*self.__capabilities_]

    def add_capability(self, **kwargs) -> None:
        self.__capabilities_.append(
            super().create_payload_endpoint_capability(**kwargs)
        )
