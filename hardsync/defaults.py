from typing import Type
from hardsync import root_dir
from hardsync.interfaces import TypeMapping, Encoding
from hardsync.transpiler import Targets
from hardsync.encodings import AsciiEncoding

DEFAULT_GENERATED_DIR = root_dir / 'generated'
DEFAULT_TARGET_PLATFORM = Targets.ARDUINO
DEFAULT_TYPE_MAPPING: TypeMapping = TypeMapping({float: 'double', int: 'int', str: "std::string", None: 'void'})
DEFAULT_ENCODING: Type[Encoding] = AsciiEncoding
