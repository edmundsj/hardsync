# Here's the question - does it make more sense to expose a set of functions, or a
# Here's the first question, do we open and close a serial connection dynamically, or open it once and keep it open?
# For maximum flexibility, initially I say we open it and then close at the end of communication, but we can change that in the future. Perhaps the device itself could be a context manager.

from dataclasses import is_dataclass, dataclass
from typing import TypeVar, Type, Dict
from hardsync.interfaces import Channel, Exchange, Stringable
from hardsync.client import BaseClient
from hardsync.channels import SerialChannel
from hardsync.encodings import AsciiEncoding

T = TypeVar('T')


channel = SerialChannel(baud_rate=9600, channel_identifier='') # Unknown channel identifier


class Ping(Exchange):
    @dataclass
    class Request:
        pass

    @dataclass
    class Response:
        pass


# A fully-qualified and explicit version of the contract
class MeasureVoltage(Exchange):
    class Encoding(AsciiEncoding):
        pass

    @dataclass
    class Request:
        integration_time: float
        channel: int

    @dataclass
    class Response:
        voltage: float


# This code should be auto-generated. It probably needs to know the channel
@dataclass
class Client(BaseClient):
    channel: Channel = SerialChannel(baud_rate=9600, channel_identifier='')

    def request_ping(self) -> Dict[str, Stringable]:
        return self.request({}, exchange=Ping, channel=channel)

    def request_measure_voltage(self, channel: int, integration_time: float) -> float:
        values = self.request(
            request_values={'channel': channel, 'integration_time': integration_time},
            channel=self.channel,
            exchange=MeasureVoltage,
        )
        return values['voltage']

