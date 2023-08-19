#include "comms.h"

BaseCommunicationClient::BaseCommunicationClient() = default;

BaseCommunicationClient::~BaseCommunicationClient() = default;

String BaseCommunicationClient::identify() const {
    // Implementation can be provided here if needed
    return "";
}

void BaseCommunicationClient::begin() {
    Serial.begin(9600);
}

void BaseCommunicationClient::measureVoltageWrapper() {
    double voltage = this->measureVoltage();
    
    // actually send the value over the serial port
    Serial.print("MeasureVoltageResponse(voltage=");
    Serial.print(voltage);
    Serial.print(")");
    Serial.print("\n");
}

void BaseCommunicationClient::identifyWrapper() {
    String identifier = this->identify();
    Serial.print("IdentifyResponse(serial=");
    Serial.print(identifier);
    Serial.print(")");
    Serial.print("\n");
}

void BaseCommunicationClient::unidentifiedCommand(String command_name) {
    Serial.print("Unidentified command: ");
    Serial.print(command_name);
    Serial.print("\n");
}

void BaseCommunicationClient::badCommandFormat(String message) {
    Serial.print("Unable to parse command. Message should be of format XXXRequest([args]). Raw message received: ");
    Serial.print(message);
    Serial.print("\n");
}

void BaseCommunicationClient::checkMessage() {
    if (Serial.available()) {
        String message = Serial.readStringUntil('\n');
        ParsedFunction fn = parseFunction(message);

        if (fn.name == "MeasureVoltageRequest") {
            this->measureVoltageWrapper();
        } else if (fn.name == "IdentifyRequest") {
            this->identifyWrapper();
        } else if (fn.name == "") {
            this->badCommandFormat(message);
        } else {
            this->unidentifiedCommand(fn.name);
        }
    }
}
