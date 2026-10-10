import numbers
import types

class OnOffThermostat():

    def __init__(self, _setpoint, _below_hysteresis, _above_hysteresis, below_callback, above_callback):
        if (not isinstance(_setpoint, numbers.Number)):
            raise TypeError('setpoint must be a number!')

        if (not isinstance(_below_hysteresis, numbers.Number)):
            raise TypeError('below_hysteresis must be a number!')

        if (not isinstance(_above_hysteresis, numbers.Number)):
            raise TypeError('above_hysteresis must be a number!')

        if (not isinstance(below_callback, types.FunctionType)):
            raise TypeError('below_callback must be callable!')

        if (not isinstance(above_callback, types.FunctionType)):
            raise TypeError('above_callback must be callable!')

        self._setpoint = _setpoint
        self.state = None
        self._below_hysteresis = _below_hysteresis
        self._above_hysteresis = _above_hysteresis
        self.below_callback = below_callback
        self.above_callback = above_callback

    @property
    def setpoint(self):
        return float(self._setpoint)

    @setpoint.setter
    def setpoint(self, value):
        self._setpoint = value

    @property
    def above_hysteresis(self):
        return float(self._above_hysteresis)

    @above_hysteresis.setter
    def above_hysteresis(self, value):
        self._above_hysteresis = value

    @property
    def below_hysteresis(self):
        return float(self._below_hysteresis)

    @below_hysteresis.setter
    def below_hysteresis(self, value):
        self._below_hysteresis = value

    def run(self, temperature):
        print(self.state)
        if (temperature > (self.setpoint + self.above_hysteresis)):
            if (not self.state == "above"):
                self.above_callback()
                self.state = "above"
        
        if (temperature < (self.setpoint - self.below_hysteresis)):
            if (not self.state == "below"):
                self.below_callback()
                self.state = "below"


        

        




if __name__ == '__main__':
    import I2CGPIO
    import I2CPWM
    import I2CServos
    import DS18B20
    import time
    import threading

    DS18B20_Sensors = DS18B20.enumerate_DS18B20_sensors()

    #find the sensor with alias 1
    _temp_sensor = None
    for sensor in DS18B20_Sensors:
        if (sensor.alias == "bus.1"):
            _temp_sensor = sensor
            break

    print(_temp_sensor.alias)
    print(_temp_sensor.temperature)

    #tMCP = I2CGPIO.I2CGPIO()
    tPWM = I2CPWM.I2CPWM()
    #tServo = I2CServos.I2CServos()

    def on_callback():
        print("Cooling On!")
        tPWM.set_channel(0, 1)

    def off_callback():
        print("Cooling Off!")
        tPWM.set_channel(0, 0)

    tempController = OnOffThermostat(35, 0, 2, off_callback, on_callback)
    tempController.setpoint = 32

    while(1):
        tempController.run(_temp_sensor.temperature)
        time.sleep(1)

