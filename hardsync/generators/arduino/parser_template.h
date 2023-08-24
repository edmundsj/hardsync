#define MAX_ARGS 10


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
