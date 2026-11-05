from datetime import datetime
from pydantic import BaseModel


class DeviceInfo(BaseModel):
    hash: str
    name: str
    logo: str


class MeasurementListItem(BaseModel):
    hash: str
    device: DeviceInfo
    time: datetime
    t1: float
    t2: float
    voltage: float


class ListMeasurementsResponse(BaseModel):
    items: list[MeasurementListItem]
    total: int
    page_index: int
    page_size: int