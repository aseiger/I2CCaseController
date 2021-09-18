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

        // assign the injected parameters, e.g.:
        // self.loginStateViewModel = parameters[0];
        // self.settingsViewModel = parameters[1];

        self.auxtemp7 = ko.observable();
        self.auxtemp6 = ko.observable();
        self.auxtemp5 = ko.observable();
        self.auxtemp4 = ko.observable();
        self.auxtemp3 = ko.observable();
        self.auxtemp2 = ko.observable();
        self.auxtemp1 = ko.observable();
        self.auxtemp0 = ko.observable();

        self.onDataUpdaterPluginMessage = function(plugin, data) {
          if (plugin != "I2CCaseController") {
            return;
          }

          if (data.msgType == "tempUpdate") {
            if (data.sensorAlias == "bus.7") {
                self.auxtemp7(data.sensorName + ": " + data.value + " °C");
            }
            if (data.sensorAlias == "bus.6") {
                self.auxtemp6(data.sensorName + ": " + data.value + " °C");
            }
            if (data.sensorAlias == "bus.5") {
                self.auxtemp5(data.sensorName + ": " + data.value + " °C");
            }
            if (data.sensorAlias == "bus.4") {
                self.auxtemp4(data.sensorName + ": " + data.value + " °C");
            }
            if (data.sensorAlias == "bus.3") {
                self.auxtemp3(data.sensorName + ": " + data.value + " °C");
            }
            if (data.sensorAlias == "bus.2") {
                self.auxtemp2(data.sensorName + ": " + data.value + " °C");
            }
            if (data.sensorAlias == "bus.1") {
                self.auxtemp1(data.sensorName + ": " + data.value + " °C");
            }
            if (data.sensorAlias == "bus.0") {
                self.auxtemp0(data.sensorName + ": " + data.value + " °C");
            }
          }
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
