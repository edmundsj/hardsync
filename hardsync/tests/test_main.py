import pytest
import os
import shutil
from hardsync import test_data_dir
from hardsync.__main__ import generate, main_undecorated
from hardsync.interfaces import Exchange, ContractError, Channel as ChannelI
from dataclasses import dataclass
from types import ModuleType
from hardsync.defaults import DEFAULT_TYPE_MAPPING


class MeasureVoltage(Exchange):

    @dataclass
    class Request:
        integration_time: float
        channel: int

    @dataclass
    class Response:
        voltage: float


class Channel(ChannelI):
    baud_rate = 9600


contract = ModuleType('hello')
contract.MeasureVoltage = MeasureVoltage
contract.TypeMapping = DEFAULT_TYPE_MAPPING
contract.Channel = Channel

desired_client_files = ('client.py', 'application.py')
desired_firmware_files = ('client.h', 'client.cpp', 'parser.h', 'parser.cpp', 'firmware.ino')

def delete_contents_of_directory(directory_path):
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')


def test_generate_everything(tmp_path):
    generate(contract=contract, output_dir=tmp_path)
    firmware_path = tmp_path / 'firmware'
    desired_client_paths = [tmp_path / fn for fn in desired_client_files]
    desired_firmware_paths = [firmware_path / fn for fn in desired_firmware_files]
    desired_paths = desired_firmware_paths + desired_client_paths

    for file_path in desired_paths:
        assert os.path.exists(file_path)


def test_good_contracts(tmp_path):
    contracts_dir = test_data_dir / 'good_contracts'
    contracts = os.listdir(contracts_dir)
    contracts = [c for c in contracts if c.endswith('.py')]
    paths = [contracts_dir / c for c in contracts]
    for path in paths:
        main_undecorated(output_dir=tmp_path, contract=path, force=False)
        desired_files = set([fn for fn in desired_client_files + ('firmware',)])
        actual_files = set(os.listdir(tmp_path))
        assert actual_files == desired_files

        desired_files = set([fn for fn in desired_firmware_files])
        actual_files = set(os.listdir(tmp_path / 'firmware'))
        assert actual_files == desired_files
        delete_contents_of_directory(tmp_path)


def test_bad_contracts(tmp_path):
    contracts_dir = test_data_dir / 'bad_contracts'
    contracts = os.listdir(contracts_dir)
    contracts = [c for c in contracts if c.endswith('.py')]
    paths = [contracts_dir / c for c in contracts]
    for path in paths:
        with pytest.raises(ContractError):
            main_undecorated(output_dir=tmp_path, contract=path, force=False)


def test_unsupported_contracts(tmp_path):
    contracts_dir = test_data_dir / 'unsupported_contracts'
    contracts = os.listdir(contracts_dir)
    contracts = [c for c in contracts if c.endswith('.py')]
    paths = [contracts_dir / c for c in contracts]
    for path in paths:
        with pytest.raises(AssertionError):
            main_undecorated(output_dir=tmp_path, contract=path, force=False)
