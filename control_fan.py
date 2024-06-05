from machine import Pin, PWM
from config import FAN_PIN, FAN_PWM_FREQ

fan = PWM(Pin(FAN_PIN), freq=FAN_PWM_FREQ)
fan.duty(0)


def set_fan_speed(speed):
    fan.duty(speed)
