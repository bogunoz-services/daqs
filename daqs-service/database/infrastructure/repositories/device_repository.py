from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import select, Sequence

from database.infrastructure.models.device import DeviceORM


class DeviceRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, id: int) -> Optional[DeviceORM]:
        orm = self.session.get(DeviceORM, id)
        if not orm:
            return None
        return orm

    def get_all_by_id(self, ids: set[int]) -> Sequence[DeviceORM]:
        stmt = select(DeviceORM).where(DeviceORM.id.in_(ids))
        return self.session.scalars(stmt).all()

    def get_all(self) -> Sequence[DeviceORM]:
        stmt = select(DeviceORM).order_by(DeviceORM.id)
        rows = self.session.scalars(stmt).all()
        return rows

    def create(self, orm: DeviceORM) -> int:
        self.session.add(orm)
        self.session.commit()
        return orm.id

    def update(self, orm: DeviceORM) -> int:
        orm_n = self.session.get(DeviceORM, orm.id)

        if orm_n is None:
            return None

        print(orm_n.id)

        orm_n.name = orm.name
        orm_n.logo = orm.logo
        orm_n.resource_address = orm.resource_address
        orm_n.thermocouple_1_slot = orm.thermocouple_1_slot
        orm_n.thermocouple_1_channel = orm.thermocouple_1_channel
        orm_n.thermocouple_2_slot = orm.thermocouple_2_slot
        orm_n.thermocouple_2_channel = orm.thermocouple_2_channel
        orm_n.voltage_slot = orm.voltage_slot
        orm_n.voltage_channel = orm.voltage_channel

        self.session.commit()

        return orm_n.id

    def delete(self, id: int) -> bool:
        orm = self.session.get(DeviceORM, id)
        if not orm:
            return False

        self.session.delete(orm)
        self.session.commit()
        return True
