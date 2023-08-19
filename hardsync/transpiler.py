"""
This takes generic C++ code and converts it into the equivalent arduino-C code.
This transpiler can probably afford to be fragile, at least in the beginning, as we
have complete control over both the code being transpiled and the transpiler.
"""
from typing import Mapping
import re


cpp_to_arduino = {
    '#include <string>': '#include <WString.h>',
    'std::string': 'String',
    '.substr({{start}},{{count}})': '.substring({{start}},{{start}}+{{count}})',
    '.find(': '.indexOf(',
}

def extract_variable_values(template, input_text):
    # Extract the function name and all variables from the template string
    match = re.match(r"([a-zA-Z_]\w*)\((.*?)\)", template)
    if not match:
        return None

    func_name, var_sequence = match.groups()
    var_names = re.findall(r"\{\{(\w+)\}\}", var_sequence)

    # Build a regex pattern for the actual string
    pattern = r"{}\((.*?)\)$".format(func_name)

    match = re.match(pattern, input_text)
    if not match:
        return None

    # Extracting all values within the parentheses of the actual string
    values = [v.strip() for v in match.group(1).split(',')]

    # Check if the number of variables matches the number of values
    if len(var_names) != len(values):
        return None

    return dict(zip(var_names, values))


def transpile(content: str, mapping: Mapping) -> str:
    replacement_string = content
    for key, val in mapping.items():
        if '{{' not in key:
            replacement_string = replacement_string.replace(key, val)
            continue

        variables_to_replace = extract_variable_values(template=key, input_text=replacement_string)
        breakpoint()

    return replacement_string
