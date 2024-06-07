import uasyncio as asyncio
import socket
import network
from machine import Pin, PWM
from config import FAN_PIN, FAN_PWM_FREQ, LED_PIN
from control_fan import set_fan_speed
from control_led import control_led

# Configurar pines
fan = PWM(Pin(FAN_PIN), freq=FAN_PWM_FREQ)
fan.duty(0)
led = Pin(LED_PIN, Pin.OUT)

# Cargar el contenido de index.html
with open("index.html", "r") as file:
    INDEX_HTML = file.read()


def get_local_ip():
    sta_if = network.WLAN(network.STA_IF)
    if sta_if.isconnected():
        return sta_if.ifconfig()[0]
    else:
        return None


def web_page():
    led_state = "ON" if led.value() == 1 else "OFF"
    return INDEX_HTML.replace(
        '<strong id="ledState">OFF</strong>',
        f'<strong id="ledState">{led_state}</strong>',
    )


async def handle_client(client_sock):
    try:
        request = client_sock.recv(1024).decode()
        print("Request:", request)

        if "GET /?led=on" in request:
            print("LED ON")
            control_led(True)
        elif "GET /?led=off" in request:
            print("LED OFF")
            control_led(False)
        elif "GET /fan?" in request:
            params = request.split("GET /fan?")[1].split(" ")[0]
            if "=" in params:
                speed = int(params.split("=")[1])
                set_fan_speed(speed)
            else:
                print("Invalid fan parameters")

        response = web_page()
        client_sock.send("HTTP/1.1 200 OK\r\n")
        client_sock.send("Content-Type: text/html\r\n")
        client_sock.send("Connection: close\r\n\r\n")
        client_sock.sendall(response.encode("utf-8"))
    except Exception as e:
        print("Error handling client:", e)
    finally:
        if client_sock:
            client_sock.close()


async def start_server():
    local_ip = get_local_ip()
    if local_ip:
        addr = socket.getaddrinfo(local_ip, 80)[0][-1]
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(addr)
        s.listen(5)
        s.setblocking(False)
        print(f"Server running at http://{local_ip}/")

        while True:
            try:
                client_sock, client_addr = s.accept()
                print("Got a connection from", client_addr)
                asyncio.create_task(handle_client(client_sock))
            except OSError as e:
                if e.args[0] == 11:  # EAGAIN
                    await asyncio.sleep(0.1)
                else:
                    print("Error accepting connection:", e)
                    await asyncio.sleep(1)
    else:
        print("Error: No se pudo obtener la dirección IP local.")
