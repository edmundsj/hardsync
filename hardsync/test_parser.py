from hardsync.parser import arg_string, encode_args, encode, decode_args, lookup_field_type, decode
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
    actual = arg_string(input_string)
    assert actual == desired


def test_encode_args():
    values = {'arg1': 4, 'arg2': 'hello'}
    desired = 'arg1=4,arg2=hello'
    actual = encode_args(exchange=MeasureVoltage, values=values)
    assert actual == desired


def test_encode_full():
    values = {'arg1': 4, 'arg2': 'hello'}
    desired = 'MeasureVoltageRequest(arg1=4,arg2=hello)'
    actual = encode(exchange=MeasureVoltage, values=values, request=True)
    assert actual == desired


def test_decode_args():
    to_decode = 'MeasureVoltageRequest(channel=4,integration_time=0.5)'
    desired = {'channel': 4, 'integration_time': 0.5}
    actual = decode_args(request_response=to_decode, exchange=MeasureVoltage)
    assert actual == desired


def test_decode():
    to_decode = 'MeasureVoltageRequest(channel=4,integration_time=0.5)'
    desired = {'channel': 4, 'integration_time': 0.5}
    actual = decode(request_response=to_decode, exchange=MeasureVoltage)
    assert actual == desired


def test_lookup_field_type():
    available_fields = fields(MeasureVoltage.Request)
    desired = float
    actual = lookup_field_type(name='integration_time', available_fields=available_fields)
    assert desired is actual
