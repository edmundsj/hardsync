from typing import Type
from hardsync import root_dir
from hardsync.interfaces import (
    TypeMapping as TypeMappingI,
    Exchange,
)
from hardsync.transpiler import Targets
from hardsync.encodings import AsciiEncoding
from hardsync.channels import SerialChannel
from serial import Serial


class TypeMapping(TypeMappingI):
    double: float
    int: int
    String: str


DEFAULT_TYPE_MAPPING = TypeMapping

DEFAULT_GENERATED_DIR = root_dir / 'generated'
DEFAULT_TARGET_PLATFORM = Targets.ARDUINO


class Encoding(AsciiEncoding):
    pass


DEFAULT_ENCODING = Encoding


class Ping(Exchange):
    pass


class Channel(SerialChannel):
    pass


DEFAULT_CHANNEL = Channel(baud_rate=9600, channel_identifier='')
