from typing import Type, Mapping, Dict, Collection, Any
from hardsync.interfaces import Encoding, Exchange
from hardsync.types import FieldNotFoundError, ResponseValues, DecodedExchange, Stringable
from dataclasses import Field, fields
import struct


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


# Here's the fundamental problem with binary encoding. Either we make the transmitted and received arguments purely
# positional, in which case they must be of fixed length, or we make them variable, in which case we need a way of
# separating them. It's not obvious to me how to do this, when the binary-encoded stuff can take any value.
# The argument beginner and enders are easy - we just don't need them. Our encoding identifier can simply be a
# single- or two-byte sequence, and our exchange terminator has to be a longer sequence.
# The problem with this is that we can't enforce a single schema. How does JSON get binary-encoded?
# Looks like protobufs solve this by adding the type in the message itself. Perhaps this is what I have instead of
# the name of the argument. Have its type. Each type should have a pre-defined length, with the exception of strings,
# which will need to have a variable length and will need to be handled separately. For the time being, we could just
# prevent strings from being used in binary encodings and I think for most people that would be acceptable.
class BinaryEncoding(Encoding):
    argument_beginner = b''
    argument_ender = b''
    argument_assigner = b''
    argument_delimiter = b''
    exchange_terminator = b'\0\n\r'
    argument_signifiers = {
        float: b'1',
        int: b'2',
    }
    argument_formats = {
        float: 'f',
        int: 'i',
    }
    exchange_identifier_bytes = 2

    @staticmethod
    def encode(exchange: Type[Exchange], values: Mapping, is_request: bool) -> bytes:
        if len(exchange.identifier()) != BinaryEncoding.exchange_identifier_bytes:
            raise AssertionError("Exchange identifier must be exactly two bytes")
        if type(exchange.identifier()) is not bytes:
            raise AssertionError("Exchange identifier must have type bytes")

        arg_bytes = BinaryEncoding._encode_args(exchange=exchange, values=values, is_request=is_request)
        return exchange.identifier() + arg_bytes + BinaryEncoding.exchange_terminator

    @staticmethod
    def _encode_args(exchange: Type[Exchange], is_request: bool, values: Mapping[str, Any]):
        if is_request:
            request_fields = fields(exchange.Request)
        else:
            request_fields = fields(exchange.Response)

        arg_bytes = b''

        for field in request_fields:
            if field.type not in BinaryEncoding.argument_formats.keys():
                raise AssertionError(f"Cannot handle binary field type {field.type}.")

            fmt = BinaryEncoding.argument_formats[field.type]
            arg_bytes += BinaryEncoding.argument_signifiers[field.type]

            binary_representation = struct.pack(fmt, values[field.name])
            arg_bytes += binary_representation

        return arg_bytes

    def decode(exchange: Type[Exchange], contents: bytes) -> DecodedExchange:
        pass