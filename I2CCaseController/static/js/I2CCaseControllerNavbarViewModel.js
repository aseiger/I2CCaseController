/*
 * View model for I2CCaseController
 *
 * Author: Alexander Seiger
 * License: AGPLv3
 */
$(function() {
    function I2CcaseControllerNavbarViewModel(parameters) {
        var self = this;

        self.loginStateViewModel = parameters[0];

        // assign the injected parameters, e.g.:
        // self.loginStateViewModel = parameters[0];
        // self.settingsViewModel = parameters[1];

        self.machinePowerState = ko.observable('unknown');
        self.fanPowerState = ko.observable('unknown');
        self.caseLightState = ko.observable('unknown');
        self.machineLightState = ko.observable('unknown');

        // self.onTabChange = function(next, current) {
        //   if(next == "#control")
        //   {
        //     $.ajax({
        //       url: API_BASEURL + "plugin/I2CCaseController",
        //       type: "POST",
        //       dataType: "json",
        //       data: JSON.stringify({
        //         command: "caseLightOn"
        //       }),
        //       contentType: "application/json; charset=UTF-8",
        //       error: function (data, status) {
        //         var options = {
        //           title: "Case Light On Failed.",
        //           text: data.responseText,
        //           hide: true,
        //           buttons: {
        //             sticker: false,
        //             closer: true
        //           },
        //           type: "error"
        //         };
  
        //         new PNotify(options);
        //       }
        //     });
        //   }
        //   else if(current == "#control")
        //   {
        //     $.ajax({
        //       url: API_BASEURL + "plugin/I2CCaseController",
        //       type: "POST",
        //       dataType: "json",
        //       data: JSON.stringify({
        //         command: "caseLightOff"
        //       }),
        //       contentType: "application/json; charset=UTF-8",
        //       error: function (data, status) {
        //         var options = {
        //           title: "Case Light Off Failed.",
        //           text: data.responseText,
        //           hide: true,
        //           buttons: {
        //             sticker: false,
        //             closer: true
        //           },
        //           type: "error"
        //         };
  
        //         new PNotify(options);
        //       }
        //     });
        //   }
        // }

        self.onDataUpdaterPluginMessage = function(plugin, data) {
          if (plugin != "I2CCaseController") {
            return;
          }

          if (data.msgType == "caseLightState") {
            self.caseLightState(data.value);
          }

          if (data.msgType == "fanPowerState") {
            self.fanPowerState(data.value);
          }

          if (data.msgType == "machinePowerState") {
            self.machinePowerState(data.value);
          }

          if (data.msgType == "machineLightState") {
            self.machineLightState(data.value);
          }
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
                title: "Case Light Toggle Failed.",
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

        //called when the machine light button is pressed
        self.machineLightCb = function() {
          $.ajax({
            url: API_BASEURL + "plugin/I2CCaseController",
            type: "POST",
            dataType: "json",
            data: JSON.stringify({
              command: "machineLightToggle"
            }),
            contentType: "application/json; charset=UTF-8",
            error: function (data, status) {
              var options = {
                title: "Machine Light Toggle Failed.",
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
                title: "Machine Power Toggle.",
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
                title: "Fan Power Toggle Failed.",
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
        construct: I2CcaseControllerNavbarViewModel,
        // ViewModels your plugin depends on, e.g. loginStateViewModel, settingsViewModel, ...
        dependencies: ['loginStateViewModel'],
        // Elements to bind to, e.g. #settings_plugin_I2CCaseController, #tab_plugin_I2CCaseController, ...
        elements: ['#navbar_plugin_I2CCaseController']
    });
});
