#ifndef BASE_COMMUNICATION_CLIENT_H
#define BASE_COMMUNICATION_CLIENT_H

#include "Arduino.h"
#include "parser.h"
#include <WString.h>

class Client {
public:
    // Constructor
    Client();

    // Virtual destructor to ensure proper cleanup for derived classes
    virtual ~Client();

    void pingWrapper() const;

    // {{virtual_declarations}}
    // {{wrapper_declarations}}

    void begin();
    void unidentifiedCommand(String command_name);
    void badCommandFormat(String message);
    void respond();
};

#endif
