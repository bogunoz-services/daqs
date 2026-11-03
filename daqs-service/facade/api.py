import asyncio

from container import Services
from facade.websocket.broadcaster import StateBroadcaster
from facade.websocket.connections import ConnectionRegistry
from facade.websocket.handlers.database import DatabaseHandlers
from facade.websocket.handlers.experiment import ExperimentHandlers
from facade.websocket.router import Router
from facade.websocket.server import WebSocketServer


class WebSocketApi:
    def __init__(self, server: WebSocketServer, broadcaster: StateBroadcaster) -> None:
        self._server = server
        self._broadcaster = broadcaster

    async def run(self) -> None:
        await asyncio.gather(
            self._server.serve_forever(),
            self._broadcaster.run(),
        )


def build_websocket_api(services: Services, host: str = "localhost", port: int = 12345) -> WebSocketApi:
    router = Router()
    ExperimentHandlers(services.experiment).register(router)
    DatabaseHandlers(services.database).register(router)

    registry = ConnectionRegistry()
    server = WebSocketServer(router, registry, host, port)
    broadcaster = StateBroadcaster(services.experiment, registry)

    return WebSocketApi(server, broadcaster)