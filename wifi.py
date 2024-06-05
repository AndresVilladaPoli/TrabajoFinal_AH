import network
from config import SSID, PASSWORD


def connect_wifi():
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect(SSID, PASSWORD)
    while not sta_if.isconnected():
        pass
    print("Conexión Wi-Fi establecida:", sta_if.ifconfig())
