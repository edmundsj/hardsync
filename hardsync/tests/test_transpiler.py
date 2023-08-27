import pytest
from hardsync import test_data_dir
from dataclasses import dataclass
from hardsync.interfaces import TypeMapping, Exchange
from hardsync.transpiler import (
    template_to_regex,
    var_names_from_template,
    populate_template,
    transpile_template,
    transpile,
    TARGETS,
    Targets,
    verify_template,
    ReplacementsMissingVariableError,
    ContractError
)
from hardsync.encodings import AsciiEncoding
import types


class STANDARD_MAPPING(TypeMapping):
    double: float
    int: int
    void: None


class MeasureVoltage(Exchange):
    @dataclass
    class Encoding(AsciiEncoding):
        pass

    @dataclass
    class Request:
        channel: int

    @dataclass
    class Response:
        voltage: float


good_contract = types.ModuleType('good_contract')
good_contract.MeasureVoltage = MeasureVoltage


def test_template_to_regex_novar():
    template = 'variable'
    expected = 'variable'
    actual = template_to_regex(template)
    assert actual == expected


def test_var_names_from_template_one():
    template = 'variable{{hi}}'
    expected = ['hi']
    actual = var_names_from_template(template)
    assert actual == expected


def test_var_names_from_template_two():
    template = 'variable{{hi}}other{{there}}'
    expected = ['hi', 'there']
    actual = var_names_from_template(template)
    assert actual == expected


def test_populate_template_novars():
    template = 'variable'
    desired = 'variable'
    actual = populate_template(template=template, replacements={})
    assert actual == desired


def test_populate_template_single():
    template = 'variable{{yolo}}'
    desired = 'variableswag'
    actual = populate_template(template=template, replacements={'yolo': 'swag'})
    assert actual == desired


def test_populate_template_two():
    template = 'variable{{yolo}}othervar{{swag}}'
    desired = 'variableswagothervarhello'
    actual = populate_template(template=template, replacements={'yolo': 'swag', 'swag': 'hello'})
    assert actual == desired


def test_transpile_template_novars():
    original_text = 'variable 1400'
    template = 'variable'
    replacement = 'swag'
    desired = 'swag 1400'
    actual = transpile_template(template=template, replacement_template=replacement, input_text=original_text)
    assert actual == desired


def test_transpile_template_single_var():
    original_text = 'variable 1400'
    template = 'variable {{val}}'
    replacement = '{{val}} variable'
    desired = '1400 variable'
    actual = transpile_template(template=template, replacement_template=replacement, input_text=original_text)
    assert actual == desired


def test_transpile_template_two_vars():
    original_text = 'variable 1400 1900'
    template = 'variable {{val1}} {{val2}}'
    replacement = '{{val1}} variable {{val2}}'
    desired = '1400 variable 1900'
    actual = transpile_template(template=template, replacement_template=replacement, input_text=original_text)
    assert actual == desired


def test_transpile_template_function():
    original_text = 'myFunc(1400, 1900)'
    template = 'myFunc({{val1}}, {{val2}})'
    replacement = 'myFunc({{val2}}, {{val1}})'
    desired = 'myFunc(1900, 1400)'
    actual = transpile_template(template=template, replacement_template=replacement, input_text=original_text)
    assert actual == desired


def test_transpile_template_import():
    original_text = '#import <string>'
    template = '#import <string>'
    replacement = '#import <WString.h>'
    desired = '#import <WString.h>'
    actual = transpile_template(template=template, replacement_template=replacement, input_text=original_text)
    assert actual == desired


def test_transpile_switch_vars():
    original_text = 'myFunc(1400, 1200)'
    mapping = {r'myFunc({{val1}}, {{val2}})': 'myFunc({{val2}}, {{val1}})'}
    desired = 'myFunc(1200, 1400)'
    actual = transpile(template_mapping=mapping, input_text=original_text)
    assert desired == actual


def test_transpile_cpp_to_arduino_substr():
    original_text = "string.substr(start, count)"
    mapping = TARGETS[Targets.ARDUINO]
    desired = 'string.substring(start, start + count)'
    actual = transpile(template_mapping=mapping, input_text=original_text)
    assert desired == actual


def test_transpile_cpp_to_arduino_program():
    original_text = \
"""
#include <string>

std::string newString = oldString.substr(start, end)
"""
    desired = \
"""
#include <WString.h>

String newString = oldString.substring(start, start + end)
"""
    mapping = TARGETS[Targets.ARDUINO]
    actual = transpile(template_mapping=mapping, input_text=original_text)
    assert desired == actual


def test_transpile_cpp_files():
    mapping = TARGETS[Targets.ARDUINO]
    input_filename = test_data_dir / 'parser_initial.cpp'
    desired_filename = test_data_dir / 'parser_arduino.cpp'
    with open(input_filename, 'r') as input_file, open(desired_filename, 'r') as desired_file:
        input_text = input_file.read()
        desired_text = desired_file.read()
        actual_text = transpile(input_text=input_text, template_mapping=mapping)
        assert actual_text == desired_text


def test_transpile_cpp_files_no_transpilation():
    mapping = TARGETS[Targets.CPP]
    input_filename = test_data_dir / 'parser_initial.cpp'
    desired_filename = test_data_dir / 'parser_initial.cpp'
    with open(input_filename, 'r') as input_file, open(desired_filename, 'r') as desired_file:
        input_text = input_file.read()
        desired_text = desired_file.read()
        actual_text = transpile(input_text=input_text, template_mapping=mapping)
        assert actual_text == desired_text


def test_verify_template_ok():
    template = '{{key}}'
    replacements = {'key': 'val'}
    verify_template(template=template, replacements=replacements)


def test_verify_template_missing_replacement():
    template = '{{key}} {{missing_key}}'
    replacements = {'key': 'val'}
    with pytest.raises(ReplacementsMissingVariableError):
        verify_template(template=template, replacements=replacements)


