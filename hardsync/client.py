from dataclasses import is_dataclass
from typing import TypeVar, Type
from hardsync.channel import Channel
from contracts import Encoding, Exchange

T = TypeVar('T')


class DeviceNotFoundError(Exception):
    pass


class BaseClient:
    """
    Each client-side BaseDevice implementation needs to be coupled to the
    device-side implementation. Well, we have a basic implementation on the client-side
    that I think could work, now let's see if we can write some arduino code that could work.
    """

    @staticmethod
    def request(request_values: T, exchange: Type[Exchange], channel: Channel) -> T:
        if not is_dataclass(request_values):
            raise ValueError("The provided object is not a dataclass instance.")

        encoding = exchange.Encoding
        encoded_representation = encoding.encode(exchange=exchange, values=request_values, is_request=True)
        with channel.open() as ch:
            ch.write(data=encoded_representation)
            contents = ch.read_until(expected=encoding.exchange_terminator)
            return encoding.decode(exchange=exchange, contents=contents)