import re
import enum
from typing import Mapping


class CaseType(enum.Enum):
    CAMEL_CASE = "camelCase"
    SNAKE_CASE = "snake_case"
    PASCAL_CASE = "PascalCase"
    UNKNOWN = "UNKNOWN"


class Language(enum.Enum):
    ARDUINO = "arduino"
    CPP = "cpp"
    PYTHON = "python"


def indent(language: Language):
    if language == language.ARDUINO or language == language.CPP:
        return "    "
    elif language == language.PYTHON:
        return "    "
    raise ValueError(f"Unspported language {language}")


CPP_INDENT = indent(language=Language.CPP)
ARDUINO_INDENT = indent(language=Language.ARDUINO)
PYTHON_INDENT = indent(language=Language.PYTHON)



def detect_case(s: str) -> CaseType:
    if re.match('^[a-z]+([A-Z][a-z0-9]+)+$', s):
        return CaseType.CAMEL_CASE
    elif re.match('^[a-z]+(_[a-z0-9]+)+$', s):
        return CaseType.SNAKE_CASE
    elif re.match('^[A-Z][a-z0-9]+([A-Z][a-z0-9]+)*$', s):
        return CaseType.PASCAL_CASE
    else:
        return CaseType.UNKNOWN


def convert_case(s: str, to_case: CaseType) -> str:
    # Convert any case to snake_case
    s = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s).lower()

    if to_case == CaseType.SNAKE_CASE:
        return s
    elif to_case == CaseType.CAMEL_CASE:
        return re.sub('_([a-z])', lambda x: x.group(1).upper(), s)
    elif to_case == CaseType.PASCAL_CASE:
        return s.title().replace('_', '')
    else:
        raise ValueError(f"Unsupported target case: {to_case}")


def populate_template(template: str, replacements: Mapping[str, str], language: Language) -> str:
    populated_template = template
    if language == Language.PYTHON:
        comment_sequence = '#'
    elif language == Language.CPP or language == Language.ARDUINO:
        comment_sequence = '//'
    else:
        raise ValueError(f"Language {language} not supported.")
    for key, val in replacements.items():
        var_to_match = comment_sequence + ' {{' + key + '}}'
        populated_template = populated_template.replace(var_to_match, val)

    return populated_template

