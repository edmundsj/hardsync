import serial
from dataclasses import dataclass
from typing import Any

# Here's the question - does it make more sense to expose a set of functions, or a 
# device class? Personally, I think it will be much easier to encapsulate things for the 
# user if we expose a generic device class.
# Here's the first question, do we open and close a serial connection dynamically, or open it once and keep it open?
# For maximum flexibility, initially I say we open it and then close at the end of communication, but we can change that in the future. Perhaps the device itself could be a context manager.

# How should we serialize things? Probably into byte arrays, as these are what is actually being written.

import serial
import abc
from serial.tools import list_ports
from dataclasses import is_dataclass
from typing import TypeVar, Type
from hardsync.example.contract import IdentifyRequest, MeasureVoltageRequest, IdentifyResponse, MeasureVoltageResponse
from hardsync.device import BaseDevice

T = TypeVar('T')


# This code should be auto-generated
class Device(BaseDevice):
    def __init__(self, serial_number: str, baudrate: int):
        super().__init__(
            serial_number=serial_number,
            baudrate=baudrate
        )

    def identify(self) -> str:
        request = IdentifyRequest()

        return self.query(request)

    def measure_voltage(self, integration_time: int, channel: int) -> float:
        request = MeasureVoltageRequest(
            integration_time=integration_time,
            channel=channel
        )

