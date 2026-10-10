/*
 * View model for I2CCaseController
 *
 * Author: Alexander Seiger
 * License: AGPLv3
 */
$(function() {
    function I2CcaseControllerSettingsViewModel(parameters) {
        var self = this;

        self.settings = parameters[0];

        // Send an API command with clean error reporting.
        self.sendCommand = function(command, data, errorTitle) {
            var payload = { command: command };
            if (data) {
                payload = $.extend(payload, data);
            }
            $.ajax({
                url: API_BASEURL + "plugin/I2CCaseController",
                type: "POST",
                dataType: "json",
                data: JSON.stringify(payload),
                contentType: "application/json; charset=UTF-8",
                error: function (xhr) {
                    var message = xhr.responseText;
                    try {
                        var parsed = JSON.parse(xhr.responseText);
                        if (parsed.error) {
                            message = parsed.error;
                        }
                    } catch (e) {
                        // keep the raw response
                    }
                    new PNotify({
                        title: errorTitle,
                        text: message,
                        type: "error"
                    });
                }
            });
        };

        // "Test" buttons: apply the current slider value to the hardware
        // immediately, without saving the settings form. (The sliders
        // themselves only edit the stored parameters and are applied when
        // the settings form is saved.)
        self.testLightBrightness = function() {
            var value = parseFloat(self.settings.settings.plugins.I2CCaseController.param_case_light_brightness());
            self.sendCommand("lightBrightnessSet", { lightBrightness: value }, "Setting light brightness failed.");
        };

        self.testFanPower = function() {
            var value = parseFloat(self.settings.settings.plugins.I2CCaseController.param_fan_power());
            self.sendCommand("fanPowerSet", { fanPowerLevel: value }, "Setting fan power failed.");
        };

        self.testValveOpen = function() {
            var value = parseFloat(self.settings.settings.plugins.I2CCaseController.param_vent_valve_open());
            self.sendCommand("valvePositionSet", { valvePosition: value }, "Setting valve position failed.");
        };

        self.testValveClosed = function() {
            var value = parseFloat(self.settings.settings.plugins.I2CCaseController.param_vent_valve_closed());
            self.sendCommand("valvePositionSet", { valvePosition: value }, "Setting valve position failed.");
        };
    }

    /* view model class, parameters for constructor, container to bind to
     * Please see http://docs.octoprint.org/en/master/plugins/viewmodels.html#registering-custom-viewmodels for more details
     * and a full list of the available options.
     */
    OCTOPRINT_VIEWMODELS.push({
        construct: I2CcaseControllerSettingsViewModel,
        // ViewModels your plugin depends on, e.g. loginStateViewModel, settingsViewModel, ...
        dependencies: ['settingsViewModel'],
        // Elements to bind to, e.g. #settings_plugin_I2CCaseController, #tab_plugin_I2CCaseController, ...
        elements: ['#settings_plugin_I2CCaseController']
    });
});
