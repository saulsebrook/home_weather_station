# Weather Station

Flask-based weather monitoring system for ESP8266 using BME280 sensors.

## Features
- Real time monitoring of temperature data between three seperate sensors
- Historical graphing with overlays between sensors
- Real time battery monitoring
- ADSB aircraft tracking integration
- Power saving via switching of voltage detector using a 2N7000 mosfet
- On board voltage regulation using the MCP1700-3302E/TO with low quiescent current // yet to be implemented

## Battery monitor calculations for outdoor monitor;
 
  VOUT of divider = VBatt * R1(Bottom) / (R2 + R1) 
                  = VBatt * 0.2326
  ADC conversion = Divider output / 3.3(reference of analog in) * 1023
  Divider Output = (ADC conversion / 1023) * 3.3
  Vbatt = (Divider output * (R1 + R2) / R1) / (R1(Bottom) / (R2 + R1) // In the case of R2 of 330K and R1 of 100k you divide by 0.2326

## Further info

  Schematic shows a break in the wire that goes to rst. This is for flashing of updates. Unable to flash while rst pin connected.

Note: Weather station schematic shows a 10K resistor to 3.3v. This is there to enable the board to reboot after deep sleep. The resistor is connceted to GPIO7 (SD0). The problem seems obscure and was only solved after finding someone else who solved it in this thread. https://github.com/esp8266/Arduino/issues/5892
