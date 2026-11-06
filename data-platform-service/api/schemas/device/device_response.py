from pydantic import BaseModel
class DeviceResponse(BaseModel):
    hash: str
    name: str
    logo: str
    resource_address: str
    thermocouple_1_slot: str
    thermocouple_1_channel: str
    thermocouple_2_slot: str
    thermocouple_2_channel: str
    voltage_slot: str
    voltage_channel: str