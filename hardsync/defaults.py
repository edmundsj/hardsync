from typing import Type
from hardsync import root_dir
from hardsync.interfaces import TypeMapping as TypeMappingI
from hardsync.transpiler import Targets
from hardsync.encodings import AsciiEncoding


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
