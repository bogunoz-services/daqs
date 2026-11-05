from typing import List

from domain.models.device import Device
from infrastructure.models.device import DeviceORM
from infrastructure.repositories.sql_alchemy_device_repository import DeviceRepository
from utils.hasher import Hasher

from sqlalchemy.orm import Session, sessionmaker


class DeviceService:
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