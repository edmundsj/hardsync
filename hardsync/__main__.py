import click
import os
from pathlib import Path
from hardsync.transpiler import Targets
from hardsync.generators.python import generate as generate_python
from hardsync.generators.arduino import generate as generate_arduino
from hardsync.generators.common import write
from hardsync.dynamics import apply_defaults
from hardsync.defaults import DEFAULT_GENERATED_DIR, DEFAULT_TARGET_PLATFORM
import importlib
import importlib.util
from types import ModuleType

from typing import Sequence


def to_cpp_str(lines: Sequence[str]):
    snippet = ''
    for line in lines:
        snippet += line + "\n"
    return snippet


def load_contract(contract_path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location('contract', contract_path)
    contract = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module=contract)
    apply_defaults(contract)
    return contract


def generate(contract: ModuleType, output_dir: Path):
    type_mapping = contract.TypeMapping

    arduino_files = generate_arduino(contract=contract, type_mapping=type_mapping)
    arduino_output_dir = output_dir / 'firmware'
    os.makedirs(arduino_output_dir)

    for file in arduino_files:
        write(file=file, dirname=arduino_output_dir)

    python_files = generate_python(contract=contract)

    for file in python_files:
        write(file=file, dirname=output_dir)


@click.command()
@click.argument('contract', type=str)
@click.option('--output-dir', required=False)
def main(contract: str, output_dir: str):
    contract = Path(contract)
    if not output_dir:
        output_dir = Path(os.getcwd()) / 'generated'
    if not os.path.exists(contract):
        raise ValueError('Contract file path does not exist')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_dir = Path(output_dir)

    contract_module = load_contract(contract_path=contract)
    generate(output_dir=output_dir, contract=contract_module)


if __name__ == '__main__':
    main()