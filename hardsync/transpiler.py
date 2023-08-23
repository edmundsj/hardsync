"""
This takes generic C++ code and converts it into the equivalent arduino-C code.
This transpiler can probably afford to be fragile, at least in the beginning, as we
have complete control over both the code being transpiled and the transpiler.

TODO: Figure out when exactly to throw errors in transpilation.

"""
from dataclasses import fields, Field
from hardsync.interfaces import Exchange, TypeMapping
import inspect
from typing import Mapping, Dict, List, Sequence, Type
from types import ModuleType
import re
import enum


class TemplateMissingVariableError(Exception):
    pass


class ReplacementsMissingVariableError(Exception):
    pass


class ContractError(Exception):
    pass


class Targets(enum.Enum):
    ARDUINO = 'arduino'
    CPP = 'cpp'


TARGETS = {
    Targets.ARDUINO: {
        '#include <string>': '#include <WString.h>',
        'std::string': 'String',
        '.substr({{expr1}}, {{expr2}})': '.substring({{expr1}}, {{expr1}} + {{expr2}})',
        '.substr({{expr}})': '.substring({{expr}})',
        '.find(': '.indexOf(',
    },
    Targets.CPP: {},
}

EXPRESSION_REGEX = r'[\w\+\-\*/\(\) ]+'
EXPRESSION_REGEX_LITERAL = EXPRESSION_REGEX.replace('\\', '\\\\')
SOFTTAB = "    "


def template_to_regex(template: str):
    pattern = r'{{(?P<name>' + EXPRESSION_REGEX + r')}}'
    matches = re.finditer(pattern=pattern, string=template)
    new_string = template

    special_characters = ['(', ')', '[', ']']
    # Replace all regex special characters
    new_string = new_string.replace('(', r'\(')
    new_string = new_string.replace(')', r'\)')

    for match in matches:
        name = match.group('name')
        new_regex = r'(?P<' + name + r'>' + EXPRESSION_REGEX_LITERAL + r')'
        new_string = re.sub(pattern=pattern, repl=new_regex, string=new_string, count=1)

    return new_string


def var_names_from_template(template: str):
    var_names = []
    pattern = r'{{(?P<name>\w+)}}'
    matches = re.finditer(pattern=pattern, string=template)
    for match in matches:
        name = match.group('name')
        var_names.append(name)
    return var_names


def populate_template(template: str, replacements: Mapping[str, str]) -> str:
    populated_template = template
    for key, val in replacements.items():
        var_to_match = '{{' + key + '}}'
        populated_template = populated_template.replace(var_to_match, val)

    return populated_template


def verify_template(template: str, replacements: Mapping[str, str]):
    template_vars = var_names_from_template(template=template)
    not_in_template = []
    not_in_replacements = []

    for var in template_vars:
        if var not in replacements.keys():
            not_in_replacements.append(var)

    if not_in_replacements:
        raise ReplacementsMissingVariableError(
            f'Error: replacements missing variables {not_in_replacements} which is in replacements')


def transpile_template(template: str, replacement_template: str, input_text: str) -> Dict[str, str]:
    regex = template_to_regex(template)
    matches = re.finditer(pattern=regex, string=input_text)
    var_names = var_names_from_template(template)

    modified_text = input_text
    for match in reversed(list(matches)): # Reverse the list so we are mutating the string from the end
        replacements = {var: match.group(var) for var in var_names}
        replacement_string = populate_template(replacement_template, replacements=replacements)
        modified_text = modified_text[0:match.start()] + replacement_string + modified_text[match.end():]

    return modified_text


def transpile(input_text: str, template_mapping: Mapping[str, str]) -> str:
    modified_text = input_text
    for template, replacement_template in template_mapping.items():
        modified_text = transpile_template(template=template, replacement_template=replacement_template, input_text=modified_text)
    return modified_text


def classes(contract: ModuleType) -> List[Type]:
    all_classes = inspect.getmembers(contract, predicate=inspect.isclass)
    all_classes = [cls[1] for cls in all_classes]
    contract_objects = []
    for cls in all_classes:
        members = inspect.getmembers(cls, predicate=inspect.isclass)
        names = [mem[0] for mem in members]
        if 'Response' in names and 'Request' in names:
            contract_objects.append(cls)
        if 'Response' in names and not 'Request' in names:
            raise ContractError(f'Error: contract class {cls.__name__} has a Response but no Request.')
        if 'Request' in names and not 'Response' in names:
            raise ContractError(f'Error: contract class {cls.__name__} has a Request but no Response.')

    return contract_objects


def to_camel_case(val: str) -> str:
    if not val:
        return ""

    return val[0].lower() + val[1:]


def transform_type(t: type, type_mapping: TypeMapping):
    return type_mapping.get(t)


def cpp_declaration(
        return_type: type | None,
        name: str,
        args: Mapping[str, type],
        type_mapping: TypeMapping,
        prefix='virtual',
        suffix='const',
        namespace='',
):
    arg_type = [transform_type(t=t, type_mapping=type_mapping) for t in args.values()]
    arg_names = [name for name in args.keys()]
    arg_pairs = [t + ' ' + name for t, name in zip(arg_type, arg_names)]
    arg_string = ', '.join(arg_pairs)
    arg_string.removesuffix(', ')
    return_type = transform_type(t=return_type, type_mapping=type_mapping)
    preamble = ' '.join([prefix, return_type]).strip()
    if namespace:
        preamble += ' ' + namespace + '::' + name
    else:
        preamble += ' ' + name

    return preamble + '(' + arg_string + ')' + ' ' + suffix + ';'


def exchange_to_declaration(
        exchange: Type[Exchange],
        type_mapping: TypeMapping,
        prefix='virtual',
        suffix='const',
        nampespace='',
        return_type: None | type = '',
):
    function_name = to_camel_case(exchange.__name__)
    if return_type != '':
        return_type = return_type
    else:
        return_type = fields(exchange.Response)[0].type
    request_fields = fields(exchange.Request)
    args = {field.name: field.type for field in request_fields}

    return cpp_declaration(
        return_type=return_type,
        type_mapping=type_mapping,
        name=function_name,
        args=args,
        prefix=prefix,
        suffix=suffix,
        namespace=nampespace,
    )


def virtual_declarations(exchanges: Sequence[Type[Exchange]], type_mapping: TypeMapping) -> List[str]:
    lines = []
    for ex in exchanges:
        lines.append(
            exchange_to_declaration(exchange=ex, type_mapping=type_mapping, prefix='virtual', suffix='const')
        )
    return lines


def wrapper_declarations(exchanges: Sequence[Type[Exchange]], type_mapping: TypeMapping) -> List[str]:
    lines = []
    for ex in exchanges:
        function_name = 'void ' + to_camel_case(ex.identifier()) + "Wrapper() const;"
        lines.append(function_name)
    return lines


def wrapper_result_invocation(exchange: Type[Exchange], type_mapping: TypeMapping) -> str:
    response_fields = fields(exchange.Response)
    function_name = to_camel_case(exchange.__name__)
    if len(response_fields) == 1:
        output_type = transform_type(response_fields[0].type, type_mapping=type_mapping)
    else:
        output_type = exchange.__name__ + 'Response'

    line = ' '.join([output_type, response_fields[0].name, '=', f'this->{function_name}();'])
    return line


def wrapper_implementation(exchange: Type[Exchange], type_mapping: TypeMapping) -> List[str]:
    core_lines = []
    function_name = 'void BaseCommunicationClient::' + to_camel_case(exchange.identifier()) + "Wrapper()"

    encoding = exchange.Encoding
    line1 = function_name + ' ' + '{'
    contents_to_print = exchange.identifier() + 'Response' + encoding.argument_beginner
    line3 = f"Serial.print(\"{contents_to_print}\")" + ';'

    response_fields = fields(exchange.Response)
    if len(response_fields) > 1:
        raise AssertionError("Error: Do not currently support responses with more than one field. This should be easy to fix, submit an issue.")

    if len(response_fields) > 0 and response_fields[0].type is not None:
        field = response_fields[0]
        line = (f"{transform_type(field.type, type_mapping=type_mapping)} {field.name} = this->"
                f"{to_camel_case(exchange.identifier())}();")
        core_lines.append(line)

    core_lines.append(line3)
    for field in response_fields:
        preamble_line = f"Serial.print(\"{field.name}{encoding.argument_assigner}\");"
        value_line = f"Serial.print({field.name});"
        core_lines.extend([preamble_line, value_line])

    end_arguments_line = f"Serial.print(\"{encoding.argument_ender}\");"
    core_lines.append(end_arguments_line)

    end_exchange_line = f"Serial.print(\"{encoding.exchange_terminator}\");"
    core_lines.append(end_exchange_line)

    lines = [SOFTTAB + line for line in core_lines]
    lines.insert(0, line1)
    lines.append('}')

    return lines


def wrapper_implementations(exchanges: Sequence[Type[Exchange]], type_mapping: TypeMapping) -> List[str]:
    lines = []
    for exchange in exchanges:
        lines.extend(wrapper_implementation(exchange=exchange, type_mapping=type_mapping))
        lines.append('')
    return lines


def check_message_invocations(exchanges: Sequence[Type[Exchange]]) -> List[str]:
    lines = []
    for exchange in exchanges:
        line1 = '} else if (fn.name == \"' + exchange.identifier() + "Request\") {"
        line2 = SOFTTAB*3 + 'this->' + to_camel_case(exchange.identifier()) + "Wrapper();"
        lines.extend([line1, line2])

    return lines


def get_exchanges(module: ModuleType):
    exchanges = []
    for item in inspect.getmembers(module, predicate=inspect.isclass):
        if issubclass(item[1], Exchange):
            exchanges.append(item[1])
    return exchanges
