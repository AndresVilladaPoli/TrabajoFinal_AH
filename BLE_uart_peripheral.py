import ubluetooth
from machine import Pin
from ubluetooth import BLE, UUID, FLAG_NOTIFY, FLAG_WRITE, FLAG_WRITE_NO_RESPONSE
from micropython import const

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)


class BLEUART:
    def __init__(self, ble, name="ESP32_UART"):
        self._ble = ble
        self._ble.active(True)
        self._ble.irq(self._irq)

        self._name = name
        self._rx_buffer = bytearray()
        self._conn_handle = None
        self._handler = None

        # Definir UUIDs
        self._service_uuid = UUID(
            "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
        )  # UUID del servicio UART
        self._tx_uuid = UUID(
            "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"
        )  # UUID de la característica TX
        self._rx_uuid = UUID(
            "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"
        )  # UUID de la característica RX

        # Configurar las características
        self._tx = (self._tx_uuid, FLAG_NOTIFY)
        self._rx = (self._rx_uuid, FLAG_WRITE | FLAG_WRITE_NO_RESPONSE)

        # Registrar el servicio UART
        self._service = (self._service_uuid, (self._tx, self._rx))
        ((self._tx_handle, self._rx_handle),) = self._ble.gatts_register_services(
            (self._service,)
        )

        self._advertise()

    def _irq(self, event, data):
        if event == _IRQ_CENTRAL_CONNECT:
            self._conn_handle, _, _ = data
            print("Central connected")
        elif event == _IRQ_CENTRAL_DISCONNECT:
            self._conn_handle = None
            print("Central disconnected")
            self._advertise()
        elif event == _IRQ_GATTS_WRITE:
            conn_handle, value_handle = data
            if value_handle == self._rx_handle:
                self._rx_buffer += self._ble.gatts_read(value_handle)
                self._on_rx()

    def _advertise(self):
        try:
            self._ble.gap_advertise(
                100,
                b"\x02\x01\x06"
                + bytearray((len(self._name) + 1, 0x09))
                + self._name.encode("UTF-8"),
            )
            print("Advertising as", self._name)
        except OSError as e:
            print("Advertising failed with OSError:", e)
            # Reintentar después de un breve retraso
            time.sleep(1)
            self._advertise()

    def irq(self, handler):
        self._handler = handler

    def _on_rx(self):
        if self._handler:
            self._handler()

    def read(self):
        result = self._rx_buffer
        self._rx_buffer = bytearray()
        return result

    def write(self, data):
        if self._conn_handle is not None:
            try:
                self._ble.gatts_notify(self._conn_handle, self._tx_handle, data)
            except OSError as e:
                print("Failed to send data:", e)
        else:
            print("No connection handle, cannot send data")
