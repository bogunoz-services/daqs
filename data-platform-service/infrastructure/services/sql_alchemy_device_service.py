from typing import List

from domain.models.device import Device
from domain.services.device_service import DeviceService
from infrastructure.repositories.sql_alchemy_device_repository import DeviceRepository
from utils.hasher import Hasher


class SqlAlchemyDeviceService(DeviceService):
    def __init__(self, devices: DeviceRepository, hasher: Hasher = Hasher()):
        self._devices = devices
        self._hasher = hasher

    def get_device(self, device_id: int) -> Device:
        return self._devices.get_by_id(device_id)

    def get_all_devices(self) -> List[Device]:
        return self._devices.get_all()

    def add_new_device(self, device: Device) -> None:
        return self._devices.create(device)

    def update_device(self, device: Device) -> None:
        return self._devices.update(device)

    def delete_device(self, device_id: int) -> bool:
        return self._devices.delete(device_id)