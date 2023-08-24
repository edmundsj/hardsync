from pathlib import Path
import os
from hardsync.generators.common import convert_case, CaseType, populate_template
from types import ModuleType


def generate_client_template_cpp(contract: ModuleType):
    dir_name = Path(os.path.dirname(os.path.abspath(__file__)))
    file_path = dir_name / 'client_template.cpp'
    replacements = {
        'wrapper_implementations': '',
        'check_message_invocations': '',
    }
    with open(file_path, 'r') as file:
        template = file.read()
        populated_template = populate_template(template=template, replacements=replacements)
        return populated_template
    pass


def generate(contract: ModuleType):
    generate_client_template_cpp(contract=contract)
