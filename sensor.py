import machine
import dht


def read_sensor():
    sensor = dht.DHT11(machine.Pin(13))
    sensor.measure()
    temp = sensor.temperature()
    hum = sensor.humidity()
    return temp, hum
