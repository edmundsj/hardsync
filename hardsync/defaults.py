from hardsync import root_dir
from hardsync.contracts import TypeMapping
from hardsync.transpiler import Targets

DEFAULT_GENERATED_DIR = root_dir / 'generated'
DEFAULT_TARGET_PLATFORM = Targets.ARDUINO
DEFAULT_TYPE_MAPPING: TypeMapping = TypeMapping({float: 'double', int: 'int', str: "std::string", None: 'void'})
