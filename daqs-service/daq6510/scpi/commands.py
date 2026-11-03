from typing import Literal

from daq6510.scpi.exceptions import TcTypeValueError


class ScpiCommands:
    IDENTIFY = "*IDN?"
    RESET = "*RST"
    INITIATE = "INIT"

    @staticmethod
    def set_function_temperature(channel: str) -> str:
        return f'SENS:FUNC "TEMP", (@{channel})'

    @staticmethod
    def set_thermocouple_type(channel: str, tc_type: str) -> str:
        if tc_type not in ["B", "E", "J", "K", "N", "R", "S", "T"]:
            raise TcTypeValueError(str(tc_type))
        return f"SENS:TEMP:TC:TYPE {tc_type}, (@{channel})"

    @staticmethod
    def set_function_voltage_dc(channel: str) -> str:
        return f'SENS:FUNC "VOLT", (@{channel})'

    @staticmethod
    def create_scan(channels: list[str]) -> str:
        channel_list = ",".join(channels)
        return f"ROUT:SCAN:CRE (@{channel_list})"

    @staticmethod
    def read_scan_data(count: int, buffer_name: str = "defbuffer1") -> str:
        return f'TRAC:DATA? 1, {count}, "{buffer_name}", CHAN, READ'