CREATE TABLE IF NOT EXISTS sensor_logs (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    device_id VARCHAR(100) NOT NULL,
    sensor_name VARCHAR(100) NOT NULL,
    sensor_value DOUBLE PRECISION NOT NULL,
    button_state BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS actuator_status (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    device_id VARCHAR(100) NOT NULL,
    led_state BOOLEAN NOT NULL,
    updated_by VARCHAR(100) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_sensor_logs_timestamp
    ON sensor_logs(timestamp);

CREATE INDEX IF NOT EXISTS idx_sensor_logs_device_id
    ON sensor_logs(device_id);

CREATE INDEX IF NOT EXISTS idx_sensor_logs_sensor_name
    ON sensor_logs(sensor_name);

CREATE INDEX IF NOT EXISTS idx_actuator_status_timestamp
    ON actuator_status(timestamp);

CREATE INDEX IF NOT EXISTS idx_actuator_status_device_id
    ON actuator_status(device_id);