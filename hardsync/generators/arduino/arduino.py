from pathlib import Path
import os
from typing import Type, List
from hardsync.interfaces import Exchange, TypeMapping
from hardsync.generators.common import convert_case, CaseType, populate_template
from hardsync.generators.common import Language, ARDUINO_INDENT, CPP_INDENT, flatten
from hardsync.dynamics import get_exchanges
from dataclasses import fields
from types import ModuleType

dir_name = Path(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = dir_name / 'templates'


def virtual_declaration(exchange: Type[Exchange], type_mapping: TypeMapping) -> List[str]:
    function_name = convert_case(exchange.identifier(), CaseType.CAMEL_CASE)
    cpp_code = "virtual "

    response_fields = fields(exchange.Response)
    if len(response_fields) > 1:
        raise ValueError(f"Unspported number of response fields: {len(fields(exchange.Response))} only support 1 field")

    if len(response_fields) == 1:
        response_field = fields(exchange.Response)[0]
        cpp_code += type_mapping[response_field.type] + " "
    else:
        cpp_code += "void "

    cpp_code += f"{function_name}("
    cpp_code += ', '.join([f"{type_mapping[field.type]} {field.name}" for field in fields(exchange.Request)])

    cpp_code += ") const;"
    return [cpp_code]


def wrapper_declaration(exchange: Type[Exchange], type_mapping: TypeMapping) -> List[str]:
    function_name = convert_case(exchange.identifier(), CaseType.CAMEL_CASE)
    cpp_code = "void "

    cpp_code += f"{function_name}Wrapper("
    cpp_code += ', '.join([f"{type_mapping[field.type]} {field.name}" for field in fields(exchange.Request)])

    cpp_code += ") const;"
    return [cpp_code]


def respond_invocation(exchange: Type[Exchange], type_mapping: TypeMapping) -> List[str]:
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


def wrapper_implementation(exchange: Type[Exchange], type_mapping: TypeMapping) -> List[str]:
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
    lines.append(f'{CPP_INDENT}{response_fields} = this->{function_name}({request_field_names});')
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


def populate_client_template_cpp(contract: ModuleType, type_mapping: TypeMapping):
    file_path = TEMPLATE_DIR / 'client.cpp'
    exchanges = get_exchanges(contract)
    wrapper_implementations = flatten([wrapper_implementation(ex, type_mapping=type_mapping) for ex in exchanges])
    respond_invocations = flatten([respond_invocation(ex, type_mapping=type_mapping) for ex in exchanges])
    replacements = {
        'wrapper_implementations': wrapper_implementations,
        'respond_invocations': respond_invocations,
    }
    with open(file_path, 'r') as file:
        template = file.read()
        populated_template = populate_template(template=template, replacements=replacements, language=Language.CPP)
        return populated_template


def populate_client_template_h(contract: ModuleType, type_mapping: TypeMapping):
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


def generate(contract: ModuleType):
    generate_client_template_cpp(contract=contract)
