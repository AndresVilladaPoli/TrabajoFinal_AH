from umqtt.simple import MQTTClient
from config import AWS_ENDPOINT, CLIENT_ID, CERT_FILE, KEY_FILE
import uio
import uasyncio as asyncio


def connect_aws():
    try:
        with open(KEY_FILE, "r") as f:
            key = f.read()
        with open(CERT_FILE, "r") as f:
            cert = f.read()
    except OSError as e:
        print("Error al leer archivos de certificados:", e)
        raise

    client = MQTTClient(
        client_id=CLIENT_ID,
        server=AWS_ENDPOINT,
        port=8883,
        keepalive=4000,
        ssl=True,
        ssl_params={"cert": cert, "key": key},
    )

    try:
        client.connect()
        print("Conectado a AWS IoT")
    except Exception as e:
        print("Error al conectar a AWS IoT:", e)
        raise

    return client
