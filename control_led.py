from machine import Pin
from config import LED_PIN

led = Pin(LED_PIN, Pin.OUT)


def control_led(state):
    led.value(state)
