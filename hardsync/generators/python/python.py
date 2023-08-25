import inspect
from dataclasses import is_dataclass, fields
from typing import Type, Mapping
import os
from hardsync.generators.common import convert_case, CaseType, populate_template, Language
from hardsync.dynamics import get_exchanges
from pathlib import Path
from types import ModuleType

INDENT = "    "


def exchange_definition(cls: Type) -> str:
    class_str = f"class {cls.__name__}(Exchange):\n"

    # Check each attribute of the class
    for name, member in inspect.getmembers(cls):
        is_request_response = (name == 'Request' or name == 'Response')
        is_encoding = (name == 'Encoding')

        if is_request_response and not is_dataclass(member):
            raise AssertionError('Request is not a dataclass. This should never happen.')

        if is_encoding:
            # TODO: THIS IS A HACK. NEED TO MODIFY SO THAT WE CAN HANDLE OTHER ENCODINGS
            class_str += f"{INDENT}@dataclass\n{INDENT}class {name}(AsciiEncoding):\n{INDENT * 2}pass\n"
            class_str += "\n"

        if is_request_response:
            class_str += f"{INDENT}@dataclass\n{INDENT}class {name}:\n"
            for field in fields(member):
                if isinstance(field.type, str):
                    field_type = field.type
                else:
                    field_type = field.type.__name__
                class_str += f"{INDENT * 2}{field.name}: {field_type}\n"
            class_str += "\n"

    return class_str


def request_function(cls: Type) -> str:
    # Find the Request dataclass
    request_subclass = getattr(cls, 'Request', None)
    if not request_subclass or not is_dataclass(request_subclass):
        raise ValueError(f"'{cls.__name__}' does not have a valid 'Request' sub-dataclass.")

    # Collect field names and their types
    field_strings = [f"{field.name}: {field.type.__name__}" for field in fields(request_subclass)]

    # Join fields for the function signature
    func_signature = ", ".join(field_strings)

    # Construct the request values for the function body
    request_values = ", ".join([f"'{field.name}': {field.name}" for field in fields(request_subclass)])

    # Return the final string
    converted_name = convert_case(cls.__name__, to_case=CaseType.SNAKE_CASE)
    return f"""\
def request_{converted_name}(self, {func_signature}) -> DecodedExchange:
{INDENT * 2}return self.request(
{INDENT * 3}request_values={{ {request_values} }},
{INDENT * 3}exchange={cls.__name__},
{INDENT * 2})
"""


def request_function_typed(cls: Type) -> str:
    # Find the Request and Response dataclasses
    request_subclass = getattr(cls, 'Request', None)
    response_subclass = getattr(cls, 'Response', None)

    if not request_subclass or not is_dataclass(request_subclass):
        raise ValueError(f"'{cls.__name__}' does not have a valid 'Request' sub-dataclass.")
    if not response_subclass or not is_dataclass(response_subclass):
        raise ValueError(f"'{cls.__name__}' does not have a valid 'Response' sub-dataclass.")

    # Construct function signature based on Request fields
    func_signature = ", ".join([f"{field.name}: {field.type.__name__}" for field in fields(request_subclass)])

    # Construct request values for function body
    request_values = ", ".join([f"'{field.name}': {field.name}" for field in fields(request_subclass)])

    # Construct the namedtuple return type based on Response fields
    response_type_fields = ", ".join([f"{field.name}: {field.type.__name__}" for field in fields(response_subclass)])
    return_type = f"namedtuple('ReturnData', ['name', 'values: namedtuple('Values', ['{response_type_fields}'])'])"

    # Return the final string
    return f"""\
def Request{cls.__name__}(self, {func_signature}) -> {return_type}:
    return self.request(
        request_values={{ {request_values} }},
        exchange={cls.__name__},
"""


def generate(contract: ModuleType):
    dir_name = Path(os.path.dirname(os.path.abspath(__file__)))
    template_filename = dir_name / 'templates' / 'client.py'
    exchanges = get_exchanges(module=contract)

    exchange_strings = [exchange_definition(ex) for ex in exchanges]
    exchange_definitions = '\n\n\n'.join(exchange_strings)

    request_strings = [request_function(ex) for ex in exchanges]
    request_definitions = '\n\n'.join(request_strings)

    replacements = {
        'exchange_definitions': exchange_definitions,
        'request_definitions': request_definitions,
    }

    with open(template_filename, 'r') as template_file:
        template = template_file.read()
        return populate_template(template=template, replacements=replacements, language=Language.PYTHON)

