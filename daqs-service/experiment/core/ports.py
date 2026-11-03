from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


@dataclass(frozen=True)
class MeasurementRecord:
    device_hash: str
    time: datetime
    t1: float
    t2: float
    voltage: float


class MeasurementSink(Protocol):
    def write(self, record: MeasurementRecord) -> None: ...