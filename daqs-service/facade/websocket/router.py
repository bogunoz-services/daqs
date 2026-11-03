from typing import Callable, Awaitable, Any

from experiment.service.exceptions import ServiceError
from facade.websocket.protocol import Response, Request, UnknownActionError, ProtocolError

Handler = Callable[[dict], Awaitable[Any]]

class Router:
    def __init__(self) -> None:
        self._routes: dict[str, Handler] = {}

    def add(self, action: str, handler: Handler) -> None:
        self._routes[action] = handler

    async def dispatch(self, raw: str) -> Response:
        request_id = None
        try:
            request = Request.parse(raw)
            request_id = request.id
            handler = self._routes.get(request.action)
            if not handler:
                raise UnknownActionError()
            result = await handler(request.payload)
            return Response.success(request_id, result)

        except ProtocolError as e:
            return Response.failure(request_id)
        except ServiceError as e:
            return Response.failure(request_id)
        except Exception:
            return Response.failure(request_id)

