#include "comms.h"

BaseCommunicationClient::BaseCommunicationClient() = default;

BaseCommunicationClient::~BaseCommunicationClient() = default;

void BaseCommunicationClient::begin() {
    Serial.begin({{baud_rate}});
}

void BaseCommunicationClient::identifyWrapper() {
    String identifier = this->identify();
    Serial.print("IdentifyResponse(serial=");
    Serial.print(identifier);
    Serial.print(")");
    Serial.print("\n");
}

{{wrapper_implementations}}

void BaseCommunicationClient::unidentifiedCommand(String command_name) {
    Serial.print("Unidentified command: ");
    Serial.print(command_name);
    Serial.print("\n");
}

void BaseCommunicationClient::badCommandFormat(String message) {
    Serial.print("Unable to parse command. Message should be of format XXXRequest(key=val). Raw message received: ");
    Serial.print(message);
    Serial.print("\n");
}

void BaseCommunicationClient::checkMessage() {
    if (Serial.available()) {
        String message = Serial.readStringUntil('\n');
        ParsedFunction fn = parseFunction(message);

        if (fn.name == "IdentifyRequest") {
            this->identifyWrapper();
        {{check_message_invocations}}
        } else if (fn.name == "") {
            this->badCommandFormat(message);
        } else {
            this->unidentifiedCommand(fn.name);
        }
    }
}
