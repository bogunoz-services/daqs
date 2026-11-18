from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import select

from domain.models.device import Device
from domain.ports.device_repository import DeviceRepository
from infrastructure.models.device import DeviceORM

def _to_domain(orm: DeviceORM) -> Device:
    return Device(
        id=orm.id,
        name=orm.name,
        logo=orm.logo,
        resource_address=orm.resource_address,
        voltage_slot=orm.voltage_slot,
        voltage_channel=orm.voltage_channel,
        port=orm.port,
    )

def _to_orm(model: Device) -> DeviceORM:
    return DeviceORM(
        id=model.id,
        name=model.name,
        logo=model.logo,
        resource_address=model.resource_address,
        voltage_slot=model.voltage_slot,
        voltage_channel=model.voltage_channel,
        port=model.port,
    )

class SqlAlchemyDeviceRepository(DeviceRepository):
    def __init__(self, session: Session):
        self._session = session

    def get_by_id(self, device_id: int) -> Optional[Device]:
        orm = self._session.get(DeviceORM, device_id)
        print(orm)
        if not orm:
            return None
        return _to_domain(orm)


    def get_all(self) -> list[Device]:
        stmt = select(DeviceORM).order_by(DeviceORM.id)
        rows = self._session.scalars(stmt).all()
        return [_to_domain(row) for row in rows]

    def get_all_by_id(self, ids: set[int]) -> list[Device]:
        stmt = select(DeviceORM).where(DeviceORM.id.in_(ids))
        rows = self._session.scalars(stmt).all()
        return [_to_domain(row) for row in rows]

    def create(self, device: Device) -> None:
        orm = _to_orm(device)
        self._session.add(orm)
        self._session.commit()

    def update(self, device: Device) -> None:

        orm_n = self._session.get(DeviceORM, device.id)

        if orm_n is None:
            return None


        orm_n.name = device.name
        orm_n.logo = device.logo
        orm_n.resource_address = device.resource_address
        orm_n.voltage_slot = device.voltage_slot
        orm_n.voltage_channel = device.voltage_channel
        port = device.port

        self._session.commit()


    def delete(self, device_id: int) -> bool:
        orm = self._session.get(DeviceORM, id)
        if not orm:
            return False

        self._session.delete(orm)
        self._session.commit()
        return True
