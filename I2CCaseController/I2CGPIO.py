import board
import busio
from digitalio import Direction
from adafruit_mcp230xx.mcp23008 import MCP23008
import time
import threading
import inspect

NUM_IO_PINS=8
RISING_AND_FALLING=0


class I2CGPIO(MCP23008):
    def __init__(self):
        i2c = busio.I2C(board.SCL, board.SDA)
        super().__init__(i2c, address=0x20)

        # initialize io polling threads
        self.poll_thread_executors = []
        for i in range(0, NUM_IO_PINS):
            self.poll_thread_executors.append(threading.Event())

    def set_direction(self, pin, direction):
        self.validate_pin(pin)
        self.validate_direction(direction)

        self.get_pin(pin).direction = direction

    def set_pin_value(self, pin, value):
        self.validate_pin(pin)
        self.get_pin(pin).value = value

    def get_pin_value(self, pin):
        self.validate_pin(pin)
        return self.get_pin(pin).value

    def poll_pin(self, pin, callback, poll_rate=0.1):
        self.validate_pin(pin)
        if(not callable(callback)):
            raise ValueError("Callback is not callable")

        if(len(inspect.getfullargspec(callback).args) != 2):
            raise ValueError("Callback must be of form callback(pin, state)")

        poll_thread = threading.Thread(target=self.thread_poll_pin, args=(pin, callback, poll_rate), daemon=True)
        self.poll_thread_executors[pin].clear()
        poll_thread.start()

    def stop_poll_pin(self, pin):
        self.validate_pin(pin)
        self.poll_thread_executors[pin].set()

    def thread_poll_pin(self, pin, callback, poll_rate):
        last_value = self.get_pin_value(pin)
        while(1):
            new_value = self.get_pin_value(pin)
            if(last_value != new_value):
                callback(pin, new_value)
            last_value = self.get_pin_value(pin)
            if(self.poll_thread_executors[pin].wait(timeout=poll_rate)):
                break;

    def validate_pin(self, pin):
        if(pin < 0 or pin > NUM_IO_PINS-1):
            raise ValueError('MCP23008 Pin Index Out of Bounds')

    def validate_direction(self, direction):
        if(not isinstance(direction, Direction)):
            raise TypeError('Direction argument must be of type digitalio.Direction')





if __name__ == '__main__':
    tMCP = I2CGPIO()
    tMCP.set_direction(0, Direction.OUTPUT)
    tMCP.set_direction(1, Direction.OUTPUT)

    tMCP.set_pin_value(0, 1)
    tMCP.set_pin_value(1, 1)

    def pressed_callback(pin, value):
        tMCP.set_pin_value(0, not value)
        print(pin, " ", value)

    tMCP.poll_pin(2, pressed_callback, poll_rate = 0.1)

    while(1):
        tMCP.get_pin_value(3)
        time.sleep(1)
