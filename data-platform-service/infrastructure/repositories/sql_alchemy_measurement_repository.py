from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_, false

from domain.models.measurement import Measurement, DeviceL
from domain.ports.measurement_repository import MeasurementRepository
from infrastructure.models.measurement import MeasurementORM
from utils.hasher import Hasher


def _build_conditions(filters: list[dict], ) -> list:
    conditions = []
    for f in filters:
        field_id = f.get("id")
        value = f.get("value")

        if field_id == "time" and value:
            if value.get("from"):
                conditions.append(MeasurementORM.time >= value["from"])
            if value.get("to"):
                conditions.append(MeasurementORM.time <= value["to"])

        elif field_id == "device_ids":
            ids = value if isinstance(value, list) else []
            if ids:
                conditions.append(MeasurementORM.device_id.in_(ids))
            else:
                conditions.append(false())

        elif field_id == "t1" and value:
            if value.get("min") is not None:
                conditions.append(MeasurementORM.t1 >= value["min"])
            if value.get("max") is not None:
                conditions.append(MeasurementORM.t1 <= value["max"])

        elif field_id == "t2" and value:
            if value.get("min") is not None:
                conditions.append(MeasurementORM.t2 >= value["min"])
            if value.get("max") is not None:
                conditions.append(MeasurementORM.t2 <= value["max"])

        elif field_id == "voltage" and value:
            if value.get("min") is not None:
                conditions.append(MeasurementORM.voltage >= value["min"])
            if value.get("max") is not None:
                conditions.append(MeasurementORM.voltage <= value["max"])

    print(conditions)
    return conditions


def _to_domain(orm: MeasurementORM) -> Measurement:
    return Measurement(
        id=orm.id,
        device_id=orm.device_id,
        time=orm.time,
        t1=orm.t1,
        t2=orm.t2,
        voltage=orm.voltage,
    )


class SqlAlchemyMeasurementRepository(MeasurementRepository):
    def __init__(self, session: Session):
        self._session = session
        self._hasher = Hasher()

    def create(self, measurement: Measurement) -> None:
        orm = MeasurementORM(
            device_id=measurement.device_id,
            time=measurement.time,
            t1=measurement.t1,
            t2=measurement.t2,
            voltage=measurement.voltage,
        )
        self._session.add(orm)

    def get_all(
        self,
        filters: list[dict],
        page_index: int,
        page_size: int,
    ) -> tuple[list[Measurement], int]:
        stmt = select(MeasurementORM)
        count_stmt = select(func.count()).select_from(MeasurementORM)

        conditions = _build_conditions(filters)
        if conditions:
            stmt = stmt.where(and_(*conditions))
            count_stmt = count_stmt.where(and_(*conditions))

        total = self._session.scalar(count_stmt) or 0

        rows = self._session.scalars(
            stmt.order_by(MeasurementORM.time.desc())
            .offset(page_index * page_size)
            .limit(page_size)
        ).all()

        result = [_to_domain(row) for row in rows]
        return result, total

    def _escape_like(text: str) -> str:
        return text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")

