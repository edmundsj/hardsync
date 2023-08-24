#define MAX_ARGS 10

struct Encoding {
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
}

struct Argument {
    std::string key;
    std::string value;
};

struct ParsedFunction {
    std::string name;
    Argument arguments[MAX_ARGS];
    int argCount;
};

ParsedFunction parseFunction(const std::string& input);
std::string extractName(const std::string& input);
std::string extractArgs(const std::string& input);
int measureVoltageExtractChannel(ParsedFunction* parsed_function);
double measureVoltageExtractIntegrationTime(ParsedFunction* parsed_function);
