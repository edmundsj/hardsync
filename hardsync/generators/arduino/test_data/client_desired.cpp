#include "comms.h"

#define ARGUMENT_BEGINNER "("
#define ARGUMENT_ENDER ")"
#define ARGUMENT_DELIMITER ","
#define ARGUMENT_ASSIGNER ","
#define EXCHANGE_TERMINATOR "\n"

BaseCommunicationClient::BaseCommunicationClient() = default;

BaseCommunicationClient::~BaseCommunicationClient() = default;


void BaseCommunicationClient::begin() {
    Serial.begin({{baud_rate}});
}

void BaseCommunicationClient::pingWrapper() const {
    Serial.print("PingResponse()");
    Serial.print(EXCHANGE_TERMINATOR);
}

void BaseCommunicationClient::measureVoltageWrapper(int channel, double integration_time) const {
    double voltage = this->measureVoltage(channel, integration_time);
    Serial.print("MeasureVoltageResponse");
    Serial.print(ARGUMENT_BEGINNER);
    Serial.print("voltage");
    Serial.print(ARGUMENT_ASSIGNER);
    Serial.print(voltage);
    Serial.print(ARGUMENT_ENDER);
    Serial.print(EXCHANGE_TERMINATOR);
}

void BaseCommunicationClient::unidentifiedCommand(String command_name) {
    Serial.print("ErrorResponse(msg=Unidentified command: ");
    Serial.print(command_name);
    Serial.print(ARGUMENT_ENDER);
    Serial.print(EXCHANGE_TERMINATOR);
}

void BaseCommunicationClient::badCommandFormat(String message) {
    Serial.print("ErrorResponse");
    Serial.print(ARGUMENT_BEGINNER);
    Serial.print("msg");
    Serial.print(ARGUMENT_ASSIGNER);
    Serial.print("Unable to parse command. Message should be of format XXXRequest(key=val). Raw message received: ");
    Serial.print(message);
    Serial.print(ARGUMENT_ENDER);
    Serial.print(EXCHANGE_TERMINATOR);
}

void BaseCommunicationClient::checkMessage() {
    if (Serial.available()) {
        String message = Serial.readStringUntil('\n');
        ParsedFunction fn = parseFunction(message);

        if (fn.name == "IdentifyRequest") {
            this->identifyWrapper();
        else if (fn.name == "MeasureVoltageRequest")
            int channel = measureVoltageExtractChannel(ParsedFunction)
            double integration_time = measureVoltageExtractIntegrationTime(ParsedFunction)
            this->measureVoltageWrapper(channel, integration_time)
        } else if (fn.name == "") {
            this->badCommandFormat(message);
        } else {
            this->unidentifiedCommand(fn.name);
        }
    }
}