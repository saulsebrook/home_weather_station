
#include <ESP8266WiFi.h>
#include <WiFiClient.h>
#include <ESP8266WebServer.h>
#include <ESP8266mDNS.h>
#include <LittleFS.h>
#include <ArduinoJson.h>
#include <SPI.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>
#include <Wire.h>
#include <ESP8266HTTPClient.h>

#define PI_API "http://192.168.1.133:5000/api/sensor"
#define MY_ALTITUDE_M 647.0
#define SEALEVELPRESSURE_HPA (1013.25)

const char* ssid = "It Burns When IP";
const char* password = "lucy1816647";

Adafruit_BME280 bme;
WiFiClient client;
HTTPClient http;

void sendPi(){
  float seaLevelPressure = bme.seaLevelForAltitude(MY_ALTITUDE_M, bme.readPressure() / 100.0F);
  float temp = bme.readTemperature();
  float humidity = bme.readHumidity();
  float pressure = bme.readPressure() / 100.0F;
  
  // Check if readings are valid
  if (isnan(temp) || isnan(humidity) || isnan(pressure)) {
    Serial.println("ERROR: Invalid sensor readings!");
    return;
  }
  
  http.begin(client, PI_API);
  http.addHeader("Content-Type", "application/json");

  String payload = "{";
  payload += "\"sensor_id\":\"ESP8266_BME280\",";  // Add sensor_id
  payload += "\"temperature\":";
  payload += String(temp);
  payload += ",\"humidity\":";
  payload += String(humidity);
  payload += ",\"pressure\":";
  payload += String(seaLevelPressure);
  payload += "}";
  
  Serial.println(payload);
  int httpCode = http.POST(payload);
  
  if (httpCode > 0) {
      Serial.printf("[HTTP] POST... code: %d\n", httpCode);
      String response = http.getString();
      Serial.println(response);
  } else {
      Serial.printf("[HTTP] POST... failed, error: %s\n", http.errorToString(httpCode).c_str());
  }
  http.end();
}

void printValues(){
  Serial.print("Temperature: ");
  Serial.print(bme.readTemperature());
  Serial.println(" ");
  Serial.print(bme.readPressure() / 100.0F);
    Serial.println(" hPa");
    Serial.print("Approx. Altitude = ");
    Serial.print(bme.readAltitude(SEALEVELPRESSURE_HPA));
    Serial.println(" m");
}

void setup() {
  Serial.begin(115200);
  Wire.begin(); // Begin I2C
  WiFi.begin(ssid, password);
  Serial.println("");

// Wait for a conection
  while (WiFi.status() != WL_CONNECTED) { // While wifi.status is not equal to connected
    delay(500);
    Serial.print(".");
  }

// Connection established
  Serial.println("");
  Serial.print("Connected to ");
  Serial.println(ssid);
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
 
  unsigned status = bme.begin(0x77);
  if (!status) {
        Serial.println("Could not find a valid BME280 sensor, check wiring, address, sensor ID!");
        Serial.print("SensorID was: 0x"); 
        Serial.println(bme.sensorID(),16);
        Serial.print("        ID of 0xFF probably means a bad address, a BMP 180 or BMP 085\n");
        Serial.print("   ID of 0x56-0x58 represents a BMP 280,\n");
        Serial.print("        ID of 0x60 represents a BME 280.\n");
        Serial.print("        ID of 0x61 represents a BME 680.\n");
        while (1) delay(10);
    }
  bme.setSampling(Adafruit_BME280::MODE_FORCED,
                    Adafruit_BME280::SAMPLING_X1, // temperature
                    Adafruit_BME280::SAMPLING_X1, // pressure
                    Adafruit_BME280::SAMPLING_X1, // humidity
                    Adafruit_BME280::FILTER_OFF   );
}

void loop() {
  bme.takeForcedMeasurement();
  sendPi();
  ESP.deepSleep(600e6);

}
