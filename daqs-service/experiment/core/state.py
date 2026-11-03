import threading
from dataclasses import dataclass, field
from enum import Enum, auto


class ExperimentState(Enum):
    MEASURING_TEMPERATURE = auto()
    MEASURING_VOLTAGE = auto()
    DONE = auto()

@dataclass
class SharedExperimentData:
    state: ExperimentState = ExperimentState.MEASURING_TEMPERATURE
    thermocouple_1_temperature: float = None
    thermocouple_2_temperature: float = None
    voltage: float  = None
    seebeck_coefficient: float  = None

    thermocouple_1_history: list[float] = field(default_factory=list)
    thermocouple_2_history: list[float] = field(default_factory=list)
    voltage_history: list[float] = field(default_factory=list)

    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def update_temperatures(self, t1: float, t2: float) -> None:
        with self._lock:
            self.thermocouple_1_temperature = t1
            self.thermocouple_2_temperature = t2
            self.thermocouple_1_history.append(t1)
            self.thermocouple_2_history.append(t2)

    def update_voltage(self, voltage: float) -> None:
        with self._lock:
            self.voltage = voltage

    def update_seebeck_coefficient(self, coefficient: float) -> None:
        with self._lock:
            self.seebeck_coefficient = coefficient

    def transition_to(self, new_state: ExperimentState) -> None:
        with self._lock:
            self.state = new_state

    def snapshot(self) -> dict:
        with self._lock:
            return {
                "state": self.state.name,
                "thermocouple_1_temperature": self.thermocouple_1_temperature,
                "thermocouple_2_temperature": self.thermocouple_2_temperature,
                "voltage": self.voltage,
                "seebeck_coefficient": self.seebeck_coefficient,
            }


    def full_history(self) -> dict:
        with self._lock:
            return {
                "thermocouple_1_history": list(self.thermocouple_1_history),
                "thermocouple_2_history": list(self.thermocouple_2_history),
                "voltage_history": list(self.voltage_history),
            }