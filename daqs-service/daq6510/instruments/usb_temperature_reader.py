from daq6510.scpi.parser import parse_temperature_line
from daq6510.transport.serial_connection import SerialConnection


class UsbTemperatureReader:
    def __init__(self, connection: SerialConnection):
        self._connection = connection

    def connect(self) -> None:
        self._connection.open()

    def disconnect(self) -> None:
        self._connection.close()

    def read_temperatures(self) -> dict[str, float]:
        """Zwraca np. {'t_hot': 23.5, 't_cold': 24.1}"""
        line = self._connection.readline()
        return parse_temperature_line(line)