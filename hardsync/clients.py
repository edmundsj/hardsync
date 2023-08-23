from dataclasses import is_dataclass, dataclass
from typing import TypeVar, Type, Mapping, Dict, Any
from hardsync.interfaces import Channel, Exchange
from contextlib import contextmanager

T = TypeVar('T')


class DeviceNotFoundError(Exception):
    pass


@dataclass
class BaseClient:
    """
    Each client-side BaseDevice implementation needs to be coupled to the
    device-side implementation. Well, we have a basic implementation on the client-side
    that I think could work, now let's see if we can write some arduino code that could work.
    """
    channel: Channel

    def request(self, request_values: Mapping, exchange: Type[Exchange]) -> Dict[str, Any]:
        encoding = exchange.Encoding
        encoded_representation = encoding.encode(exchange=exchange, values=request_values, is_request=True)
        with self.channel.open() as ch:
            ch.write(data=encoded_representation)
            contents = ch.read_until(expected=encoding.exchange_terminator)
            return encoding.decode(exchange=exchange, contents=contents)

    # to be overriden by a wrapper.
    @contextmanager
    def listen(self) -> None:
        yield self.channel.open()


