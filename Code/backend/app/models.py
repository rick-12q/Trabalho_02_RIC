from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Index
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class SensorLog(Base):
    __tablename__ = "sensor_logs"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    device_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    sensor_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    sensor_value: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    button_state: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    __table_args__ = (
        Index("idx_sensor_logs_timestamp", "timestamp"),
        Index("idx_sensor_logs_device_id", "device_id"),
        Index("idx_sensor_logs_sensor_name", "sensor_name"),
    )


class ActuatorStatus(Base):
    __tablename__ = "actuator_status"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    device_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    led_state: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )

    updated_by: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    __table_args__ = (
        Index("idx_actuator_status_timestamp", "timestamp"),
        Index("idx_actuator_status_device_id", "device_id"),
    )