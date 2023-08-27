import platform
import click
import os
import logging
from pathlib import Path
import hardsync
from hardsync.generators.python import generate as generate_python
from hardsync.generators.arduino import generate as generate_arduino
from hardsync.generators.common import write, preface_string, Language
from hardsync.dynamics import apply_defaults
import importlib
import importlib.util
from types import ModuleType

from typing import Sequence

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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


def generate(contract: ModuleType, output_dir: Path, force=False):
    type_mapping = contract.TypeMapping

    arduino_files = generate_arduino(contract=contract, type_mapping=type_mapping)
    arduino_output_dir = output_dir / 'firmware'

    if not os.path.exists(arduino_output_dir):
        os.makedirs(arduino_output_dir)

    for file in arduino_files:
        preface = preface_string(language=Language.ARDUINO)
        write(file=file, dirname=arduino_output_dir, force=force, preface=preface)

    python_files = generate_python(contract=contract)

    for file in python_files:
        preface = preface_string(language=Language.PYTHON)
        write(file=file, dirname=output_dir, force=force, preface=preface)


@click.group(invoke_without_command=True)
@click.option('--contract', type=str)
@click.option('--output-dir', required=False)
@click.option('--force', required=False, default=False, type=bool, is_flag=True)
@click.pass_context
def main(context, contract: str, output_dir: str, force: bool):
    if context.invoked_subcommand is None:

        contract = Path(contract)
        if not output_dir:
            output_dir = Path(os.getcwd()) / 'generated'
        if not os.path.exists(contract):
            raise ValueError('Contract file path does not exist')
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        output_dir = Path(output_dir)

        contract_module = load_contract(contract_path=contract)
        generate(output_dir=output_dir, contract=contract_module, force=force)


@main.command(help="Output information useful for debugging")
def dump():
    """
    Creates a helpful output for the user
    """
    click.echo(f'hardsync_version: {hardsync.__version__}')
    click.echo(f'hardsync_hash: {hardsync.__hash__}')
    click.echo(f'os_name: {os.name}')
    click.echo(f'platform: {platform.system()}')
    click.echo(f'platform_version: {platform.uname()[3]}')
    click.echo(f'python_version: {platform.python_version()}')


if __name__ == '__main__':
    main()
