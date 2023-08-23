import inspect

import click
import os
from pathlib import Path
from hardsync.transpiler import (
    transpile,
    Targets,
    TARGETS,
    populate_template,
    verify_template,
    virtual_declarations,
    wrapper_declarations,
    check_message_invocations,
    wrapper_implementations,
)
from hardsync.generators.python import generate as generate_python
from hardsync import cpp_src_dir, root_dir
from hardsync.dynamics import apply_defaults, get_exchanges
from hardsync.defaults import DEFAULT_GENERATED_DIR, DEFAULT_TARGET_PLATFORM
import importlib
import importlib.util

from typing import Sequence


def to_cpp_str(lines: Sequence[str]):
    snippet = ''
    for line in lines:
        snippet += line + "\n"
    return snippet


def generate(contract: Path, target_platform: Targets, output_dir: Path):
    transpiler_mapping = TARGETS[target_platform]
    files_to_augment = [
        'comms.h',
        'comms.cpp',
    ]
    spec = importlib.util.spec_from_file_location('contract', contract)
    contract_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module=contract_module)
    apply_defaults(contract_module)

    exchanges = get_exchanges(module=contract_module)
    type_mapping = contract_module.TypeMapping

    for filename in files_to_augment:
        input_filename = cpp_src_dir / filename
        output_filename = output_dir / filename
        with open(input_filename, 'r') as input_file, open(output_filename, 'w') as output_file:
            replacements = {
                'baud_rate': '9600',
                'wrapper_declarations': to_cpp_str(
                    wrapper_declarations(exchanges=exchanges, type_mapping=type_mapping)
                ),
                'virtual_declarations': to_cpp_str(
                    virtual_declarations(exchanges=exchanges, type_mapping=type_mapping)
                ),
                'wrapper_implementations': to_cpp_str(
                    wrapper_implementations(exchanges=exchanges, type_mapping=type_mapping)
                ),
                'check_message_invocations': to_cpp_str(check_message_invocations(exchanges=exchanges)),
            }
            template = input_file.read()
            verify_template(template=template, replacements=replacements)
            populated_template = populate_template(template=template, replacements=replacements)
            transpiled_contents = transpile(input_text=populated_template, template_mapping=transpiler_mapping)
            output_file.write(transpiled_contents)

    files_to_transpile = [
        'parser.h',
        'parser.cpp',
    ]
    for filename in files_to_transpile:
        input_filename = cpp_src_dir / filename
        output_filename = output_dir / filename
        with open(input_filename, 'r') as input_file, open(output_filename, 'w') as output_file:
            contents = input_file.read()
            transpiled_contents = transpile(input_text=contents, template_mapping=transpiler_mapping)
            output_file.write(transpiled_contents)

    python_client = generate_python(contract=contract_module)
    python_output_file = output_dir / 'client.py'
    with open(python_output_file, 'w') as client_file:
        client_file.write(python_client)


@click.command()
@click.argument('contract', type=str)
@click.option('--output-dir', default=DEFAULT_GENERATED_DIR, required=False)
@click.option('--target-platform', default=DEFAULT_TARGET_PLATFORM, type=click.Choice(Targets))
def main(contract: str, output_dir: str, target_platform: Targets):
    contract = Path(contract)
    output_dir = Path(output_dir)
    if not os.path.exists(contract):
        raise ValueError('Contract file path does not exist')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    generate(output_dir=output_dir, contract=contract, target_platform=target_platform)


if __name__ == '__main__':
    main()