let DEVICE_ID = "esp32-simulator-001";

const API_BASE = "http://127.0.0.1:8000";

let sourceSelect = null;

let temperatureChart = null;


/* ============================================================
   ELEMENTOS DO DOM
   ============================================================ */

const temperatureElement =
    document.getElementById("temperature");

const humidityElement =
    document.getElementById("humidity");

const pressureElement =
    document.getElementById("pressure");

const buttonStateElement =
    document.getElementById("buttonState");

const ledToggle =
    document.getElementById("ledToggle");

const ledText =
    document.getElementById("ledText");

const connectionDot =
    document.getElementById("connectionDot");

const connectionText =
    document.getElementById("connectionText");

const deviceIdElement =
    document.getElementById("deviceId");

const temperatureChartElement =
    document.getElementById("temperatureChart");


/* ============================================================
   CONFIGURAÇÃO INICIAL
   ============================================================ */

if (deviceIdElement) {
    deviceIdElement.textContent = DEVICE_ID;
}


/* ============================================================
   FONTE DE DADOS
   ============================================================ */

function createSourceControl() {
    const header =
        document.querySelector(".header");

    if (!header) {
        return;
    }

    const wrapper =
        document.createElement("div");

    wrapper.style.display = "flex";
    wrapper.style.alignItems = "center";
    wrapper.style.gap = "12px";
    wrapper.style.marginTop = "12px";

    const label =
        document.createElement("span");

    label.textContent = "Fonte:";
    label.style.fontSize = "14px";

    sourceSelect =
        document.createElement("select");

    sourceSelect.innerHTML = `
        <option value="simulator">
            Simulador
        </option>

        <option value="real">
            ESP32 Real
        </option>
    `;

    sourceSelect.style.padding =
        "6px 10px";

    sourceSelect.style.borderRadius =
        "6px";

    sourceSelect.style.border =
        "1px solid rgba(255,255,255,0.15)";

    sourceSelect.style.background =
        "rgba(255,255,255,0.06)";

    sourceSelect.style.color =
        "inherit";

    sourceSelect.addEventListener(
        "change",
        async () => {
            await setSource(
                sourceSelect.value
            );
        }
    );

    wrapper.appendChild(label);

    wrapper.appendChild(
        sourceSelect
    );

    const titleBlock =
        header.querySelector("div");

    if (titleBlock) {
        titleBlock.appendChild(
            wrapper
        );
    }
}


async function loadSource() {
    try {
        const data =
            await apiFetch(
                "/api/source"
            );

        DEVICE_ID =
            data.device_id;

        if (deviceIdElement) {
            deviceIdElement.textContent =
                DEVICE_ID;
        }

        if (sourceSelect) {
            sourceSelect.value =
                data.source;
        }

    } catch (error) {
        console.error(
            "Erro ao carregar fonte de dados:",
            error
        );
    }
}


async function setSource(
    source
) {
    try {
        const data =
            await apiFetch(
                "/api/source",
                {
                    method: "POST",

                    body: JSON.stringify({
                        source: source
                    })
                }
            );

        DEVICE_ID =
            data.device_id;

        if (deviceIdElement) {
            deviceIdElement.textContent =
                DEVICE_ID;
        }

        if (sourceSelect) {
            sourceSelect.value =
                data.source;
        }

        await refreshDashboard();

    } catch (error) {
        console.error(
            "Erro ao alterar fonte de dados:",
            error
        );

        await loadSource();
    }
}


/* ============================================================
   API
   ============================================================ */

async function apiFetch(
    endpoint,
    options = {}
) {
    const response =
        await fetch(
            `${API_BASE}${endpoint}`,
            {
                ...options,

                headers: {
                    "Content-Type":
                        "application/json",

                    ...(options.headers || {})
                }
            }
        );

    if (!response.ok) {
        throw new Error(
            `HTTP ${response.status}`
        );
    }

    return response.json();
}


/* ============================================================
   CONEXÃO
   ============================================================ */

function setConnectionStatus(
    online
) {
    if (
        !connectionDot ||
        !connectionText
    ) {
        return;
    }

    if (online) {
        connectionDot.classList.remove(
            "offline"
        );

        connectionDot.classList.add(
            "online"
        );

        connectionText.textContent =
            "Online";

    } else {
        connectionDot.classList.remove(
            "online"
        );

        connectionDot.classList.add(
            "offline"
        );

        connectionText.textContent =
            "Offline";
    }
}


/* ============================================================
   TELEMETRIA ATUAL
   ============================================================ */

async function loadTelemetry() {
    try {
        const data =
            await apiFetch(
                `/api/telemetry/latest?device_id=${encodeURIComponent(DEVICE_ID)}`
            );

        if (temperatureElement) {
            temperatureElement.textContent =
                data.temperature !== null &&
                data.temperature !== undefined
                    ? Number(
                        data.temperature
                    ).toFixed(2)
                    : "--";
        }

        if (humidityElement) {
            humidityElement.textContent =
                data.humidity !== null &&
                data.humidity !== undefined
                    ? Number(
                        data.humidity
                    ).toFixed(2)
                    : "--";
        }

        if (pressureElement) {
            pressureElement.textContent =
                data.pressure !== null &&
                data.pressure !== undefined
                    ? Number(
                        data.pressure
                    ).toFixed(2)
                    : "--";
        }

        if (buttonStateElement) {
            buttonStateElement.textContent =
                data.button_state
                    ? "Pressionado"
                    : "Solto";
        }

        setConnectionStatus(true);

    } catch (error) {
        console.error(
            "Erro ao carregar telemetria:",
            error
        );

        setConnectionStatus(false);
    }
}


/* ============================================================
   LED
   ============================================================ */

async function loadLedState() {
    try {
        const data =
            await apiFetch(
                `/api/actuators/led?device_id=${encodeURIComponent(DEVICE_ID)}`
            );

        const state =
            Boolean(
                data.led_state
            );

        if (ledToggle) {
            ledToggle.checked =
                state;
        }

        updateLedText(
            state
        );

    } catch (error) {
        console.error(
            "Erro ao carregar estado do LED:",
            error
        );
    }
}


function updateLedText(
    state
) {
    if (!ledText) {
        return;
    }

    ledText.textContent =
        state
            ? "Ligado"
            : "Desligado";
}


async function setLedState(
    state
) {
    try {
        const data =
            await apiFetch(
                "/api/actuators/led",
                {
                    method: "POST",

                    body: JSON.stringify({
                        device_id:
                            DEVICE_ID,

                        led_state:
                            state,

                        updated_by:
                            "frontend"
                    })
                }
            );

        const newState =
            Boolean(
                data.led_state
            );

        if (ledToggle) {
            ledToggle.checked =
                newState;
        }

        updateLedText(
            newState
        );

    } catch (error) {
        console.error(
            "Erro ao controlar LED:",
            error
        );

        if (ledToggle) {
            ledToggle.checked =
                !state;
        }
    }
}


/* ============================================================
   HISTÓRICO
   ============================================================ */

async function loadHistory() {
    try {
        const records =
            await apiFetch(
                `/api/telemetry/history?device_id=${encodeURIComponent(DEVICE_ID)}&sensor_name=temperature&limit=50`
            );

        if (
            !Array.isArray(
                records
            )
        ) {
            return;
        }

        const ordered =
            [...records].reverse();

        const labels =
            ordered.map(
                item =>
                    formatTime(
                        item.timestamp
                    )
            );

        const values =
            ordered.map(
                item =>
                    Number(
                        item.sensor_value
                    )
            );

        updateTemperatureChart(
            labels,
            values
        );

    } catch (error) {
        console.error(
            "Erro ao carregar histórico:",
            error
        );
    }
}


/* ============================================================
   GRÁFICO
   ============================================================ */

function createTemperatureChart() {
    if (
        !temperatureChartElement ||
        typeof Chart === "undefined"
    ) {
        return;
    }

    const context =
        temperatureChartElement.getContext(
            "2d"
        );

    temperatureChart =
        new Chart(
            context,
            {
                type: "line",

                data: {
                    labels: [],

                    datasets: [
                        {
                            label:
                                "Temperatura",

                            data: [],

                            borderWidth: 2,

                            tension: 0.35,

                            pointRadius: 2,

                            fill: false
                        }
                    ]
                },

                options: {
                    responsive: true,

                    maintainAspectRatio:
                        false,

                    animation: {
                        duration: 300
                    },

                    plugins: {
                        legend: {
                            display: false
                        }
                    },

                    scales: {
                        x: {
                            ticks: {
                                color:
                                    "#9aaca4"
                            },

                            grid: {
                                color:
                                    "rgba(255,255,255,0.05)"
                            }
                        },

                        y: {
                            ticks: {
                                color:
                                    "#9aaca4"
                            },

                            grid: {
                                color:
                                    "rgba(255,255,255,0.05)"
                            }
                        }
                    }
                }
            }
        );
}


function updateTemperatureChart(
    labels,
    values
) {
    if (!temperatureChart) {
        return;
    }

    temperatureChart.data.labels =
        labels;

    temperatureChart
        .data
        .datasets[0]
        .data =
        values;

    temperatureChart.update();
}


/* ============================================================
   DATA / HORA
   ============================================================ */

function formatTime(
    timestamp
) {
    if (!timestamp) {
        return "--";
    }

    const date =
        new Date(
            timestamp
        );

    if (
        Number.isNaN(
            date.getTime()
        )
    ) {
        return "--";
    }

    return date.toLocaleTimeString(
        "pt-BR",
        {
            hour: "2-digit",
            minute: "2-digit",
            second: "2-digit"
        }
    );
}


/* ============================================================
   EVENTOS
   ============================================================ */

if (ledToggle) {
    ledToggle.addEventListener(
        "change",
        async () => {
            await setLedState(
                ledToggle.checked
            );
        }
    );
}


/* ============================================================
   ATUALIZAÇÃO
   ============================================================ */

async function refreshDashboard() {
    await loadTelemetry();

    await loadLedState();

    await loadHistory();
}


/* ============================================================
   INICIALIZAÇÃO
   ============================================================ */

document.addEventListener(
    "DOMContentLoaded",
    async () => {
        createTemperatureChart();

        createSourceControl();

        await loadSource();

        await refreshDashboard();

        setInterval(
            refreshDashboard,
            5000
        );
    }
);