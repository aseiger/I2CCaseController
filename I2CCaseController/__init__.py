# coding=utf-8
from __future__ import absolute_import
from . import I2CGPIO
from . import I2CPWM
from . import I2CServos
from digitalio import Direction
import time
import threading
from octoprint.events import Events

### (Don't forget to remove me)
# This is a basic skeleton for your plugin's __init__.py. You probably want to adjust the class name of your plugin
# as well as the plugin mixins it's subclassing from. This is really just a basic skeleton to get you started,
# defining your plugin as a template plugin, settings and asset plugin. Feel free to add or remove mixins
# as necessary.
#
# Take a look at the documentation on what other plugin mixins are available.

import octoprint.plugin

class I2ccasecontrollerPlugin(octoprint.plugin.StartupPlugin,
                              octoprint.plugin.SettingsPlugin,
                              octoprint.plugin.AssetPlugin,
                              octoprint.plugin.TemplatePlugin,
                              octoprint.plugin.SimpleApiPlugin,
                              octoprint.plugin.EventHandlerPlugin):


    tMCP = I2CGPIO.I2CGPIO()
    tPWM = I2CPWM.I2CPWM()
    tServo = I2CServos.I2CServos()

    lightTimer = threading.Timer(0, 0)
	##~~ SettingsPlugin mixin

    def get_settings_defaults(self):
        return dict(
			pwm_addr="0x41",
            servo_addr="0x40",
            gpio_addr="0x20",
            thermistors_addr="0x48",
            pin_gpio_machine_power="1",
            pin_gpio_machine_on_state="0",
            pin_gpio_fan_power="0",
            pin_gpio_fan_power_on_state="0",
            pin_pwm_fan="4",
            pin_pwm_light="3",
            pin_gpio_door_switch="2",
            pin_gpio_side_button="3",
            param_case_light_timeout="60",
            param_case_light_ramp_time="1",
            param_case_light_brightness="0.2",
            param_fan_power="0.4",
            pin_servo_vent_valve="0",
            param_vent_valve_open="90",
            param_vent_valve_closed="180"
        )

    def case_light_on(self, timeout=0):
        self.lightTimer.cancel()
        self.tPWM.ramp_channel(self.pin_pwm_light, self.param_case_light_brightness, self.param_case_light_ramp_time)
        self.update_case_light_status("on")
        if(timeout > 0):
            self.lightTimer = threading.Timer(timeout, self.case_light_off)
            self.lightTimer.start()
            self.update_case_light_status("on_timeout")

        self._logger.info("Case Light on %d", timeout)



    def case_light_off(self, delay=0):
        self.lightTimer.cancel()

        # if we try to turn the light off and the door is open, just cancel the timeout
        if(self.tMCP.get_pin_value(self.pin_gpio_door_switch) == True):
            self.update_case_light_status("on")
            return

        if(delay == 0):
            self.tPWM.ramp_channel(self.pin_pwm_light, 0, self.param_case_light_ramp_time)
            self.update_case_light_status("off")
        else:
            self.lightTimer = threading.Timer(delay, self.case_light_off)
            self.lightTimer.start()

        self._logger.info("Case Light off %d", delay)

    def door_switch_callback(self, pin, value):
        self._logger.info("Door Switch %d", value)

        if(not self.lightTimer.is_alive()):
            if(value == True):
                self.case_light_on()
            else:
                self.case_light_off()

    def side_button_callback(self, pin, value):
        self._logger.info("Side Button %d", value)

        if(value == True):
            if(self.tPWM.get_channel(self.pin_pwm_light) == 0.0):
                self.case_light_on(timeout=self.param_case_light_timeout)
            else:
                self.case_light_off()

    @property
    def pwm_addr(self):
        return int(self._settings.get(["pwm_addr"]))

    @property
    def servo_addr(self):
        return int(self._settings.get(["servo_addr"]))

    @property
    def gpio_addr(self):
        return int(self._settings.get(["gpio_addr"]))

    @property
    def thermistors_addr(self):
        return int(self._settings.get(["thermistors_addr"]))

    @property
    def pin_gpio_machine_power(self):
        return int(self._settings.get(["pin_gpio_machine_power"]))

    @property
    def pin_gpio_machine_on_state(self):
        return int(self._settings.get(["pin_gpio_machine_on_state"]))

    @property
    def pin_gpio_fan_power(self):
        return int(self._settings.get(["pin_gpio_fan_power"]))

    @property
    def pin_gpio_fan_power_on_state(self):
        return int(self._settings.get(["pin_gpio_fan_power_on_state"]))

    @property
    def pin_pwm_fan(self):
        return int(self._settings.get(["pin_pwm_fan"]))

    @property
    def pin_pwm_light(self):
        return int(self._settings.get(["pin_pwm_light"]))

    @property
    def pin_gpio_door_switch(self):
        return int(self._settings.get(["pin_gpio_door_switch"]))

    @property
    def pin_gpio_side_button(self):
        return int(self._settings.get(["pin_gpio_side_button"]))

    @property
    def param_case_light_timeout(self):
        return int(self._settings.get(["param_case_light_timeout"]))

    @property
    def param_case_light_ramp_time(self):
        return float(self._settings.get(["param_case_light_ramp_time"]))

    @property
    def param_case_light_brightness(self):
        return float(self._settings.get(["param_case_light_brightness"]))

    @property
    def param_fan_power(self):
        return float(self._settings.get(["param_fan_power"]))

    @property
    def pin_servo_vent_valve(self):
        return int(self._settings.get(["pin_servo_vent_valve"]))

    @property
    def param_vent_valve_open(self):
        return float(self._settings.get(["param_vent_valve_open"]))

    @property
    def param_vent_valve_closed(self):
        return float(self._settings.get(["param_vent_valve_closed"]))

    def get_api_commands(self):
        return dict(
            caseLightToggle=[],
            fanPowerToggle=[],
            machinePowerToggle=[],
            fanPowerSet=[],
            valvePositionSet=[],
            lightBrightnessSet=[]
        )

    def update_machine_power(self):
        stateStr = "unknown"
        if(self.tMCP.get_pin_value(self.pin_gpio_machine_power) == self.pin_gpio_machine_on_state):
            stateStr = "on"
        else:
            stateStr = "off"

        self._plugin_manager.send_plugin_message(self._identifier,
                                                 dict(
                                                      msgType="machinePowerState",
                                                      value=stateStr))

    def update_fan_power(self):
        stateStr = "unknown"
        if(self.tMCP.get_pin_value(self.pin_gpio_fan_power) == self.pin_gpio_fan_power_on_state):
            stateStr = "on"
        else:
            stateStr = "off"

        self._plugin_manager.send_plugin_message(self._identifier,
                                                 dict(
                                                      msgType="fanPowerState",
                                                      value=stateStr))

    def update_case_light_status(self, state="unknown"):
        stateStr = state
        if(state == "unknown"):
            if(self.tPWM.get_channel(self.pin_pwm_light) == 0.0):
                stateStr = "off"
            else:
                stateStr = "on"

        self._plugin_manager.send_plugin_message(self._identifier,
                                                 dict(
                                                      msgType="caseLightState",
                                                      value=stateStr))

    def on_api_command(self, command, data):
        import flask
        self._logger.info(data)
        if command == "caseLightToggle":
            if(self.tPWM.get_channel(self.pin_pwm_light) == 0.0):
                self.case_light_on(timeout=self.param_case_light_timeout)
            else:
                self.case_light_off()
        elif command == "fanPowerToggle":
            self.tMCP.set_pin_value(self.pin_gpio_fan_power, not self.tMCP.get_pin_value(self.pin_gpio_fan_power))
            if(self.tMCP.get_pin_value(self.pin_gpio_fan_power) == self.pin_gpio_fan_power_on_state):
                self.tPWM.set_channel(self.pin_pwm_fan, self.param_fan_power)
                self.tServo.ramp_channel(self.pin_servo_vent_valve, self.param_vent_valve_open, 2)
            else:
                self.tPWM.set_channel(self.pin_pwm_fan, 0)
                self.tServo.ramp_channel(self.pin_servo_vent_valve, self.param_vent_valve_closed, 2)

            self.update_fan_power()

        elif command == "machinePowerToggle":
            if(not self._printer.is_printing()):
                self.tMCP.set_pin_value(self.pin_gpio_machine_power, not self.tMCP.get_pin_value(self.pin_gpio_machine_power))
                self.update_machine_power()

        elif command == "fanPowerSet":
            self.tPWM.set_channel(self.pin_pwm_fan, float(data["fanPowerLevel"]))

        elif command == "valvePositionSet":
            self.tServo.set_channel(self.pin_servo_vent_valve, float(data["valvePosition"]))

        elif command == "lightBrightnessSet":
            self.tPWM.set_channel(self.pin_pwm_light, float(data["lightBrightness"]))

    def on_event(self, event, payload):
        if event == Events.CLIENT_OPENED:
            self.update_fan_power()
            self.update_machine_power()
            self.update_case_light_status()

    # def get_template_vars(self):
    #     return dict(
    #         pwm_addr=self._settings.get(["pwm_addr"]),
    #         servo_addr=self._settings.get(["servo_addr"]),
    #         gpio_addr=self._settings.get(["gpio_addr"]),
    #         thermistor_addr=self._settings.get(["thermistor_addr"])
    #     )

    def get_template_configs(self):
        return [
            dict(type="navbar", custom_bindings=True),
            dict(type="settings", custom_bindings=False)
        ]

	##~~ AssetPlugin mixin

    def get_assets(self):
		# Define your plugin's asset files to automatically include in the
		# core UI here.
        return dict(
            js=["js/I2CCaseController.js"],
            css=["css/I2CCaseController.css"],
            less=["less/I2CCaseController.less"]
        )

	##~~ Softwareupdate hook

    def get_update_information(self):
		# Define the configuration for your plugin to use with the Software Update
		# Plugin here. See https://docs.octoprint.org/en/master/bundledplugins/softwareupdate.html
		# for details.
        return dict(
            I2CCaseController=dict(
                displayName="I2ccasecontroller Plugin",
                displayVersion=self._plugin_version,

				# version check: github repository
                type="github_release",
                user="aseiger",
                repo="I2CCaseController",
                current=self._plugin_version,

				# update method: pip
                pip="https://github.com/aseiger/I2CCaseController/archive/{target_version}.zip"
			)
		)

    ##~~ OnAfterStartup hook

    def on_after_startup(self):
        self._logger.info("Starting I2C Case Controller!")
        self._logger.info("PWM Addr: %s", self._settings.get(["pwm_addr"]))
        self._logger.info("Servo Addr: %s", self._settings.get(["servo_addr"]))
        self._logger.info("GPIO Addr: %s", self._settings.get(["gpio_addr"]))
        self._logger.info("Thermistors Addr: %s", self._settings.get(["thermistors_addr"]))

        self._logger.info("Machine Power GPIO Pin: %s", self._settings.get(["pin_gpio_machine_power"]))
        self._logger.info("Fan Power GPIO Pin: %s", self._settings.get(["pin_gpio_fan_power"]))
        self._logger.info("Fan PWM Pin: %s", self._settings.get(["pin_pwm_fan"])),
        self._logger.info("Light PWM Pin: %s", self._settings.get(["pin_pwm_light"]))
        self._logger.info("Door Switch GPIO Pin: %s", self._settings.get(["pin_gpio_door_switch"]))
        self._logger.info("Side Button GPIO Pin: %s", self._settings.get(["pin_gpio_side_button"]))

        self._logger.info("Machine GPIO On State: %s", self.pin_gpio_machine_on_state)
        self._logger.info("Machine GPIO On State: %s", self.pin_gpio_fan_power_on_state)

        self.tPWM.set_channel(self.pin_pwm_light, 0)
        self.tPWM.set_channel(self.pin_pwm_fan, 0)

        self.tMCP.set_direction(self.pin_gpio_machine_power, Direction.OUTPUT)
        self.tMCP.set_pin_value(self.pin_gpio_machine_power, not self.pin_gpio_machine_on_state)

        self.tMCP.set_direction(self.pin_gpio_fan_power, Direction.OUTPUT)
        self.tMCP.set_pin_value(self.pin_gpio_fan_power, not self.pin_gpio_machine_on_state)

        self.tMCP.set_direction(self.pin_gpio_door_switch, Direction.INPUT)
        self.tMCP.set_direction(self.pin_gpio_side_button, Direction.INPUT)

        self.tMCP.poll_pin(self.pin_gpio_door_switch, self.door_switch_callback, poll_rate = 0.1)
        self.tMCP.poll_pin(self.pin_gpio_side_button, self.side_button_callback, poll_rate = 0.1)

        self.tServo.set_channel(self.pin_servo_vent_valve, self.param_vent_valve_closed)

def __plugin_check__():
    # Make sure we only run our plugin if some_dependency is available
    try:
        import board
        import busio
        import time
        import adafruit_pca9685
        from digitalio import Direction
        from adafruit_mcp230xx.mcp23008 import MCP23008
        from adafruit_servokit import ServoKit
        import Adafruit_ADS1x15
    except ImportError:
        return False

    return True


# If you want your plugin to be registered within OctoPrint under a different name than what you defined in setup.py
# ("OctoPrint-PluginSkeleton"), you may define that here. Same goes for the other metadata derived from setup.py that
# can be overwritten via __plugin_xyz__ control properties. See the documentation for that.
__plugin_name__ = "I2ccasecontroller Plugin"

# Starting with OctoPrint 1.4.0 OctoPrint will also support to run under Python 3 in addition to the deprecated
# Python 2. New plugins should make sure to run under both versions for now. Uncomment one of the following
# compatibility flags according to what Python versions your plugin supports!
#__plugin_pythoncompat__ = ">=2.7,<3" # only python 2
__plugin_pythoncompat__ = ">=3,<4" # only python 3
#__plugin_pythoncompat__ = ">=2.7,<4" # python 2 and 3

def __plugin_load__():
	global __plugin_implementation__
	__plugin_implementation__ = I2ccasecontrollerPlugin()

	global __plugin_hooks__
	__plugin_hooks__ = {
		"octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
	}
