from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_, false

from database.infrastructure.models.measurement import MeasurementORM


class MeasurementRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, orm: MeasurementORM) -> int:
        self.session.add(orm)
        self.session.commit()
        self.session.refresh(orm)
        return orm.id

    def get_all(
        self,
        filters: list[dict],
        page_index: int,
        page_size: int,
    ) -> tuple[list[MeasurementORM], int]:
        stmt = select(MeasurementORM)
        count_stmt = select(func.count()).select_from(MeasurementORM)

        conditions = self._build_conditions(filters)
        if conditions:
            stmt = stmt.where(and_(*conditions))
            count_stmt = count_stmt.where(and_(*conditions))

        total = self.session.scalar(count_stmt) or 0

        stmt = (
            stmt
            .order_by(MeasurementORM.time.desc())
            .offset(page_index * page_size)
            .limit(page_size)
        )
        rows = self.session.scalars(stmt).all()

        result = [
            MeasurementORM(
                id=row.id,
                device_id=row.device_id,
                time=row.time,
                t1=row.t1,
                t2=row.t2,
                voltage=row.voltage,
            )
            for row in rows
        ]
        return result, total

    def _build_conditions(self, filters: list[dict], ) -> list:
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

    def _escape_like(text: str) -> str:
        return text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")