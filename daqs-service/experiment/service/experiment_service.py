import threading
from typing import Callable

from daq6510.transport.exceptions import InstrumentError
from experiment.core.orchestrator import Orchestrator
from experiment.core.state import SharedExperimentData
from experiment.service.exceptions import InstrumentUnavailableError, InvalidConfigError
from experiment.service.ports import ConfigStore


class ExperimentService:

    def __init__(self, orchestrator_factory: Callable[[], Orchestrator], config_store: ConfigStore):
        self._factory = orchestrator_factory
        self._config_store = config_store
        self._lock = threading.Lock()
        self._orchestrator: Orchestrator = None

    def start(self):
        with self._lock:
            self._ensure_not_running_locked()
            self._release_current_locked()

            orch = None
            try:
                orch = self._factory()
                orch.start()
            except InstrumentError as e:
                self._safe_disconnect(orch)
                raise InstrumentUnavailableError(str(e)) from e
            except KeyError as e:
                self._safe_disconnect(orch)
                raise InvalidConfigError()
            except Exception:
                self._safe_disconnect(orch)
                raise

            self._orchestrator = orch

    def stop(self):
        with self._lock:
            self._stop_locked()

    def shutdown(self) -> None:
        with self._lock:
            self._stop_locked()
            self._release_current_locked()

    def update_channel_map(self, channels: dict) -> None:
        with self._lock:
            self._ensure_not_running_locked()
            self._config_store.save_channel_map(channels)

    def update_connection_config(self, connection: dict) -> None:
        with self._lock:
            self._ensure_not_running_locked()
            self._config_store.save_connection_config(connection)

    def get_history(self) -> dict:
        orch = self._orchestrator
        return SharedExperimentData().full_history() if orch is None else orch.get_full_history()

    def is_running(self) -> bool:
        orch = self._orchestrator
        return orch is not None and orch.is_running()

    def is_connected(self) -> bool:
        orch = self._orchestrator
        return orch is not None and orch.is_connected()

    def get_state(self) -> dict:
        orch = self._orchestrator
        return self._idle_state() if orch is None else orch.get_current_state()

    def _idle_state(self) -> dict:
        state = SharedExperimentData().snapshot()
        state["state"] = "IDLE"
        return state

    def _ensure_not_running_locked(self) -> None:
        orch = self._orchestrator
        if orch is not None and orch.is_running():
            raise ExperimentRunningError()

    def _stop_locked(self) -> None:
        orch = self._orchestrator
        if orch is None:
            return
        orch.stop()

    def _release_current_locked(self) -> None:
        orch = self._orchestrator
        self._orchestrator = None
        self._safe_disconnect(orch)

    @staticmethod
    def _safe_disconnect(orch: Orchestrator) -> None:
        if orch is None:
            return
        orch.disconnect_instrument()


