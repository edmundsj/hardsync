#include "client.h"
#include "parser.h"

#define ARGUMENT_BEGINNER "("
#define ARGUMENT_ENDER ")"
#define ARGUMENT_DELIMITER ","
#define ARGUMENT_ASSIGNER ","
#define EXCHANGE_TERMINATOR "\n"

Client::Client() = default;

Client::~Client() = default;


void Client::begin() {
    Serial.begin(9600);
}

void Client::pingWrapper() const {
    String response = encode({}, 0, "Ping", false);
    Serial.print(response);
}

// {{wrapper_implementations}}
// {{request_implementations}}

void Client::unidentifiedCommand(String command_name) {
    Argument args[1] = {{"msg", "Unidentified command" + command_name}};
    String response = encode(args, 1, "Error", false);
    Serial.print(response);
}

void Client::badCommandFormat(String message) {
    String response = encode({}, 0, "Error", false);
    Serial.print(response);
}

void Client::respond() {
    if (Serial.available()) {
        String message = Serial.readStringUntil('\n');
        ParsedFunction fn = parseFunction(message);

        if (fn.name == "PingRequest") {
            this->pingWrapper();
        // {{respond_invocations}}
        } else if (fn.name == "") {
            this->badCommandFormat(message);
        } else {
            this->unidentifiedCommand(fn.name);
        }
    }
}
