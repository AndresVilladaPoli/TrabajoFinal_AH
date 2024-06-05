import ubluetooth
from BLE_uart_peripheral import BLEUART
from control_fan import set_fan_speed
from control_led import control_led
import uasyncio as asyncio


async def init_bluetooth():
    ble = ubluetooth.BLE()
    uart = BLEUART(ble, "ESP32_Fan_LED_Controller")

    def on_rx():
        try:
            data = uart.read().decode("utf-8").strip()
            print("Received data:", data)
            if data.startswith("FAN:"):
                try:
                    speed = int(data.split(":")[1])
                    set_fan_speed(speed)
                    uart.write("FAN speed set to " + str(speed))
                except ValueError:
                    uart.write("Invalid speed value")
            elif data == "LED:ON":
                control_led(True)
                uart.write("LED turned ON")
            elif data == "LED:OFF":
                control_led(False)
                uart.write("LED turned OFF")
            else:
                uart.write("Unknown command")
        except Exception as e:
            print("Error processing data:", e)
            uart.write("Error processing data")

    uart.irq(handler=on_rx)
