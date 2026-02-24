
#include <ESP8266WiFi.h>
#include <WiFiClient.h>
#include <ESP8266WebServer.h>
#include <ESP8266mDNS.h>
#include <LittleFS.h>
#include <ArduinoJson.h>
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
float temp;
float humidity;
float pressure;
float seaLevelPressure;

Adafruit_BME280 bme;
WiFiClient client;
HTTPClient http;

void read_sensor(){
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
  Serial.println(temp);
  Serial.println(humidity);
  Serial.println(pressure);
}

void sendPi(){
  read_sensor();  
  http.begin(client, PI_API);
  http.addHeader("Content-Type", "application/json");

  String payload = "{";
  payload += "\"sensor_id\":\"TEST\",";  // Add sensor_id
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
  unsigned long now = millis();
  while (WiFi.status() != WL_CONNECTED) { // While wifi.status is not equal to connected
    if(millis() - now >= 60000){
      ESP.deepSleep(300e6);
    }
    Serial.print(".");
    delay(200);
  }
  // Connection established
  Serial.println("");
  Serial.print("Connected to ");
  Serial.println(ssid);
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
  delay(500);
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
      Serial.printf("[HTTP] BATT POST... failed, error: %s\n", http.errorToString(httpCode).c_str());
  }
  http.end();
}

float batteryVoltageToPercent(float voltage) {
    // Voltage to percentage lookup table (1% resolution)
    const float voltageTable[] = {
        3.00, 3.10, 3.20, 3.30, 3.40, 3.50, 3.60, 3.70, 3.75, 3.79,
        3.83, 3.87, 3.91, 3.95, 3.98, 4.02, 4.05, 4.08, 4.11, 4.14,
        4.17, 4.20
    };
    const float percentTable[] = {
        0, 2, 5, 8, 12, 17, 22, 28, 34, 40,
        46, 52, 58, 64, 70, 75, 80, 85, 90, 94,
        97, 100
    };
    const int tableSize = 22;

    if (voltage <= voltageTable[0]) return 0;
    if (voltage >= voltageTable[tableSize - 1]) return 100;

    // Find position in table and interpolate
    for (int i = 1; i < tableSize; i++) {
        if (voltage <= voltageTable[i]) {
            float ratio = (voltage - voltageTable[i-1]) / (voltageTable[i] - voltageTable[i-1]);
            return percentTable[i-1] + ratio * (percentTable[i] - percentTable[i-1]);
        }
    }
    return 0;
}

void read_batt(){
  delay(20);
  digitalWrite(D6, HIGH);
  Serial.println("Setting D6 HIGH");
  int raw = 0;
  for(int i = 0; i < 10; i++){
    raw += analogRead(A0);
  }
  ADC = raw / 10;
  voltage = (ADC / 1023.0) * 3.3 /  0.1993;
  level = batteryVoltageToPercent(voltage);
  Serial.println(voltage);
  Serial.println(level);
  delay(50);
  digitalWrite(D6, LOW);
}

void setup() {  
  delay(50);
  Serial.begin(115200);
  pinMode(A0, INPUT);
  pinMode(D5, OUTPUT);
  pinMode(D6, OUTPUT);
  wifiConnect();
  I2C();  
  //read_sensor(); // For troubleshooting
}

void loop() {
  sendPi();
  delay(10);
  read_batt();
  POST_batt();
  Serial.print("Raw ADC: ");
  Serial.println(ADC);
  ESP.deepSleep(300e6);
}
