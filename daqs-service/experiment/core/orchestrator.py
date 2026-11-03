import threading
import time
from datetime import datetime, timezone

from daq6510.instrument import DAQ6510
from daq6510.transport.exceptions import InstrumentError
from experiment.config.config import ChannelRole
from experiment.core.ports import MeasurementSink, MeasurementRecord
from experiment.core.state import SharedExperimentData, ExperimentState
from experiment.methods.kalman import ScalarKalmanFilter
from experiment.methods.seebeck import calculate_seebeck_coefficient
from experiment.methods.stability import StabilityDetector


class Orchestrator:
    def __init__(
            self,
            daq: DAQ6510,
            channel_map: dict[str, ChannelRole],
            device_hash: str,
            process_variance: float,
            measurement_variance: float,
            sink: MeasurementSink,
            record_interval_seconds: float = 10.0,
            poll_interval_seconds: float = 1.0,
            max_consecutive_errors: int = 5,
    ):
        self._daq = daq
        self._channel_map = channel_map
        self._poll_interval = poll_interval_seconds
        self._shared_data = SharedExperimentData()
        self._temp_detector_1 = StabilityDetector()
        self._temp_detector_2 = StabilityDetector()
        self._voltage_detector = StabilityDetector()
        self._voltage_filter = ScalarKalmanFilter(
            process_variance=process_variance,
            measurement_variance=measurement_variance
        )

        self._stop_event = threading.Event()
        self._thread: threading.Thread = None

        self._max_consecutive_errors = max_consecutive_errors
        self._consecutive_errors = 0

        self._device_hash = device_hash
        self._sink = sink
        self._record_interval = record_interval_seconds
        self._last_recorded = None

    def start(self) -> None:
        self._setup_channels()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def _setup_channels(self) -> None:
        t1 = self._channel_map["thermocouple_1"].address
        t2 = self._channel_map["thermocouple_2"].address
        voltage = self._channel_map["voltage_probe"].address

        self._daq.set_function_temperature(t1)
        self._daq.set_thermocouple_type(t1, "K")
        self._daq.set_function_temperature(t2)
        self._daq.set_thermocouple_type(t2, "K")
        self._daq.set_function_voltage_dc(voltage)
        self._daq.create_scan([t1, t2, voltage])

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread:
            self._thread.join()

    def get_current_state(self) -> dict:
        return self._shared_data.snapshot()

    def get_full_history(self) -> dict:
        return self._shared_data.full_history()

    def is_connected(self) -> bool:
        return self._consecutive_errors < self._max_consecutive_errors

    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def disconnect_instrument(self) -> None:
        self._daq.disconnect()

    def _run_loop(self) -> None:
        while not self._stop_event.is_set():
            try:
                self._daq.initiate()
                readings = self._daq.read_scan_data(count=3)
                self._record(readings)
                self._step(readings)
                self._consecutive_errors = 0  # reset po udanym kroku
            except InstrumentError as e:
                self._consecutive_errors += 1
                if self._consecutive_errors >= self._max_consecutive_errors:
                    self._stop_event.set()
            time.sleep(self._poll_interval)

    def _step(self, readings: dict[str, float]) -> None:
        state = self._shared_data.state
        if state == ExperimentState.MEASURING_TEMPERATURE:
            self._step_measuring_temperature(readings)
        elif state == ExperimentState.MEASURING_VOLTAGE:
            self._step_measuring_voltage(readings)
        elif state == ExperimentState.DONE:
            self._stop_event.set()

    def _step_measuring_temperature(self, readings: dict[str, float]) -> None:
        t1 = readings[self._channel_map["thermocouple_1"].address]
        t2 = readings[self._channel_map["thermocouple_2"].address]

        self._temp_detector_1.add_sample(t1)
        self._temp_detector_2.add_sample(t2)
        self._shared_data.update_temperatures(t1, t2)

        if self._temp_detector_1.is_stable() and self._temp_detector_2.is_stable():
            self._shared_data.transition_to(ExperimentState.MEASURING_VOLTAGE)

    def _step_measuring_voltage(self, readings: dict[str, float]) -> None:
        raw_voltage = readings[self._channel_map["voltage_probe"].address]

        filtered_voltage = self._voltage_filter.update(raw_voltage)

        self._voltage_detector.add_sample(filtered_voltage)
        self._shared_data.update_voltage(filtered_voltage)

        if self._voltage_detector.is_stable():
            data = self._shared_data.snapshot()
            delta_t = data["thermocouple_1_temperature"] - data["thermocouple_2_temperature"]
            coefficient = calculate_seebeck_coefficient(filtered_voltage, delta_t)
            self._shared_data.update_seebeck_coefficient(coefficient)
            self._shared_data.transition_to(ExperimentState.DONE)

    def _record(self, readings: dict[str, float]) -> None:
        if self._shared_data.state == ExperimentState.DONE:
            return

        now = time.monotonic()
        if self._last_recorded is not None and now - self._last_recorded < self._record_interval:
            return
        self._last_recorded = now

        self._sink.write(MeasurementRecord(
            device_hash=self._device_hash,
            time=datetime.now(timezone.utc),
            t1=readings[self._channel_map["thermocouple_1"].address],
            t2=readings[self._channel_map["thermocouple_2"].address],
            voltage=readings[self._channel_map["voltage_probe"].address],
        ))