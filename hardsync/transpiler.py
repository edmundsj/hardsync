"""
This takes generic C++ code and converts it into the equivalent arduino-C code.
This transpiler can probably afford to be fragile, at least in the beginning, as we
have complete control over both the code being transpiled and the transpiler.

TODO: Figure out when exactly to throw errors in transpilation.

"""
from typing import Mapping, Dict
import re
import enum


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


