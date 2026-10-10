/*
 * View model for I2CCaseController
 *
 * Author: Alexander Seiger
 * License: AGPLv3
 */
$(function() {
    function I2CcaseControllerTabViewModel(parameters) {
        var self = this;

        self.loginStateViewModel = parameters[0];

        self.auxtemp7 = ko.observable();
        self.auxtemp6 = ko.observable();
        self.auxtemp5 = ko.observable();
        self.auxtemp4 = ko.observable();
        self.auxtemp3 = ko.observable();
        self.auxtemp2 = ko.observable();
        self.auxtemp1 = ko.observable();
        self.auxtemp0 = ko.observable();

        self.valvePosition = ko.observable();
        self.valveSlider = ko.observable(0);

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

        self.onDataUpdaterPluginMessage = function(plugin, data) {
          if (plugin != "I2CCaseController") {
            return;
          }

          if (data.msgType == "tempUpdate") {
            var text = data.sensorName + ": " + data.value + " °C";
            if (data.sensorAlias == "bus.7") {
                self.auxtemp7(text);
            }
            if (data.sensorAlias == "bus.6") {
                self.auxtemp6(text);
            }
            if (data.sensorAlias == "bus.5") {
                self.auxtemp5(text);
            }
            if (data.sensorAlias == "bus.4") {
                self.auxtemp4(text);
            }
            if (data.sensorAlias == "bus.3") {
                self.auxtemp3(text);
            }
            if (data.sensorAlias == "bus.2") {
                self.auxtemp2(text);
            }
            if (data.sensorAlias == "bus.1") {
                self.auxtemp1(text);
            }
            if (data.sensorAlias == "bus.0") {
                self.auxtemp0(text);
            }
          }

          // value is the actual servo angle in degrees
          if (data.msgType == "valvePositionUpdate")
          {
            self.valvePosition("Valve Position: " + data.value + "°");
          }
        }

        // Apply the valve percentage on slider release (not on every input
        // event) so dragging the slider does not command the servo in a
        // rapid burst.
        self.valveSliderCb = function() {
            var value = parseFloat(self.valveSlider());
            self.sendCommand("valvePercentageSet", { valvePercentage: value }, "Setting valve position failed.");
        }
    }

    /* view model class, parameters for constructor, container to bind to
     * Please see http://docs.octoprint.org/en/master/plugins/viewmodels.html#registering-custom-viewmodels for more details
     * and a full list of the available options.
     */
    OCTOPRINT_VIEWMODELS.push({
        construct: I2CcaseControllerTabViewModel,
        // ViewModels your plugin depends on, e.g. loginStateViewModel, settingsViewModel, ...
        dependencies: ['loginStateViewModel'],
        // Elements to bind to, e.g. #settings_plugin_I2CCaseController, #tab_plugin_I2CCaseController, ...
        elements: ['#tab_plugin_I2CCaseController']
    });
});
