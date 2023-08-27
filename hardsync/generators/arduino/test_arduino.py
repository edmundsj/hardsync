from types import ModuleType
from hardsync.generators.arduino.arduino import (
    generate,
    core_implementation,
    populate_client_template_cpp,
    populate_client_template_h,
    wrapper_implementation,
    respond_invocation,
    virtual_declaration,
    wrapper_declaration,
)
from hardsync.generators.common import CPP_INDENT
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


class DoAction(Exchange):
    @dataclass
    class Request:
        pass

    @dataclass
    class Response:
        pass


def test_wrapper_implementation():
    actual = wrapper_implementation(exchange=MeasureVoltage, type_mapping=DEFAULT_TYPE_MAPPING)
    desired = [
        'void Client::measureVoltageWrapper(int channel, double integration_time) const {',
        CPP_INDENT + 'double voltage = this->measureVoltage(channel, integration_time);',
        CPP_INDENT + 'Serial.print("MeasureVoltageResponse");',
        CPP_INDENT + 'Serial.print(ARGUMENT_BEGINNER);',
        CPP_INDENT + 'Serial.print("voltage");',
        CPP_INDENT + 'Serial.print(ARGUMENT_ASSIGNER);',
        CPP_INDENT + 'Serial.print(voltage);',
        CPP_INDENT + 'Serial.print(ARGUMENT_ENDER);',
        CPP_INDENT + 'Serial.print(EXCHANGE_TERMINATOR);',
        '}',
    ]
    assert actual == desired


def test_respond_invocation():
    actual = respond_invocation(exchange=MeasureVoltage, type_mapping=DEFAULT_TYPE_MAPPING)
    desired = [
        '} else if (fn.name == "MeasureVoltageRequest") {',
        CPP_INDENT + 'int channel = extractInt(&fn, "channel");',
        CPP_INDENT + 'double integration_time = extractDouble(&fn, "integration_time");',
        CPP_INDENT + 'this->measureVoltageWrapper(channel, integration_time);'
    ]
    assert actual == desired


def test_virtual_declaration():
    actual = virtual_declaration(exchange=MeasureVoltage, type_mapping=DEFAULT_TYPE_MAPPING)
    desired = ["virtual double measureVoltage(int channel, double integration_time) const;"]
    assert actual == desired


def test_virtual_declaration_void():
    actual = virtual_declaration(exchange=DoAction, type_mapping=DEFAULT_TYPE_MAPPING)
    desired = ["virtual void doAction() const;"]
    assert actual == desired


def test_wrapper_declaration():
    actual = wrapper_declaration(exchange=MeasureVoltage, type_mapping=DEFAULT_TYPE_MAPPING)
    desired = ["void measureVoltageWrapper(int channel, double integration_time) const;"]
    assert actual == desired


def test_core_implementation_declaration():
    actual = core_implementation(exchange=MeasureVoltage, type_mapping=DEFAULT_TYPE_MAPPING)
    desired = [
        "double measureVoltage(int channel, double integration_time) const {",
        CPP_INDENT + '// YOUR CODE GOES HERE',
        '}',
    ]
    assert actual == desired


def test_populate_client_template_cpp():
    module = ModuleType('hi')
    module.MeasureVoltage = MeasureVoltage
    desired_filepath = TEST_DATA_DIR / 'client.cpp'

    actual = populate_client_template_cpp(contract=module, type_mapping=DEFAULT_TYPE_MAPPING)
    with open(desired_filepath, 'r') as desired_file:
        desired = desired_file.read()

        assert actual == desired


def test_populate_client_template_h():
    module = ModuleType('hi')
    module.MeasureVoltage = MeasureVoltage
    desired_filepath = TEST_DATA_DIR / 'client.h'

    actual = populate_client_template_h(contract=module, type_mapping=DEFAULT_TYPE_MAPPING)
    with open(desired_filepath, 'r') as desired_file:
        desired = desired_file.read()

        assert actual == desired

