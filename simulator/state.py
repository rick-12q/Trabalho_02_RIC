from datetime import datetime, timezone


class DeviceState:
    def __init__(self, device_id: str):
        self.device_id = device_id
        self.led_state = False
        self.button_state = False
        self.temperature = 25.0
        self.humidity = 60.0
        self.pressure = 1013.25
        self.last_update = datetime.now(timezone.utc)

    def telemetry(self) -> dict:
        return {
            "device_id": self.device_id,
            "temperature": self.temperature,
            "humidity": self.humidity,
            "pressure": self.pressure,
            "button_state": self.button_state,
            "timestamp": self.last_update.isoformat(),
        }

    def set_led(self, state: bool) -> None:
        self.led_state = state
        self.last_update = datetime.now(timezone.utc)