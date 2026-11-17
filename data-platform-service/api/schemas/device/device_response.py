from pydantic import BaseModel
class DeviceResponse(BaseModel):
    hash: str
    name: str
    logo: str
    resource_address: str
    voltage_slot: str
    voltage_channel: str
    port: str