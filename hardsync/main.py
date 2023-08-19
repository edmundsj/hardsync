import click
import os
from pathlib import Path
from hardsync.transpiler import transpile, Targets, TARGETS
from hardsync import cpp_src_dir, root_dir

DEFAULT_GENERATED_DIR = root_dir / 'generated'
DEFAULT_TARGET_PLATFORM = Targets.ARDUINO


def generate(contract: Path, target_platform: Targets, output_dir: Path):
    # First, transpile the base code
    transpiler_mapping = TARGETS[target_platform]
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