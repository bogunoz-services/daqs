from datetime import datetime

from pydantic import BaseModel, Field


class RecordMeasurementRequest(BaseModel):
    device_hash: str = Field(min_length=1)
    time: datetime
    t1: float
    t2: float
    voltage: float = Field(description="Voltage in volts")