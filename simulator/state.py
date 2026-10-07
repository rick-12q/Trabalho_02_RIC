from datetime import datetime, timezone
from typing import Any


class DeviceState:

    def __init__(
        self,
        device_id: str,
    ):
        self.device_id = device_id

        self.led_state = False
        self.button_state = False

        self.temperature = 25.0
        self.humidity = 60.0
        self.pressure = 1013.25

        self.last_update = datetime.now(
            timezone.utc
        )

        self.last_sent_telemetry: dict[str, Any] | None = None

        self.telemetry_history: list[dict[str, Any]] = []

    def telemetry(self) -> dict:
        return {
            "device_id": self.device_id,
            "temperature": self.temperature,
            "humidity": self.humidity,
            "pressure": self.pressure,
            "button_state": self.button_state,
            "timestamp": self.last_update.isoformat(),
        }

    def set_led(
        self,
        state: bool,
    ) -> None:
        self.led_state = bool(state)

        self.last_update = datetime.now(
            timezone.utc
        )

    def set_button(
        self,
        state: bool,
    ) -> None:
        self.button_state = bool(state)

        self.last_update = datetime.now(
            timezone.utc
        )

    def register_sent_telemetry(
        self,
        payload: dict[str, Any],
    ) -> None:

        self.last_sent_telemetry = payload.copy()

        self.telemetry_history.append(
            payload.copy()
        )

        if len(self.telemetry_history) > 50:
            self.telemetry_history.pop(0)