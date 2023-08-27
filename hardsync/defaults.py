from typing import Type
from hardsync import root_dir
from hardsync.interfaces import TypeMapping, Encoding
from hardsync.transpiler import Targets
from hardsync.encodings import AsciiEncoding


class DEFAULT_TYPE_MAPPING(TypeMapping):
    double: float
    int: int
    String: str


DEFAULT_GENERATED_DIR = root_dir / 'generated'
DEFAULT_TARGET_PLATFORM = Targets.ARDUINO
DEFAULT_ENCODING: Type[Encoding] = AsciiEncoding
