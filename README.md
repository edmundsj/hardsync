# Hardsync

## What problem is this solving?
Traditionally, when developing embedded applications, the software and firmware are developed separately. Often, the most time-consuming piece of the entire process is deciding on and implementing a communication protocol between the software and embedded device.

Projects like Firmata aim to solve this, but because of its domain-specific architecture, it is severely limited in the applications it can serve.

## How hardsync solves this
Hardsync attempts to solve this with a different approach. Instead of writing one set of code on your target 
embedded system (for example, an Arduino) and one set of code on your computer to communicate with the Arduino write a *single* contract and then dynamically generate code which you can import from your firmware and software that handles all the communication for you.

You no longer have to worry about encodings, termination characters, error handling, device discovery, or any of the 
other painful, repetitive, and stupid things about communicating with embedded systems. Hardsync handles all this 
for you, so you can focus on what matters - your application code.

## Getting Started
### Install hardsync
First, you will need to install hardsync. The easiest way is via `pip`
```
pip install hardsync
```
### Write your first contract

What is a contract? A contract is a dead-simple python file that states the requests you want to send to your embedded system, and the responses you expect to receive, with their types:
```
class MeasureVoltage:
    class Request:
        channel: int
        integration_time: float
        samples: int
    class Response:
        voltage: float
```
Once you have your contract, run the hardsync code generator to create your device-side firmware and computer-side client you will use to interact with your device:

```
python -m hardsync path/to/your/contract.py
```

By default, the generated code will be placed in a folder called `generated` inside your current directory. You can override this by specifying the `--generated-dir` option like so:

```
python -m hardsync path/to/your/contract.py --generated-dir path/to/your/directory
```

On the device-side, you now need to upload the generated firmware to your device. This is located in a `firmware` folder inside your `generated` directory. How you incorporate and upload this code will depend on your target. 

### Arduino
The generated `device` folder contains a full sketch that can simply be uploaded to the device. In the main `sketch.ino` file, you will see something near the top of the file like this:
```
class DeviceClient : public BaseDeviceClient {
public: 
    double measureVoltage() const override {
        // YOUR measureVoltage CODE GOES HERE
    }
}
```
This is where you put the code that actually measures the voltage. For example, if measuring from one of the arduino's analog pins, you might replace `//YOUR CODE GOES HERE` with:
```
double DEVICE_VOLTAGE = 3.3;
double MAXIMUM_ANALOG_VALUE = 1024.0;
int analog_value = analogRead(A0);
double voltage = DEVICE_VOLTAGE * analog_value / MAXIMUM_ANALOG_VALUE;
return voltage;
```

To create a program that interacts with the device, import the generated code:
```
from generated.client import Client
client = Client()

response = client.request_voltage(channel=1, integration_time=0.5)
voltage = response.values['voltage']
print(voltage)
```


Now, running this program will have the python code communicate with the arduino, make it run the `measureVoltage()` code you specified, and communicate with the arduino to get the value returned from `measureVoltage(), and print that to the screen.`.

## Re-generating code
If you need to change your contract frequently, to minimize the amount of manual steps involved in re-generating code, we recommend that you set up a project-specific hardsync configuration file. To create a basic file for your current directory, run:

```
hardsync config
```
This creates a `hardsync.ini` file in your current directory. Here you can specify the default directories that your generated client-side and device-side code will go to. Now, when running `hardsync` from the same directory or a subdirectory as your `hardsync.ini` file, the default settings in that file will be used.

NOTE: By default, when using a `hardsync.ini` file, the main sketch for the device-side and client-side code is omitted by default, to avoid accidentally overriding it.

## Debugging
If you encounter an unexpected error and it's not immediately obvious how to fix it from the error message you received, submit a bug report on this repository. Make sure to attach the output of `hardsync dump` to the issue to help with reproducing it and identifying the issue.

## Supported Targets
All targets are support both on the client- and device- side. That being said, the `arduino` target are intended to be used on the device-side, and the `python` target is intended to be used on the host side.
- `arduino`
- `python`

## Design philosophy
1. Pervasive reasonable defaults for batteries-included operation
1. Total flexibility - users should be able to override virtually everything.
1. Absolute simplicity - users should be able to specificy the minimum amount of information to get their application working, not be beholden to the framework
1. Testing, testing, testing. Everything should be rigorously, repeatedly, and completely tested.

## Architecture
This library is based on simple request/response-based communication. The *client* - this can be the device OR your computer, sends a *request* to the *server* (which can be either your PC or your device), and the server returns a *response*. This request-response communication is referred to as an *exchange*, and it is the *exchanges* that are the most important element of your contract.

## Feature Request
This library is under active development. If you have a feature request (or want to change the priority of the features below), submit an issue on this repository.


## Remaining (for MVP)
- Add "ping"-based auto-discovery of serial devices
- [DONE] Support for user-defined type mappings, clean syntax for this
	- [DONE] Add function to get all the types used and verify they are all defined
	- [DONE] Add tests to verify this functionality
- [DONE] Add tests for zero-length requests and responses, ensure void declarations are generated
- [DONE] Fix bugs in generated device arduino code
- [DONE] Move exchange to top-level of contract
- [DONE] Fix code generation so that it generates in the current directory, not the module directory.
- [DONE] Publish package to PyPi
- [DONE] Add generated client-side code
- [DONE] Add "ping" default request/response to firmware + client code
- [DONE] Add Getting started flow for how to actually use it
- [DONE] Add "Channel" class to allow users to override baud rate, serial number

## Future (in order of priority)
- Heavy post-decorating contract validation to ensure that it meets all downstream requirements
    - Tests with good and bad contracts, verifying that everything meets specifications
- Support for device-initiate request/response pairs
- Support for fixed-size arrays in requests and responses
- Support for binary encoding
- Add channel.write wrapper around Serial.print statements to reduce program memory, Serial library flexibility
- Add example with how to override baud rate and device serial number
- Variable-size arrays in requests and responses
- Verify that generated client-side code is valid python
- Set up CI for automatic testing and publishing to PyPi
- Implement hardsync.ini file, static configuration
- Support for multi-hardsync device discovery on same machine
- More tests to verify edge cases, especially around type conversion and multiple arguments
- Multiple device channels
- Add generated code testing in sandbox environment to verify it works
- Add example of how to add an additional target to the framework
- Support for overriding device implementation (see below)
- "time" types
- Support for multiple response fields
- Casting of non-string request types when received by device
- Support specifying the output directories with a config file in a project
- Add @asciiencoding, @utf8encoding, and @binaryencoding decorators
- Add header with number of transmitted bytes as option with @validate_transmission wrapper
- Add @jsonencoding decorator and implementation
- Add @retryable decorator and implementation to Exchange class
- Add retries on non-error response.
- Add optional timeouts
- Client-side async support
- Add a hash of the contract used to generate auto-generated files
- Add verilog target
- Add VHDL target
- Add support for default values in contract, make these optional kwargs with defaults
- [DONE] Add a hash of the `hardsync` codebase in a comment in all generated code for complete traceability
- [DONE] Add the version number of hardsync used to generate files in a comment
- [DONE] Replace exceptions with ERROR logging on receiving a ErrorResponse
- [DONE] Add INFO logging for sent requests / received responses
- [DONE] Add INFO logging for generated files being written
- [DONE] Verify as part of testing that generated arduino code compiles
- [DONE] Add tests to verify that the command-line tool works as expected
- [efficiency] Change the size of the C++ Arguments array to be specific to the number of arguments actually present.

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
