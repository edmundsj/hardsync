#define MAX_ARGS 10
#ifndef ENCODING_H
#define ENCODING_H

class Encoding {
public:
    const String argument_beginner;
    const String argument_ender;
    const String argument_assigner;
    const String argument_delimiter;
    const String exchange_ender;

    Encoding(
        String argument_beginner,
        String argument_ender,
        String argument_assigner,
        String argument_delimiter,
        String exchange_ender
    ): argument_beginner(argument_beginner), argument_ender(argument_ender), argument_assigner(argument_assigner),
    argument_delimiter(argument_delimiter), exchange_ender(exchange_ender) {}
};

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
