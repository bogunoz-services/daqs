import httpx

from experiment.domain.models import MeasurementSink, MeasurementRecord


class HttpMeasurementSink(MeasurementSink):

    def __init__(self, base_url: str):
        self._client = httpx.Client(
            base_url=base_url,
            timeout=5.0,
        )

    def write(self, record: MeasurementRecord) -> None:
        payload = {
            "device_hash": record.device_hash,
            "time": record.time.isoformat(),
            "t1": record.t1,
            "t2": record.t2,
            "voltage": record.voltage,
        }

        try:
            response = self._client.post(
                "/measurements/record-measurement",
                json=payload,
            )
            response.raise_for_status()

        except httpx.HTTPError as exc:
            raise RuntimeError(
                f"Measurement persistence failed: {exc}"
            ) from exc

    def close(self) -> None:
        self._client.close()