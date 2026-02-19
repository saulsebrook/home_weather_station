# Weather Station

Flask-based weather monitoring system for ESP32/ESP8266 sensors with BME280.

## Features
- Real-time temperature, humidity, and pressure monitoring
- Multiple sensor support
- Historical data visualization
- ADSB aircraft tracking integration

Note: Weather station schematic shows a 10K resistor to 3.3v. This is there to enable the board to reboot after deep sleep. The resistor is connceted to GPIO7 (SD0). The problem seems obscure and was only solved after finding someone else who solved it in this thread. https://github.com/esp8266/Arduino/issues/5892
