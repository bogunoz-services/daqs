from daq6510.scpi.commands import ScpiCommands
from daq6510.scpi.parser import parse_idn, parse_channel_readings
from daq6510.transport.visa_connection import VisaConnection


class DAQ6510:
    def __init__(self, connection: VisaConnection):
        self._connection = connection

    def connect(self):
        self._connection.open()

    def initiate(self) -> None:
        self._connection.write(ScpiCommands.INITIATE)

    def identify(self) -> dict:
        raw = self._connection.query(ScpiCommands.IDENTIFY)
        return parse_idn(raw)

    def reset(self):
        raw = self._connection.query(ScpiCommands.RESET)

    def set_function_temperature(self, channel: str) -> None:
        self._connection.write(ScpiCommands.set_function_temperature(channel))

    def set_thermocouple_type(self, channel: str, tc_type: str) -> None:
        self._connection.write(ScpiCommands.set_thermocouple_type(channel, tc_type))

    def set_function_voltage_dc(self, channel: str) -> None:
        self._connection.write(ScpiCommands.set_function_voltage_dc(channel))

    def create_scan(self, channels: list[str]) -> None:
        self._connection.write(ScpiCommands.create_scan(channels))

    def read_scan_data(self, count: int, buffer_name: str = "defbuffer1") -> dict[str, float]:
        raw = self._connection.query(ScpiCommands.read_scan_data(count, buffer_name))
        return parse_channel_readings(raw)

    def disconnect(self):
        self._connection.close()