from typing import Type, Mapping, Dict, Collection
from hardsync.contracts import Encoding, Stringable, Exchange, FieldNotFoundError
from dataclasses import Field, fields


class AsciiEncoding(Encoding):
    argument_delimiter = ','
    argument_beginner = '('
    argument_ender = ')'
    argument_assigner = '='
    exchange_terminator = "\n"

    @staticmethod
    def encode(exchange: Type[Exchange], values: Mapping[str, Stringable | str], request=True):
        encoded_args = AsciiEncoding._encode_args(exchange=exchange, values=values)
        if request:
            r = 'Request'
        else:
            r = 'Response'
        encoded_function = exchange.identifier() + r
        return encoded_function + '(' + encoded_args + ')'

    @staticmethod
    def decode(exchange: Type[Exchange], request_response: str) -> Dict[str, Stringable | str]:
        decoded_args = AsciiEncoding._decode_args(request_response=request_response, exchange=exchange)
        return decoded_args

    @staticmethod
    def _encode_args(exchange: Type[Exchange], values: Mapping[str, Stringable | str]) -> str:
        encoded_args = ''
        for key, val in values.items():
            encoded_args += f'{key}{AsciiEncoding.argument_assigner}{val}{AsciiEncoding.argument_delimiter}'
        encoded_args = encoded_args.removesuffix(AsciiEncoding.argument_delimiter)
        return encoded_args

    @staticmethod
    def _arg_string(request_response: str) -> str:
        start = request_response.index('(')
        stop = request_response.index(')')
        return request_response[start+1:stop]

    @staticmethod
    def _lookup_field_type(name: str, available_fields: Collection[Field]):
        for field in available_fields:
            if field.name == name:
                return field.type
        raise FieldNotFoundError('Could not find field {name} in exchange')

    @staticmethod
    def _decode_args(exchange: Type[Exchange], request_response: str, request=True) -> Dict[str, Stringable | str]:
        inner_string = AsciiEncoding._arg_string(request_response=request_response)
        args = inner_string.split(AsciiEncoding.argument_delimiter)
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
