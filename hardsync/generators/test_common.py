import pytest
import os
from hardsync.generators.common import CaseType, detect_case, convert_case, starting_whitespace, write
from hardsync.utils import flatten
from hardsync.types import PopulatedFile


@pytest.mark.parametrize(
    'string,desired',(
            ('PascalCase', CaseType.PASCAL_CASE),
            ('snake_case_really', CaseType.SNAKE_CASE),
            ('camelCaseItReallyIs', CaseType.CAMEL_CASE),
            ('snake_orPascal', CaseType.UNKNOWN),
    ))
def test_detect_case(string, desired):
    actual = detect_case(string)
    assert actual == desired


@pytest.mark.parametrize(
    'string,to_case,desired',(
            ('PascalCase',CaseType.SNAKE_CASE, 'pascal_case'),
            ('snake_case_really', CaseType.PASCAL_CASE, 'SnakeCaseReally'),
            ('camel_case_from2', CaseType.CAMEL_CASE, 'camelCaseFrom2'),
    )
)
def test_convert_case(string, to_case, desired):
    actual = convert_case(s=string, to_case=to_case)
    assert actual == desired


@pytest.mark.parametrize(
    'string,match,desired',(
            ('   {{HelloThere}}', '{{HelloThere}}', '   '),
            (' snake_case_really', 'snake_case_', ' '),
            ('flargle', 'flarg', ''),
            ('nomatch', 'DEFNOT', ''),
    )
)
def test_starting_whitespace(string, match, desired):
    actual = starting_whitespace(input_string=string, match_string=match)
    assert actual == desired


def test_flatten():
    input_list = [['hi'], ['there']]
    desired = ['hi', 'there']
    actual = flatten(input_list)
    assert actual == desired


def test_write(tmp_path):
    desired = 'hello'
    file = PopulatedFile(filename='test_file.cpp', content=desired)
    full_path = tmp_path / file.filename
    write(file=file, dirname=tmp_path)
    assert os.path.exists(full_path)
    with open(full_path, 'r') as read_file:
        actual = read_file.read()
        assert actual == desired
