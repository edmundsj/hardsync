import logging
from dataclasses import is_dataclass, dataclass
from typing import TypeVar, Type, Mapping, Dict, Any
from hardsync.interfaces import Channel, Exchange, Encoding, Client
from hardsync.types import ReceivedErrorResponse, DecodedExchange
from contextlib import contextmanager

T = TypeVar('T')


class DeviceNotFoundError(Exception):
    pass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
            logger.info(f"Wrote: {encoded_representation}")
            contents = ch.read_until(expected=self.encoding.exchange_terminator)
            decoded_contents = self.encoding.decode(exchange=exchange, contents=contents)
            logger.info(f"Received: {encoded_representation}")

            if decoded_contents.name == 'ErrorResponse':
                logger.error(f"Received Error from device: {decoded_contents}")

            return decoded_contents

    # to be overriden by a wrapper.
    @contextmanager
    def listen(self) -> None:
        yield self.channel.open()


