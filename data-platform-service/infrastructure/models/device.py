from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.models.base import Base


class DeviceORM(Base):
    __tablename__ = 'devices'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    logo: Mapped[str]
    resource_address: Mapped[str]
    voltage_slot: Mapped[str]
    voltage_channel: Mapped[str]
    port: Mapped[str]

    measurements: Mapped[list["MeasurementORM"]] = relationship(back_populates="device")