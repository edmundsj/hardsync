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
    Serial.print("PingResponse()");
    Serial.print(EXCHANGE_TERMINATOR);
}

// {{wrapper_implementations}}

void Client::unidentifiedCommand(String command_name) {
    Serial.print("ErrorResponse(msg=Unidentified command: ");
    Serial.print(command_name);
    Serial.print(ARGUMENT_ENDER);
    Serial.print(EXCHANGE_TERMINATOR);
}

void Client::badCommandFormat(String message) {
    Serial.print("ErrorResponse");
    Serial.print(ARGUMENT_BEGINNER);
    Serial.print("msg");
    Serial.print(ARGUMENT_ASSIGNER);
    Serial.print("Unable to parse command. Message should be of format XXXRequest(key=val). Raw message received: ");
    Serial.print(message);
    Serial.print(ARGUMENT_ENDER);
    Serial.print(EXCHANGE_TERMINATOR);
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
