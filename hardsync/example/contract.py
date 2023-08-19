# Simple "hello world" contract. 
# How should errors be handled?
# How should bi-directional communication be handled?
# The vanilla python language might not do this very well

# What do I need to define?
# - The type of requests / responses that can be sent back and forth
# OK, now how would I actually implement something like this on the software side and 
# on the hardware side?

from dataclasses import dataclass

@dataclass
class IdentifyRequest:
    pass

@dataclass
class IdentifyResponse:
    response: str


@dataclass
class MeasureVoltageRequest:
    integration_time: int
    channel: int


@dataclass
class MeasureVoltageResponse:
    voltage: float


# The desired generated client-side code
def identify(request: IdentifyRequest) -> IdentifyResponse:
    # Do something to communicate with the device, and wait for a response
    pass

# The desired generated device-side code
def identify(request: IdentifyRequest) -> IdentifyResponse:
    # Do something to communicate with the software and return
    pass

