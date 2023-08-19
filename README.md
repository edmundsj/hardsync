# Hardsync

## What problem is this solving?
Traditionally, when developing embedded applications, the software and firmware are developed separately. Often, the most time-consuming piece of the entire process is deciding on and implementing a communication protocol between the software and embedded device.

Projects like Firmata aim to solve this, but because of its domain-specific architecture, it is severely limited in the applications it can serve.

## How hardsync solves this
Hardsync attempts to solve this with a different approach. Instead of writing code to communicate with the firmware, instead write a *single* contract and then dynamically generate code which you can import from your firmware and software that handles all the communication for you.

## Target platforms
The first platform we aim to support is the Arduino platform, as it has a well-developed ecosystem, and high-level libraries that allow for communication

## Target languages
The first target language we aim to support is python.

## Design philosophy
1. Borrow as much as possible from existing tooling (don't reinvent the wheel)


## Write your first contract
A hardsync contract is written in vanilla python. The reason is simple - python is popular, and why force people to learn a new language?

In this example, we have two functions we would like to be able to call from the device - `identify` and `measure_voltage`. To write the contract, we need to write what the requests and responses for each of these functions will be.

`contract.py`:
```
from dataclasses import dataclass
from typing import Optional

class Identify:
	@dataclass
	class Request:
		pass

	@dataclass
	class Response:
		response: str


class MeasureVoltage:
	@dataclass
	class Request:
		channel: int
		integration_time: Optional[float]

	@dataclass
	class Response:
		voltage: float
```
Now, to generate the code you will use, simply run `hardsync`:

```
python -m hardsync contract.py
```

This will create a set of files inside a folder called `generated`. The first of these files is `generated/client.py`. This contains your client-side code which will contain a single class called `Device`. This class will have two available methods: `identify`, which takes no arguments, and `measure_voltage`, which takes two arguments: `channel`, which is required, and `integration_time`, which is optional.

You can use this client-side code directly:


```
from generated.client import Device

device = Device()
identity = device.identify()

voltage = device.measure_voltage(channel=2, integration_time=0.5)

```
For this code to actually *do* anything, you have to also include the device-side generated code. This is also in the `generated` folder by default in a file called `device.cpp` and `device.h`. These files expose two functions: `beginCommunication()`, which is meant to be put inside your `setup()` function, and `parseCommunication()`, which should be placed inside your `void loop()` function.
```
#include "device.h"

Device device()

void identify() {
	device.identify("Hello there this is my thing")
}

float measureVoltage() {
	device.measureVoltage()
}

void setup() {
	beginCommunication()
}

void loop() {
	waitForCommunication()
}

```
We need to figure out how this will actually work. Putting communication initialization and checking is fine and good, but those functions themselves actually need to invoke user-defined functions. How do I do that? I'm not even sure that is possible. They basically need to define measureVoltage(). I need to think through how this will actually work. On the device-side, we need to check for the type of function that we want to call, and then call it from the waitForCommunication() section of the code. The user needs to provide the implementations, and may need to pass them in at compile-time to waitForCommunication() or something like that. I should just try to do a stupid implementation and then go backwards. Let's try this tomorrow.



## Architecture
This library is based on simple request/response-based communication. The software (client) sends a request to the device, and the device returns a response. 

You specify a *contract*, which is a set of *exchanges*, each of which contains a *request* and a *response*. By 
default, the request is assumed to be initiated from the computer, although support for device-initiated 
communication would be easy to add.

### Supported Targets
- `cpp` (no transpilation)
- `arduino`


## Future (non-MVP)
- Support for streaming / listening
- Support for sending requests from the device to the software
- Support for overriding device implementation (see below)
- Figure out how to check if generated code compiles.
- "time" types
- Multiple response fields
- Variable-size arrays in requests and responses
- Fixed-size arrays in requests and responses
- Casting of non-string request types when received by device
- Permit user to override default encoding per-exchange
- More tests to verify edge cases, especially around type conversion

### Overriding device implementation
By default, the `Device` class uses utf-8 (text-based) communication. This can lead to unacceptably bloated back-and-forth communication. Embedded systems requiring high speed can change the implementation to use binary-based comunication instead:

NOT YET IMPLEMENTED:
```
python -m hardsync contract.py --protocol=binary
```
Notes:
- We need to introduce the concept of an "encoding" now, to avoid massive duplication. This "encoding" can be part 
  of the Request/Response class definitions, or will default to a default one.

## FAQ
### Why generated code, and not a universal device library?
First, embedded systems (the target for this library) have extremely tight memory constraints. Because of this, a 
"universal" library that works with 
all 
microcontrollers, should it be built, would immediately be useless because it's too large for anyone to include. 
Second, even on the client side where memory is less constrained, generating code allows for total flexibility on 
the user-side should they wish to modify the code without the friction of contributing to an open-source project 
(yes, that friction is still very much a barrier to entry).
It also allows for easy integration with 
build systems.

### Why don't you support X platform?
We hope to! I've made it as simple as possible to support a new platform, and I plan to provide specific 
instructions on how to onboard new platforms that are not currently supported. If you need help onboarding a specific 
platform, submit an issue on this repository. If you work for a company, feel free to reach out 
directly if you 
want 
better support - I'm happy to provide paid support.

### Why did you open-source this library?
Partly because I hate closed-source tools that try to solve the same problem (I'm looking at you LabView). Partly 
because I myself heavily use open-source libraries. And partly for the street cred ;)