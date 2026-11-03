# services/exceptions.py
class ServiceError(Exception):
    pass
class ExperimentRunningError(ServiceError):
    pass

class InstrumentUnavailableError(ServiceError):
    pass

class InvalidConfigError(ServiceError):
    pass