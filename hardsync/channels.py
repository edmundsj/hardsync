from hardsync.channel import Channel, BaudRate
from contextlib import contextmanager
from serial import Serial
from serial.tools import list_ports


class ChannelNotFoundError(Exception):
    pass


class SerialChannel(Channel):
    def __init__(self, baud_rate: BaudRate, channel_identifier: str):
        super().__init__(self, baud_rate=baud_rate, channel_identifier=channel_identifier)
        self.port = self._find_port_by_serial(self.channel_identifier)
        if not self.port:
            raise Exception(f"Device with serial number {self.channel_identifier} not found")

    @staticmethod
    def _find_port_by_serial(serial_number: str) -> str:
        for port in list_ports.comports():
            if port.serial_number == serial_number:
                return port.device
        raise ChannelNotFoundError(f"Could not find device with serial number {serial_number}.")

    @contextmanager
    def open(self) -> Serial:
        ser = None
        try:
            ser = Serial(port=self.port, baudrate=self.baud_rate)
            yield ser
        finally:
            ser.close() if ser else None