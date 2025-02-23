import I2CGPIO
import I2CPWM
from digitalio import Direction
import time

_CASE_LIGHT_PIN = 3
_FAN_SPEED_PIN = 4
_DOOR_SWITCH_PIN = 2
_SIDE_BUTTON_PIN = 3
_MACHINE_POWER_PIN = 1
_FAN_POWER_PIN = 0
_MACHINE_ON_OFF_PIN = 5

_LIGHT_RAMP_TIME = 2
_LIGHT_ON_VAL = 1.0
_LIGHT_OFF_VAL = 0.0
_LIGHT_LOW_VAL = 0.10

tMCP = I2CGPIO.I2CGPIO()
tPWM = I2CPWM.I2CPWM()

def pressed_callback(pin, value):
    lightState = False
    if(tPWM.get_channel(_CASE_LIGHT_PIN) > 0):
        lightState = True

    if((pin == 2) and (value == True)):
        tPWM.ramp_channel(_CASE_LIGHT_PIN, _LIGHT_ON_VAL, _LIGHT_RAMP_TIME)
        lightState = True
    elif((pin == 2) and (value == False)):
        tPWM.ramp_channel(_CASE_LIGHT_PIN, _LIGHT_OFF_VAL, _LIGHT_RAMP_TIME)
        lightState = False
    elif((pin == 3) and (value == True)):
        if(lightState == False):
            tPWM.ramp_channel(_CASE_LIGHT_PIN, _LIGHT_LOW_VAL, _LIGHT_RAMP_TIME)
            lightState = True
        else:
            tPWM.ramp_channel(_CASE_LIGHT_PIN, _LIGHT_OFF_VAL, _LIGHT_RAMP_TIME)
            lightState = False

    machine_power_state = tMCP.get_pin_value(_MACHINE_POWER_PIN)
    if (machine_power_state == False and pin == _MACHINE_ON_OFF_PIN):
        tMCP.set_pin_value(_MACHINE_POWER_PIN, True)


if __name__ == '__main__':
    tPWM.set_channel(_CASE_LIGHT_PIN, 0)
    tPWM.set_channel(_FAN_SPEED_PIN, 0)

    tMCP.set_direction(_MACHINE_POWER_PIN, Direction.OUTPUT)
    tMCP.set_direction(_FAN_POWER_PIN, Direction.OUTPUT)

    tMCP.set_pin_value(_MACHINE_POWER_PIN, 0)
    tMCP.set_pin_value(_FAN_POWER_PIN, 0)

    tMCP.poll_pin(_DOOR_SWITCH_PIN, pressed_callback, poll_rate = 0.1)
    tMCP.poll_pin(_SIDE_BUTTON_PIN, pressed_callback, poll_rate = 0.1)
    tMCP.poll_pin(_MACHINE_ON_OFF_PIN, pressed_callback, poll_rate = 0.1)

    tPWM.ramp_channel(_FAN_SPEED_PIN, 0, 1)

    while(1):
        time.sleep(1)
