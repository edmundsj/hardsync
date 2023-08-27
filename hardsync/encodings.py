from typing import Type, Mapping, Dict, Collection
from hardsync.interfaces import Encoding, Exchange
from hardsync.types import FieldNotFoundError, ResponseValues, DecodedExchange, Stringable
from dataclasses import Field, fields


class AsciiEncoding(Encoding):
    argument_delimiter = ','
    argument_beginner = '('
    argument_ender = ')'
    argument_assigner = '='
    exchange_terminator = "\n"

    @staticmethod
    def encode(exchange: Type[Exchange], values: Mapping[str, Stringable | str], is_request=True) -> bytes:
        encoded_args = AsciiEncoding._encode_args(exchange=exchange, values=values)
        if is_request:
            r = 'Request'
        else:
            r = 'Response'
        encoded_function = exchange.identifier() + r
        encoded_string = encoded_function + '(' + encoded_args + ')' + AsciiEncoding.exchange_terminator
        return encoded_string.encode('ascii')

    @staticmethod
    def decode(exchange: Type[Exchange], contents: bytes) -> DecodedExchange:
        decoded_str = contents.decode('ascii')
        decoded_args = AsciiEncoding._decode_args(contents=decoded_str, exchange=exchange)
        decoded_name = AsciiEncoding._decode_name(contents=decoded_str)
        return DecodedExchange(name=decoded_name, values=decoded_args)

    @staticmethod
    def _encode_args(exchange: Type[Exchange], values: Mapping[str, Stringable | str]) -> str:
        encoded_args = ''
        for key, val in values.items():
            encoded_args += f'{key}{AsciiEncoding.argument_assigner}{val}{AsciiEncoding.argument_delimiter}'
        encoded_args = encoded_args.removesuffix(AsciiEncoding.argument_delimiter)
        return encoded_args

    @staticmethod
    def _arg_string(contents: str) -> str:
        start = contents.index(AsciiEncoding.argument_beginner)
        stop = contents.index(AsciiEncoding.argument_ender)
        return contents[start+1:stop]

    @staticmethod
    def _decode_args(exchange: Type[Exchange], contents: str, request=True) -> Dict[str, Stringable | str]:
        inner_string = AsciiEncoding._arg_string(contents=contents)
        args = inner_string.split(AsciiEncoding.argument_delimiter) if inner_string else []
        values = {}
        if request:
            decode_fields = fields(exchange.Request)
        else:
            decode_fields = fields(exchange.Response)

        for arg in args:
            key, value = arg.split(AsciiEncoding.argument_assigner)
            target_type = AsciiEncoding._lookup_field_type(name=key, available_fields=decode_fields)
            values[key] = target_type(value)

        return values

    @staticmethod
    def _lookup_field_type(name: str, available_fields: Collection[Field]):
        for field in available_fields:
            if field.name == name:
                return field.type
        raise FieldNotFoundError('Could not find field {name} in exchange')

    @staticmethod
    def _decode_name(contents: str) -> str:
        end = contents.index(AsciiEncoding.argument_beginner)
        return contents[:end]

