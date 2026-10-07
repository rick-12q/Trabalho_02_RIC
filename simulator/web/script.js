const API = "";

// Backend real
const BACKEND = "http://127.0.0.1:8000";

const DEVICE_ID = "esp32-simulator-001";

const SEND_INTERVAL = 5;


// ============================================================
// ELEMENTOS
// ============================================================

const connectionDot =
    document.getElementById("connectionDot");

const connectionText =
    document.getElementById("connectionText");

const visualLed =
    document.getElementById("visualLed");

const ledStatus =
    document.getElementById("ledStatus");

const buttonStatus =
    document.getElementById("buttonStatus");

const sensorButton =
    document.getElementById("sensorButton");

const temperature =
    document.getElementById("temperature");

const humidity =
    document.getElementById("humidity");

const pressure =
    document.getElementById("pressure");

const jsonOutput =
    document.getElementById("jsonOutput");

const jsonStatus =
    document.getElementById("jsonStatus");

const eventLog =
    document.getElementById("eventLog");

const buttonToggle =
    document.getElementById("buttonToggle");

const ledOn =
    document.getElementById("ledOn");

const ledOff =
    document.getElementById("ledOff");

const clearJson =
    document.getElementById("clearJson");

const countdown =
    document.getElementById("countdown");


// ============================================================
// ESTADO LOCAL
// ============================================================

let buttonPressed = false;

let countdownValue = SEND_INTERVAL;


// ============================================================
// LOG
// ============================================================

function logEvent(message) {

    const entry =
        document.createElement("div");

    entry.className =
        "log-entry";

    const time =
        new Date().toLocaleTimeString();

    entry.innerHTML = `
        <span class="log-time">
            ${time}
        </span>

        <span class="log-message">
            ${message}
        </span>
    `;

    eventLog.prepend(entry);

    while (eventLog.children.length > 50) {

        eventLog.removeChild(
            eventLog.lastChild
        );
    }
}


// ============================================================
// CONEXÃO
// ============================================================

function setConnection(
    connected
) {

    if (connected) {

        connectionDot.classList.add(
            "online"
        );

        connectionText.textContent =
            "Simulator online";

    } else {

        connectionDot.classList.remove(
            "online"
        );

        connectionText.textContent =
            "Simulator offline";
    }
}


// ============================================================
// ATUALIZAR LED VISUAL
// ============================================================

function updateLed(
    state
) {

    const isOn = Boolean(state);

    if (isOn) {

        visualLed.classList.add(
            "led-on"
        );

        visualLed.classList.remove(
            "led-off"
        );

        ledStatus.textContent =
            "ON";

    } else {

        visualLed.classList.remove(
            "led-on"
        );

        visualLed.classList.add(
            "led-off"
        );

        ledStatus.textContent =
            "OFF";
    }
}


// ============================================================
// ATUALIZAR BOTÃO VISUAL
// ============================================================

function updateButton(
    state
) {

    const isPressed =
        Boolean(state);

    buttonPressed =
        isPressed;

    if (isPressed) {

        buttonStatus.textContent =
            "ON";

        sensorButton.textContent =
            "ON";

        buttonToggle.textContent =
            "SOLTAR";

        buttonToggle.classList.add(
            "pressed"
        );

    } else {

        buttonStatus.textContent =
            "OFF";

        sensorButton.textContent =
            "OFF";

        buttonToggle.textContent =
            "PRESSIONAR";

        buttonToggle.classList.remove(
            "pressed"
        );
    }
}


// ============================================================
// ATUALIZAR SENSORES
// ============================================================

function updateSensors(
    telemetry
) {

    if (!telemetry) {
        return;
    }

    temperature.textContent =
        `${Number(
            telemetry.temperature
        ).toFixed(2)} °C`;

    humidity.textContent =
        `${Number(
            telemetry.humidity
        ).toFixed(2)} %`;

    pressure.textContent =
        `${Number(
            telemetry.pressure
        ).toFixed(2)} hPa`;

    updateButton(
        telemetry.button_state
    );
}


// ============================================================
// JSON
// ============================================================

function showJson(
    payload
) {

    if (!payload) {
        return;
    }

    jsonOutput.textContent =
        JSON.stringify(
            payload,
            null,
            4
        );

    jsonStatus.textContent =
        "enviado";

    logEvent(
        "Telemetria enviada ao backend"
    );
}


// ============================================================
// BUSCAR STATUS DO SIMULADOR
// ============================================================

async function updateSimulator() {

    try {

        const response =
            await fetch(
                `${API}/api/status`,
                {
                    cache: "no-store"
                }
            );

        if (!response.ok) {
            throw new Error(
                `HTTP ${response.status}`
            );
        }

        const data =
            await response.json();

        setConnection(true);

        updateLed(
            data.led_state
        );

        updateButton(
            data.button_state
        );

        updateSensors(
            data.telemetry
        );

        if (data.last_sent_telemetry) {

            showJsonSilently(
                data.last_sent_telemetry
            );
        }

    } catch (error) {

        setConnection(false);

        console.error(
            error
        );
    }
}


// ============================================================
// JSON SEM CRIAR EVENTO NO LOG
// ============================================================

function showJsonSilently(
    payload
) {

    if (!payload) {
        return;
    }

    jsonOutput.textContent =
        JSON.stringify(
            payload,
            null,
            4
        );
}


// ============================================================
// BOTÃO FÍSICO
// ============================================================

async function setButtonState(
    state
) {

    try {

        const response =
            await fetch(
                `${API}/api/button?button_state=${state}`,
                {
                    method: "POST"
                }
            );

        if (!response.ok) {

            throw new Error(
                `HTTP ${response.status}`
            );
        }

        const data =
            await response.json();

        updateButton(
            data.button_state
        );

        logEvent(
            `Botão físico: ${
                data.button_state
                    ? "PRESSIONADO"
                    : "SOLTO"
            }`
        );

    } catch (error) {

        logEvent(
            `Erro no botão: ${error.message}`
        );
    }
}


// ============================================================
// CONTROLE DO LED VIA BACKEND
// ============================================================

async function setBackendLed(
    state
) {

    try {

        const response =
            await fetch(
                `${BACKEND}/api/actuators/led`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({

                        device_id:
                            DEVICE_ID,

                        led_state:
                            state,

                        updated_by:
                            "simulator-ui"
                    })
                }
            );

        if (!response.ok) {

            throw new Error(
                `HTTP ${response.status}`
            );
        }

        const data =
            await response.json();

        updateLed(
            data.led_state
        );

        logEvent(
            `Comando LED enviado ao backend: ${
                data.led_state
                    ? "ON"
                    : "OFF"
            }`
        );

    } catch (error) {

        logEvent(
            `Erro controlando LED: ${error.message}`
        );
    }
}


// ============================================================
// BOTÃO DE PRESSIONAR
// ============================================================

buttonToggle.addEventListener(
    "click",
    async () => {

        await setButtonState(
            !buttonPressed
        );
    }
);


// ============================================================
// LED ON
// ============================================================

ledOn.addEventListener(
    "click",
    async () => {

        await setBackendLed(
            true
        );
    }
);


// ============================================================
// LED OFF
// ============================================================

ledOff.addEventListener(
    "click",
    async () => {

        await setBackendLed(
            false
        );
    }
);


// ============================================================
// LIMPAR JSON
// ============================================================

clearJson.addEventListener(
    "click",
    () => {

        jsonOutput.textContent =
            "Aguardando telemetria...";

        jsonStatus.textContent =
            "aguardando";
    }
);


// ============================================================
// POLLING DA INTERFACE
// ============================================================

setInterval(
    updateSimulator,
    1000
);


// ============================================================
// CONTADOR VISUAL
// ============================================================

setInterval(
    () => {

        countdownValue--;

        if (countdownValue <= 0) {

            countdownValue =
                SEND_INTERVAL;
        }

        countdown.textContent =
            countdownValue;

    },
    1000
);


// ============================================================
// INICIALIZAÇÃO
// ============================================================

logEvent(
    "Interface do simulador iniciada"
);

updateSimulator();