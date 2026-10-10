# dev/

Experiments and standalone scripts, kept in the repo for reference but
**not part of the plugin package** (not installed by pip, not imported by
the plugin).

- `CaseControl.py` — early standalone prototype of the case light /
  machine power logic (pre-plugin). Uses absolute imports, so run it
  from the `I2CCaseController/` package directory if you ever need it.
- `I2CThermistor.py` — ADS1115 thermistor reading experiment. Executed at
  module import time (reads the hardware and prints); run as a script,
  never import it.
- `OnOffThermostat.py` — hysteresis thermostat experiment (candidate for
  the case-temperature PID work). Run as a script.
