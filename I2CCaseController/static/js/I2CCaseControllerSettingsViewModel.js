/*
 * View model for I2CCaseController
 *
 * Author: Alexander Seiger
 * License: AGPLv3
 */
$(function() {
    function I2CcaseControllerSettingsViewModel(parameters) {
        var self = this;

        // assign the injected parameters, e.g.:
        // self.loginStateViewModel = parameters[0];
        self.settings = parameters[0];
        self.i2CCaseControllerNavbarViewModel = parameters[1];
        
        self.onSettingsShown = function() {
            console.log("settings shown!");
            console.log(self.i2CCaseControllerNavbarViewModel);
        }

        self.onSettingsHidden = function() {
            console.log("settings hidden!")
        }

        //for the fan power slider
        var fanPowerSlider = document.getElementById("fanPowerSlider");
        fanPowerSlider.oninput = function() {
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
        var valveOpenPositionSlider = document.getElementById("valveOpenPositionSlider");
        valveOpenPositionSlider.oninput = function() {
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

        var valveClosedPositionSlider = document.getElementById("valveClosedPositionSlider");
        valveClosedPositionSlider.oninput = function() {
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
    }

    /* view model class, parameters for constructor, container to bind to
     * Please see http://docs.octoprint.org/en/master/plugins/viewmodels.html#registering-custom-viewmodels for more details
     * and a full list of the available options.
     */
    OCTOPRINT_VIEWMODELS.push({
        construct: I2CcaseControllerSettingsViewModel,
        // ViewModels your plugin depends on, e.g. loginStateViewModel, settingsViewModel, ...
        dependencies: ['settingsViewModel', 'i2CcaseControllerNavbarViewModel'],
        // Elements to bind to, e.g. #settings_plugin_I2CCaseController, #tab_plugin_I2CCaseController, ...
        elements: ['#settings_plugin_I2CCaseController']
    });
});
