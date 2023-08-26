import pytest
import os
from hardsync.__main__ import generate
from hardsync.interfaces import Exchange
from dataclasses import dataclass
from types import ModuleType
from hardsync.encodings import AsciiEncoding
from hardsync.defaults import DEFAULT_TYPE_MAPPING


class MeasureVoltage(Exchange):

    @dataclass
    class Request:
        integration_time: float
        channel: int

    @dataclass
    class Response:
        voltage: float


contract = ModuleType('hello')
contract.MeasureVoltage = MeasureVoltage
contract.TypeMapping = DEFAULT_TYPE_MAPPING


def test_generate_everything(tmp_path):
    generate(contract=contract, output_dir=tmp_path)
    firmware_path = tmp_path / 'firmware'
    desired_client_paths = [tmp_path / fn for fn in ['client.py']]
    desired_firmware_paths = [firmware_path / fn for fn in ['client.h', 'client.cpp', 'parser.h', 'parser.cpp', 'firmware.ino']]
    desired_paths = desired_firmware_paths + desired_client_paths

    for file_path in desired_paths:
        assert os.path.exists(file_path)
