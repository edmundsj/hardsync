#ifndef BASE_COMMUNICATION_CLIENT_H
#define BASE_COMMUNICATION_CLIENT_H

#include "Arduino.h"
#include "parser.h"
#include <string>

class BaseCommunicationClient {
public:
    // Constructor
    BaseCommunicationClient();

    // Virtual destructor to ensure proper cleanup for derived classes
    virtual ~BaseCommunicationClient();

    virtual std::string identify() const;
    void identifyWrapper() const;
    virtual double measureVoltage(int channel, double integration_time);
    void measureVoltageWrapper(int channel, double integration_time);


    void begin();
    void unidentifiedCommand(String command_name);
    void badCommandFormat(String message);
    void checkMessage();
};

#endif
