-- ============================================================
-- INSERIR TEMPERATURA
-- ============================================================

INSERT INTO sensor_logs (
    device_id,
    sensor_name,
    sensor_value,
    button_state
)
VALUES (
    'esp32-001',
    'temperature',
    25.4,
    FALSE
);


-- ============================================================
-- INSERIR UMIDADE
-- ============================================================

INSERT INTO sensor_logs (
    device_id,
    sensor_name,
    sensor_value,
    button_state
)
VALUES (
    'esp32-001',
    'humidity',
    61.2,
    FALSE
);


-- ============================================================
-- INSERIR PRESSÃO
-- ============================================================

INSERT INTO sensor_logs (
    device_id,
    sensor_name,
    sensor_value,
    button_state
)
VALUES (
    'esp32-001',
    'pressure',
    1013.25,
    FALSE
);


-- ============================================================
-- REGISTRAR LED
-- ============================================================

INSERT INTO actuator_status (
    device_id,
    led_state,
    updated_by
)
VALUES (
    'esp32-001',
    TRUE,
    'manual'
);


-- ============================================================
-- HISTÓRICO DE TEMPERATURA
-- ============================================================

SELECT
    timestamp,
    device_id,
    sensor_value,
    button_state
FROM sensor_logs
WHERE sensor_name = 'temperature'
ORDER BY timestamp DESC
LIMIT 100;


-- ============================================================
-- HISTÓRICO ENTRE DATAS
-- ============================================================

SELECT
    timestamp,
    device_id,
    sensor_name,
    sensor_value,
    button_state
FROM sensor_logs
WHERE timestamp BETWEEN
    '2026-10-01 00:00:00+00'
    AND
    '2026-10-07 23:59:59+00'
ORDER BY timestamp DESC;


-- ============================================================
-- ÚLTIMO ESTADO DO LED
-- ============================================================

SELECT
    timestamp,
    device_id,
    led_state,
    updated_by
FROM actuator_status
ORDER BY timestamp DESC
LIMIT 1;