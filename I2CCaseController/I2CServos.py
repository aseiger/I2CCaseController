import time
from adafruit_servokit import ServoKit
import threading

NUM_IO_PINS = 16
RAMP_DELAY = 0.05
MIN_ANGLE = 0
MAX_ANGLE = 180
# Ramps shorter than this are clamped to one step instead of dividing by ~0.
MIN_RAMP_TIME = RAMP_DELAY


class I2CServos(ServoKit):

    def __init__(self, address=0x40, channels=NUM_IO_PINS):
        super().__init__(channels=channels, address=address)

        # Servo angle writes are I2C transactions; busio.I2C is not thread
        # safe, so every servo access happens under this lock.
        self._i2c_lock = threading.Lock()
        # Bumped for each new ramp command; a running ramp thread that notices
        # a newer generation stops instead of fighting the new command.
        self._ramp_generation = [0] * channels

    def set_channel(self, pin, angle):
        self.validate_pin(pin)
        angle = self.validate_angle(angle)
        with self._i2c_lock:
            self.servo[pin].angle = angle

    def get_channel(self, pin):
        self.validate_pin(pin)
        with self._i2c_lock:
            return self.servo[pin].angle

    def ramp_channel(self, pin, new_angle, ramp_time):
        """Ramp a servo to new_angle over ramp_time seconds.

        Starting a new ramp supersedes any ramp already in flight on the same
        channel: the old ramp thread stops, the new one starts from the
        servo's current angle. ramp_time is clamped to MIN_RAMP_TIME so a
        zero (or negative) value can never crash or hang the ramp thread.
        """
        self.validate_pin(pin)
        new_angle = self.validate_angle(new_angle)
        ramp_time = max(float(ramp_time or 0.0), MIN_RAMP_TIME)

        current_angle = self.get_channel(pin)
        if abs(new_angle - current_angle) < 0.01:
            return None

        with self._i2c_lock:
            self._ramp_generation[pin] += 1
            generation = self._ramp_generation[pin]

        thread = threading.Thread(
            target=self._ramp_channel_thread,
            args=(pin, current_angle, new_angle, ramp_time, generation),
            daemon=True,
        )
        thread.start()
        return thread

    def _ramp_channel_thread(self, pin, start_angle, target_angle, ramp_time, generation):
        steps = max(1, int(round(ramp_time / RAMP_DELAY)))
        for step in range(1, steps + 1):
            if self._ramp_generation[pin] != generation:
                return  # superseded by a newer command
            angle = start_angle + (target_angle - start_angle) * step / steps
            angle = max(MIN_ANGLE, min(MAX_ANGLE, angle))
            with self._i2c_lock:
                self.servo[pin].angle = angle
            if step < steps:
                time.sleep(RAMP_DELAY)

    def validate_pin(self, pin):
        if(pin < 0 or pin > NUM_IO_PINS-1):
            raise ValueError('Servo Pin Index Out of Bounds')

    def validate_angle(self, angle):
        angle = float(angle)
        if(angle < MIN_ANGLE or angle > MAX_ANGLE):
            raise ValueError('Servo Accepts Angles 0-180 Only')
        return angle

if __name__ == '__main__':
    tServo = I2CServos()

    tServo.set_channel(0, 90)

    time.sleep(1)

    while(1):
        tServo.ramp_channel(0, 180, 1)
        time.sleep(0)
        tServo.ramp_channel(0, 0, 1)
        time.sleep(0)
