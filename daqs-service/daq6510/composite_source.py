# instruments/composite_source.py
from __future__ import annotations

from daq6510.instruments.daq6510 import DAQ6510
from daq6510.instruments.usb_temperature_reader import UsbTemperatureReader


class CompositeMeasurementSource:
    def __init__(
        self,
        voltage_instrument: DAQ6510,
        temperature_instrument: UsbTemperatureReader,
        voltage_channel: str,
    ):
        self._daq = voltage_instrument
        self._temp = temperature_instrument
        self._voltage_channel = voltage_channel

    def connect(self) -> None:
        self._daq.connect()
        self._temp.connect()
        self._daq.set_function_voltage_dc(self._voltage_channel)
        self._daq.create_scan([self._voltage_channel])

    def disconnect(self) -> None:
        try:
            self._temp.disconnect()
        finally:
            self._daq.disconnect()

    def read_sample(self) -> dict[str, float]:
        temps = self._temp.read_temperatures()   # {'t_hot', 't_cold'}
        self._daq.initiate()
        voltage_map = self._daq.read_scan_data(count=1)
        voltage = next(iter(voltage_map.values()))

        return {
            "voltage": voltage,
            "t_hot": temps["t_hot"],
            "t_cold": temps["t_cold"],
        }