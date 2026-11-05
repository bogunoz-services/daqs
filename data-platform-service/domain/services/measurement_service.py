from typing import Protocol

from domain.models.measurement import Measurement


class MeasurementService(Protocol):
    def record_measurement(self, measurement: Measurement) -> None: ...

    def list_measurements(
            self,
            filters: list[dict],
            page_index: int,
            page_size: int,
    ) -> tuple[list[Measurement], int]: ...