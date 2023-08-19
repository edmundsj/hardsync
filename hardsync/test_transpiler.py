import pytest
from hardsync.transpiler import extract_variable_values, transpile  # Make sure to import the function


def test_basic_functionality():
    template = "myFunc({{var1}}, {{var2}}, {{var3}})"
    actual = "myFunc('hello', 'world', 'test')"
    expected = {'var1': "'hello'", 'var2': "'world'", 'var3': "'test'"}
    assert extract_variable_values(template, actual) == expected

def test_outside_function():
    template = "yolo{{var1}}"
    actual = "yoloswag"
    expected = {'var1': "swag"}
    assert extract_variable_values(template, actual) == expected


def test_unequal_vars_and_values():
    template = "myFunc({{var1}}, {{var2}})"
    actual = "myFunc('hello', 'world', 'test')"
    assert extract_variable_values(template, actual) is None


def test_different_function_names():
    template = "myFunc1({{var1}}, {{var2}})"
    actual = "myFunc2('hello', 'world')"
    assert extract_variable_values(template, actual) is None


def test_no_variables():
    template = "myFunc()"
    actual = "myFunc()"
    assert extract_variable_values(template, actual) is None


def test_non_matching_brackets():
    template = "myFunc({{var1}, {{var2}})"
    actual = "myFunc('hello', 'world')"
    assert extract_variable_values(template, actual) is None



def test_full_transpile_no_vars():
    mapping = {"<string>": "<Wstring.hhh>"}
    input_text = "#include <string>"
    desired_text = "#include <Wstring.hhh>"
    actual_text = transpile(content=input_text, mapping=mapping)
    assert actual_text == desired_text


def test_full_transpile_one_var():
    mapping = {"myFunc({{var}})": "myFunc(2*{{var}})"}
    input_text = "myFunc(hello)"
    desired_text = "myFunc(2*hello)"
    actual_text = transpile(content=input_text, mapping=mapping)
    assert actual_text == desired_text
