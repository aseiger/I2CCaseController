# I2CCaseController

OctoPrint plugin that drives a custom I2C case controller board for the
printer enclosure:

- **Machine power** — relay GPIO, with automatic connect/disconnect of the
  printer after power on, and an optional power-down delay after the
  print finishes. A latching power button on the case controls it
  (latch on = power on, latch off = power off after a 5 s grace period).
- **Case light** — PWM with ramp, door-switch auto on/off, side button
  with timeout, timelapse capture support.
- **Machine light + machine cooling fan** — PWM, tied to print state.
- **Vent fan + vent valve (servo)** — powered on while printing, valve
  position controllable from the tab (percentage) and calibrable in
  settings (open/closed angle, actuation time).
- **1-wire DS18B20 temperature sensors** — up to 8, renameable per bus,
  shown on the tab and published to MQTT
  (`octoPrint/i2ccasecontroller/<sensor name>`).

## Hardware

The board is three I2C chips plus a 1-wire host:

| Chip | Default address | Used for |
|---|---|---|
| MCP23008 (GPIO expander) | `0x20` | machine power relay, fan power relay, door switch, side button, power button |
| PCA9685 (16-ch PWM) | `0x41` | case light, vent fan, machine fan, machine light |
| PCA9685 (servo driver) | `0x40` | vent valve servo |
| 1-wire host (owserver) | `localhost:4304` | DS18B20 temperature sensors |

If the board is missing or the I2C bus is busy at startup the plugin
stays enabled, logs the error, and retries the hardware initialization
every 30 s until the board responds.

## Install

Via the bundled [Plugin Manager](https://docs.octoprint.org/en/master/bundledplugins/pluginmanager.html)
or manually:

    https://github.com/aseiger/I2CCaseController/archive/master.zip

Development install (this is how the board's Pi runs it):

    cd I2CCaseController
    /path/to/octoprint/bin/pip install -e .

The plugin requires the Adafruit CircuitPython libraries (`board`,
`busio`, `digitalio`, `adafruit-pca9685`, `adafruit-mcp230xx`,
`adafruit-servokit`, `adafruit-ads1x15`), `pyownet` and `simple-pid`
in the OctoPrint virtualenv.

## Configuration

All settings live under *Settings → I2CCaseController*:

- I2C addresses of the three chips (accept `0xNN` or decimal).
- GPIO/PWM/servo pin assignments for every function.
- Light brightness, ramp time, and timeout for the side button.
- Vent fan power level.
- Valve open/closed servo angles (with **Test** buttons to move the valve
  to the current slider value) and actuation time.
- Temperature display update interval.
- 1-wire sensor display names per bus.
- Machine connect/disconnect-after-power toggle, power-on connect delay,
  and post-print shutdown delay.
- Case PID tuning (work in progress — not yet wired to the valve).

## Behavior notes

- Print started → case fan + valve open, machine light on, any pending
  power-down disarmed.
- Print done → case fan + valve closed, machine light off, machine
  powers off after the configured shutdown delay (unless it is still
  printing).
- Print cancelled → pending power-down is disarmed.
- If the Pi restarts mid-print, the plugin resyncs the case state from
  the printer state at startup.

## Development

- `dev/` holds standalone experiments that are not part of the plugin
  package.
- Unit tests (no hardware needed):

      /path/to/octoprint/bin/python -m unittest discover -s tests -v

- `PLAN.md` tracks the refactor history.
