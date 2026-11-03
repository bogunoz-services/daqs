from dataclasses import dataclass
from datetime import datetime

@dataclass
class DeviceL:
    hash: str
    name: str
    logo: str

@dataclass
class Measurement:
    hash: str
    device: DeviceL
    time: datetime
    t1: float
    t2: float
    voltage: float