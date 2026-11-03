import asyncio

from experiment.service.experiment_service import ExperimentService
from facade.websocket.connections import ConnectionRegistry
from facade.websocket.protocol import Event
from facade.websocket.utils.handlers_actions import ExperimentActions


class StateBroadcaster:
    def __init__(self, service: ExperimentService, registry: ConnectionRegistry,
                 interval: float = 1.0) -> None:
        self._service = service
        self._registry = registry
        self._interval = interval

    async def run(self) -> None:
        while True:
            event = Event(ExperimentActions.STATUS.value, self._service.get_state())
            self._registry.broadcast(event.to_json())

            await asyncio.sleep(self._interval)