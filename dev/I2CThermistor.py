import board
import busio
import math
from adafruit_ads1x15.analog_in import AnalogIn
i2c = busio.I2C(board.SCL, board.SDA)
import adafruit_ads1x15.ads1115 as ADS
import adafruit_ads1x15.ads1x15 as ADSx

ads = ADS.ADS1115(i2c)
ads.mode = ADSx.Mode.SINGLE
chan = AnalogIn(ads, ADS.P1)

resistance = 10000 / (3.3 / chan.voltage - 1)

temperature = 1/((1/298.15) + (1/4036)*math.log(resistance/100000.0)) - 273.15

print(chan.value, chan.voltage, resistance, temperature)
