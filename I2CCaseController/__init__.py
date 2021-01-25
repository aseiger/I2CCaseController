# coding=utf-8
from __future__ import absolute_import

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
                              octoprint.plugin.TemplatePlugin):

	##~~ SettingsPlugin mixin

    def get_settings_defaults(self):
        return dict(
			pwm_addr="0x41",
            servo_addr="0x40",
            gpio_addr="0x20",
            thermistors_addr="0x48"
        )

    # def get_template_vars(self):
    #     return dict(
    #         pwm_addr=self._settings.get(["pwm_addr"]),
    #         servo_addr=self._settings.get(["servo_addr"]),
    #         gpio_addr=self._settings.get(["gpio_addr"]),
    #         thermistor_addr=self._settings.get(["thermistor_addr"])
    #     )

    def get_template_configs(self):
        return [
            dict(type="navbar", custom_bindings=False),
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
