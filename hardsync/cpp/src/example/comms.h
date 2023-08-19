#ifndef BASE_COMMUNICATION_CLIENT_H
#define BASE_COMMUNICATION_CLIENT_H

#include "Arduino.h"
#include "parser.h"

class BaseCommunicationClient {
public:
    // Constructor
    BaseCommunicationClient();

    // Virtual destructor to ensure proper cleanup for derived classes
    virtual ~BaseCommunicationClient();

    // Virtual method to measure voltage
    virtual double measureVoltage() const = 0;
    virtual String identify() const;

    void begin();
    void measureVoltageWrapper();
    void identifyWrapper();
    void unidentifiedCommand(String command_name);
    void badCommandFormat(String message);
    void checkMessage();
};

#endif
