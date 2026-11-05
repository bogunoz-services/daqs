from http.client import HTTPException

from fastapi import APIRouter, Depends

from api.deps import get_measurement_service, get_hasher, get_device_service
from api.exceptions.measurement_exceptions import RecordMeasurementError, ListMeasurementError
from api.schemas.measurement.list_measurements_response import MeasurementListItem, DeviceInfo, ListMeasurementsResponse
from api.schemas.measurement.record_measurement_request import RecordMeasurementRequest
from domain.models.measurement import Measurement
from domain.services.device_service import DeviceService
from domain.services.measurement_service import MeasurementService
from utils.hasher import Hasher

router = APIRouter(prefix="/api/v1/measurements", tags=["measurements"])


@router.post("/record-measurement")
def record_measurement(
    payload: RecordMeasurementRequest,
    measurement_service: MeasurementService = Depends(get_measurement_service),
    hasher: Hasher = Depends(get_hasher),
):
    try:
        measurement = Measurement(
            id = None,
            device_id=hasher.decode(payload.device_hash),
            time=payload.time,
            t1=payload.t1,
            t2=payload.t2,
            voltage=payload.voltage,
        )
        measurement_service.record_measurement(measurement)
    except Exception as e:
        raise RecordMeasurementError(e)

    return {"ok": True}

@router.get("/list-measurements")
def list_measurements(
    payload: RecordMeasurementRequest,
        measurement_service: MeasurementService = Depends(get_measurement_service),
        device_service: DeviceService = Depends(get_device_service),
        hasher: Hasher = Depends(get_hasher),
):
    try:
        measurements, total = measurement_service.list_measurements(
            filters=payload.filters,
            page_index=payload.page_index,
            page_size=payload.page_size,
        )

        items: list[MeasurementListItem] = []
        for m in measurements:
            device = device_service.get_device(m.device_id)

            items.append(
                MeasurementListItem(
                    hash=hasher.encode(m.id),
                    device=DeviceInfo(
                        hash=hasher.encode(device.id),
                        name=device.name,
                        logo=device.logo,
                    ),
                    time=m.time,
                    t1=m.t1,
                    t2=m.t2,
                    voltage=m.voltage,
                )
            )

        return ListMeasurementsResponse(
            items=items,
            total=total,
            page_index=payload.page_index,
            page_size=payload.page_size,
        )
    except Exception as e:
        raise ListMeasurementError(e)