
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
#include <Arduino.h>

#define PI_API "http://192.168.1.133:5000/api/sensor"
#define PI_API_BATT "http://192.168.1.133:5000/api/batt"
#define MY_ALTITUDE_M 647.0
#define SEALEVELPRESSURE_HPA (1013.25)
#define BATT_DETECT_PIN D7

const char* ssid = "It Burns When IP";
const char* password = "lucy1816647";
int level;
float voltage;
int ADC;

Adafruit_BME280 bme;
WiFiClient client;
HTTPClient http;

void sendPi(){
  bme.setSampling(Adafruit_BME280::MODE_FORCED,
                    Adafruit_BME280::SAMPLING_X1, // temperature
                    Adafruit_BME280::SAMPLING_X1, // pressure
                    Adafruit_BME280::SAMPLING_X1, // humidity
                    Adafruit_BME280::FILTER_OFF   );
  bme.takeForcedMeasurement();
  //Variables
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
  payload += "\"sensor_id\":\"OUTSIDE\",";  // Add sensor_id
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

void wifiConnect(){
  WiFi.begin(ssid, password);
  Serial.println("");
  while (WiFi.status() != WL_CONNECTED) { // While wifi.status is not equal to connected
    Serial.print(".");
  }
  // Connection established
  Serial.println("");
  Serial.print("Connected to ");
  Serial.println(ssid);
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}

void I2C(){
  Wire.begin(); // Begin I2C
  String address = "0x77";
  unsigned status = bme.begin(0x77);
  if(!status){
    String address = "0x76";
    status = bme.begin(0x76);
    if(!status){
      Serial.println("Cannot communicate via I2C, addresses 0x76 and 0x77 unsuccessful");
      while(true){// Fast flash red and green LED indefinitely to signify that I2C sensor connection failed
        digitalWrite(D5, HIGH);
        digitalWrite(D6, LOW);
        delay(200);
        digitalWrite(D5, LOW);
        digitalWrite(D6, HIGH);
        delay(200);
    }
  }
  }
  Serial.print("Connected to I2C via address ");
  Serial.println(status);
}

void POST_batt(){
  http.begin(client, PI_API_BATT);
  http.addHeader("Content-Type", "application/json");

  String payload = "{";
  payload += "\"level\":";
  payload += String(level);
  payload += ",\"value\":";
  payload += String(voltage);
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

float batteryVoltageToPercent(float voltage) {
    // Voltage : Percentage lookup for LiPo/Li-ion
    if (voltage >= 4.20) return 100;
    if (voltage >= 4.15) return 95;
    if (voltage >= 4.11) return 90;
    if (voltage >= 4.08) return 85;
    if (voltage >= 4.02) return 80;
    if (voltage >= 3.98) return 75;
    if (voltage >= 3.95) return 70;
    if (voltage >= 3.91) return 65;
    if (voltage >= 3.87) return 60;
    if (voltage >= 3.83) return 55;
    if (voltage >= 3.79) return 50;
    if (voltage >= 3.75) return 45;
    if (voltage >= 3.71) return 40;
    if (voltage >= 3.67) return 35;
    if (voltage >= 3.61) return 30;
    if (voltage >= 3.55) return 25;
    if (voltage >= 3.49) return 20;
    if (voltage >= 3.42) return 15;
    if (voltage >= 3.35) return 10;
    if (voltage >= 3.20) return 5;
    return 0;
}

void read_batt(){
  delay(20);
  int raw = 0;
  for(int i = 0; 1 < 10; i++){
    raw += analogRead(A0);
  }
  ADC = raw / 10;
  voltage = (ADC / 1023.0) * 3.3 / 0.1993;
  level = batteryVoltageToPercent(voltage);
  Serial.println(voltage);
  Serial.println(level);
}

void setup() {
  delay(50);
  Serial.begin(115200);
  pinMode(A0, INPUT);
  pinMode(D5, OUTPUT);
  pinMode(D6, OUTPUT);
  wifiConnect();
  I2C();  
  
}

void loop() {
  sendPi();
  delay(10);
  read_batt();
  POST_batt();
  Serial.print("Raw ADC: ");
  Serial.println(ADC);
  ESP.deepSleep(180e6);
}
