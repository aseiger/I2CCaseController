# coding=utf-8
"""Hardware-free unit tests for the I2CCaseController plugin.

Run with:
    /path/to/octoprint/bin/python -m unittest discover -s tests -v
"""
import logging
import sys
import os
import threading
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import I2CCaseController as plugin
from I2CCaseController import I2CPWM, I2CServos, VentValve


# ---------------------------------------------------------------------------
# fakes
# ---------------------------------------------------------------------------

class FakeSettings(object):
    def __init__(self, defaults):
        self.d = defaults

    def get(self, path):
        return self.d[path[0]]


class FakeCallLog(object):
    def __init__(self):
        self.calls = []

    def __getattr__(self, name):
        def fn(*args, **kwargs):
            self.calls.append((name, args, kwargs))
            return 0
        return fn

    def messages(self, msg_type):
        return [c[1][1]["value"] for c in self.calls
                if c[0] == "send_plugin_message" and c[1][1].get("msgType") == msg_type]


class FakePrinter(object):
    def __init__(self, printing=False):
        self.printing = printing
        self.calls = []

    def is_printing(self):
        return self.printing

    def connect(self):
        self.calls.append("connect")

    def disconnect(self):
        self.calls.append("disconnect")


class FakeMCP(object):
    def __init__(self):
        self.pins = {}

    def set_direction(self, pin, direction):
        pass

    def set_pin_value(self, pin, value):
        self.pins[pin] = value

    def get_pin_value(self, pin):
        return self.pins.get(pin, 0)


class FakePWM(object):
    def __init__(self):
        self.values = {}

    def set_channel(self, pin, power):
        self.values[pin] = power

    def get_channel(self, pin):
        return self.values.get(pin, 0.0)

    def ramp_channel(self, pin, power, ramp_time):
        self.set_channel(pin, power)


class FakeServo(object):
    def __init__(self):
        self.angles = {}

    def set_channel(self, pin, angle):
        self.angles[pin] = angle

    def get_channel(self, pin):
        return self.angles.get(pin, 0.0)

    def ramp_channel(self, pin, angle, ramp_time):
        self.set_channel(pin, angle)


def make_plugin(printing=False):
    p = plugin.I2ccasecontrollerPlugin()
    p._logger = logging.getLogger("test")
    p._settings = FakeSettings(p.get_settings_defaults())
    p._identifier = "I2CCaseController"
    p._plugin_manager = FakeCallLog()
    p._printer = FakePrinter(printing)
    p.tMCP, p.tPWM, p.tServo = FakeMCP(), FakePWM(), FakeServo()
    return p


# ---------------------------------------------------------------------------
# address parsing
# ---------------------------------------------------------------------------

class TestParseI2CAddress(unittest.TestCase):
    def test_prefixed_hex(self):
        self.assertEqual(plugin.parse_i2c_address("0x41", 0x40), 0x41)
        self.assertEqual(plugin.parse_i2c_address("0x20", 0x40), 0x20)

    def test_plain_int(self):
        self.assertEqual(plugin.parse_i2c_address(0x48, 0x40), 0x48)

    def test_decimal_string(self):
        self.assertEqual(plugin.parse_i2c_address("72", 0x40), 72)

    def test_whitespace(self):
        self.assertEqual(plugin.parse_i2c_address("  0x41  ", 0x40), 0x41)

    def test_garbage_falls_back(self):
        self.assertEqual(plugin.parse_i2c_address("garbage", 0x40), 0x40)
        self.assertEqual(plugin.parse_i2c_address(None, 0x40), 0x40)

    def test_out_of_range_falls_back(self):
        self.assertEqual(plugin.parse_i2c_address("0x100", 0x40), 0x40)
        self.assertEqual(plugin.parse_i2c_address("0", 0x40), 0x40)


# ---------------------------------------------------------------------------
# vent valve mapping
# ---------------------------------------------------------------------------

class TestVentValve(unittest.TestCase):
    def setUp(self):
        self.valve = VentValve.VentValve(180, 90)  # closed=180, open=90

    def test_endpoints(self):
        self.assertEqual(self.valve.set_percent(0.0), 180)
        self.assertEqual(self.valve.set_percent(1.0), 90)

    def test_midpoint(self):
        self.assertEqual(self.valve.set_percent(0.5), 135)

    def test_clamps(self):
        self.assertEqual(self.valve.set_percent(1.5), 90)
        self.assertEqual(self.valve.set_percent(-0.5), 180)

    def test_inverted_range(self):
        valve = VentValve.VentValve(10, 170)  # closed=10, open=170
        self.assertEqual(valve.set_percent(0.0), 10)
        self.assertEqual(valve.set_percent(1.0), 170)


# ---------------------------------------------------------------------------
# ramp math (hardware classes without a constructor - no I2C touched)
# ---------------------------------------------------------------------------

class FakePwmChannel(object):
    def __init__(self, duty=0):
        self.duty_cycle = duty


class FakeServoChannel(object):
    def __init__(self, angle=0.0):
        self.angle = angle


def bare_pwm(start_raw=0):
    pwm = I2CPWM.I2CPWM.__new__(I2CPWM.I2CPWM)
    pwm._i2c_lock = threading.Lock()
    pwm._ramp_generation = [0] * 16
    pwm.channels = [FakePwmChannel(start_raw) for _ in range(16)]
    return pwm


def bare_servos(start_angle=0.0):
    s = I2CServos.I2CServos.__new__(I2CServos.I2CServos)
    s._i2c_lock = threading.Lock()
    s._ramp_generation = [0] * 16
    # 'servo' is a read-only property on ServoKit; set its backing store
    s._servo = [FakeServoChannel(start_angle) for _ in range(16)]
    return s


class TestPwmRamp(unittest.TestCase):
    def test_ramp_up_reaches_target(self):
        pwm = bare_pwm(0)
        with mock.patch("time.sleep"):
            pwm._ramp_channel_thread(0, 0, 0xFFFF, 1.0, 0)
        self.assertEqual(pwm.channels[0].duty_cycle, 0xFFFF)

    def test_ramp_down_reaches_target(self):
        pwm = bare_pwm(0xFFFF)
        with mock.patch("time.sleep"):
            pwm._ramp_channel_thread(0, 0xFFFF, 0, 1.0, 0)
        self.assertEqual(pwm.channels[0].duty_cycle, 0)

    def test_minimum_ramp_time_is_one_step(self):
        pwm = bare_pwm(0)
        with mock.patch("time.sleep") as sleeper:
            pwm._ramp_channel_thread(0, 0, 0xFFFF, I2CPWM.MIN_RAMP_TIME, 0)
        self.assertEqual(pwm.channels[0].duty_cycle, 0xFFFF)
        self.assertEqual(sleeper.call_count, 0)  # no sleep on a 1-step ramp

    def test_superseded_ramp_stops(self):
        pwm = bare_pwm(0)
        pwm._ramp_generation[0] = 1  # a newer command was issued
        with mock.patch("time.sleep"):
            pwm._ramp_channel_thread(0, 0, 0xFFFF, 1.0, 0)
        self.assertEqual(pwm.channels[0].duty_cycle, 0)  # never wrote


class TestServoRamp(unittest.TestCase):
    def test_ramp_open_reaches_target(self):
        s = bare_servos(0.0)
        with mock.patch("time.sleep"):
            s._ramp_channel_thread(0, 0.0, 180.0, 1.0, 0)
        self.assertEqual(s.servo[0].angle, 180.0)

    def test_ramp_close_reaches_target(self):
        s = bare_servos(180.0)
        with mock.patch("time.sleep"):
            s._ramp_channel_thread(0, 180.0, 0.0, 1.0, 0)
        self.assertEqual(s.servo[0].angle, 0.0)

    def test_superseded_ramp_stops(self):
        s = bare_servos(0.0)
        s._ramp_generation[0] = 1
        with mock.patch("time.sleep"):
            s._ramp_channel_thread(0, 0.0, 180.0, 1.0, 0)
        self.assertEqual(s.servo[0].angle, 0.0)

    def test_zero_ramp_time_does_not_hang(self):
        # regression: ramp_time=0 used to make step_amount 0 and loop forever
        s = bare_servos(0.0)
        with mock.patch("time.sleep"):
            # MIN_RAMP_TIME clamp is applied in ramp_channel(); the thread
            # itself must handle a single step without looping
            s._ramp_channel_thread(0, 0.0, 180.0, I2CServos.MIN_RAMP_TIME, 0)
        self.assertEqual(s.servo[0].angle, 180.0)


# ---------------------------------------------------------------------------
# plugin logic with fake hardware
# ---------------------------------------------------------------------------

class TestApiCommands(unittest.TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)
        self.p = make_plugin()

    def tearDown(self):
        logging.disable(logging.NOTSET)

    def test_missing_key_returns_400(self):
        resp = self.p.on_api_command("valvePercentageSet", {})
        self.assertEqual(resp.status_code, 400)
        self.assertIn("valvePercentage is required", resp.get_data(as_text=True))

    def test_non_numeric_returns_400(self):
        resp = self.p.on_api_command("lightBrightnessSet", {"lightBrightness": "bright"})
        self.assertEqual(resp.status_code, 400)
        self.assertIn("must be a number", resp.get_data(as_text=True))

    def test_out_of_range_returns_400(self):
        resp = self.p.on_api_command("fanPowerSet", {"fanPowerLevel": 1.5})
        self.assertEqual(resp.status_code, 400)
        self.assertIn("between", resp.get_data(as_text=True))

    def test_none_data_returns_400(self):
        resp = self.p.on_api_command("fanPowerSet", None)
        self.assertEqual(resp.status_code, 400)

    def test_fan_power_set_applies_and_pushes_state(self):
        self.assertIsNone(self.p.on_api_command("fanPowerSet", {"fanPowerLevel": 0.5}))
        self.assertEqual(self.p.tPWM.values[self.p.pin_pwm_fan], 0.5)
        self.assertIn("on", self.p._plugin_manager.messages("fanPowerState"))

    def test_valve_percentage_maps_through_vent_valve(self):
        self.p.on_api_command("valvePercentageSet", {"valvePercentage": 0.5})
        expected = VentValve.VentValve(
            self.p.param_vent_valve_closed, self.p.param_vent_valve_open).set_percent(0.5)
        self.assertEqual(self.p.tServo.angles[self.p.pin_servo_vent_valve], expected)
        self.assertEqual(self.p._plugin_manager.messages("valvePositionUpdate")[-1], expected)

    def test_valve_position_set_pushes_position(self):
        # regression: valvePositionSet never pushed the new position
        self.p.on_api_command("valvePositionSet", {"valvePosition": 120})
        self.assertEqual(self.p.tServo.angles[self.p.pin_servo_vent_valve], 120)
        self.assertEqual(self.p._plugin_manager.messages("valvePositionUpdate")[-1], 120)

    def test_light_brightness_pushes_state(self):
        self.p.on_api_command("lightBrightnessSet", {"lightBrightness": 0.7})
        self.assertEqual(self.p._plugin_manager.messages("caseLightState")[-1], "on")

    def test_no_hardware_returns_none(self):
        self.p.tMCP = None
        self.assertIsNone(self.p.on_api_command("fanPowerSet", {"fanPowerLevel": 0.5}))


class TestPrintState(unittest.TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)
        from octoprint.events import Events
        self.events = Events
        self.p = make_plugin()

    def tearDown(self):
        logging.disable(logging.NOTSET)

    def wait_dead(self, timer, timeout=2):
        import time
        end = time.time() + timeout
        while timer.is_alive() and time.time() < end:
            time.sleep(0.01)
        return not timer.is_alive()

    def test_print_started_applies_case_state(self):
        self.p.on_event(self.events.PRINT_STARTED, None)
        self.assertEqual(self.p.tMCP.pins[self.p.pin_gpio_fan_power],
                         self.p.pin_gpio_fan_power_on_state)
        self.assertEqual(self.p.tPWM.values[self.p.pin_pwm_fan], self.p.param_fan_power)
        self.assertEqual(self.p.tServo.angles[self.p.pin_servo_vent_valve],
                         self.p.param_vent_valve_open)
        self.assertEqual(self.p.tPWM.values[self.p.pin_pwm_machine_light], 1.0)

    def test_print_done_arms_power_down(self):
        self.p.on_event(self.events.PRINT_DONE, None)
        self.assertNotEqual(self.p.tMCP.pins[self.p.pin_gpio_fan_power],
                            self.p.pin_gpio_fan_power_on_state)
        self.assertEqual(self.p.tPWM.values[self.p.pin_pwm_fan], 0)
        self.assertEqual(self.p.tServo.angles[self.p.pin_servo_vent_valve],
                         self.p.param_vent_valve_closed)
        self.assertEqual(self.p.tPWM.values[self.p.pin_pwm_machine_light], 0.0)
        self.assertIsNotNone(self.p.machinePowerDownTimer)
        self.assertTrue(self.p.machinePowerDownTimer.is_alive())

    def test_print_cancelled_disarms_power_down(self):
        # regression: machine powered off 5 min after a cancel
        self.p.on_event(self.events.PRINT_DONE, None)
        self.p.on_event(self.events.PRINT_CANCELLED, None)
        self.assertTrue(self.wait_dead(self.p.machinePowerDownTimer))

    def test_print_started_disarms_stale_power_down(self):
        self.p.on_event(self.events.PRINT_DONE, None)
        self.p.on_event(self.events.PRINT_STARTED, None)
        self.assertTrue(self.wait_dead(self.p.machinePowerDownTimer))

    def test_machine_off_refused_while_printing(self):
        p = make_plugin(printing=True)
        p.tMCP.pins[p.pin_gpio_machine_power] = p.pin_gpio_machine_on_state
        p.machine_off()
        self.assertEqual(p.tMCP.pins[p.pin_gpio_machine_power],
                         p.pin_gpio_machine_on_state)  # still on

    def test_resync_if_printing(self):
        p = make_plugin(printing=True)
        p.tPWM.values.clear()
        p.tServo.angles.clear()
        p._resync_if_printing()
        self.assertEqual(p.tServo.angles[p.pin_servo_vent_valve], p.param_vent_valve_open)
        self.assertEqual(p.tPWM.values[p.pin_pwm_fan], p.param_fan_power)

    def test_resync_idle_is_noop(self):
        p = make_plugin(printing=False)
        before = dict(p.tPWM.values)
        p._resync_if_printing()
        self.assertEqual(dict(p.tPWM.values), before)


class TestLightLogic(unittest.TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)
        self.p = make_plugin()

    def tearDown(self):
        logging.disable(logging.NOTSET)

    def test_timelapse_restores_off_light(self):
        p = self.p
        p.tPWM.values[p.pin_pwm_light] = 0.0
        p.lightOnReason = "none"
        p.timelapse_capture_pre("f.jpg")
        self.assertEqual(p.tPWM.values[p.pin_pwm_light], 1)
        p.timelapse_capture_post("f.jpg", True)
        self.assertEqual(p.tPWM.values[p.pin_pwm_light], 0.0)

    def test_timelapse_restores_manual_brightness(self):
        # regression: old code turned the light off (reason was "none")
        p = self.p
        p.tPWM.values[p.pin_pwm_light] = 0.7
        p.lightOnReason = "none"
        p.timelapse_capture_pre("f.jpg")
        p.timelapse_capture_post("f.jpg", True)
        self.assertEqual(p.tPWM.values[p.pin_pwm_light], 0.7)

    def test_door_open_keeps_light_and_reason(self):
        # regression: case_light_off cleared the reason before checking the
        # door, letting a capture post-hook kill a door-kept-on light
        p = self.p
        p.tPWM.values[p.pin_pwm_light] = 0.2
        p.lightOnReason = "door"
        p.tMCP.pins[p.pin_gpio_door_switch] = True
        p.case_light_off()
        self.assertEqual(p.tPWM.values[p.pin_pwm_light], 0.2)
        self.assertEqual(p.lightOnReason, "door")
        p.timelapse_capture_pre("f.jpg")
        p.timelapse_capture_post("f.jpg", True)
        self.assertEqual(p.tPWM.values[p.pin_pwm_light], 0.2)

    def test_door_closed_turns_light_off(self):
        p = self.p
        p.tPWM.values[p.pin_pwm_light] = 0.2
        p.lightOnReason = "door"
        p.tMCP.pins[p.pin_gpio_door_switch] = False
        p.case_light_off()
        self.assertEqual(p.tPWM.values[p.pin_pwm_light], 0.0)
        self.assertEqual(p.lightOnReason, "none")


class TestSensorAliases(unittest.TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)
        self.p = make_plugin()

    def tearDown(self):
        logging.disable(logging.NOTSET)

    def test_configured_name(self):
        self.p._settings.d["ds18b20_bus1_alias"] = "Chamber"
        self.assertEqual(self.p.onewire_bus_to_alias("bus.1"), "Chamber")

    def test_unknown_bus_falls_back_to_raw_name(self):
        # regression: KeyError aborted the whole temp update loop
        self.assertEqual(self.p.onewire_bus_to_alias("bus.9"), "bus.9")
        self.assertEqual(self.p.onewire_bus_to_alias("weird/path"), "weird/path")

    def test_empty_alias_falls_back(self):
        self.assertEqual(self.p.onewire_bus_to_alias("bus.3"), "bus.3")


if __name__ == "__main__":
    unittest.main(verbosity=2)
