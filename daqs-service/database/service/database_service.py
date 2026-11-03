from datetime import datetime
from typing import List

from sqlalchemy.orm import Session, sessionmaker

from database.domain.models.device import Device
from database.domain.models.measurement import DeviceL, Measurement
from database.infrastructure.models.device import DeviceORM
from database.infrastructure.models.measurement import MeasurementORM
from database.infrastructure.repositories.device_repository import DeviceRepository
from database.infrastructure.repositories.measurement_repository import MeasurementRepository
from database.utils.hasher import Hasher


class DatabaseService:

    def __init__(self, session_factory: sessionmaker[Session]):
        self._session_factory = session_factory
        self._hasher = Hasher()

    def get_device(self, device_hash: str) -> Device:
        id_ = self._hasher.decode(device_hash)
        with self._session_factory() as session:
            orm = DeviceRepository(session).get_by_id(id_)
            return self._device_to_model(orm)

    def get_all_devices(self) -> List[Device]:
        with self._session_factory() as session:
            return [self._device_to_model(o) for o in DeviceRepository(session).get_all()]

    def add_new_device(self, device: Device) -> str:
        orm = self._device_to_orm(device, is_new=True)
        with self._session_factory.begin() as session:
            created_id = DeviceRepository(session).create(orm)
        return self._hasher.encode(created_id)

    def update_device(self, device: Device) -> str:
        orm = self._device_to_orm(device)
        with self._session_factory.begin() as session:
            repo = DeviceRepository(session)
            updated_id = repo.update(orm)
        return self._hasher.encode(updated_id)

    def delete_device(self, device_hash: str) -> bool:
        id_ = self._hasher.decode(device_hash)
        with self._session_factory.begin() as session:
            DeviceRepository(session).delete(id_)

    def add_new_measurement(self, measurement: Measurement) -> str:
        orm = MeasurementORM(
            device_id=self._hasher.decode(measurement.device.hash),
            time=measurement.time,
            t1=measurement.t1,
            t2=measurement.t2,
            voltage=measurement.voltage,
        )
        with self._session_factory.begin() as session:
            created_id = MeasurementRepository(session).create(orm)
        return self._hasher.encode(created_id)

    def record_measurement(self, device_hash: str, time: datetime,
                           t1: float, t2: float, voltage: float) -> None:
        orm = MeasurementORM(
            device_id=self._hasher.decode(device_hash),
            time=time, t1=t1, t2=t2, voltage=voltage,
        )
        with self._session_factory.begin() as session:
            MeasurementRepository(session).create(orm)

    def list_measurements(
            self,
            filters: list[dict],
            page_index: int,
            page_size: int,
    ) -> tuple[list[Measurement], int]:
        page_index = max(0, page_index)
        page_size = min(max(1, page_size), 50)

        with self._session_factory() as session:
            resolved = self._resolve_filters(session, filters)

            orms, total = MeasurementRepository(session).get_all(
                resolved, page_index, page_size
            )

            device_ids = {orm.device_id for orm in orms}
            device_list = DeviceRepository(session).get_all_by_id(device_ids)
            devices = {d.id: d for d in device_list}

            result = [
                self._measurement_to_model(orm, devices[orm.device_id])
                for orm in orms
            ]
        return result, total

    def _resolve_filters(self, session: Session, filters: list[dict]) -> list[dict]:
        resolved = []
        device_repo = DeviceRepository(session)

        for f in filters:
            if f.get("id") == "device" and isinstance(f.get("value"), str) and f["value"].strip():
                needle = f["value"].strip().lower()
                matching_ids = [
                    d.id
                    for d in device_repo.get_all()
                    if needle in (d.name or "").lower()
                ]
                resolved.append({"id": "device_ids", "value": matching_ids})
            else:
                resolved.append(f)

        return resolved

    def _device_to_model(self, orm: DeviceORM) -> Device:
        return Device(
            hash=self._hasher.encode(orm.id),
            name=orm.name,
            logo=orm.logo,
            resource_address=orm.resource_address,
            thermocouple_1_slot=orm.thermocouple_1_slot,
            thermocouple_1_channel=orm.thermocouple_1_channel,
            thermocouple_2_slot=orm.thermocouple_2_slot,
            thermocouple_2_channel=orm.thermocouple_2_channel,
            voltage_slot=orm.voltage_slot,
            voltage_channel=orm.voltage_channel,
        )

    def _device_to_orm(self, device: Device, is_new: bool = False) -> DeviceORM:
        orm = DeviceORM(
            name=device.name,
            logo=device.logo,
            resource_address=device.resource_address,
            thermocouple_1_slot=device.thermocouple_1_slot,
            thermocouple_1_channel=device.thermocouple_1_channel,
            thermocouple_2_slot=device.thermocouple_2_slot,
            thermocouple_2_channel=device.thermocouple_2_channel,
            voltage_slot=device.voltage_slot,
            voltage_channel=device.voltage_channel,
        )

        if not is_new:
            orm.id = self._hasher.decode(device.hash)

        return orm

    def _measurement_to_model(self, orm: MeasurementORM, device_orm: DeviceORM) -> Measurement:
        return Measurement(
            hash=self._hasher.encode(orm.id),
            device=DeviceL(
                hash=self._hasher.encode(device_orm.id),
                logo=device_orm.logo,
                name=device_orm.name,
            ),
            time=orm.time,
            t1=orm.t1,
            t2=orm.t2,
            voltage=orm.voltage,
        )


