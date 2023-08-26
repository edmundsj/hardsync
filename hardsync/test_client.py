import pytest
from hardsync.interfaces import Exchange
from hardsync.types import ReceivedErrorResponse, DecodedExchange
from unittest.mock import Mock, patch
from hardsync.clients import BaseClient
from hardsync.channels import SerialChannel
from hardsync.encodings import AsciiEncoding
from dataclasses import dataclass


class Ping(Exchange):
    @dataclass
    class Request:
        pass

    @dataclass
    class Response:
        pass


def test_ping_with_client():
    mock_serial_instance = Mock()
    mock_serial_instance.isOpen.return_value = True
    mock_serial_instance.read_until = lambda expected: "PingResponse()"

    class MockOpenContextManager:
        def __enter__(self):
            return mock_serial_instance

        def __exit__(self, exc_type, exc_value, traceback):
            pass

    mock_channel = Mock()
    mock_channel.open = MockOpenContextManager

    with (
        patch('hardsync.channels.SerialChannel._find_port_by_serial', return_value='COM3'),
    ):
        client = BaseClient(channel=mock_channel, encoding=AsciiEncoding)
        response = client.request(request_values={}, exchange=Ping)
        assert response == DecodedExchange(name='PingResponse', values={})


def test_error_with_client():
    mock_serial_instance = Mock()
    mock_serial_instance.isOpen.return_value = True
    mock_serial_instance.read_until = lambda expected: "ErrorResponse()"

    class MockOpenContextManager:
        def __enter__(self):
            return mock_serial_instance

        def __exit__(self, exc_type, exc_value, traceback):
            pass

    mock_channel = Mock()
    mock_channel.open = MockOpenContextManager

    with (
        patch('hardsync.channels.SerialChannel._find_port_by_serial', return_value='COM3'),
    ):
        client = BaseClient(channel=mock_channel, encoding=AsciiEncoding)
        with pytest.raises(ReceivedErrorResponse):
            response = client.request(request_values={}, exchange=Ping)
