from pathlib import Path
import os
import inspect
from typing import Type, List
from hardsync.interfaces import Exchange, TypeMapping, Channel, Contract
from hardsync.types import PopulatedFile
from hardsync.generators.common import convert_case, CaseType, populate_template
from hardsync.generators.common import Language, ARDUINO_INDENT, CPP_INDENT
from hardsync.utils import flatten
from hardsync.dynamics import get_exchanges
from dataclasses import fields
from types import ModuleType

dir_name = Path(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = dir_name / 'templates'


def virtual_declaration(exchange: Type[Exchange], type_mapping: Type[TypeMapping]) -> List[str]:
    function_name = convert_case(exchange.identifier(), CaseType.CAMEL_CASE)
    cpp_code = "virtual "

    response_fields = fields(exchange.Response)
    if len(response_fields) > 1:
        raise AssertionError(f"Unspported number of response fields: {len(fields(exchange.Response))} only support 1 field")

    if len(response_fields) == 1:
        response_field = fields(exchange.Response)[0]
        cpp_code += type_mapping[response_field.type] + " "
    else:
        cpp_code += "void "

    cpp_code += f"{function_name}("
    cpp_code += ', '.join([f"{type_mapping[field.type]} {field.name}" for field in fields(exchange.Request)])

    cpp_code += ") const;"
    return [cpp_code]


def wrapper_declaration(exchange: Type[Exchange], type_mapping: Type[TypeMapping]) -> List[str]:
    function_name = convert_case(exchange.identifier(), CaseType.CAMEL_CASE)
    cpp_code = "void "

    cpp_code += f"{function_name}Wrapper("
    cpp_code += ', '.join([f"{type_mapping[field.type]} {field.name}" for field in fields(exchange.Request)])

    cpp_code += ") const;"
    return [cpp_code]


def core_implementation(exchange: Type[Exchange], type_mapping: Type[TypeMapping]) -> List[str]:
    function_name = convert_case(exchange.identifier(), CaseType.CAMEL_CASE)
    lines = []
    response_fields = fields(exchange.Response)
    if len(response_fields) > 1:
        raise AssertionError("TO BE IMPLEMENTED: Response that supports more than one value")

    if len(response_fields) == 0:
        function_type = None
    elif len(response_fields) == 1:
        function_type = fields(exchange.Response)[0].type

    line1 = f"{type_mapping[function_type]} {function_name}("
    line1 += ', '.join([f"{type_mapping[field.type]} {field.name}" for field in fields(exchange.Request)])
    line1 += ") const {"
    lines.append(line1)
    lines.append(CPP_INDENT + '// YOUR CODE GOES HERE')
    lines.append("}")

    return lines


def respond_invocation(exchange: Type[Exchange], type_mapping: Type[TypeMapping]) -> List[str]:
    class_name = exchange.identifier()
    function_name = convert_case(class_name, to_case=CaseType.CAMEL_CASE)
    lines = []

    lines.append(f'}} else if (fn.name == "{class_name}Request") {{')

    for field in fields(exchange.Request):

        lines.append(
            f'{ARDUINO_INDENT}{type_mapping[field.type]} {field.name} = extract'
            f'{type_mapping[field.type].capitalize()}(&fn, "{field.name}");'
        )

    lines.append(f'{ARDUINO_INDENT}this->{function_name}Wrapper'
                 f'({", ".join([field.name for field in fields(exchange.Request)])});')

    return lines


def wrapper_implementation(exchange: Type[Exchange], type_mapping: Type[TypeMapping]) -> List[str]:
    if len(fields(exchange.Response)) > 1:
        raise AssertionError("TO BE IMPLEMENTED: Response cannot have more than one field.")

    class_name = exchange.identifier()
    function_name = convert_case(class_name, CaseType.CAMEL_CASE)
    request_fields = ", ".join(
        [f"{type_mapping[field.type]} {field.name}" for field in fields(exchange.Request)]
    )
    response_fields = ", ".join(
        [f"{type_mapping[field.type]} {field.name}" for field in fields(exchange.Response)]
    )

    request_field_names = ", ".join([f"{field.name}" for field in fields(exchange.Request)])
    lines = []

    lines.append(f'void Client::{function_name}Wrapper({request_fields}) const {{')
    line = f'{CPP_INDENT}{response_fields}'
    if response_fields:
        line += ' = '
    line += f'this->{function_name}({request_field_names});'
    lines.append(line)

    lines.append(f'{CPP_INDENT}Serial.print("{class_name}Response");')
    lines.append(f'{CPP_INDENT}Serial.print(ARGUMENT_BEGINNER);')

    for field in fields(exchange.Response):
        lines.append(f'{CPP_INDENT}Serial.print("{field.name}");')
        lines.append(f'{CPP_INDENT}Serial.print(ARGUMENT_ASSIGNER);')
        lines.append(f'{CPP_INDENT}Serial.print({field.name});')
        lines.append(f'{CPP_INDENT}Serial.print(ARGUMENT_ENDER);')

    lines.append(f'{CPP_INDENT}Serial.print(EXCHANGE_TERMINATOR);')
    lines.append('}')
    return lines


def serial_begin(channel: Type[Channel]) -> List[str]:
    lines = [
        f"Serial.begin({channel.baud_rate});"
    ]
    return lines


def populate_client_template_cpp(contract: Contract, type_mapping: Type[TypeMapping]) -> str:
    file_path = TEMPLATE_DIR / 'client.cpp'
    exchanges = get_exchanges(contract)
    wrapper_implementations = flatten([wrapper_implementation(ex, type_mapping=type_mapping) for ex in exchanges])
    respond_invocations = flatten([respond_invocation(ex, type_mapping=type_mapping) for ex in exchanges])
    serial_begins = serial_begin(contract.Channel)
    replacements = {
        'wrapper_implementations': wrapper_implementations,
        'respond_invocations': respond_invocations,
        'serial_begin': serial_begins,
    }
    with open(file_path, 'r') as file:
        template = file.read()
        populated_template = populate_template(template=template, replacements=replacements, language=Language.CPP)
        return populated_template


def populate_client_template_h(contract: Contract, type_mapping: Type[TypeMapping]) -> str:
    file_path = TEMPLATE_DIR / 'client.h'
    exchanges = get_exchanges(contract)
    virtual_declarations = flatten([virtual_declaration(exchange=ex, type_mapping=type_mapping) for ex in exchanges])
    wrapper_declarations = flatten([wrapper_declaration(exchange=ex, type_mapping=type_mapping) for ex in exchanges])
    replacements = {
        'virtual_declarations': virtual_declarations,
        'wrapper_declarations': wrapper_declarations,
    }
    with open(file_path, 'r') as file:
        template = file.read()
        populated_template = populate_template(template=template, replacements=replacements, language=Language.CPP)
        return populated_template


def populate_parser_template_h(contract: Contract, type_mapping: Type[TypeMapping]) -> str:
    file_path = TEMPLATE_DIR / 'parser.h'
    with open(file_path) as file:
        contents = file.read()
        return contents


def populate_parser_template_cpp(contract: Contract, type_mapping: Type[TypeMapping]) -> str:
    file_path = TEMPLATE_DIR / 'parser.cpp'
    with open(file_path) as file:
        contents = file.read()
        return contents


def populate_firmware_ino(contract: Contract, type_mapping: Type[TypeMapping]) -> str:
    file_path = TEMPLATE_DIR / 'firmware.ino'
    exchanges = get_exchanges(contract)
    core_implementations = flatten([core_implementation(exchange=ex, type_mapping=type_mapping) for ex in exchanges])
    replacements = {
        'core_implementations': core_implementations,
    }
    with open(file_path) as file:
        template = file.read()
        populated_template = populate_template(template=template, replacements=replacements, language=Language.CPP)
        return populated_template


def generate(contract: Contract, type_mapping: Type[TypeMapping]) -> List[PopulatedFile]:
    client_h = populate_client_template_h(contract=contract, type_mapping=type_mapping)
    client_cpp = populate_client_template_cpp(contract=contract, type_mapping=type_mapping)
    parser_h = populate_parser_template_h(contract=contract, type_mapping=type_mapping)
    parser_cpp = populate_parser_template_cpp(contract=contract, type_mapping=type_mapping)
    firmware_ino = populate_firmware_ino(contract=contract, type_mapping=type_mapping)
    files = [
        PopulatedFile(filename='client.h', content=client_h),
        PopulatedFile(filename='client.cpp', content=client_cpp),
        PopulatedFile(filename='parser.h', content=parser_h),
        PopulatedFile(filename='parser.cpp', content=parser_cpp),
        PopulatedFile(filename='firmware.ino', content=firmware_ino, is_main=True),
    ]

    return files
