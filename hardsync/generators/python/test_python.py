import os.path

from hardsync.interfaces import Exchange
from hardsync.generators.python import exchange_definition, request_function, generate
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
    expected = """\
class MeasureVoltage(Exchange):
    @dataclass
    class Request:
        integration_time: float
        channel: int

    @dataclass
    class Response:
        voltage: float

"""
    result = exchange_definition(MeasureVoltage)
    assert result == expected, f"Expected:\n{expected}\nGot:\n{result}"


# Test classes

def test_generate_request_for_measure_voltage():
    expected = """\
def request_measure_voltage(self, integration_time: float, channel: int) -> DecodedExchange:
        return self.request(
            request_values={ 'integration_time': integration_time, 'channel': channel },
            exchange=MeasureVoltage,
        )
"""
    result = request_function(MeasureVoltage)
    assert result == expected, f"Expected:\n{expected}\nGot:\n{result}"


def test_generate_request_for_current_reading():
    expected = """\
def request_current_reading(self, duration: float, range: int) -> DecodedExchange:
        return self.request(
            request_values={ 'duration': duration, 'range': range },
            exchange=CurrentReading,
        )
"""
    result = request_function(CurrentReading)
    assert result == expected, f"Expected:\n{expected}\nGot:\n{result}"


def test_populate_template():
    module = ModuleType('hi')
    module.MeasureVoltage = MeasureVoltage

    actual = generate(contract=module)
    desired_filepath = Path(os.path.dirname(os.path.abspath(__file__))) / 'test_data' / 'client.py'
    with open(desired_filepath, 'r') as desired_file:
        desired = desired_file.read()
        #desired = desired.replace('\n', '')

        #actual = actual.replace("\n", "")
        assert actual == desired

