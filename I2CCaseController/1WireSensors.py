import pyownet 
import time

def enumerate_DS18B20_sensors(host='localhost', port=4304):
    owproxy = pyownet.protocol.proxy(host, port)
    devices_raw = owproxy.dir()
    devices = []
    [devices.append(x) for x in devices_raw if x not in devices]

    busses_raw = owproxy.dir(bus=True)
    busses = []
    [busses.append(x) for x in busses_raw if x not in busses]

    DS18B20_Sensors = []

    for bus in busses:
        #make sure we only look for busses
        if bus.find("bus.") == -1:
            continue

        devices_on_bus = owproxy.dir(bus)
        #try to find the device on the bus
        for bus_device in devices_on_bus:
            for device in devices:
                if(bus_device.find(device) != -1):
                    DS18B20_Sensors.append(DS18B20_Sensor(device, bus.replace('/', ''), host, port))
                    
    return DS18B20_Sensors


class DS18B20_Sensor():
    def __init__(self, _id, _alias, host='localhost', port=4304):
        self._id = _id
        self._alias = _alias

        self.owproxy = pyownet.protocol.proxy(host, port)

        if(not self.owproxy.present(self._id)):
            raise Exception("{} not found on 1-wire bus".format(self._id))

        if(not self.owproxy.present(self._id + 'type')):
            raise Exception("{} does not have a 'type' field...".format(self._id))

        if(self.owproxy.read(self._id + 'type').decode("utf-8") != "DS18B20"):
            raise Exception("{} is not a DS18B20".format(self._id))
    
    @property
    def alias(self):
        return self._alias

    @property
    def id(self):
        return self._id.replace('/', '')

    @property
    def temperature(self):
        return float(self.owproxy.read(self._id + 'temperature').decode("utf-8"))

    @property
    def temperature9(self):
        return float(self.owproxy.read(self._id + 'temperature9').decode("utf-8"))

    @property
    def temperature10(self):
        return float(self.owproxy.read(self._id + 'temperature10').decode("utf-8"))
    
    @property
    def temperature11(self):
        return float(self.owproxy.read(self._id + 'temperature11').decode("utf-8"))

    @property
    def temperature12(self):
        return float(self.owproxy.read(self._id + 'temperature12').decode("utf-8"))



if __name__ == '__main__':
    sensors = enumerate_DS18B20_sensors()

    while(1):
        for sensor in sensors:
            print(sensor.alias, sensor.temperature)