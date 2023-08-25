from pathlib import Path
import os
from typing import Type
from hardsync.interfaces import Exchange, TypeMapping
from hardsync.generators.common import convert_case, CaseType, populate_template
from hardsync.generators.common import Language, ARDUINO_INDENT
from dataclasses import fields
from types import ModuleType

dir_name = Path(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = dir_name / 'templates'


def virtual_declaration(exchange: Type[Exchange], type_mapping: TypeMapping):
    class_name = exchange.identifier()
    cpp_code = "virtual "

    response_fields = fields(exchange.Response)
    if len(response_fields) > 1:
        raise ValueError(f"Unspported number of response fields: {len(fields(exchange.Response))} only support 1 field")

    if len(response_fields) == 1:
        response_field = fields(exchange.Response)[0]
        cpp_code += type_mapping[response_field.type] + " "
    else:
        cpp_code += "void "

    cpp_code += f"{class_name.lower()}("
    cpp_code += ', '.join([f"{type_mapping[field.type]} {field.name}" for field in fields(exchange.Request)])

    cpp_code += ") const;"
    return cpp_code


def wrapper_declaration(exchange: Type[Exchange], type_mapping: TypeMapping):
    class_name = exchange.identifier()
    cpp_code = "void "

    cpp_code += f"{class_name.lower()}Wrapper("
    cpp_code += ', '.join([f"{type_mapping[field.type]} {field.name}" for field in fields(exchange.Request)])

    cpp_code += ") const;"
    return cpp_code


def respond_invocation(exchange: Type[Exchange], type_mapping: TypeMapping):
    class_name = exchange.identifier()
    function_name = convert_case(class_name, to_case=CaseType.CAMEL_CASE)

    cpp_code = f'}} else if (fn.name == "{class_name}Request") {{\n'

    for field in fields(exchange.Request):

        cpp_code += (
            f'{ARDUINO_INDENT}{type_mapping[field.type]} {field.name} = extract'
            f'{type_mapping[field.type].capitalize()}(&fn, "{field.name}");\n'
        )

    cpp_code += (f'{ARDUINO_INDENT}this->{function_name}Wrapper'
                 f'({", ".join([field.name for field in fields(exchange.Request)])});\n')

    return cpp_code


def wrapper_implementation(exchange: Type[Exchange], type_mapping: TypeMapping):
    class_name = exchange.identifier()
    function_name = convert_case(class_name, CaseType.CAMEL_CASE)
    request_fields = ", ".join(
        [f"{type_mapping[field.type]} {field.name}" for field in fields(exchange.Request)]
    )
    response_fields = ", ".join(
        [f"{type_mapping[field.type]} {field.name}" for field in fields(exchange.Response)]
    )

    request_field_names = ", ".join([f"{field.name}" for field in fields(exchange.Request)])

    cpp_code = f"""void Client::{function_name}Wrapper({request_fields}) const {{
    {response_fields} = this->{function_name}({request_field_names});
    Serial.print("{class_name}Response");
    Serial.print(ARGUMENT_BEGINNER);"""

    for field in fields(exchange.Response):
        cpp_code += f"""
    Serial.print("{field.name}");
    Serial.print(ARGUMENT_ASSIGNER);
    Serial.print({field.name});
    Serial.print(ARGUMENT_ENDER);"""

    cpp_code += """
    Serial.print(EXCHANGE_TERMINATOR);
}"""
    return cpp_code


def populate_client_template_cpp(contract: ModuleType):
    file_path = TEMPLATE_DIR / 'client.cpp'
    replacements = {
        'wrapper_implementations': '',
        'check_message_invocations': '',
    }
    with open(file_path, 'r') as file:
        template = file.read()
        populated_template = populate_template(template=template, replacements=replacements, language=Language.CPP)
        return populated_template


def generate(contract: ModuleType):
    generate_client_template_cpp(contract=contract)
