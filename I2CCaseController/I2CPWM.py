import board
import busio
import time
import adafruit_pca9685
import threading

NUM_IO_PINS = 16
MAX_CHANNEL_POWER = 0xFFFF
RAMP_DELAY = 0.05
# Ramps shorter than this are clamped to one step instead of dividing by ~0.
MIN_RAMP_TIME = RAMP_DELAY


class I2CPWM(adafruit_pca9685.PCA9685):

    def __init__(self, address=0x41):
        i2c = busio.I2C(board.SCL, board.SDA)
        super().__init__(i2c, address=address)

        # All pwm_regs reads and writes are I2C transactions; busio.I2C is not
        # thread safe, so every access happens under this lock.
        self._i2c_lock = threading.Lock()
        # Bumped for each new ramp command; a running ramp thread that notices
        # a newer generation stops instead of fighting the new command.
        self._ramp_generation = [0] * NUM_IO_PINS

        self.frequency = 1600

    def set_channel(self, pin, power):
        self.validate_pin(pin)
        self.validate_power(power)
        with self._i2c_lock:
            self.channels[pin].duty_cycle = int(power * MAX_CHANNEL_POWER)

    def get_channel(self, pin):
        self.validate_pin(pin)
        with self._i2c_lock:
            return self.channels[pin].duty_cycle / MAX_CHANNEL_POWER

    def ramp_channel(self, pin, new_power, ramp_time):
        """Ramp a channel to new_power over ramp_time seconds.

        Starting a new ramp supersedes any ramp already in flight on the same
        channel: the old ramp thread stops, the new one starts from the
        channel's current value. ramp_time is clamped to MIN_RAMP_TIME so a
        zero (or negative) value can never crash or hang the ramp thread.
        """
        self.validate_pin(pin)
        self.validate_power(new_power)
        ramp_time = max(float(ramp_time or 0.0), MIN_RAMP_TIME)

        current_raw = int(self.get_channel(pin) * MAX_CHANNEL_POWER)
        target_raw = int(new_power * MAX_CHANNEL_POWER)
        if current_raw == target_raw:
            return None

        with self._i2c_lock:
            self._ramp_generation[pin] += 1
            generation = self._ramp_generation[pin]

        thread = threading.Thread(
            target=self._ramp_channel_thread,
            args=(pin, current_raw, target_raw, ramp_time, generation),
            daemon=True,
        )
        thread.start()
        return thread

    def _ramp_channel_thread(self, pin, start_raw, target_raw, ramp_time, generation):
        steps = max(1, int(round(ramp_time / RAMP_DELAY)))
        for step in range(1, steps + 1):
            if self._ramp_generation[pin] != generation:
                return  # superseded by a newer command
            value = start_raw + (target_raw - start_raw) * step // steps
            with self._i2c_lock:
                self.channels[pin].duty_cycle = value
            if step < steps:
                time.sleep(RAMP_DELAY)

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
    #     tPWM.ramp_channel(3, 1, 3)
    #     time.sleep(0)

    #     tPWM.ramp_channel(3, 0, 3)
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
