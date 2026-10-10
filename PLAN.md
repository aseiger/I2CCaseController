# I2CCaseController — Refactor Plan

Baseline: `v0.1.0` (commit `ae802e2`). Working branch: `refactor`.
Live copy: `/home/pi/devel/I2CCaseController` (editable install into `/home/pi/oprint`).
The copy at `~/.octoprint/plugins/I2CCaseController` is **not** loaded by OctoPrint and is
stale — keep in sync only if it is to remain, or remove it.

Conventions:
- One commit per fix, message states what and why.
- `python -m py_compile` + unit tests (`tests/`) after every Python change.
- OctoPrint is restarted **only with user approval** to activate changes.
  Rollback: `git checkout v0.1.0` (or `master`) + restart.

## P0 — Real bugs (fix first)

- [ ] **C2** `I2CPWM`: parameterize I2C address (settings were dead knobs — 0x41 was hardcoded);
      move `channelRampThreads` from class attribute to instance state; add I2C write lock;
      rewrite ramp as generation-guarded step interpolation (fixes `ZeroDivisionError` on
      `ramp_time=0` and race between `set_channel`/ramp thread, e.g. timelapse hook).
- [ ] **C3** `I2CServos`: same treatment (address was hardcoded 0x40); fixes the
      `ramp_time=0` **infinite loop** in `ramp_channel_thread`; fix "PCA9685" copy-paste error text.
- [ ] **C4** `__init__.py`: startup set fan-power GPIO with `pin_gpio_machine_on_state`
      instead of `pin_gpio_fan_power_on_state` (works only because both default to 0).
- [ ] **C5** `__init__.py`: handle `Events.PRINT_CANCELLED` — the post-print power-down timer
      must be cancelled, otherwise the machine powers off 5 min after a cancel.
- [ ] **C6** `__init__.py`: move hardware construction out of import time (class-body
      `tMCP/tPWM/tServo` ran at module import; missing/broken I2C board crashed plugin import,
      `__plugin_check__` could never gate it). Lazy init in `on_after_startup` with try/except,
      clear logging, 30 s retry. All timers + `lightOnReason` become instance state; replace
      private `Timer.finished` checks with `is_alive()`/None-guards; API/status methods degrade
      gracefully to "unknown" before hardware is ready. Wire configured addresses
      (`pwm_addr`/`gpio_addr`/`servo_addr`) into the constructors, with robust hex/dec parsing
      (`int("0x20")` raises ValueError — another latent crash).
      Behavior note: latching the power button on while a completed off-countdown is stale now
      powers the machine on (previously did nothing — button/machine state divergence).

## P1 — Robustness & correctness

- [ ] **C7** Temp polling: cache `enumerate_DS18B20_sensors()` result (currently re-enumerates
      all sensors + opens a new pyownet proxy per sensor *every tick*); re-enumerate on failure;
      `onewire_bus_to_alias` must not raise `KeyError` for unknown buses (aborted the whole
      update loop); skip MQTT publish for empty display names (duplicate topics).
- [ ] **C8** API commands: validate/clamp all numeric data (`valvePercentage`, `valvePosition`,
      `fanPowerLevel`, `lightBrightness`), return clean 400s instead of raw 500 tracebacks;
      fix `get_api_commands` metadata (data-taking commands declared `[]`).
- [ ] **C9** Startup resync: if the printer is already printing (Pi rebooted mid-print),
      re-apply the "printing" case state (fan, valve, machine light) instead of forcing
      everything off.
- [ ] **C10** Timelapse hooks: drop the blocking `time.sleep(2)`; restore the *measured*
      pre-capture brightness instead of guessing from `lightOnReason`; push light state to UI.
      `case_light_off`: move `lightOnReason = "none"` after the door-open check so a
      door-kept-on light can't be killed by a coincidental post-capture.
- [ ] **C11** UI: push state updates after `lightBrightnessSet`/`fanPowerSet`;
      `valvePositionSet` never pushed the new position (navbar/tab went stale);
      push valve position on `CLIENT_OPENED`; tab shows servo *angle* labeled as `%`;
      settings sliders drove the physical valve/servo on every `input` event via raw
      `document.getElementById` handlers (fragile + AJAX spam) — replace with KO bindings
      (edit saved params) + explicit "Test" buttons; fix duplicate DOM id.

## P2 — Cleanup & maintainability

- [ ] **C12** Remove dead code from the package: `CaseControl.py` (standalone script,
      absolute imports), `I2CThermistor.py` (runs hardware + print at module import —
      would crash if imported), `OnOffThermostat.py` (unused, debug print) → move to `dev/`;
      remove unused imports, py2 leftover, trailing-comma log tuple.
- [ ] **C13** Metadata: `plugin_version` → `0.2.0`, real `plugin_description`,
      `plugin_url` points at `awseiger` but the repo is `aseiger`; write the README
      (still the plugin skeleton).
- [ ] **C14** Tests: `tests/` with pytest for pure logic — valve percent↔angle mapping,
      ramp step interpolation, thermostat hysteresis, address parsing, alias fallback.
- [ ] **C15** (optional, later) settings live-reload via `on_settings_changed`; per-pin
      poll-thread consolidation; i18n of PNotify strings; decide fate of the
      `~/.octoprint/plugins` duplicate.

## Definition of done (this pass)

1. P0 + P1 + P2(C12–C14) committed on `refactor`, pushed to GitHub (backup current).
2. `py_compile` clean, unit tests pass under `/home/pi/oprint/bin/python`.
3. User restarts OctoPrint; live check: navbar states, door light, power button, valve
   slider, temp tab, print start/cancel/done behavior, timelapse capture.
4. Merge `refactor` → `master`, tag `v0.2.0`.
