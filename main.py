import time
from wifi import connect_wifi
from web_server import start_server
import uasyncio as asyncio
from bluetooth import init_bluetooth
from aws import connect_aws
from sensor import read_sensor
from config import TOPIC
import json


DEVICE_ID = "esp32_001"


async def publish_data(client):
    while True:
        try:
            temp, hum = read_sensor()
            if temp is not None and hum is not None:
                payload = {"humidity": hum, "device_id": DEVICE_ID, "temperature": temp}
                payload_json = json.dumps(payload)
                client.publish(TOPIC, payload_json)
                print("Datos publicados:", payload_json)
            else:
                print("No se pudieron leer los datos del sensor.")
            await asyncio.sleep(20)
        except Exception as e:
            print("Error al publicar los datos:", e)
            await asyncio.sleep(10)


async def init_services():
    await asyncio.gather(init_bluetooth())
    print("Bluetooth iniciado")


async def main():
    connect_wifi()

    client = connect_aws()

    # Iniciar el Bluetooth y otros servicios
    await init_services()

    # Crear tareas para publicar datos y el servidor
    publish_task = asyncio.create_task(publish_data(client))
    server_task = asyncio.create_task(start_server())

    # Ejecutar ambas tareas en paralelo
    await asyncio.gather(publish_task, server_task)


if __name__ == "__main__":
    asyncio.run(main())
