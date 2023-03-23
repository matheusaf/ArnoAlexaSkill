import json
from typing import List

from .alexa_response import AlexaResponse


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


DEFAULT_FAN_CAPABILITIES = [
    {
        "interface": "Alexa.EndpointHealth",
        "supported": [
            {"name": "connectivity"},
        ]
    },
    {
        "interface": "Alexa.PowerController",
        "supported": [
            {"name": "powerState"},
        ],
        "retrievable": True,
        "proactively_reported": True
    },
    {
        "interface": "Alexa.PercentageController",
        "instance": "Fan.Speed",
        "supported": [
            {"name": "percentage"},
        ],
        "retrievable": True,
        "proactively_reported": True
    },
    {
        "interface": "Alexa.ToggleController",
        "instance": "Fan.Oscillate",
        "supported": [
            {"name": "toggleState"},
        ],
        "retrievable": True,
        "proactively_reported": True
    },
]


class ArnoFanDevice(AlexaDiscoveryResponse):
    def __init__(self,
                 friendly_name: str,
                 endpoint_id: int,
                 manufacturer="Arno",
                 model_name="VX10",
                 serial_number="ARNO_VX10_2023",
                 firmware_version="1.0.0a",
                 software_version="1.0.0a",
                 description="Ventilador de Teto",
                 display_categories=["FAN"],
                 manufacturer_name="Arno",
                 custom_identifier="Arno Ventilador VX-10",
                 capabilities=DEFAULT_FAN_CAPABILITIES) -> None:
        super().__init__()

        super().add_capability()

        for capability in capabilities:
            super().add_capability(**capability)


        super().add_payload_endpoint(
            friendly_name=friendly_name,
            endpoint_id=endpoint_id,
            capabilities=self.capabilities,
            manufacturer=manufacturer,
            model_name=model_name,
            serial_number=serial_number,
            firmware_version=firmware_version,
            software_version=software_version,
            description=description,
            display_categories=display_categories,
            manufacturer_name=manufacturer_name,
            custom_identifier=custom_identifier
        )


if __name__ == "__main__":
    fan = ArnoFanDevice("Ventilador 1", 1)
    print(json.dumps(fan.get(), indent=4))
