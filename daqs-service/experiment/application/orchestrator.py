import threading
import time
from datetime import datetime, timezone

from daq6510.composite_source import CompositeMeasurementSource
from daq6510.transport.exceptions import InstrumentError
from experiment.domain.models import Sample, MeasurementSink, MeasurementRecord
from experiment.domain.state import SharedExperimentData, ExperimentState
from experiment.domain.methods.kalman import ScalarKalmanFilter
from experiment.domain.methods.seebeck import calculate_seebeck_coefficient
from experiment.domain.methods.stability import StabilityDetector


class Orchestrator:
    def __init__(
        self,
        source: CompositeMeasurementSource,
        device_hash: str,
        process_variance: float,
        measurement_variance: float,
        measurement_sink: MeasurementSink,
        record_interval_seconds: float = 10.0,
        poll_interval_seconds: float = 1.0,
        max_consecutive_errors: int = 5,
    ):
        self._source = source
        self._poll_interval = poll_interval_seconds
        self._shared_data = SharedExperimentData()
        self._temp_detector_1 = StabilityDetector()
        self._temp_detector_2 = StabilityDetector()
        self._voltage_detector = StabilityDetector()
        self._voltage_filter = ScalarKalmanFilter(
            process_variance=process_variance,
            measurement_variance=measurement_variance,
        )

        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

        self._max_consecutive_errors = max_consecutive_errors
        self._consecutive_errors = 0

        self._device_hash = device_hash
        self._record_interval = record_interval_seconds
        self._last_recorded: float | None = None

        self._sink = measurement_sink

    def start(self) -> None:
        self._source.setup()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread is not None:
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
        self._source.disconnect()

    def _run_loop(self) -> None:
        while not self._stop_event.is_set():
            try:
                sample = self._source.read_sample()
                self._record(sample)
                self._step(sample)
                self._consecutive_errors = 0
            except InstrumentError:
                self._consecutive_errors += 1
                if self._consecutive_errors >= self._max_consecutive_errors:
                    self._stop_event.set()
            time.sleep(self._poll_interval)

    def _step(self, sample: Sample) -> None:
        state = self._shared_data.state
        if state == ExperimentState.MEASURING_TEMPERATURE:
            self._step_measuring_temperature(sample)
        elif state == ExperimentState.MEASURING_VOLTAGE:
            self._step_measuring_voltage(sample)
        elif state == ExperimentState.DONE:
            self._stop_event.set()

    def _step_measuring_temperature(self, sample: Sample) -> None:
        self._temp_detector_1.add_sample(sample.t1)
        self._temp_detector_2.add_sample(sample.t2)
        self._shared_data.update_temperatures(sample.t1, sample.t2)

        if self._temp_detector_1.is_stable() and self._temp_detector_2.is_stable():
            self._shared_data.transition_to(ExperimentState.MEASURING_VOLTAGE)

    def _step_measuring_voltage(self, sample: Sample) -> None:
        filtered_voltage = self._voltage_filter.update(sample.voltage)
        self._voltage_detector.add_sample(filtered_voltage)
        self._shared_data.update_voltage(filtered_voltage)

        if self._voltage_detector.is_stable():
            data = self._shared_data.snapshot()
            delta_t = (
                data["thermocouple_1_temperature"]
                - data["thermocouple_2_temperature"]
            )
            coefficient = calculate_seebeck_coefficient(filtered_voltage, delta_t)
            self._shared_data.update_seebeck_coefficient(coefficient)
            self._shared_data.transition_to(ExperimentState.DONE)

    def _record(self, sample: Sample) -> None:
        if self._shared_data.state == ExperimentState.DONE:
            return

        now = time.monotonic()
        if (
            self._last_recorded is not None
            and now - self._last_recorded < self._record_interval
        ):
            return

        record = MeasurementRecord(
            device_hash=self._device_hash,
            time=datetime.now(timezone.utc),
            t1=sample.t1,
            t2=sample.t2,
            voltage=sample.voltage,
        )

        self._sink.write(record)

        self._last_recorded = now
