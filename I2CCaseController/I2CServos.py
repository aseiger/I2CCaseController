"""Simple test for a standard servo on channel 0 and a continuous rotation servo on channel 1."""
import time
from adafruit_servokit import ServoKit
import threading

NUM_IO_PINS=16
RAMP_DELAY=0.05

class I2CServos(ServoKit):

    channelRampThreads = [threading.Thread()] * NUM_IO_PINS

    def __init__(self):
        super().__init__(channels=16, address=0x40)

    def set_channel(self, pin, angle):
        self.validate_pin(pin)
        self.servo[pin].angle = angle

    def get_channel(self, pin):
        self.validate_pin(pin)
        return self.servo[pin].angle

    def ramp_channel(self, pin, new_angle, ramp_time):
        self.validate_pin(pin)
        if(not self.channelRampThreads[pin].is_alive()):
            self.channelRampThreads[pin] = threading.Thread(target=self.ramp_channel_thread, args=(pin, new_angle, ramp_time), daemon=True)
            self.channelRampThreads[pin].start()
        return self.channelRampThreads[pin]

    def ramp_channel_thread(self, pin, new_angle, ramp_time):
        current_angle = self.get_channel(pin)
        angle_to_go = new_angle - current_angle
        step_amount = (RAMP_DELAY * angle_to_go) / ramp_time

        while abs(angle_to_go) > abs(step_amount):
            hitBound = False
            newAngle = current_angle + step_amount
            if(newAngle < 0):
                newAngle = 0
                hitBound = True
            if(newAngle > 180):
                newAngle = 180
                hitBound = True
            
            self.servo[pin].angle = newAngle
            current_angle = self.get_channel(pin)
            angle_to_go = new_angle - current_angle
            if(hitBound == True):
                break
            else:
                time.sleep(RAMP_DELAY)

        self.servo[pin].angle = new_angle


    def validate_pin(self, pin):
        if(pin < 0 or pin > NUM_IO_PINS-1):
            raise ValueError('PCA9685 Pin Index Out of Bounds')

if __name__ == '__main__':
    tServo = I2CServos()

    tServo.set_channel(0, 90)

    time.sleep(1)

    while(1):
        tServo.ramp_channel(0, 180, 1)
        time.sleep(0)
        tServo.ramp_channel(0, 0, 1)
        time.sleep(0)
