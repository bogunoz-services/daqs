import asyncio

import websockets
from websockets import ConnectionClosed

from facade.websocket.connections import ConnectionRegistry
from facade.websocket.router import Router


class WebSocketServer:
    def __init__(self, router: Router, registry: ConnectionRegistry,
                 host: str = "0.0.0.0", port: int = 12345) -> None:
        self._router = router
        self._registry = registry
        self._host = host
        self._port = port

    async def serve_forever(self) -> None:
        async with websockets.serve(self._handle, self._host, self._port):
            await asyncio.Future()  # czekaj bez końca, aż ktoś anuluje

    async def _handle(self, websocket) -> None:
        self._registry.register(websocket)
        try:
            async for raw in websocket:
                response = await self._router.dispatch(raw)
                await websocket.send(response.to_json())
        except ConnectionClosed:
            pass
        finally:
            self._registry.unregister(websocket)