from typing import List

from fastapi import APIRouter, Depends

from api.deps import get_device_service, get_hasher
from api.exceptions.device_exceptions import GetDeviceError, CreateDeviceError, UpdateDeviceError, DeleteDeviceError
from api.schemas.device.device_request import DeviceRequest
from api.schemas.device.device_response import DeviceResponse
from domain.models.device import Device
from domain.services.device_service import DeviceService
from utils.hasher import Hasher

router = APIRouter(prefix="/api/v1/devices", tags=["device"])

@router.get("/{device_hash}", response_model=DeviceResponse)
def get_device(
    device_hash: str,
    device_service: DeviceService = Depends(get_device_service),
    hasher: Hasher = Depends(get_hasher),
) -> DeviceResponse:
    try:
        device = device_service.get_device(hasher.decode(device_hash))
        return DeviceResponse(
            hash=hasher.encode(device.id),
            name=device.name,
            logo=device.logo,
            resource_address=device.resource_address,
            thermocouple_1_slot=device.thermocouple_1_slot,
            thermocouple_1_channel=device.thermocouple_1_channel,
            thermocouple_2_slot=device.thermocouple_2_slot,
            thermocouple_2_channel=device.thermocouple_2_channel,
            voltage_slot=device.voltage_slot,
            voltage_channel=device.voltage_channel,
        )
    except Exception as e:
        raise GetDeviceError(e)


@router.get("/get-all", response_model=List[DeviceResponse])
def get_devices(
    device_service: DeviceService = Depends(get_device_service),
    hasher: Hasher = Depends(get_hasher),
) -> List[DeviceResponse]:
    try:
        devices = device_service.get_all_devices()

        result = []
        for device in devices:
            result.append(DeviceResponse(
                hash=hasher.encode(device.id),
                name=device.name,
                logo=device.logo,
                resource_address=device.resource_address,
                thermocouple_1_slot=device.thermocouple_1_slot,
                thermocouple_1_channel=device.thermocouple_1_channel,
                thermocouple_2_slot=device.thermocouple_2_slot,
                thermocouple_2_channel=device.thermocouple_2_channel,
                voltage_slot=device.voltage_slot,
                voltage_channel=device.voltage_channel,
            ))
        return result
    except Exception as e:
        raise GetDeviceError(e)


@router.post("/create")
def create_device(
    payload: DeviceRequest,
    device_service: DeviceService = Depends(get_device_service),
):
    try:
        device = Device(
            id=None,
            name=payload.name,
            logo=payload.logo,
            resource_address=payload.resource_address,
            thermocouple_1_slot=payload.thermocouple_1_slot,
            thermocouple_1_channel=payload.thermocouple_1_channel,
            thermocouple_2_slot=payload.thermocouple_2_slot,
            thermocouple_2_channel=payload.thermocouple_2_channel,
            voltage_slot=payload.voltage_slot,
            voltage_channel=payload.voltage_channel,
        )
        device_service.add_new_device(device)
    except Exception as e:
        raise CreateDeviceError(e)

    return {"ok": True}


@router.put("/update")
def update_device(
    payload: DeviceRequest,
    device_service: DeviceService = Depends(get_device_service),
    hasher: Hasher = Depends(get_hasher),
):
    try:
        device = Device(
            id=hasher.decode(payload.hash),
            name=payload.name,
            logo=payload.logo,
            resource_address=payload.resource_address,
            thermocouple_1_slot=payload.thermocouple_1_slot,
            thermocouple_1_channel=payload.thermocouple_1_channel,
            thermocouple_2_slot=payload.thermocouple_2_slot,
            thermocouple_2_channel=payload.thermocouple_2_channel,
            voltage_slot=payload.voltage_slot,
            voltage_channel=payload.voltage_channel,
        )
        device_service.update_device(device)
    except Exception as e:
        raise UpdateDeviceError(e)

    return {"ok": True}



@router.delete("/delete/{device_hash}")
def delete_device(
    device_hash: str,
    device_service: DeviceService = Depends(get_device_service),
    hasher: Hasher = Depends(get_hasher),
) -> bool:
    try:
        return device_service.delete_device(hasher.decode(device_hash))
    except Exception as e:
        raise DeleteDeviceError(e)

