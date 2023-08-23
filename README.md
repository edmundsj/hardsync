# Hardsync
## Disclaimer
This software is currently under development, and is not yet in a working state. See below in the "Remaining for MVP" section to see what remains to be done. I expect it to be in a working state by 08/27/23 and complete the week after that. If you are feeling the pain so much that you want to use it right now, realize there will likely be bugs you will encounter and need to fix (and when you do, please submit an Issue on this repository)

## What problem is this solving?
Traditionally, when developing embedded applications, the software and firmware are developed separately. Often, the most time-consuming piece of the entire process is deciding on and implementing a communication protocol between the software and embedded device.

Projects like Firmata aim to solve this, but because of its domain-specific architecture, it is severely limited in the applications it can serve.

## How hardsync solves this
Hardsync attempts to solve this with a different approach. Instead of writing one set of code on your target 
embedded system (for example, an Arduino) and one set of code on your computer to communicate with the Arduino write a *single* contract and then dynamically generate code which you can import from your firmware and software that handles all the communication for you.

You no longer have to worry about encodings, termination characters, error handling, device discovery, or any of the 
other painful, repetitive, and stupid things about communicating with embedded systems. Hardsync handles all this 
for you, so you can focus on what matters - your application code.

## What is a contract?
A contract is a dead-simple python file that states the requests you want to send to your embedded system, and the 
responses you expect to receive, with their types:
```
class MeasureVoltage:
    class Request:
        channel: int
        integration_time: float
        samples: int
    class Response:
        voltage: float
```
That's it. That's all the code you have to write for two-way communication between your embedded system and your PC. 
Hardsync takes care of the rest. It uses reasonable defaults everywhere possible to enable this. And if you want to 
get into the nitty-gritty, Hardsync lets you do that too. Want to specify a specific baud rate? Device serial number?
Want all of your integers to be only 8 bits wide and unsigned? We've got you covered.

### Supported Targets
All targets are support both on the client- and device- side. That being said, the `cpp`, and `arduino` targets are 
intended to be used on the device-side, and the `python` target is intended to be used on the client side.
- `cpp`
- `arduino`
- `python`

## Design philosophy
1. Pervasive reasonable defaults for batteries-included operation
1. Total flexibility - users should be able to override virtually everything.
1. Absolute simplicity - users should be able to specificy the minimum amount of information to get their application working, not be beholden to the framework
1. Testing, testing, testing. Everything should be rigorously, repeatedly, and completely tested.

## Architecture
This library is based on simple request/response-based communication. The *client* - this can be the device OR your 
computer, sends a *request* to the *server* (which can be either your PC or your device), and the server returns a 
*response*. This request-response communication is referred to as an *exchange*, and it is the *exchanges* that are 
the most important element of your contract.


## Remaining (for MVP)
- Fix bugs in generated device arduino code
- Add generated client-side code
- Add "ping" default request/response to firmware + client code
- Add "ping"-based auto-discovery of serial devices
- Separate server and client implementations on both ends
- Add Getting started flow for how to actually use it
- Fix code generation so that it generates in the current directory, not the module directory.
- Add example with how to override baud rate and device serial number
- Add "Channel" class to allow users to override baud rate
- Add "Config" class to allow users to override serial number 
- Publish package to PyPi
- Set up CI for automatic testing and publishing to PyPi

## Future (non-MVP)
- Heavy post-decorating contract validation to ensure that it meets all downstream requirements
- More tests to verify edge cases, especially around type conversion and multiple arguments
- Support for streaming / listening
- Add generated code testing and verification
- Add example of how to add an additional target to the framework
- Support for sending requests from the device to the software
- Support for overriding device implementation (see below)
- Figure out how to check if generated code compiles.
- "time" types
- Support for multiple response fields
- Variable-size arrays in requests and responses
- Fixed-size arrays in requests and responses
- Casting of non-string request types when received by device
- Support specifying the output directories with a config file in a project
- Add @asciiencoding, @utf8encoding, and @binaryencoding decorators
- Add header with number of transmitted bytes as option with @validate_transmission wrapper
- Add @jsonencoding decorator and implementation
- Add @retryable decorator and implementation to Exchange class
- Add retries on non-error response.
- Add optional timeouts
- Support for binary encoding
- Client-side async support
- Add a hash of the contract and the `hardsync` codebase in a comment in all generated code for complete traceability
- Add verilog target
- Add VHDL target
- Add support for default values in contract, make these optional kwargs with defaults

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
We hope to! I've made it as simple as possible to support a new platform, and I plan to provide specific instructions on how to onboard new platforms that are not currently supported. If you need help onboarding a specific platform, submit an issue on this repository. If you work for a company, feel free to reach out directly if you want better support - I'm happy to provide paid support.

### Why did you open-source this library?
Partly because I hate closed-source tools that try to solve the same problem (I'm looking at you LabView). Partly 
because I myself heavily use open-source libraries. And partly for the street cred ;)

### Where does the name come from?
`hard`: this stands for hardware, but it also implies strictness through using *contracts*. `sync` is for synchronization - firmware and software for communication fundamentally require and manipulate the same underlying information, and should be in sync with each other. The mechanism to synchronize the two is the *contract*.

### How did you come up with the idea?
In dealing with embedded systems for the last decade, I became acutely aware of the pain points people using them experience. I always hated LabView, and always wished there was an easier way to co-develop hardware and firmware. It wasn't until after I took a job as a web developer that I was exposed to many of the concepts underlying this framework, and I borrow heavily from web development in it. It also wasn't until I worked at Meta that I discovered the idea of *interface description languages*, such as Thrift, which aim to solve this problem for process-to-process communication. These three factors conspired together to give me the idea for this framework.

### Why are contracts written in python? Why not YAML or JSON or just plain text?
1. Programming languages are powerful, and python is perhaps the most powerful programming language in existence. Its dynamic programming capabilities make defining contracts in a python file fairly straightforward, and having a contract defined directly in a programming language allows for overriding and specifying functionality at a level that would simply not be possible in any text-based format.
1. It has minimalist syntax similar to YAML. The language doesn't get in the way of the concepts being expressed.
1. It is the most accessible language on the planet. Far fewer people know YAML than know python.


### How does hardsync handle communication setup?
Hardync, by default, assumes that your device can communicate over a serial interface. All devices running the hardsync firmware will respond to a `PingRequest()` with a `PingResponse()`, and so hardsync attepmts to open available serial devices until it finds one that responds with the expected response. Unless you override it, the baud rate is set to 9600. If you know your device's serial number, you can specify it in your contract to avoid hardsync attempting to open other serial ports.
