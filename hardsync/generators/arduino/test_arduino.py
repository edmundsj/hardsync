from types import ModuleType
from hardsync.generators.arduino.arduino import (
    generate,
    populate_client_template_cpp,
    wrapper_implementation,
    respond_invocation,
)
from hardsync.interfaces import Exchange
from hardsync.defaults import DEFAULT_TYPE_MAPPING
from dataclasses import dataclass
from pathlib import Path
import os

TEST_DATA_DIR = Path(os.path.dirname(os.path.abspath(__file__))) / 'test_data'


class MeasureVoltage(Exchange):
    @dataclass
    class Request:
        channel: int
        integration_time: float

    @dataclass
    class Response:
        voltage: float


def test_populate_client_template_cpp_empty():
    module = ModuleType('hi')
    desired_filepath = TEST_DATA_DIR / 'client.cpp'

    actual = populate_client_template_cpp(contract=module)
    with open(desired_filepath, 'r') as desired_file:
        desired = desired_file.read()

        assert actual == desired


def test_wrapper_implementation():
    actual = wrapper_implementation(exchange=MeasureVoltage, type_mapping=DEFAULT_TYPE_MAPPING)
    desired = \
        """void Client::measureVoltageWrapper(int channel, double integration_time) const {
    double voltage = this->measureVoltage(channel, integration_time);
    Serial.print("MeasureVoltageResponse");
    Serial.print(ARGUMENT_BEGINNER);
    Serial.print("voltage");
    Serial.print(ARGUMENT_ASSIGNER);
    Serial.print(voltage);
    Serial.print(ARGUMENT_ENDER);
    Serial.print(EXCHANGE_TERMINATOR);
}"""
    assert actual == desired


def test_respond_invocation():
    actual = respond_invocation(exchange=MeasureVoltage, type_mapping=DEFAULT_TYPE_MAPPING)
    desired = \
        """} else if (fn.name == "MeasureVoltageRequest") {
    int channel = extractInt(&fn, "channel");
    double integration_time = extractDouble(&fn, "integration_time");
    this->measureVoltageWrapper(channel, integration_time);
"""
    assert actual == desired
