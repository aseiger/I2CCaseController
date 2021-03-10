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

        self.caseTemp = ko.observable();
        self.YTemp = ko.observable();
        self.ETemp = ko.observable();
        self.XTemp = ko.observable();
        self.Z_L_Temp = ko.observable();
        self.Z_R_Temp = ko.observable();

        self.onDataUpdaterPluginMessage = function(plugin, data) {
          if (plugin != "I2CCaseController") {
            return;
          }

          if (data.msgType == "tempUpdate") {
            if (data.sensorAlias == "bus.7") {
                self.caseTemp("Case: " + data.value + " °C");
            }
            if (data.sensorAlias == "bus.6") {
                self.YTemp("Y Motor: " + data.value + " °C");
            }
            if (data.sensorAlias == "bus.5") {
                self.ETemp("E Motor: " + data.value + " °C");
            }
            if (data.sensorAlias == "bus.4") {
              self.XTemp("X Motor: " + data.value + " °C");
            }
            if (data.sensorAlias == "bus.3") {
              self.Z_L_Temp("Z Left Motor: " + data.value + " °C");
            }
            if (data.sensorAlias == "bus.2") {
              self.Z_R_Temp("Z Right Motor: " + data.value + " °C");
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
