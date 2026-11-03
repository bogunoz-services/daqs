from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.infrastructure.models.base import Base


class DeviceORM(Base):
    __tablename__ = 'devices'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    logo: Mapped[str]
    resource_address: Mapped[str]
    thermocouple_1_slot: Mapped[str]
    thermocouple_1_channel: Mapped[str]
    thermocouple_2_slot: Mapped[str]
    thermocouple_2_channel: Mapped[str]
    voltage_slot: Mapped[str]
    voltage_channel: Mapped[str]

    measurements: Mapped[list["MeasurementORM"]] = relationship(back_populates="device")