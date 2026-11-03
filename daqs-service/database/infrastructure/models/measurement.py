from datetime import datetime

from sqlalchemy import ForeignKey

from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.infrastructure.models.base import Base
from database.infrastructure.models.types import UTCDateTime


class MeasurementORM(Base):
    __tablename__ = "measurements"

    id: Mapped[int] = mapped_column(primary_key=True)
    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id"), index=True)
    time: Mapped[datetime] = mapped_column(UTCDateTime, index=True)
    t1: Mapped[float]
    t2: Mapped[float]
    voltage: Mapped[float]

    device: Mapped["DeviceORM"] = relationship(back_populates="measurements")