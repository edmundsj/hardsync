from __future__ import annotations

from collections.abc import MutableMapping
from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Mapping, Type
from serial import Serial

from hardsync.types import DecodedExchange, BaudRate


@dataclass
class Encoding(ABC):
    argument_delimiter: str | bytes
    argument_assigner: str | bytes
    argument_beginner: str | bytes
    argument_ender: str | bytes
    exchange_terminator: str | bytes

    @staticmethod
    @abstractmethod
    def encode(exchange: Type[Exchange], values: Mapping, is_request: bool) -> str | bytes:
        pass

    @staticmethod
    @abstractmethod
    def decode(exchange: Type[Exchange], contents: str | bytes) -> DecodedExchange:
        pass


class TypeMapping(ABC, MutableMapping):
    # Define the required keys in a set
    REQUIRED_KEYS = {float, int, str, None}

    def __init__(self, input_dict: Mapping):
        self._store = dict()
        self.update(input_dict)  # Use the `update` of MutableMapping
        if not self.REQUIRED_KEYS.issubset(self._store.keys()):
            missing_keys = self.REQUIRED_KEYS - self._store.keys()
            raise KeyError(f"Missing required keys: {missing_keys}")

    # The following methods are required for MutableMapping
    def __getitem__(self, key):
        return self._store[key]

    def __setitem__(self, key, value):
        self._store[key] = value

    def __delitem__(self, key):
        del self._store[key]

    def __iter__(self):
        return iter(self._store)

    def __len__(self):
        return len(self._store)


class Exchange(ABC):
    @classmethod
    def identifier(cls):
        return cls.__name__

    @dataclass
    class Request(ABC):
        pass

    @dataclass
    class Response(ABC):
        pass


# TODO: Make this a wrapper around serial and other interfaces, and hide their underlying implementation.
# Expose read_until() and write_bytes() as the only member functions, and probably make them class methods or
# instance methods.
@dataclass
class Channel(ABC):
    baud_rate: BaudRate
    channel_identifier: str  # For example, device serial number

    @abstractmethod
    def open(self) -> Serial:
        pass


@dataclass
class Client(ABC):
    channel: Channel
    encoding: Type[Encoding]

    @abstractmethod
    def listen(self):
        pass