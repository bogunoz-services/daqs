from fastapi import Depends
from sqlalchemy.orm import Session

from domain.services.device_service import DeviceService
from domain.services.measurement_service import MeasurementService
from infrastructure.database.connection import get_session
from infrastructure.repositories.sql_alchemy_measurement_repository import SqlAlchemyMeasurementRepository
from infrastructure.repositories.sql_alchemy_device_repository import SqlAlchemyDeviceRepository
from infrastructure.services.sql_alchemy_device_service import SqlAlchemyDeviceService
from infrastructure.services.sql_alchemy_measurement_service import SqlAlchemyMeasurementService

from utils.hasher import Hasher


def get_hasher() -> Hasher:
    return Hasher()


def get_measurement_repository(
    session: Session = Depends(get_session),
) -> SqlAlchemyMeasurementRepository:
    return SqlAlchemyMeasurementRepository(session)


def get_device_repository(
    session: Session = Depends(get_session),
) -> SqlAlchemyDeviceRepository:
    return SqlAlchemyDeviceRepository(session)


def get_measurement_service(
    measurements: SqlAlchemyMeasurementRepository = Depends(get_measurement_repository),
    devices: SqlAlchemyDeviceRepository = Depends(get_device_repository),
) -> MeasurementService:
    return SqlAlchemyMeasurementService(
        measurements=measurements,
        devices=devices,
    )


def get_device_service(
    devices: SqlAlchemyDeviceRepository = Depends(get_device_repository),
    hasher: Hasher = Depends(get_hasher),
) -> DeviceService:
    return SqlAlchemyDeviceService(
        devices=devices,
        hasher=hasher,
    )