from types import ModuleType
from hardsync.generators.arduino import generate
from hardsync.interfaces import Exchange
from dataclasses import dataclass
from pathlib import Path
import os


class MeasureVoltage(Exchange):
    @dataclass
    class Request:
        integration_time: float
        channel: int

    @dataclass
    class Response:
        voltage: float


def test_populate_parser_template_cpp_empty():
    module = ModuleType('hi')
    module.MeasureVoltage = MeasureVoltage

    actual = generate(contract=module)
    desired_filepath = Path(os.path.dirname(os.path.abspath(__file__))) / 'test_data' / 'parser_template.cpp'
    with open(desired_filepath, 'r') as desired_file:
        desired = desired_file.read()

        assert actual == desired

