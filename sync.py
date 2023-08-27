import argparse
import toml
from pathlib import Path
from typing import Mapping


def replace_vars(filename: Path, vars: Mapping[str, str]) -> str:
    with open(filename, 'r') as init_file:
        new_lines = []
        for line in init_file:
            starts_with_var = any([line.startswith(var) for var in vars.keys()])
            if starts_with_var:
                for var, val in vars.items():
                    if line.startswith(var):
                        new_lines.append(f'{var} = "{val}"\n')
            else:
                new_lines.append(line)

    contents = ""
    for line in new_lines:
        contents += line

    return contents


def main():
    current_version = toml.load("pyproject.toml")["tool"]["poetry"]["version"]

    parser = argparse.ArgumentParser(description="Simple calculator")
    parser.add_argument('--hash', type=str, help='Hash of the current build.', required=True)

    args = parser.parse_args()

    hardsync_init = Path('hardsync', '__init__.py')
    contents = replace_vars(filename=hardsync_init, vars={'__hash__': args.hash, '__version__': current_version})

    with open(hardsync_init, 'w') as init_file:
        init_file.write(contents)


if __name__ == '__main__':
    main()


