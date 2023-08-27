import os
from pathlib import Path

__version__ = "0.3.0"
__hash__ = "b2265547da2cad8fe6cfe64178cf8367357586b7"
root_dir = Path(os.path.dirname(os.path.abspath(__file__)))
cpp_src_dir = root_dir / 'cpp' / 'src'
test_data_dir = root_dir / 'tests' / 'test_data'

