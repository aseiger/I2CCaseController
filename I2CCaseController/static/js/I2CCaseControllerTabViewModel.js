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

        // temperature sensors: [{alias, name, value}...] - only buses with
        // a sensor that actually reported are shown
        self.sensors = ko.observableArray();

        // valve
        self.valvePosition = ko.observable(null);
        self.valveSlider = ko.observable(0);

        // case status
        self.machinePowerState = ko.observable("unknown");
        self.fanPowerState = ko.observable("unknown");
        self.caseLightState = ko.observable("unknown");
        self.machineLightState = ko.observable("unknown");

        var stateLabels = {
            "on": "On",
            "on_timeout": "On (timeout)",
            "off": "Off",
            "unknown": "–"
        };

        function stateLabel(state) {
            return stateLabels[state] || "?";
        }

        self.machinePowerLabel = ko.pureComputed(function() {
            return stateLabel(self.machinePowerState());
        });
        self.fanPowerLabel = ko.pureComputed(function() {
            return stateLabel(self.fanPowerState());
        });
        self.caseLightLabel = ko.pureComputed(function() {
            return stateLabel(self.caseLightState());
        });
        self.machineLightLabel = ko.pureComputed(function() {
            return stateLabel(self.machineLightState());
        });

        self.valvePositionText = ko.pureComputed(function() {
            var pos = self.valvePosition();
            if (pos === null || pos === undefined) {
                return "–";
            }
            return "Position: " + Math.round(pos * 10) / 10 + "°";
        });

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

        function upsertSensor(alias, name, value) {
            var existing = null;
            ko.utils.arrayForEach(self.sensors(), function(sensor) {
                if (sensor.alias() === alias) {
                    existing = sensor;
                }
            });
            if (existing) {
                existing.name(name);
                existing.value(value);
            } else {
                self.sensors.push({
                    alias: ko.observable(alias),
                    name: ko.observable(name),
                    value: ko.observable(value)
                });
                // stable ordering by bus number (bus.2 before bus.10)
                self.sensors.sort(function(a, b) {
                    return a.alias().localeCompare(b.alias(), undefined, { numeric: true });
                });
            }
        }

        self.onDataUpdaterPluginMessage = function(plugin, data) {
            if (plugin != "I2CCaseController") {
                return;
            }

            if (data.msgType == "tempUpdate") {
                upsertSensor(data.sensorAlias, data.sensorName, data.value + " °C");
            } else if (data.msgType == "valvePositionUpdate") {
                self.valvePosition(parseFloat(data.value));
            } else if (data.msgType == "machinePowerState") {
                self.machinePowerState(data.value);
            } else if (data.msgType == "fanPowerState") {
                self.fanPowerState(data.value);
            } else if (data.msgType == "caseLightState") {
                self.caseLightState(data.value);
            } else if (data.msgType == "machineLightState") {
                self.machineLightState(data.value);
            }
        }

        // Apply the valve percentage on slider release (not on every input
        // event) so dragging the slider does not command the servo in a
        // rapid burst.
        self.valveSliderCb = function() {
            self.sendCommand("valvePercentageSet",
                { valvePercentage: self.valveSlider() / 100 },
                "Setting valve position failed.");
        };

        self.valveOpenCb = function() {
            self.valveSlider(100);
            self.sendCommand("valvePercentageSet", { valvePercentage: 1 },
                "Setting valve position failed.");
        };

        self.valveCloseCb = function() {
            self.valveSlider(0);
            self.sendCommand("valvePercentageSet", { valvePercentage: 0 },
                "Setting valve position failed.");
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
