/*
 * View model for I2CCaseController
 *
 * Author: Alexander Seiger
 * License: AGPLv3
 */
$(function() {
    function I2ccasecontrollerViewModel(parameters) {
        var self = this;

        self.NavigationViewModel = parameters[0];

        // assign the injected parameters, e.g.:
        // self.loginStateViewModel = parameters[0];
        // self.settingsViewModel = parameters[1];

        self.machinePowerState = ko.observable('unknown');
        self.fanPowerState = ko.observable('unknown');
        self.caselightState = ko.observable('unknown');

        self.onDataUpdaterPluginMessage = function(plugin, data) {
          if (plugin != "I2CCaseController") {
            return;
          }

          console.log(data.msgType)

          if (data.msgType == "caseLightState") {
            self.caselightState(data.value);
          }

          if (data.msgType == "fanPowerState") {
            self.fanPowerState(data.value);
          }

          if (data.msgType == "machinePowerState") {
            self.machinePowerState(data.value);
          }
        }

        //for the fan power slider
        var fanPowerSlider = document.getElementById("fanPowerSlider");
        fanPowerSlider.oninput = function() {
          console.log(this.value);
          $.ajax({
            url: API_BASEURL + "plugin/I2CCaseController",
            type: "POST",
            dataType: "json",
            data: JSON.stringify({
              command: "fanPowerSet",
              fanPowerLevel: this.value
            }),
            contentType: "application/json; charset=UTF-8",
            error: function (data, status) {
              var options = {
                title: "Setting of Fan Power Failed!",
                text: data.responseText,
                hide: true,
                buttons: {
                  sticker: false,
                  closer: true
                },
                type: "error"
              };

              new PNotify(options);
            }
          });
        }

        //for the valve position slider
        var valvePositionSlider = document.getElementById("valvePositionSlider");
        valvePositionSlider.oninput = function() {
          console.log(this.value);
          $.ajax({
            url: API_BASEURL + "plugin/I2CCaseController",
            type: "POST",
            dataType: "json",
            data: JSON.stringify({
              command: "valvePositionSet",
              valvePosition: this.value
            }),
            contentType: "application/json; charset=UTF-8",
            error: function (data, status) {
              var options = {
                title: "Setting of Valve Position Failed!",
                text: data.responseText,
                hide: true,
                buttons: {
                  sticker: false,
                  closer: true
                },
                type: "error"
              };

              new PNotify(options);
            }
          });
        }

        //for the lighting level slider
        var lightBrightnessSlider = document.getElementById("lightBrightnessSlider");
        lightBrightnessSlider.oninput = function() {
          console.log(this.value);
          $.ajax({
            url: API_BASEURL + "plugin/I2CCaseController",
            type: "POST",
            dataType: "json",
            data: JSON.stringify({
              command: "lightBrightnessSet",
              lightBrightness: this.value
            }),
            contentType: "application/json; charset=UTF-8",
            error: function (data, status) {
              var options = {
                title: "Setting of Light Brightness Failed!",
                text: data.responseText,
                hide: true,
                buttons: {
                  sticker: false,
                  closer: true
                },
                type: "error"
              };

              new PNotify(options);
            }
          });
        }

        // called when the case light button is pressed
        self.caseLightCb = function() {
          $.ajax({
            url: API_BASEURL + "plugin/I2CCaseController",
            type: "POST",
            dataType: "json",
            data: JSON.stringify({
              command: "caseLightToggle"
            }),
            contentType: "application/json; charset=UTF-8",
            error: function (data, status) {
              var options = {
                title: "Case Light On Failed.",
                text: data.responseText,
                hide: true,
                buttons: {
                  sticker: false,
                  closer: true
                },
                type: "error"
              };

              new PNotify(options);
            }
          });
        }

        self.machinePowerCb = function() {
          $.ajax({
            url: API_BASEURL + "plugin/I2CCaseController",
            type: "POST",
            dataType: "json",
            data: JSON.stringify({
              command: "machinePowerToggle"
            }),
            contentType: "application/json; charset=UTF-8",
            error: function (data, status) {
              var options = {
                title: "Case Light On Failed.",
                text: data.responseText,
                hide: true,
                buttons: {
                  sticker: false,
                  closer: true
                },
                type: "error"
              };

              new PNotify(options);
            }
          });
        }

        self.fanPowerCb = function() {
          $.ajax({
            url: API_BASEURL + "plugin/I2CCaseController",
            type: "POST",
            dataType: "json",
            data: JSON.stringify({
              command: "fanPowerToggle"
            }),
            contentType: "application/json; charset=UTF-8",
            error: function (data, status) {
              var options = {
                title: "Case Light On Failed.",
                text: data.responseText,
                hide: true,
                buttons: {
                  sticker: false,
                  closer: true
                },
                type: "error"
              };

              new PNotify(options);
            }
          });
        }
    }

    /* view model class, parameters for constructor, container to bind to
     * Please see http://docs.octoprint.org/en/master/plugins/viewmodels.html#registering-custom-viewmodels for more details
     * and a full list of the available options.
     */
    OCTOPRINT_VIEWMODELS.push({
        construct: I2ccasecontrollerViewModel,
        // ViewModels your plugin depends on, e.g. loginStateViewModel, settingsViewModel, ...
        dependencies: ['navigationViewModel'],
        // Elements to bind to, e.g. #settings_plugin_I2CCaseController, #tab_plugin_I2CCaseController, ...
        elements: ['#navbar_plugin_I2CCaseController', '#tab_plugin_I2CCaseController']
    });
});
