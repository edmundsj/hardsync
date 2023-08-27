#define MAX_ARGS 10
#include <WString.h>

#ifndef Parser
#define Parser

struct Argument {
    String key;
    String value;
};

struct ParsedFunction {
    String name;
    Argument arguments[MAX_ARGS];
    int argCount;
};
struct Argument;
struct ParsedFunction;


ParsedFunction parseFunction(const String& input);
String extractName(const String& input);
String extractArgs(const String& input);

#endif
