import json

from .alexa_discovery import AlexaDiscoveryResponse


class ArnoFanDiscoveryResponse(AlexaDiscoveryResponse):

    __supported_capabilities_ = {
        "Alexa.EndpointHealth": {
            "supported": [
                {"name": "connectivity"},
            ]
        },
        "Alexa.PowerController": {
            "supported": [
                {"name": "powerState"},
            ],
            "retrievable": True,
            "proactively_reported": True
        },
        "Alexa.PercentageController": {
            "supported": [
                {"name": "percentage"},
            ],
            "retrievable": True,
            "proactively_reported": True
        },
        "Alexa.ToggleController": {
            "instance": "Fan.Oscillate",
            "supported": [
                {"name": "toggleState"},
            ],
            "retrievable": True,
            "proactively_reported": True,
            "capabilityResources": {
                "friendlyNames": [
                    {
                        "@type": "asset",
                        "value": {
                            "assetId": "Alexa.Setting.Oscillate"
                        }
                    },
                    {
                        "@type": "text",
                        "value": {
                            "text": "girar",
                            "locale": "pt-BR"
                        }
                    },
                    {
                        "@type": "text",
                        "value": {
                            "text": "girar",
                            "locale": "es-MX"
                        }
                    },
                    {
                        "@type": "text",
                        "value": {
                            "text": "spin",
                            "locale": "en-US"
                        }
                    }
                ]
            }
        },
    }

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
                 custom_identifier="Arno Ventilador VX-10") -> None:
        super().__init__()

        super().add_capability()

        for interface, capability in self.__supported_capabilities_.items():
            super().add_capability(interface=interface, **capability)

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

    def __add__(self, obj: object) -> object:
        self.payload_endpoints.append(*obj.payload_endpoints)
        return self

    @classmethod
    def supported_capabilities(cls) -> list:
        return {**cls.__supported_capabilities_}


if __name__ == "__main__":
    fan_1 = ArnoFanDiscoveryResponse("Ventilador 1", 1)
    fan_4 = ArnoFanDiscoveryResponse("Ventilador 4", 4)
    print(json.dumps((fan_1 + fan_4).get(), indent=4))
    print(ArnoFanDiscoveryResponse.supported_capabilities())
