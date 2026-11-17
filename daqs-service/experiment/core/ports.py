# experiment/core/ports.py  (rozszerzenie)

from typing import Protocol
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class MeasurementRecord:
    device_hash: str
    time: datetime
    t1: float
    t2: float
    voltage: float


class MeasurementSink(Protocol):
    def write(self, record: MeasurementRecord) -> None: ...


@dataclass(frozen=True)
class Sample:
    t1: float
    t2: float
    voltage: float