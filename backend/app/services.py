from datetime import datetime, timezone

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from .models import ActuatorStatus, SensorLog
from .schemas import TelemetryCreate


def save_telemetry(
    db: Session,
    telemetry: TelemetryCreate,
) -> datetime:

    timestamp = telemetry.timestamp or datetime.now(timezone.utc)

    logs = [
        SensorLog(
            timestamp=timestamp,
            device_id=telemetry.device_id,
            sensor_name="temperature",
            sensor_value=telemetry.temperature,
            button_state=telemetry.button_state,
        ),
        SensorLog(
            timestamp=timestamp,
            device_id=telemetry.device_id,
            sensor_name="humidity",
            sensor_value=telemetry.humidity,
            button_state=telemetry.button_state,
        ),
        SensorLog(
            timestamp=timestamp,
            device_id=telemetry.device_id,
            sensor_name="pressure",
            sensor_value=telemetry.pressure,
            button_state=telemetry.button_state,
        ),
    ]

    db.add_all(logs)
    db.commit()

    return timestamp


def get_led_state(
    db: Session,
    device_id: str,
) -> ActuatorStatus | None:

    statement = (
        select(ActuatorStatus)
        .where(ActuatorStatus.device_id == device_id)
        .order_by(desc(ActuatorStatus.timestamp))
        .limit(1)
    )

    return db.execute(statement).scalar_one_or_none()


def set_led_state(
    db: Session,
    device_id: str,
    led_state: bool,
    updated_by: str,
) -> ActuatorStatus:

    actuator = ActuatorStatus(
        device_id=device_id,
        led_state=led_state,
        updated_by=updated_by,
        timestamp=datetime.now(timezone.utc),
    )

    db.add(actuator)
    db.commit()
    db.refresh(actuator)

    return actuator