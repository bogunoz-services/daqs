class InstrumentError(Exception):
    """Bazowy wyjątek dla wszystkich błędów komunikacji z przyrządem."""
    pass

class InstrumentTimeoutError(InstrumentError):
    pass

class InstrumentDisconnectedError(InstrumentError):
    pass

class InstrumentNotFoundError(InstrumentError):
    pass

class InstrumentWriteError(InstrumentError):
    pass
