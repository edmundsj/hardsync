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


class bidict(dict):
    def __init__(self, *args, **kwargs):
        super(bidict, self).__init__(*args, **kwargs)
        self.inverse = {}
        for key, value in self.items():
            self.inverse.setdefault(value, []).append(key)

    def __setitem__(self, key, value):
        if key in self:
            self.inverse[self[key]].remove(key)
        super(bidict, self).__setitem__(key, value)
        self.inverse.setdefault(value, []).append(key)

    def __delitem__(self, key):
        self.inverse.setdefault(self[key], []).remove(key)
        if self[key] in self.inverse and not self.inverse[self[key]]:
            del self.inverse[self[key]]
        super(bidict, self).__delitem__(key)