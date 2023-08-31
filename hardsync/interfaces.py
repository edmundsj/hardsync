from __future__ import annotations

from dataclasses import dataclass, fields
from abc import ABC, abstractmethod
from typing import Mapping, Type, Dict, Protocol, Any
from serial import Serial

from hardsync.types import DecodedExchange, BaudRateT


class ContractError(Exception):
    pass


@dataclass
class Encoding(ABC):
    argument_delimiter: str | bytes
    argument_assigner: str | bytes
    argument_beginner: str | bytes
    argument_ender: str | bytes
    exchange_terminator: str | bytes

    @staticmethod
    @abstractmethod
    def encode(exchange: Type[Exchange], values: Mapping, is_request: bool) -> bytes:
        pass

    @staticmethod
    @abstractmethod
    def decode(exchange: Type[Exchange], contents: bytes) -> DecodedExchange:
        pass


class TypeMapping:

    @classmethod
    def __class_getitem__(cls, item):
        lookup_dict = {val: key for key, val in cls.__annotations__.items()}
        return lookup_dict[item]

    @classmethod
    def keys(cls):
        return cls.__annotations__.values()


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


class Contract(Protocol):
    Encoding: Type[Encoding]
    Channel: Type[Channel]
    TypeMapping: Type[TypeMapping]
