import board
import busio
import time
import adafruit_pca9685
import threading

NUM_IO_PINS=16
MAX_CHANNEL_POWER=0xFFFF
RAMP_DELAY=0.05

class I2CPWM(adafruit_pca9685.PCA9685):

    channelRampThreads = [threading.Thread()] * NUM_IO_PINS

    def __init__(self):
        i2c = busio.I2C(board.SCL, board.SDA)
        super().__init__(i2c, address=0x41)

        self.frequency = 2400

    def set_channel(self, pin, power):
        self.validate_pin(pin)
        self.validate_power(power)
        self.channels[pin].duty_cycle = int(power * MAX_CHANNEL_POWER)

    def get_channel(self, pin):
        self.validate_pin(pin)
        return self.channels[pin].duty_cycle / MAX_CHANNEL_POWER

    def ramp_channel(self, pin, new_power, ramp_time):
        self.validate_pin(pin)
        self.validate_power(new_power)
        if(not self.channelRampThreads[pin].is_alive()):
            self.channelRampThreads[pin] = threading.Thread(target=self.ramp_channel_thread, args=(pin, new_power, ramp_time), daemon=True)
            self.channelRampThreads[pin].start()
        return self.channelRampThreads[pin]

    def ramp_channel_thread(self, pin, new_power, ramp_time):
        current_power = self.get_channel(pin)
        current_power_raw = int(MAX_CHANNEL_POWER * current_power)
        new_power_raw = int(new_power * MAX_CHANNEL_POWER)
        steps_to_go = new_power_raw - current_power_raw
        step_amount = int((RAMP_DELAY * abs(steps_to_go)) / ramp_time)
        if(step_amount < 1):
            step_amount = 1

        if(steps_to_go < 0):
            step_amount = step_amount*-1

        for i in range(current_power_raw, new_power_raw, step_amount):
            newDutyCycle = 0
            if(i < 0):
                newDutyCycle = 0
            elif(i > MAX_CHANNEL_POWER):
                newDutyCycle = MAX_CHANNEL_POWER
            else:
                newDutyCycle = i
            self.channels[pin].duty_cycle = newDutyCycle
            time.sleep(RAMP_DELAY)

        self.channels[pin].duty_cycle = new_power_raw


    def validate_pin(self, pin):
        if(pin < 0 or pin > NUM_IO_PINS-1):
            raise ValueError('PCA9685 Pin Index Out of Bounds')

    def validate_power(self, pin):
        if(pin < 0 or pin > 1):
            raise ValueError('Driver Accepts 0-1 Only')

if __name__ == '__main__':
    tPWM = I2CPWM()


    lowlevel = 0
    highlevel = 1

    tPWM.set_channel(3, 1)
    tPWM.set_channel(0, 0)
    tPWM.set_channel(1, 0)
    tPWM.set_channel(4, 0.4)
    time.sleep(1)

    # while(1):
    #     tPWM.ramp_channel(3, 1, 1)
    #     time.sleep(0)

    #     tPWM.ramp_channel(3, 0, 1)
    #     time.sleep(0)

    while(1):
        currentVal = tPWM.get_channel(3)
        print(currentVal, tPWM.get_channel(2))
        if(currentVal == lowlevel):
            tPWM.ramp_channel(3, 1, 3)
            tPWM.ramp_channel(0, 0, 0.1)
            tPWM.ramp_channel(1, 0, 0.1)
            tPWM.ramp_channel(2, 0, 0.1)
            rampdir = 1

        if(currentVal == highlevel):
            tPWM.ramp_channel(3, 0, 3)
            tPWM.ramp_channel(0, 1, 0.1)
            tPWM.ramp_channel(1, 1, 0.1)
            tPWM.ramp_channel(2, 1, 0.1)
            rampdir = 0

        time.sleep(0.1)
