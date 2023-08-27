#include <string>
#include "parser.h"

std::string extractName(const std::string& input) {
    std::string result;
    int start = 0;
    int end = input.find('(');
    if (end == -1) {
        return result;
    }
    result = input.substr(start, end);
    return result;
}

std::string extractArgs(const std::string& input) {
    int start = input.find('(');
    int end = input.find(')');
    
    std::string result;
    if (start == -1 || end == -1) {
        return result;
    }
    int count = end - start - 1;
    result = input.substr(start + 1, count);
    return result;
}

ParsedFunction parseFunction(const std::string& input) {
    ParsedFunction result;
    result.argCount = 0;

    result.name = extractName(input);

    std::string args = extractArgs(input);
  
    int argStart = 0;
    int argEnd;
    int eqPos;
    int length;
    while ((eqPos = args.find('=', argStart)) != -1) {
        argEnd = args.find(',', argStart);
        if (argEnd == -1) {
            argEnd = args.length();
        }
        length = argEnd - argStart;
    
        std::string arg = args.substr(argStart, length);
        if (eqPos == -1) {
            return result;
        }
        eqPos = arg.find('=');
        result.arguments[result.argCount].key = arg.substr(0, eqPos);
        result.arguments[result.argCount].value = arg.substr(eqPos + 1);
        result.argCount++;

        argStart = argEnd + 1;
  }

  return result;
}
