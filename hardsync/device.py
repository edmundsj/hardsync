import serial
import abc
from serial.tools import list_ports
from dataclasses import is_dataclass
from typing import TypeVar, Type

T = TypeVar('T')


# A first implementation should use text-based utf-8 serialization, but this should be
# configurable so that we could use more greedy binary encoding to keep the communication
# overhead low. Though, there is value in having both.

class DeviceNotFoundError(Exception):
    pass


class BaseDevice:
    """
    A first implementation of this should use text-based utf-8 encoding / serialization, but this
    should be configurable so that we could use more greedy binary encoding if necessary
    to keep the communication overhead low, as is often the need.

    Each client-side BaseDevice implementation needs to be coupled to the
    device-side implementation. Well, we have a basic implementation on the client-side
    that I think could work, now let's see if we can write some arduino code that could work.

    """
    def __init__(self, serial_number: str, baudrate: int = 9600):
        self.serial_number = serial_number
        self.baudrate = baudrate
        self.port = self._find_port_by_serial(serial_number)
        if not self.port:
            raise Exception(f"Device with serial number {serial_number} not found")

    @staticmethod
    def _find_port_by_serial(serial_number: str) -> str:
        for port in list_ports.comports():
            if port.serial_number == serial_number:
                return port.device
        raise DeviceNotFoundError(f"Could not find device with serial number {serial_number}.")

    def serialize(self, dataclass_obj: T) -> bytes:
        if not is_dataclass(dataclass_obj):
            raise ValueError("The provided object is not a dataclass instance.")

        string_representation = str(dataclass_obj)
        breakpoint()
        encoded_representation = string_representation.encode('utf-8')
        return encoded_representation

    def query(self, dataclass_obj: T) -> str:
        serialized_data = self.serialize(dataclass_obj)

        with serial.Serial(self.port, self.baudrate) as ser:
            ser.write(serialized_data)
            response = ser.readline().decode('utf-8').strip()
        return response

