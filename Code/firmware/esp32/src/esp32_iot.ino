/*
  ============================================================
  PROJETO 2 - RIC
  ESP32 + BME280 + OLED + REST + Wi-Fi + OTA
  ============================================================
*/

#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <WebServer.h>
#include <ArduinoOTA.h>
#include <ESPmDNS.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>
#include <SSD1306.h>

// ============================================================
// CONFIGURACAO - ALTERE SOMENTE AQUI
// ============================================================

const char* WIFI_SSID     = "labautomacao";
const char* WIFI_PASSWORD = "L@bA1to25";

// IP atual do notebook na mesma rede do ESP32
const char* BACKEND_HOST = "200.145.26.3";
const int   BACKEND_PORT = 8000;

// Identificacao do ESP32
const char* DEVICE_ID = "esp32-001";
const char* HOSTNAME  = "esp32-001";

// Senha para futuras atualizacoes OTA
const char* OTA_PASSWORD = "ric-ota-2026";

// ============================================================
// HARDWARE
// ============================================================

// Codigo da pratica da disciplina
#define LEDPIN 25
#define BUTTON 0

// BME280
#define I2C_SDA 21
#define I2C_SCL 22
#define SEALEVELPRESSURE_HPA 1029.9

// OLED
#define OLED_I2C_ADDR 0x3C
#define OLED_RESET 16
#define OLED_SDA 4
#define OLED_SCL 15

// ============================================================
// INTERVALOS
// ============================================================

const unsigned long TELEMETRY_INTERVAL = 5000;
const unsigned long LED_POLL_INTERVAL  = 2000;
const unsigned long WIFI_RETRY_INTERVAL = 10000;
const unsigned long DISPLAY_INTERVAL = 1000;

// ============================================================
// OBJETOS
// ============================================================

TwoWire I2CBME = TwoWire(1);
Adafruit_BME280 bme;
SSD1306 display(OLED_I2C_ADDR, OLED_SDA, OLED_SCL);
WebServer server(80);

// ============================================================
// ESTADOS
// ============================================================

bool bmeOK = false;
bool ledState = false;
bool buttonState = false;
bool lastButtonState = false;
bool otaStarted = false;

float temperature = 0;
float humidity = 0;
float pressure = 0;
float altitude = 0;

unsigned long lastTelemetry = 0;
unsigned long lastLedPoll = 0;
unsigned long lastWiFiRetry = 0;
unsigned long lastDisplayUpdate = 0;

// ============================================================
// AUXILIARES
// ============================================================

String boolJson(bool value) {
  return value ? "true" : "false";
}

String backendURL() {
  return "http://" + String(BACKEND_HOST) + ":" + String(BACKEND_PORT);
}

// ============================================================
// LED
// ============================================================

void setLed(bool state) {
  ledState = state;
  digitalWrite(LEDPIN, state ? HIGH : LOW);

  Serial.print("LED: ");
  Serial.println(state ? "ON" : "OFF");
}

// ============================================================
// BME280
// ============================================================

void setupBME280() {
  Serial.println("Inicializando BME280...");

  I2CBME.begin(I2C_SDA, I2C_SCL, 100000);

  bmeOK = bme.begin(0x76, &I2CBME);

  if (!bmeOK) {
    Serial.println("Tentando BME280 em 0x77...");
    bmeOK = bme.begin(0x77, &I2CBME);
  }

  Serial.println(bmeOK ? "BME280 - OK" : "BME280 - ERRO");
}

void readSensors() {
  buttonState = digitalRead(BUTTON) == LOW;

  // Inverte o LED somente no momento em que o botao e pressionado
  if (buttonState && !lastButtonState) {
    setLed(!ledState);
  }

  lastButtonState = buttonState;

  if (!bmeOK) return;

  temperature = bme.readTemperature();
  humidity = bme.readHumidity();
  pressure = bme.readPressure() / 100.0F;
  altitude = bme.readAltitude(SEALEVELPRESSURE_HPA);
}

// ============================================================
// OLED
// ============================================================

void setupDisplay() {
  Serial.println("Inicializando OLED...");

  pinMode(OLED_RESET, OUTPUT);
  digitalWrite(OLED_RESET, LOW);
  delay(50);
  digitalWrite(OLED_RESET, HIGH);
  delay(50);

  display.init();
  display.setFont(ArialMT_Plain_10);
  display.setTextAlignment(TEXT_ALIGN_LEFT);
  display.clear();
  display.drawString(0, 0, "Projeto RIC - ESP32");
  display.drawString(0, 16, "OLED - OK");
  display.display();

  Serial.println("OLED - OK");
}

void updateDisplay() {
  display.clear();
  display.drawString(0, 0, "ESP32 RIC - REAL");

  if (bmeOK) {
    display.drawString(0, 12, "Temp: " + String(temperature, 1) + " C");
    display.drawString(0, 22, "Umid: " + String(humidity, 1) + " %");
    display.drawString(0, 32, "Press: " + String(pressure, 1) + " hPa");
  } else {
    display.drawString(0, 20, "BME280: ERRO");
  }

  if (WiFi.status() == WL_CONNECTED)
    display.drawString(0, 44, "IP: " + WiFi.localIP().toString());
  else
    display.drawString(0, 44, "WiFi desconectado");

  display.drawString(
    0, 54,
    "LED:" + String(ledState ? "ON " : "OFF") +
    " BTN:" + String(buttonState ? "ON" : "OFF")
  );

  display.display();
}

// ============================================================
// WI-FI
// ============================================================

void connectWiFi() {
  Serial.println();
  Serial.println("Conectando ao Wi-Fi...");
  Serial.print("SSID: ");
  Serial.println(WIFI_SSID);

  WiFi.mode(WIFI_STA);
  WiFi.setHostname(HOSTNAME);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  unsigned long start = millis();

  while (WiFi.status() != WL_CONNECTED && millis() - start < 20000) {
    delay(500);
    Serial.print(".");
  }

  Serial.println();

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("Wi-Fi conectado!");
    Serial.print("IP ESP32: ");
    Serial.println(WiFi.localIP());
    Serial.print("RSSI: ");
    Serial.print(WiFi.RSSI());
    Serial.println(" dBm");
  } else {
    Serial.println("Falha ao conectar ao Wi-Fi.");
  }
}

void ensureWiFi() {
  if (WiFi.status() == WL_CONNECTED) return;

  if (millis() - lastWiFiRetry < WIFI_RETRY_INTERVAL) return;

  lastWiFiRetry = millis();

  Serial.println("Reconectando Wi-Fi...");
  WiFi.disconnect();
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
}

// ============================================================
// OTA
// ============================================================

void setupOTA() {
  if (otaStarted || WiFi.status() != WL_CONNECTED) return;

  ArduinoOTA.setHostname(HOSTNAME);
  ArduinoOTA.setPassword(OTA_PASSWORD);

  ArduinoOTA.onStart([]() {
    Serial.println("OTA iniciado...");
  });

  ArduinoOTA.onEnd([]() {
    Serial.println("\nOTA concluido.");
  });

  ArduinoOTA.onProgress([](unsigned int progress, unsigned int total) {
    Serial.printf("OTA: %u%%\r", (progress * 100) / total);
  });

  ArduinoOTA.onError([](ota_error_t error) {
    Serial.printf("Erro OTA [%u]\n", error);
  });

  ArduinoOTA.begin();
  otaStarted = true;

  Serial.print("OTA pronto: ");
  Serial.print(HOSTNAME);
  Serial.println(".local");
}

// ============================================================
// API LOCAL
// ============================================================

String telemetryJSON() {
  readSensors();

  String json = "{";
  json += "\"device_id\":\"" + String(DEVICE_ID) + "\",";
  json += "\"temperature\":" + String(temperature, 2) + ",";
  json += "\"humidity\":" + String(humidity, 2) + ",";
  json += "\"pressure\":" + String(pressure, 2) + ",";
  json += "\"button_state\":" + boolJson(buttonState);
  json += "}";

  return json;
}

void handleRoot() {
  String text =
    "ESP32 RIC\n\n"
    "Device: " + String(DEVICE_ID) +
    "\nWi-Fi: " +
    String(WiFi.status() == WL_CONNECTED ? "CONECTADO" : "DESCONECTADO") +
    "\nIP: " + WiFi.localIP().toString() +
    "\nBackend: " + String(BACKEND_HOST) + ":" + String(BACKEND_PORT) +
    "\n\nEndpoints:\n"
    "/api/status\n"
    "/api/telemetry\n"
    "/api/led?state=on\n"
    "/api/led?state=off\n";

  server.send(200, "text/plain; charset=utf-8", text);
}

void handleStatus() {
  readSensors();

  String json = "{";
  json += "\"device_id\":\"" + String(DEVICE_ID) + "\",";
  json += "\"wifi_connected\":" + boolJson(WiFi.status() == WL_CONNECTED) + ",";
  json += "\"ip\":\"" + WiFi.localIP().toString() + "\",";
  json += "\"backend\":\"" + String(BACKEND_HOST) + "\",";
  json += "\"bme280_ok\":" + boolJson(bmeOK) + ",";
  json += "\"led_state\":" + boolJson(ledState) + ",";
  json += "\"button_state\":" + boolJson(buttonState);
  json += "}";

  server.send(200, "application/json", json);
}

void handleTelemetry() {
  server.send(200, "application/json", telemetryJSON());
}

void handleLed() {
  if (!server.hasArg("state")) {
    server.send(400, "application/json", "{\"error\":\"state obrigatorio\"}");
    return;
  }

  String state = server.arg("state");
  state.toLowerCase();

  if (state == "on" || state == "true" || state == "1")
    setLed(true);
  else if (state == "off" || state == "false" || state == "0")
    setLed(false);
  else {
    server.send(400, "application/json", "{\"error\":\"estado invalido\"}");
    return;
  }

  server.send(
    200,
    "application/json",
    "{\"device_id\":\"" + String(DEVICE_ID) +
    "\",\"led_state\":" + boolJson(ledState) + "}"
  );
}

void setupWebServer() {
  server.on("/", HTTP_GET, handleRoot);
  server.on("/api/status", HTTP_GET, handleStatus);
  server.on("/api/telemetry", HTTP_GET, handleTelemetry);
  server.on("/api/led", HTTP_GET, handleLed);
  server.on("/led", HTTP_GET, handleLed);

  server.begin();
  Serial.println("Servidor HTTP local iniciado.");
}

// ============================================================
// ESP32 -> FASTAPI
// ============================================================

void sendTelemetry() {
  if (WiFi.status() != WL_CONNECTED || !bmeOK) return;

  String url = backendURL() + "/api/telemetry";
  String json = telemetryJSON();

  HTTPClient http;
  http.setTimeout(3000);
  http.begin(url);
  http.addHeader("Content-Type", "application/json");

  int code = http.POST(json);

  Serial.println();
  Serial.println("----- TELEMETRIA -----");
  Serial.print("URL: ");
  Serial.println(url);
  Serial.print("JSON: ");
  Serial.println(json);
  Serial.print("HTTP: ");
  Serial.println(code);

  if (code > 0) {
    Serial.print("Resposta: ");
    Serial.println(http.getString());
  } else {
    Serial.print("Erro: ");
    Serial.println(http.errorToString(code));
  }

  http.end();
}

// ============================================================
// FASTAPI -> ESTADO DO LED
// ============================================================

void pollLedState() {
  if (WiFi.status() != WL_CONNECTED) return;

  String url =
    backendURL() +
    "/api/actuators/led?device_id=" +
    String(DEVICE_ID);

  HTTPClient http;
  http.setTimeout(3000);
  http.begin(url);

  int code = http.GET();

  if (code == 200) {
    String response = http.getString();

    if (response.indexOf("\"led_state\":true") >= 0)
      setLed(true);
    else if (response.indexOf("\"led_state\":false") >= 0)
      setLed(false);
  } else {
    Serial.print("Consulta LED HTTP: ");
    Serial.println(code);
  }

  http.end();
}

// ============================================================
// SETUP
// ============================================================

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println();
  Serial.println("================================");
  Serial.println("PROJETO RIC - ESP32 REAL");
  Serial.println("================================");
  Serial.print("Device ID: ");
  Serial.println(DEVICE_ID);

  pinMode(LEDPIN, OUTPUT);
  pinMode(BUTTON, INPUT_PULLUP);
  setLed(false);

  setupDisplay();
  setupBME280();
  connectWiFi();
  setupWebServer();

  if (WiFi.status() == WL_CONNECTED) {
    MDNS.begin(HOSTNAME);
    setupOTA();
  }

  readSensors();
  updateDisplay();

  Serial.println("Inicializacao concluida.");
}

// ============================================================
// LOOP
// ============================================================

void loop() {
  server.handleClient();
  ensureWiFi();

  if (WiFi.status() == WL_CONNECTED) {
    if (!otaStarted) {
      MDNS.begin(HOSTNAME);
      setupOTA();
    }

    ArduinoOTA.handle();
  }

  readSensors();

  if (millis() - lastDisplayUpdate >= DISPLAY_INTERVAL) {
    lastDisplayUpdate = millis();
    updateDisplay();
  }

  if (millis() - lastTelemetry >= TELEMETRY_INTERVAL) {
    lastTelemetry = millis();
    sendTelemetry();
  }

  if (millis() - lastLedPoll >= LED_POLL_INTERVAL) {
    lastLedPoll = millis();
    pollLedState();
  }

  delay(10);
}