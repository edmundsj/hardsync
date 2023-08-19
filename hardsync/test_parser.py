from hardsync.encodings import AsciiEncoding
from hardsync.contracts import Exchange
from dataclasses import dataclass, fields


class MeasureVoltage(Exchange):
    @dataclass
    class Request:
        channel: int
        integration_time: float

    @dataclass
    class Response:
        voltage: float


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
    desired = 'MeasureVoltageRequest(arg1=4,arg2=hello)'
    actual = AsciiEncoding.encode(exchange=MeasureVoltage, values=values, request=True)
    assert actual == desired


def test_decode_args():
    to_decode = 'MeasureVoltageRequest(channel=4,integration_time=0.5)'
    desired = {'channel': 4, 'integration_time': 0.5}
    actual = AsciiEncoding._decode_args(request_response=to_decode, exchange=MeasureVoltage)
    assert actual == desired


def test_decode():
    to_decode = 'MeasureVoltageRequest(channel=4,integration_time=0.5)'
    desired = {'channel': 4, 'integration_time': 0.5}
    actual = AsciiEncoding.decode(request_response=to_decode, exchange=MeasureVoltage)
    assert actual == desired


def test_lookup_field_type():
    available_fields = fields(MeasureVoltage.Request)
    desired = float
    actual = AsciiEncoding._lookup_field_type(name='integration_time', available_fields=available_fields)
    assert desired is actual
