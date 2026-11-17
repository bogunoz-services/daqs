import httpx

class MeasurementClient:

    def __init__(self, base_url: str):
        self.base_url = base_url

    def record_measurement(self, payload: dict):
        url = f"{self.base_url}/api/v1/measurements/record-measurement"

        try:
            response = httpx.post(
                url,
                json=payload,
                timeout=5.0
            )

            response.raise_for_status()

            return response.json()

        except httpx.HTTPError as e:
            raise RuntimeError(
                f"Error communicating with measurement service: {e}"
            ) from e