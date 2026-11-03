import websockets


class ConnectionRegistry:
    def __init__(self) -> None:
        self._clients: set = set()

    def register(self, websocket) -> None:
        self._clients.add(websocket)

    def unregister(self, websocket) -> None:
        self._clients.discard(websocket)

    def broadcast(self, message: str) -> None:
        if self._clients:
            websockets.broadcast(self._clients, message)