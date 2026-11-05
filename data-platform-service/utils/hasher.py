from typing import Optional
from sqids import Sqids


class Hasher:
    def __init__(self, min_length: int = 24, alphabet: Optional[str] = None,):
        kwargs = {"min_length": min_length}
        if alphabet is not None:
            kwargs["alphabet"] = alphabet

        self._sqids = Sqids(**kwargs)

    def encode(self, id_: int) -> str:
        return self._sqids.encode([id_])

    def decode(self, encoded: str) -> int:
        result = self._sqids.decode(encoded)
        return result[0]

