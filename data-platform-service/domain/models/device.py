from dataclasses import dataclass


@dataclass
class Device:
    id: int | None
    name: str
    logo: str
    resource_address: str
    voltage_slot: str
    voltage_channel: str
    port: str
