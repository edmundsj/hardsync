from dataclasses import is_dataclass, dataclass
from typing import TypeVar, Type, Mapping, Dict, Any
from hardsync.interfaces import Channel, Exchange, DecodedExchange, ReceivedErrorResponse, Encoding, Client
from contextlib import contextmanager

T = TypeVar('T')


class DeviceNotFoundError(Exception):
    pass


@dataclass
class BaseClient(Client):
    """
    Each client-side BaseDevice implementation needs to be coupled to the
    device-side implementation. Well, we have a basic implementation on the client-side
    that I think could work, now let's see if we can write some arduino code that could work.
    """
    channel: Channel
    encoding: Type[Encoding]

    def request(self, request_values: Mapping, exchange: Type[Exchange]) -> DecodedExchange:
        encoded_representation = self.encoding.encode(exchange=exchange, values=request_values, is_request=True)

        with self.channel.open() as ch:
            ch.write(data=encoded_representation)
            contents = ch.read_until(expected=self.encoding.exchange_terminator)
            decoded_contents = self.encoding.decode(exchange=exchange, contents=contents)

            if decoded_contents.name == 'ErrorResponse':
                raise ReceivedErrorResponse(f'Received Error response. Full response contents {contents}')
            return decoded_contents

    # to be overriden by a wrapper.
    @contextmanager
    def listen(self) -> None:
        yield self.channel.open()


