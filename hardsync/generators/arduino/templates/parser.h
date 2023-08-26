#define MAX_ARGS 10
#ifndef ENCODING_H
#define ENCODING_H

#define ARGUMENT_BEGINNER "("
#define ARGUMENT_ENDER ")"
#define ARGUMENT_DELIMITER ","
#define ARGUMENT_ASSIGNER ","
#define EXCHANGE_TERMINATOR "\n"

struct Argument {
    String key;
    String value;
};

struct ParsedFunction {
    String name;
    Argument arguments[MAX_ARGS];
    int argCount;
};

ParsedFunction parseFunction(const String& input);
String extractName(const String& input);
String extractArgs(const String& input);
int extractInt(ParsedFunction* parsed_function, String arg_name);
double extractDouble(ParsedFunction* parsed_function, String arg_name);
float extractFloat(ParsedFunction* parsed_function, String arg_name);
String extractString(ParsedFunction* parsed_function, String arg_name);

#endif
