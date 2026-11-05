from domain.models.measurement import Measurement
from domain.services.measurement_service import MeasurementService
from infrastructure.repositories.sql_alchemy_device_repository import DeviceRepository
from infrastructure.repositories.sql_alchemy_measurement_repository import MeasurementRepository


class SqlAlchemyMeasurementService(MeasurementService):
    def __init__(
            self,
            measurements: MeasurementRepository,
            devices: DeviceRepository,
    ):
        self._measurements = measurements
        self._devices = devices

    def record_measurement(self, measurement: Measurement) -> None:
        self._measurements.create(measurement)

    def list_measurements(
        self,
        filters: list[dict],
        page_index: int,
        page_size: int,
    ) -> tuple[list[Measurement], int]:
        page_index = max(0, page_index)
        page_size = min(max(1, page_size), 50)

        resolved = self._resolve_filters(filters)

        return self._measurements.get_all(resolved, page_index, page_size)

    def _resolve_filters(self, filters: list[dict]) -> list[dict]:
        resolved = []
        for f in filters:
            if f.get("id") == "device" and isinstance(f.get("value"), str) and f["value"].strip():
                needle = f["value"].strip().lower()
                matching_ids = [
                    d.id
                    for d in self._devices.get_all()
                    if needle in (d.name or "").lower()
                ]
                resolved.append({"id": "device_ids", "value": matching_ids})
            else:
                resolved.append(f)
        return resolved
