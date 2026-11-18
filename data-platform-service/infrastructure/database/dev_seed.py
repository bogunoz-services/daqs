import os
import random
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select

from infrastructure.database.connection import SessionLocal
from infrastructure.models.device import DeviceORM
from infrastructure.models.measurement import MeasurementORM

POINTS_PER_DEVICE = 300
STEP = timedelta(minutes=5)
SEEBECK_V_PER_K = 180e-6


def _device(name: str, logo: str, address: str, base: int) -> DeviceORM:
    return DeviceORM(
        name=name, logo=logo, resource_address=address,
        voltage_slot="2", voltage_channel=str(base + 1),
        port="/dev/ttyACM0",
    )


def seed_dev_data() -> None:
    print("SEED: START", flush=True)

    if os.getenv("SEED_DEV_DATA") != "1":
        print("Seed not required")
        return

    rng = random.Random(42)

    with SessionLocal.begin() as session:
        count = session.scalar(
            select(func.count()).select_from(DeviceORM)
        )

        print(f"SEED: existing devices = {count}", flush=True)

        if count:
            print("SEED: SKIPPED", flush=True)
            return

        devices = [
            _device("DAQ6510-A", "cpu", "TCPIP0::192.168.1.10::inst0::INSTR", 100),
            _device("DAQ6510-B", "gauge", "TCPIP0::192.168.1.11::inst0::INSTR", 200),
            _device("Modbus-Gateway-01", "router", "TCPIP0::192.168.1.12::inst0::INSTR", 300),
        ]

        session.add_all(devices)
        session.flush()

        print(f"SEED: created devices = {len(devices)}", flush=True)

        now = datetime.now(timezone.utc)
        rows = []

        for device in devices:
            t1, t2 = rng.uniform(30, 40), rng.uniform(22, 28)

            for i in range(POINTS_PER_DEVICE):
                t1 += rng.gauss(0, 0.15)
                t2 += rng.gauss(0, 0.10)

                voltage = (t1 - t2) * SEEBECK_V_PER_K + rng.gauss(0, 2e-6)

                rows.append(
                    MeasurementORM(
                        device_id=device.id,
                        time=now - STEP * (POINTS_PER_DEVICE - i),
                        t1=t1,
                        t2=t2,
                        voltage=voltage,
                    )
                )

        print(f"SEED: measurements prepared = {len(rows)}", flush=True)

        session.add_all(rows)

    print("SEED: COMMIT COMPLETED", flush=True)