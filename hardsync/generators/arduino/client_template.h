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
    virtual std::string identify() const;
    void identifyWrapper() const;
    // {{virtual_declarations}}
    // {{wrapper_declarations}}
    virtual ~BaseCommunicationClient();

    void begin();
    void unidentifiedCommand(String command_name);
    void badCommandFormat(String message);
    void checkMessage();
};

#endif
