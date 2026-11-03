import pyvisa
from pyvisa.constants import StatusCode

from daq6510.transport.exceptions import InstrumentTimeoutError, InstrumentDisconnectedError, \
    InstrumentNotFoundError, InstrumentError, InstrumentWriteError


class VisaConnection:
    def __init__(
            self, resource_address: str,
            resource_manager: pyvisa.ResourceManager):
        self._resource_manager = resource_manager
        self._resource_address = resource_address
        self._instrument = None

    def open(self):
        self._instrument = self._resource_manager.open_resource(self._resource_address, open_timeout = 2500)

    def query(self, command: str) -> str:
        try:
            return self._instrument.query(command)
        except pyvisa.errors.VisaIOError as e:
            if e.error_code == StatusCode.error_timeout:
                raise InstrumentTimeoutError(str(e)) from e

            if e.error_code == StatusCode.error_connection_lost:
                raise InstrumentDisconnectedError(str(e)) from e

            if e.error_code == StatusCode.error_resource_not_found:
                raise InstrumentNotFoundError(str(e)) from e

            raise InstrumentError(str(e)) from e

    def write(self, command: str) -> str:
        try:
            return self._instrument.write(command)
        except pyvisa.errors.VisaIOError as e:
            raise InstrumentWriteError(str(e)) from e

    def close(self):
        if self._instrument is not None:
            self._instrument.close()