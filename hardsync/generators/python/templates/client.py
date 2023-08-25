from dataclasses import dataclass
from typing import TypeVar, Type
from hardsync.interfaces import Channel, Exchange, DecodedExchange, Encoding
from hardsync.clients import BaseClient
from hardsync.channels import SerialChannel
from hardsync.encodings import AsciiEncoding

T = TypeVar('T')

# channel = SerialChannel(baud_rate=9600, channel_identifier='')
# For now, we support only a single channel
# {{channel}}


class Ping(Exchange):
    @dataclass
    class Request:
        pass

    @dataclass
    class Response:
        pass


# {{exchange_definitions}}
@dataclass
class Client(BaseClient):
    channel: Channel = SerialChannel(baud_rate=9600, channel_identifier='')
    encoding: Type[Encoding] = AsciiEncoding

    def request_ping(self) -> DecodedExchange:
        return self.request({}, exchange=Ping)

    # {{request_definitions}}

