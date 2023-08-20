from typing import Mapping, Protocol, Dict, Type, Collection
from hardsync.contracts import Exchange
from dataclasses import fields, Field


class Stringable(Protocol):
    def __str__(self) -> str:
        pass


class FieldNotFoundError(Exception):
    pass


DEFAULT_ARGUMENT_DELIMITER = ','
DEFAULT_ARGUMENT_ASSIGNER = '='


def encode(exchange: Type[Exchange], values: Mapping[str, Stringable | str], request=True):
    encoded_args = encode_args(exchange=exchange, values=values)
    if request:
        r = 'Request'
    else:
        r = 'Response'
    encoded_function = exchange.__name__ + r
    return encoded_function + '(' + encoded_args + ')'


def encode_args(exchange: Type[Exchange], values: Mapping[str, Stringable | str]) -> str:
    encoded_args = ''
    for key, val in values.items():
        encoded_args += f'{key}={val},'
    encoded_args = encoded_args.removesuffix(',')
    return encoded_args


def arg_string(request_response: str) -> str:
    start = request_response.index('(')
    stop = request_response.index(')')
    return request_response[start+1:stop]


def lookup_field_type(name: str, available_fields: Collection[Field]):
    for field in available_fields:
        if field.name == name:
            return field.type
    raise FieldNotFoundError('Could not find field {name} in exchange')


def decode_args(exchange: Type[Exchange], request_response: str, request=True) -> Dict[str, Stringable | str]:
    inner_string = arg_string(request_response=request_response)
    args = inner_string.split(DEFAULT_ARGUMENT_DELIMITER)
    values = {}
    if request:
        decode_fields = fields(exchange.Request)
    else:
        decode_fields = fields(exchange.Response)

    for arg in args:
        key, value = arg.split(DEFAULT_ARGUMENT_ASSIGNER)
        target_type = lookup_field_type(name=key, available_fields=decode_fields)
        values[key] = target_type(value)

    return values


def decode(exchange: Type[Exchange], request_response: str) -> Dict[str, Stringable | str]:
    decoded_args = decode_args(request_response=request_response, exchange=exchange)
    return decoded_args
