import os.path

from hardsync.interfaces import Exchange
from hardsync.generators.python import exchange_definition, request_function, generate
from hardsync.generators.common import PYTHON_INDENT
from dataclasses import dataclass
from types import ModuleType
from pathlib import Path


class MeasureVoltage(Exchange):
    @dataclass
    class Request:
        integration_time: float
        channel: int

    @dataclass
    class Response:
        voltage: float


class CurrentReading:
    @dataclass
    class Request:
        duration: float
        range: int

    @dataclass
    class Response:
        current: float


def test_generate_exchange_str():
    # Test 1: MeasureVoltage class
    expected = [
        'class MeasureVoltage(Exchange):',
        PYTHON_INDENT + '@dataclass',
        PYTHON_INDENT + 'class Request:',
        PYTHON_INDENT * 2 + 'integration_time: float',
        PYTHON_INDENT * 2 + 'channel: int',
        '',
        PYTHON_INDENT + '@dataclass',
        PYTHON_INDENT + 'class Response:',
        PYTHON_INDENT * 2 + 'voltage: float',
        '',
        '',
        ]
    result = exchange_definition(MeasureVoltage)
    assert result == expected, f"Expected:\n{expected}\nGot:\n{result}"


# Test classes

def test_generate_request_for_measure_voltage():
    expected = [
        'def request_measure_voltage(self, integration_time: float, channel: int) -> DecodedExchange:',
        PYTHON_INDENT + 'return self.request(',
        PYTHON_INDENT * 2 + 'request_values={"integration_time": integration_time, "channel": channel},',
        PYTHON_INDENT * 2 + 'exchange=MeasureVoltage,',
        PYTHON_INDENT + ')',
    ]
    result = request_function(MeasureVoltage)
    assert result == expected, f"Expected:\n{expected}\nGot:\n{result}"


def test_generate_request_for_current_reading():
    expected = [
        'def request_current_reading(self, duration: float, range: int) -> DecodedExchange:',
        PYTHON_INDENT + 'return self.request(',
        PYTHON_INDENT * 2 + 'request_values={"duration": duration, "range": range},',
        PYTHON_INDENT * 2 + 'exchange=CurrentReading,',
        PYTHON_INDENT + ')',
    ]
    result = request_function(CurrentReading)
    assert result == expected, f"Expected:\n{expected}\nGot:\n{result}"


def test_populate_template():
    module = ModuleType('hi')
    module.MeasureVoltage = MeasureVoltage
    desired_filename = 'client.py'

    files = generate(contract=module)
    assert len(files) == 1

    desired_filepath = Path(os.path.dirname(os.path.abspath(__file__))) / 'test_data' / desired_filename
    with open(desired_filepath, 'r') as desired_file:
        desired_content = desired_file.read()
        assert desired_filename == files[0].filename
        assert desired_content == files[0].content

