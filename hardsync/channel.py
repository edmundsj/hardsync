from dataclasses import dataclass
from typing import Literal


BaudRate = Literal[
    300, 1200, 2400, 4800, 9600, 19_200, 38_400, 57_600,
    115_200, 230_400, 460_800, 921600, 1_000_000,
    2_000_000
]


@dataclass
class Channel:
    baud_rate: BaudRate
    channel_identifier: str  # For example, device serial number
