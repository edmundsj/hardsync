from hardsync.encodings import AsciiEncoding
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
