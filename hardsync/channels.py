from hardsync.interfaces import Channel
from hardsync.types import BaudRateT
from contextlib import contextmanager
import logging
from serial import Serial
import socket
from typing import Optional, Any
from serial.tools import list_ports


logger = logging.getLogger(__name__)


class DeviceNotFoundError(Exception):
    pass

class SocketNotOpenError(Exception):
    pass

class SerialChannel(Channel):
    baud_rate: BaudRateT

    def __init__(self, baud_rate: BaudRateT, channel_identifier: str):
        super().__init__()
        self.baud_rate = baud_rate
        self.channel_identifier = channel_identifier

    @staticmethod
    def _find_port_by_serial(serial_number: str) -> str:
        for port in list_ports.comports():
            if port.serial_number == serial_number:
                return port.device
        raise DeviceNotFoundError(f"Could not find device with serial number {serial_number}.")

    @contextmanager
    def open(self) -> Serial:
        ser = None
        try:
            port = self._find_port_by_serial(serial_number=self.channel_identifier)
            ser = Serial(port=port, baudrate=self.baud_rate)
            yield ser
        finally:
            ser.close() if ser else None


class SocketChannel(Channel):
    port: int

    def __init__(self, port: int):
        self.port = port
        self.listening_socket: Optional[socket.socket] = None
        self.connection: Optional[socket.socket] = None
        self.address = Optional[Any]

    def write(self, data: bytes):
        if self.listening_socket is None:
            raise SocketNotOpenError("You can only use write() inside the open() context manager in SocketChannel.")

        self.connection.sendall(data)

    def read_bytes(self, num_bytes: int):
        buffer = bytearray()
        data = self.connection.recv(num_bytes)  # Receive 1 byte
        buffer.extend(data)
        return bytes(buffer)

    def read_until(self, termination_sequence: bytes) -> bytes:
        buffer = bytearray()
        stop_len = len(termination_sequence)

        while True:
            data = self.connection.recv(1)  # Receive 1 byte

            if not data:  # Connection closed
                break

            buffer.extend(data)

            if buffer[-stop_len:] == termination_sequence:
                break

        return bytes(buffer)

    @contextmanager
    def open(self) -> socket.socket:
        self.listening_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listening_socket.bind(('localhost', self.port))
        self.listening_socket.listen(1)
        logger.info(f"Listening on port {self.port}")
        try:
            self.connection, self.address = self.listening_socket.accept()
            yield self.connection
        finally:
            self.listening_socket.close()
            self.connection.close()
            logger.info("Socket on port {self.port} closed")

