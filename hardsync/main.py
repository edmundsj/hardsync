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
    get_exchanges,
)
from hardsync import cpp_src_dir, root_dir
import importlib
import importlib.util

DEFAULT_GENERATED_DIR = root_dir / 'generated'
DEFAULT_TARGET_PLATFORM = Targets.ARDUINO


def generate(contract: Path, target_platform: Targets, output_dir: Path):
    transpiler_mapping = TARGETS[target_platform]
    files_to_augment = [
        'comms.h',
        'comms.cpp',
    ]
    spec = importlib.util.spec_from_file_location('contract', contract)
    contract_module = importlib.util.module_from_spec(spec)
    exchanges = get_exchanges(module=contract_module)

    for filename in files_to_augment:
        input_filename = cpp_src_dir / filename
        output_filename = output_dir / filename
        with open(input_filename, 'r') as input_file, open(output_filename, 'w') as output_file:
            replacements = {
                'wrapper_declarations': wrapper_declarations(exchanges=exchanges, type_mapping=type_mapping),
                'virtual_declarations': virtual_declarations(exchanges=exchanges, type_mapping=type_mapping),
                'baud_rate': '9600',
                'wrapper_implementations': wrapper_implementations(exchanges=exchanges, type_mapping=type_mapping),
                'check_message_invocations': check_message_invocations(exchanges=exchanges),
            }
            template = input_file.read()
            verify_template(template=template, replacements=replacements)
            populated_template = populate_template(template=template, replacements=replacements)
            output_file.write(populated_template)

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