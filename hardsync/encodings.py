from typing import Type, Mapping, Dict, Collection, Any, Optional
from hardsync.interfaces import Encoding, Exchange
from hardsync.types import FieldNotFoundError, ResponseValues, DecodedExchange, Stringable, bidict
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


# DEFAULT ENCODING
# payload bytes [2 bytes] + request/response identifier [1 byte] + argument payload [>2 bytes]
# Exmaple: two arguments, one four-byte integer and one four-byte floating point number
# Total length: 13 bytes
# Payload length: 11 bytes
# Payload header length: 2 bytes (1 + 1)
# Payload data length: 8 bytes (4 + 4)
# Header: 0x00_0B (payload of 11 bytes)
# Identifier: 0b1000_0001 (this is a request, indicated by a leading 1, with identifier of 1)
# Payload: 0b0000_0001 [4 bytes for floating-point number] 0b0000_0010 [4 bytes for integer]
# Compared to the equivalent ASCII encoding, this is about 4x more byte efficient.
# TODO: Handle things which are not little-endian.

class BinaryEncoding(Encoding):
    argument_beginner = b''
    argument_ender = b''
    argument_assigner = b''
    argument_delimiter = b''
    exchange_terminator = b''
    is_request_mask = 0b1000_0000
    argument_signifiers = {
        float: b'1',
        int: b'2',
        str: b'3',
    }
    argument_signifiers_inverse = {
        b'1': float,
        b'2': int,
        b'3': str,
    }
    argument_formats = {
        float: 'f',
        int: 'i',
    }
    exchange_identifier_bytes = 1

    @staticmethod
    def encode(exchange: Type[Exchange], values: Mapping[str, Any], is_request: bool) -> bytes:
        BinaryEncoding._validate(exchange=exchange, is_request=is_request, values=values)

        header = BinaryEncoding._header(exchange=exchange, is_request=is_request, values=values)
        arg_bytes = BinaryEncoding._encode_args(exchange=exchange, is_request=is_request, values=values)
        identifier = BinaryEncoding._identifier(exchange=exchange, is_request=is_request)

        return header + identifier + arg_bytes

    @staticmethod
    def _validate(exchange: Type[Exchange], values: Mapping[str, Any], is_request: bool):
        if len(exchange.identifier()) != BinaryEncoding.exchange_identifier_bytes:
            raise AssertionError(f"Exchange identifier must be exactly {BinaryEncoding.exchange_identifier_bytes} byte(s)")
        if type(exchange.identifier()) is not bytes:
            raise AssertionError("Exchange identifier must have type bytes")
        exchange_identifier_int = int.from_bytes(exchange.identifier(), byteorder='little')
        if exchange_identifier_int & BinaryEncoding.is_request_mask != 0:
            raise AssertionError("Exchange identifier must not overlap with request identifier bitmask")

    @staticmethod
    def _identifier(exchange: Type[Exchange], is_request: bool):
        identifier = int.from_bytes(exchange.identifier(), byteorder='little')
        if is_request:
            identifier |= BinaryEncoding.is_request_mask

        return bytes([identifier])

    @staticmethod
    def _header(exchange: Type[Exchange], values: Mapping, is_request: bool):
        arg_bytes = BinaryEncoding._encode_args(exchange=exchange, values=values, is_request=is_request)
        header = struct.pack('<H', len(arg_bytes))
        return header

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

    @staticmethod
    def decode(exchange_map: Mapping[bytes, Type[Exchange]], contents: bytes) -> DecodedExchange:
        if len(contents) < 3:
            raise AssertionError("Cannot decode fewer than 3 bytes. Violates binary encoding.")

        length = struct.unpack('<H', contents[0:2])
        actual_length = len(contents) - 3
        if actual_length != length:
            raise AssertionError(f"Expected number of bytes {length} less than actual number of bytes {actual_length}")

        exchange_bytes = contents[2:3]
        is_request = BinaryEncoding._is_request(exchange_bytes=exchange_bytes)

        exchange_id = bytes([int.from_bytes(exchange_bytes, byteorder='little') & ~BinaryEncoding.is_request_mask])
        exchange = exchange_map[exchange_id]

        name = 'Exchange'
        if is_request:
            name += "Request"
        else:
            name += "Response"

        if actual_length > 3:
            payload = contents[3:]
        else:
            payload = b''

        response_vals = BinaryEncoding._decode_args(exchange=exchange, contents=payload, return_vals=None)
        return DecodedExchange(name=name, values=response_vals)

    @staticmethod
    def _is_request(exchange_bytes: bytes):
        return int.from_bytes(exchange_bytes, byteorder='little') | BinaryEncoding.is_request_mask

    @staticmethod
    def _decode_args(exchange: Type[Exchange], contents: bytes, return_vals: Optional[Mapping] = None) -> ResponseValues:
        if return_vals is None:
            return_vals = {}

        next_arg_signifier = contents[0:1]
        arg_type = BinaryEncoding.argument_signifiers_inverse[next_arg_signifier]
        arg_format = BinaryEncoding.argument_formats[arg_type]

        required_bytes = struct.calcsize(arg_format)
        end_index = required_bytes + 1
        next_arg_bytes = contents[1:end_index]

        arg_value = struct.unpack(arg_format, next_arg_bytes)
        # TODO: WE NEED TO LOOK UP THE EXCHANGE FIELD NAME FROM THE EXCHANGE GIVEN ITS POSITION
        return_vals['exchange_field_name'] = arg_value

        if len(contents) == end_index:
            return return_vals

        BinaryEncoding._decode_args(exchange=exchange, contents=contents[end_index:], return_vals=return_vals)

