from hardsync.interfaces import Channel
from hardsync.types import BaudRate
from contextlib import contextmanager
from serial import Serial
from serial.tools import list_ports


class SerialChannel(Channel):
    def __init__(self, baud_rate: BaudRate, channel_identifier: str):
        super().__init__(baud_rate=baud_rate)
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


class DeviceNotFoundError(Exception):
    pass
