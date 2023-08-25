import inspect
import itertools
from dataclasses import is_dataclass, fields
from typing import Type, Sequence, List, Any, TypeVar
import os
from hardsync.generators.common import convert_case, CaseType, populate_template, Language, PYTHON_INDENT, flatten
from hardsync.dynamics import get_exchanges
from pathlib import Path
from types import ModuleType


def exchange_definition(cls: Type) -> List[str]:
    lines = []
    lines.append(f"class {cls.__name__}(Exchange):")

    # Check each attribute of the class
    for name, member in inspect.getmembers(cls):
        is_request_response = (name == 'Request' or name == 'Response')

        if is_request_response and not is_dataclass(member):
            raise AssertionError('Request is not a dataclass. This should never happen.')

        if is_request_response:
            lines.append(f"{PYTHON_INDENT}@dataclass")
            lines.append(f"{PYTHON_INDENT}class {name}:")
            for field in fields(member):
                if isinstance(field.type, str):
                    field_type = field.type
                else:
                    field_type = field.type.__name__
                lines.append(f"{PYTHON_INDENT * 2}{field.name}: {field_type}")
            lines.append('')
    lines.append('')

    return lines


def request_function(cls: Type) -> List[str]:
    # Find the Request dataclass
    request_subclass = getattr(cls, 'Request', None)
    if not request_subclass or not is_dataclass(request_subclass):
        raise ValueError(f"'{cls.__name__}' does not have a valid 'Request' sub-dataclass.")

    # Collect field names and their types
    field_strings = [f"{field.name}: {field.type.__name__}" for field in fields(request_subclass)]

    # Join fields for the function signature
    func_signature = ", ".join(field_strings)

    # Construct the request values for the function body
    request_values = ", ".join([f"\"{field.name}\": {field.name}" for field in fields(request_subclass)])

    # Return the final string
    converted_name = convert_case(cls.__name__, to_case=CaseType.SNAKE_CASE)
    lines = [
        f'def request_{converted_name}(self, {func_signature}) -> DecodedExchange:',
        PYTHON_INDENT + 'return self.request(',
        PYTHON_INDENT * 2 + f'request_values={{{request_values}}},',
        PYTHON_INDENT * 2 + f'exchange={cls.__name__},',
        PYTHON_INDENT + ')',
    ]
    return lines





def generate(contract: ModuleType):
    dir_name = Path(os.path.dirname(os.path.abspath(__file__)))
    template_filename = dir_name / 'templates' / 'client.py'
    exchanges = get_exchanges(module=contract)

    exchange_lines = flatten([exchange_definition(ex) for ex in exchanges])

    request_lines = flatten([request_function(ex) for ex in exchanges])

    replacements = {
        'exchange_definitions': exchange_lines,
        'request_definitions': request_lines,
    }

    with open(template_filename, 'r') as template_file:
        template = template_file.read()
        return populate_template(template=template, replacements=replacements, language=Language.PYTHON)

