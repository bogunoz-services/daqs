import json
from dataclasses import dataclass
from typing import Any


class ProtocolError(Exception):
    code = "BAD_REQUEST"

class UnknownActionError(ProtocolError):
    code = "UNKNOWN_ACTION"

@dataclass(frozen=True)
class Request:
    id: str
    action: str
    payload: dict

    @classmethod
    def parse(cls, raw: str) -> "Request":
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as e:
            raise ProtocolError()
        if not isinstance(data, dict) or not isinstance(data.get("action"), str):
            raise ProtocolError()
        payload = data.get("payload", {})
        if not isinstance(payload, dict):
            raise ProtocolError()
        return cls(id=data.get("id"), action=data["action"], payload=payload)


@dataclass(frozen=True)
class Response:
    id: str
    ok: bool
    payload: Any = None

    @classmethod
    def success(cls, request_id, payload) -> "Response":
        return cls(id=request_id, ok=True, payload=payload if payload is not None else {})

    @classmethod
    def failure(cls, request_id) -> "Response":
        return cls(id=request_id, ok=False)

    def to_json(self) -> str:
        return json.dumps({"type": "response", "id": self.id, "ok": self.ok,
                           "payload": self.payload})


@dataclass(frozen=True)
class Event:
    name: str
    payload: Any

    def to_json(self) -> str:
        return json.dumps({"type": self.name, "payload": self.payload})