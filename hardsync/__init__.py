import os
from pathlib import Path

__version__ = "0.3.0"
__hash__ = "fbf800c3ca0fe01cf17b775d33557dc501ddf8f4"
root_dir = Path(os.path.dirname(os.path.abspath(__file__)))
cpp_src_dir = root_dir / 'cpp' / 'src'
test_data_dir = root_dir / 'tests' / 'test_data'

