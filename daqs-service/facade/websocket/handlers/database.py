import asyncio
from dataclasses import asdict

from database.domain.models.device import Device
from database.domain.models.measurement import Measurement
from database.service.database_service import DatabaseService
from facade.websocket.protocol import ProtocolError
from facade.websocket.router import Router
from facade.websocket.utils.handlers_actions import DatabaseActions


class DatabaseHandlers:
    def __init__(self, service: DatabaseService) -> None:
        self._service = service

    def register(self, router: Router) -> None:
        router.add(DatabaseActions.GET_DEVICE.value, self.get_device)
        router.add(DatabaseActions.GET_ALL_DEVICES.value, self.get_all_devices)
        router.add(DatabaseActions.ADD_NEW_DEVICE.value, self.add_new_device)
        router.add(DatabaseActions.UPDATE_DEVICE.value, self.update_device)
        router.add(DatabaseActions.DELETE_DEVICE.value, self.delete_device)
        router.add(DatabaseActions.LIST_MEASUREMENTS.value, self.list_measurements)

    async def get_device(self, payload: dict) -> dict:
        device = self._service.get_device(payload["device_hash"])
        return {"device": None if device is None else asdict(device)}

    async def get_all_devices(self, payload: dict) -> dict:
        devices = self._service.get_all_devices()
        return {"items": [asdict(d) for d in devices]}

    async def add_new_device(self, payload: dict) -> dict:
        device = self._device_from_dict(payload.get("device"), is_new=True)
        device_hash = await asyncio.to_thread(self._service.add_new_device, device)
        return {"hash": device_hash}

    async def update_device(self, payload: dict) -> dict:
        device = self._device_from_dict(payload.get("device"))
        device_hash = await asyncio.to_thread(self._service.update_device, device)
        return {"hash": device_hash}

    async def delete_device(self, payload: dict) -> dict:
        await asyncio.to_thread(self._service.delete_device, payload.get("device_hash"))
        return {}

    async def list_measurements(self, payload: dict) -> dict:
        items, total = await asyncio.to_thread(
            self._service.list_measurements,
            payload.get("filters", []),
            payload.get("page_index", 0),
            payload.get("page_size", 20),
        )
        return {
            "items": [self._measurement_to_wire(m) for m in items],
            "total": total,
        }

    def _device_from_dict(self, data, *, is_new: bool = False) -> Device:
        if not isinstance(data, dict):
            raise ProtocolError()
        fields = {**data, "hash": ""} if is_new else data
        try:
            return Device(**fields)
        except TypeError as e:
            raise ProtocolError() from e

    def _measurement_to_wire(self, m: Measurement) -> dict:
        return {
            "hash": m.hash,
            "device": {
                "hash": m.device.hash,
                "name": m.device.name,
                "logo": m.device.logo,
            },
            "time": m.time.isoformat(),  # datetime → string
            "t1": m.t1,
            "t2": m.t2,
            "voltage": m.voltage,
        }