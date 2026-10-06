import random

from .state import DeviceState


def update_sensor_values(state: DeviceState) -> None:
    state.temperature = round(
        max(-40.0, min(85.0, state.temperature + random.uniform(-0.3, 0.3))),
        2,
    )
    state.humidity = round(
        max(0.0, min(100.0, state.humidity + random.uniform(-1.0, 1.0))),
        2,
    )
    state.pressure = round(
        max(300.0, min(1100.0, state.pressure + random.uniform(-0.5, 0.5))),
        2,
    )