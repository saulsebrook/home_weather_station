# Weather Station

Flask-based weather monitoring system for ESP32/ESP8266 sensors with BME280.

## Features
- Real-time temperature, humidity, and pressure monitoring
- Multiple sensor support
- Historical data visualization
- ADSB aircraft tracking integration

Battery monitor for outdoor monitor;
  Mosfets -> batt -- Drain --> Source -- gnd
  Gate -> D7
  Drain -> Batt+ end
  Source -> GND

  VOUT of divider = VBatt * 100 / (330 + 100) = VBat * 0.2326
  ADC conversion = Divider output / 1.0 * 1023
  e.g at 4.7Vbatt 0.977 / 1.0 * 1023 = 999

  Suitable mosfets -> 2N7002

Schematic shows a break in the wire that goes to rst. This is for flashing of updates. Unable to flash while rst pin connected.

Note: Weather station schematic shows a 10K resistor to 3.3v. This is there to enable the board to reboot after deep sleep. The resistor is connceted to GPIO7 (SD0). The problem seems obscure and was only solved after finding someone else who solved it in this thread. https://github.com/esp8266/Arduino/issues/5892
