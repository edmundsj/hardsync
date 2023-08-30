from __future__ import annotations

import enum
from typing import Dict, NamedTuple, Literal, Protocol


class FieldNotFoundError(Exception):
    pass


class ReceivedErrorResponse(Exception):
    pass


class Stringable(Protocol):
    def __str__(self) -> str:
        pass


ResponseValues = Dict[str, Stringable]


class DecodedExchange(NamedTuple):
    name: str
    values: ResponseValues


class PopulatedFile(NamedTuple):
    filename: str
    content: str
    is_main: bool = False


BaudRateT = Literal[
    300, 1200, 2400, 4800, 9600, 19_200, 38_400, 57_600,
    115_200, 230_400, 460_800, 921600, 1_000_000,
    2_000_000
]
