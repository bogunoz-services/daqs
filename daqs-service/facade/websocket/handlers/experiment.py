import asyncio

from experiment.service.experiment_service import ExperimentService
from facade.websocket.router import Router
from facade.websocket.utils.handlers_actions import ExperimentActions


class ExperimentHandlers:
    def __init__(self, service: ExperimentService) -> None:
        self._service = service

    def register(self, router: Router) -> None:
        router.add(ExperimentActions.START.value, self.start)
        router.add(ExperimentActions.STOP.value, self.stop)
        router.add(ExperimentActions.DEVICE_STATUS.value, self.device_status)
        router.add(ExperimentActions.GET_HISTORY.value, self.get_history)
        router.add(ExperimentActions.UPDATE_CHANNEL_MAP.value, self.update_channel_map)
        router.add(ExperimentActions.UPDATE_CONNECTION_CONFIG.value, self.update_connection_config)

    async def start(self, payload: dict) -> dict:
        await asyncio.to_thread(self._service.start)  # wolne (VISA) -> osobny wątek
        return {}

    async def stop(self, payload: dict) -> dict:
        await asyncio.to_thread(self._service.stop)
        return {}

    async def device_status(self, payload: dict) -> bool:
        return self._service.is_connected()

    async def get_history(self, payload: dict) -> dict:
        return self._service.get_history()

    async def update_channel_map(self, payload: dict) -> dict:
        await asyncio.to_thread(self._service.update_channel_map, payload.get("channels"))
        return {}

    async def update_connection_config(self, payload: dict) -> dict:
        await asyncio.to_thread(self._service.update_connection_config, payload.get("connection"))
        return {}
