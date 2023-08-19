import os
from pathlib import Path

root_dir = Path(os.path.dirname(os.path.abspath(__file__)))
cpp_src_dir = root_dir / 'cpp' / 'src'
test_data_dir = root_dir / 'test_data'

