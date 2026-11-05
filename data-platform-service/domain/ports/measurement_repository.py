from typing import Protocol

from domain.models.measurement import Measurement


class MeasurementRepository(Protocol):
    def create(self, measurement: Measurement) -> None: ...
    def get_all(self, filters, page_index, page_size) -> tuple[list[Measurement], int]: ...