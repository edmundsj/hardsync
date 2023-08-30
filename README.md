# Hardsync

## What problem is this solving?
Traditionally, when developing embedded applications, the software and firmware are developed separately. Often, the most time-consuming piece of the entire process is deciding on and implementing a communication protocol between the software and embedded device.

## How hardsync solves this
Hardsync attempts to solve this with a different approach. Instead of writing one set of code on your target embedded system (for example, an Arduino) and one set of code on your computer to communicate with the Arduino, you write a *single* contract and then dynamically generate code which you can import from your firmware and software that handles all the communication for you.

You no longer have to worry about encodings, termination characters, error handling, device discovery, or any of the other painful, repetitive, and stupid things about communicating with embedded systems. Hardsync handles all this for you, so you can focus on what matters - your application code.

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
python -m hardsync --contract path/to/your/contract.py
```

By default, the generated code will be placed in a folder called `generated` inside your current directory. You can override this by specifying the `--generated-dir` option like so:

```
python -m hardsync --contract path/to/your/contract.py --generated-dir path/to/your/directory
```

On the device-side, you now need to upload the generated firmware to your device. This is located in a `firmware` folder inside your `generated` directory. How you incorporate and upload this code will depend on your target. 

### Arduino
The generated `firmware` folder contains a full sketch that can simply be uploaded to the device. In the main `firmware.ino` file, you will see something near the top of the file like this:
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

### Device discovery
Once you upload the firmware, you can automatically discover your device using hardsync's built in device discovery tools:

```
python3 -m hardsync discover
```

And you can ask hardsync to keep track of this device's identity for future use. If you work with multiple devices, that's fine too. Hardsync will fall back to auto-discovery if no device identity is specified.

### Interacting with your device from an application

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
When re-generating code, make sure to run `hardsync` from the same directory if you want to overwrite previously-generated files. For safety reasons, by default, hardsync will not overwrite your main sketch or your main application. To override this behavior, simply add the `--force` flag.

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

## Examples
### Overriding the default baud rate
The default baud rate is set to 9600 to provide a minimum working configuration. If you need faster communication, you can specify that in your contract using the special `Channel` class. For example, if you wanted to set the baud rate to 115200, you would add the following anywhere in your contract:

```
class Channel:
    baud_rate = 115200
```
NOTE: Baud rates cannot be an arbitrary number, but must be one of the standard commonly-supported baud rates. 

## Feature Request
This library is under active development. If you have a feature request, or want to change the priority of planned features (see below), submit an issue on this repository.

## Planned features (in order of priority)
- Add ability to override default baud rate
- Add example with how to override baud rate
- Support for device-initiated request/response pairs
- Support for fixed-size arrays in requests and responses
- Support for binary encoding
- Add channel.write wrapper around Serial.print statements to reduce dynamic memory, Serial library flexibility
- Support for multiple response fields
- Variable-size arrays in requests and responses
- Break out config into separate config.py module, heavily test
- Add example with how to override device serial number
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
- Change the size of the C++ Arguments array to be specific to the number of arguments actually present.

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
1. It has minimalist syntax similar to YAML. The language does a remarkable job of "staying out of the way" and letting users express their intent.
1. It is the most accessible language on the planet. Far fewer people know YAML than know python.


### How does hardsync handle communication setup?
Hardync, by default, assumes that your device can communicate over a serial interface. All devices running the hardsync firmware will respond to a `PingRequest()` with a `PingResponse()`, and so hardsync attepmts to open available serial devices until it finds one that responds with the expected response. Unless you override it, the baud rate is set to 9600. If you know your device's serial number, you can specify it in your contract to avoid hardsync attempting to open other serial ports.

### Why don't I put my device serial number in the contract?
Initially, this was the plan - everything required for communication from host to device would be included in the contract. This adds a bit of reliability and predcitability when you are working with a single device. However, this has a few serious drawbacks. The first is that contracts tied to a single device, and can't be shared between people working on the same type of hardware, or identical clones of the same piece of hardware. The second issue is that it wouldn't be possible to run multiple devices on the same system using the same contract, which is a common use-case. The final issue is more fundamental - a contract should specify the *interface* between a host and device, and ideally is not specific to a *particular* host or *particular* device. So long as they have the required libraries, it should work. For this reason, I decided the best option is to pass in the device identifier (serial number) at runtime. If one is not passed in, the auto-discovery mechanism will attempt to find a device.
