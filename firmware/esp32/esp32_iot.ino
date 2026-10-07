#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoOTA.h>
#include <WebServer.h>
#include <DHT.h>


// ============================================================
// CONFIGURAÇÕES
// ============================================================

const char* WIFI_SSID = "SEU_WIFI";
const char* WIFI_PASSWORD = "SUA_SENHA_WIFI";


// IP do computador que executa o FastAPI.
// NÃO coloque 127.0.0.1 aqui.
// Deve ser o IP da máquina na rede.
const char* BACKEND_HOST = "192.168.1.100";

const int BACKEND_PORT = 8000;


const char* DEVICE_ID = "esp32-001";


const int LED_PIN = 2;

const int BUTTON_PIN = 0;

const int DHT_PIN = 4;

#define DHT_TYPE DHT22


const unsigned long TELEMETRY_INTERVAL = 5000;

const unsigned long LED_POLL_INTERVAL = 2000;


// ============================================================
// OBJETOS
// ============================================================

DHT dht(
    DHT_PIN,
    DHT_TYPE
);

WebServer server(80);


// ============================================================
// ESTADO
// ============================================================

bool ledState = false;

bool buttonState = false;

unsigned long lastTelemetry = 0;

unsigned long lastLedPoll = 0;


// ============================================================
// URL DO BACKEND
// ============================================================

String backendBaseUrl()
{
    return
        String("http://")
        + BACKEND_HOST
        + ":"
        + String(BACKEND_PORT);
}


// ============================================================
// WIFI
// ============================================================

void connectWiFi()
{
    Serial.println();
    Serial.println("Conectando ao Wi-Fi...");

    WiFi.mode(WIFI_STA);

    WiFi.begin(
        WIFI_SSID,
        WIFI_PASSWORD
    );

    while (
        WiFi.status() != WL_CONNECTED
    )
    {
        delay(500);

        Serial.print(".");
    }

    Serial.println();

    Serial.println(
        "Wi-Fi conectado."
    );

    Serial.print(
        "IP: "
    );

    Serial.println(
        WiFi.localIP()
    );
}


// ============================================================
// RECONEXÃO WIFI
// ============================================================

void ensureWiFi()
{
    if (
        WiFi.status()
        == WL_CONNECTED
    )
    {
        return;
    }

    Serial.println(
        "Wi-Fi desconectado."
    );

    WiFi.disconnect();

    WiFi.begin(
        WIFI_SSID,
        WIFI_PASSWORD
    );
}


// ============================================================
// OTA
// ============================================================

void setupOTA()
{
    ArduinoOTA.setHostname(
        DEVICE_ID
    );

    ArduinoOTA.onStart(
        []()
        {
            Serial.println(
                "OTA iniciada."
            );
        }
    );

    ArduinoOTA.onEnd(
        []()
        {
            Serial.println(
                "\nOTA concluída."
            );
        }
    );

    ArduinoOTA.onProgress(
        [](unsigned int progress,
           unsigned int total)
        {
            Serial.printf(
                "OTA: %u%%\r",
                (progress * 100) / total
            );
        }
    );

    ArduinoOTA.onError(
        [](ota_error_t error)
        {
            Serial.printf(
                "Erro OTA [%u]\n",
                error
            );
        }
    );

    ArduinoOTA.begin();

    Serial.println(
        "OTA pronta."
    );
}


// ============================================================
// LED
// ============================================================

void setLed(
    bool state
)
{
    ledState = state;

    digitalWrite(
        LED_PIN,
        ledState
            ? HIGH
            : LOW
    );
}


// ============================================================
// ENDPOINT LOCAL DE STATUS
// ============================================================

void handleStatus()
{
    String json = "{";

    json += "\"device_id\":\"";
    json += DEVICE_ID;
    json += "\",";

    json += "\"led_state\":";
    json += ledState
        ? "true"
        : "false";

    json += ",";

    json += "\"button_state\":";
    json += buttonState
        ? "true"
        : "false";

    json += "}";

    server.send(
        200,
        "application/json",
        json
    );
}


// ============================================================
// ENDPOINT LOCAL PARA LED
// ============================================================

void handleLed()
{
    if (
        !server.hasArg("state")
    )
    {
        server.send(
            400,
            "application/json",
            "{\"error\":\"state required\"}"
        );

        return;
    }

    String value =
        server.arg("state");

    value.toLowerCase();

    bool newState =
        (
            value == "1"
            || value == "true"
            || value == "on"
        );

    setLed(
        newState
    );

    String json = "{";

    json += "\"status\":\"ok\",";
    json += "\"device_id\":\"";
    json += DEVICE_ID;
    json += "\",";
    json += "\"led_state\":";
    json += newState
        ? "true"
        : "false";

    json += "}";

    server.send(
        200,
        "application/json",
        json
    );
}


// ============================================================
// SERVIDOR HTTP LOCAL
// ============================================================

void setupLocalServer()
{
    server.on(
        "/api/status",
        HTTP_GET,
        handleStatus
    );

    server.on(
        "/api/led",
        HTTP_GET,
        handleLed
    );

    server.begin();

    Serial.println(
        "Servidor HTTP local iniciado."
    );
}


// ============================================================
// ENVIO DE TELEMETRIA
// ============================================================

void sendTelemetry()
{
    if (
        WiFi.status()
        != WL_CONNECTED
    )
    {
        return;
    }


    float temperature =
        dht.readTemperature();

    float humidity =
        dht.readHumidity();


    if (
        isnan(temperature)
        || isnan(humidity)
    )
    {
        Serial.println(
            "Erro lendo DHT22."
        );

        return;
    }


    buttonState =
        digitalRead(
            BUTTON_PIN
        ) == LOW;


    HTTPClient http;


    String url =
        backendBaseUrl()
        + "/api/telemetry";


    http.begin(
        url
    );


    http.addHeader(
        "Content-Type",
        "application/json"
    );


    String payload = "{";

    payload += "\"device_id\":\"";
    payload += DEVICE_ID;
    payload += "\",";

    payload += "\"temperature\":";
    payload += String(
        temperature,
        2
    );

    payload += ",";

    payload += "\"humidity\":";
    payload += String(
        humidity,
        2
    );

    payload += ",";

    // O DHT22 não mede pressão.
    // Valor placeholder até integrar
    // um BME280 real.
    payload += "\"pressure\":1013.25,";

    payload += "\"button_state\":";
    payload += buttonState
        ? "true"
        : "false";

    payload += "}";


    int httpCode =
        http.POST(
            payload
        );


    Serial.print(
        "POST telemetry: "
    );

    Serial.println(
        httpCode
    );


    if (
        httpCode > 0
    )
    {
        Serial.println(
            http.getString()
        );
    }


    http.end();
}


// ============================================================
// CONSULTA ESTADO DO LED
// ============================================================

void pollLedState()
{
    if (
        WiFi.status()
        != WL_CONNECTED
    )
    {
        return;
    }


    HTTPClient http;


    String url =
        backendBaseUrl()
        + "/api/actuators/led?device_id="
        + DEVICE_ID;


    http.begin(
        url
    );


    int httpCode =
        http.GET();


    if (
        httpCode == 200
    )
    {
        String response =
            http.getString();


        Serial.print(
            "LED response: "
        );

        Serial.println(
            response
        );


        if (
            response.indexOf(
                "\"led_state\":true"
            )
            >= 0
        )
        {
            setLed(
                true
            );
        }
        else if (
            response.indexOf(
                "\"led_state\":false"
            )
            >= 0
        )
        {
            setLed(
                false
            );
        }
    }


    http.end();
}


// ============================================================
// SETUP
// ============================================================

void setup()
{
    Serial.begin(
        115200
    );


    pinMode(
        LED_PIN,
        OUTPUT
    );


    pinMode(
        BUTTON_PIN,
        INPUT_PULLUP
    );


    setLed(
        false
    );


    dht.begin();


    connectWiFi();


    setupOTA();


    setupLocalServer();
}


// ============================================================
// LOOP
// ============================================================

void loop()
{
    ArduinoOTA.handle();

    server.handleClient();


    ensureWiFi();


    unsigned long now =
        millis();


    if (
        now - lastTelemetry
        >= TELEMETRY_INTERVAL
    )
    {
        lastTelemetry =
            now;

        sendTelemetry();
    }


    if (
        now - lastLedPoll
        >= LED_POLL_INTERVAL
    )
    {
        lastLedPoll =
            now;

        pollLedState();
    }


    delay(10);
}