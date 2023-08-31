import pytest
import struct

from hardsync.encodings import AsciiEncoding, BinaryEncoding
from hardsync.interfaces import Exchange
from hardsync.types import DecodedExchange
from dataclasses import dataclass, fields
from hardsync.defaults import Ping


class MeasureVoltage(Exchange):
    @dataclass
    class Request:
        channel: int
        integration_time: float

    @dataclass
    class Response:
        voltage: float


class Ping(Exchange):
    @dataclass
    class Request:
        pass

    @dataclass
    class Response:
        pass


def test_arg_string():
    input_string = 'SomethingResponse(arg1=hi,arg2=4)'
    desired = 'arg1=hi,arg2=4'
    actual = AsciiEncoding._arg_string(input_string)
    assert actual == desired


def test_encode_args():
    values = {'arg1': 4, 'arg2': 'hello'}
    desired = 'arg1=4,arg2=hello'
    actual = AsciiEncoding._encode_args(exchange=MeasureVoltage, values=values)
    assert actual == desired


def test_encode_full():
    values = {'arg1': 4, 'arg2': 'hello'}
    desired = b'MeasureVoltageRequest(arg1=4,arg2=hello)\n'
    actual = AsciiEncoding.encode(exchange=MeasureVoltage, values=values, is_request=True)
    assert actual == desired


def test_decode_name():
    to_decode = 'MeasureVoltageRequest(channel=4,integration_time=0.5)'
    desired = 'MeasureVoltageRequest'
    actual = AsciiEncoding._decode_name(contents=to_decode)
    assert actual == desired


def test_decode_args():
    to_decode = 'MeasureVoltageRequest(channel=4,integration_time=0.5)'
    desired = {'channel': 4, 'integration_time': 0.5}
    actual = AsciiEncoding._decode_args(contents=to_decode, exchange=MeasureVoltage)
    assert actual == desired


def test_decode_args_none():
    to_decode = 'PingRequest()'
    desired = {}
    actual = AsciiEncoding._decode_args(contents=to_decode, exchange=Ping)
    assert actual == desired


def test_decode():
    to_decode = b'MeasureVoltageRequest(channel=4,integration_time=0.5)\n'
    desired = DecodedExchange(name='MeasureVoltageRequest', values={'channel': 4, 'integration_time': 0.5})
    actual = AsciiEncoding.decode(contents=to_decode, exchange=MeasureVoltage)
    assert actual == desired


def test_lookup_field_type():
    available_fields = fields(MeasureVoltage.Request)
    desired = float
    actual = AsciiEncoding._lookup_field_type(name='integration_time', available_fields=available_fields)
    assert desired is actual


def test_decode_ping_response():
    to_decode = b'PingResponse()\n'
    desired = DecodedExchange(name='PingResponse', values={})
    actual = AsciiEncoding.decode(exchange=Ping, contents=to_decode)
    assert actual == desired


class BinaryPing(Exchange):
    @classmethod
    def identifier(cls) -> bytes:
        return b'\x01'

    @dataclass
    class Request:
        pass

    @dataclass
    class Response:
        pass


def test_binary_encode_wrong_length():
    class WrongPing(BinaryPing):
        @classmethod
        def identifier(cls) -> bytes:
            return b'1'

    with pytest.raises(AssertionError):
        BinaryEncoding.encode(exchange=BinaryPing, is_request=False, values={})


def test_binary_encode_wrong_type():
    class WrongPing(BinaryPing):
        @classmethod
        def identifier(cls) -> str:
            return '1'

    with pytest.raises(AssertionError):
        BinaryEncoding.encode(exchange=WrongPing, is_request=False, values={})


def test_binary_encoding_bad_identifier():
    class WrongPing(BinaryPing):
        @classmethod
        def identifier(cls) -> bytes:
            return bytes([0b1000_0000])

    with pytest.raises(AssertionError):
        BinaryEncoding.encode(exchange=WrongPing, is_request=False, values={})


def test_binary_encode_ping_response():
    actual = BinaryEncoding.encode(exchange=BinaryPing, is_request=False, values={})
    desired = b'\x00\x00\x01' # Zero payload length, identifier of 1
    assert actual == desired


def test_binary_encode_ping_request():
    actual = BinaryEncoding.encode(exchange=BinaryPing, is_request=True, values={})
    desired = b'\x00\x00\x81' # Zero payload length, identifier of 1
    assert actual == desired


def test_binary_encode_measure_voltage():
    class MeasureVoltageBinary(MeasureVoltage):
        @classmethod
        def identifier(cls):
            return b'\x02'

    values = {'channel': 25, 'integration_time': 1.05}
    actual = BinaryEncoding.encode(exchange=MeasureVoltageBinary, is_request=True, values=values)

    desired_num_bytes = b'\x0A\x00'
    assert actual[0:2] == desired_num_bytes

    desired_identifier = b'\x82'
    assert actual[2:3] == desired_identifier

    desired_int_signifier = BinaryEncoding.argument_signifiers[int]
    assert actual[3:4] == desired_int_signifier

    desired_int_payload = b'\x19\x00\x00\x00'
    assert actual[4:8] == desired_int_payload

    desired_float_signifier = BinaryEncoding.argument_signifiers[float]
    assert actual[8:9] == desired_float_signifier

    desired_float_payload = struct.pack('<f', values['integration_time'])
    assert actual[9:13] == desired_float_payload

    assert len(actual) == 13

def test_binary_decode():
    pass

def test_binary_autoencode():
    pass

