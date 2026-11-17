# daq6510/daq6510.py
from daq6510.scpi.commands import ScpiCommands
from daq6510.scpi.parser import parse_idn, parse_channel_readings, parse_temperature_line
from daq6510.transport.serial_connection import SerialConnection
from daq6510.transport.visa_connection import VisaConnection


class DAQ6510:
    def __init__(self, connection: VisaConnection):
        self._connection = connection

    def connect(self) -> None:
        self._connection.open()

    def disconnect(self) -> None:
        self._connection.close()

    def identify(self) -> dict:
        raw = self._connection.query(ScpiCommands.IDENTIFY)
        return parse_idn(raw)

    def reset(self) -> None:
        self._connection.write(ScpiCommands.RESET)  # *RST to write, nie query

    def set_function_voltage_dc(self, channel: str) -> None:
        self._connection.write(ScpiCommands.set_function_voltage_dc(channel))

    def create_scan(self, channels: list[str]) -> None:
        self._connection.write(ScpiCommands.create_scan(channels))

    def initiate(self) -> None:
        self._connection.write(ScpiCommands.INITIATE)

    def read_scan_data(
        self, count: int, buffer_name: str = "defbuffer1"
    ) -> dict[str, float]:
        raw = self._connection.query(
            ScpiCommands.read_scan_data(count, buffer_name)
        )
        return parse_channel_readings(raw)

    def read_voltage(self, channel: str) -> float:
        self.set_function_voltage_dc(channel)
        self.create_scan([channel])
        self.initiate()
        readings = self.read_scan_data(count=1)
        return next(iter(readings.values()))


