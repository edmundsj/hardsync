from dataclasses import dataclass
from typing import Literal
from serial import Serial
import abc

# TODO: Make this a wrapper around serial and other interfaces, and hide their underlying implementation.
# Expose read_until() and write_bytes() as the only member functions, and probably make them class methods or
# instance methods.

BaudRate = Literal[
    300, 1200, 2400, 4800, 9600, 19_200, 38_400, 57_600,
    115_200, 230_400, 460_800, 921600, 1_000_000,
    2_000_000
]


@dataclass
class Channel(abc.ABC):
    baud_rate: BaudRate
    channel_identifier: str  # For example, device serial number

    @abc.abstractmethod
    def open(self) -> Serial:
        pass
