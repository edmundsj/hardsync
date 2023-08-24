#include <WString.h>
#include "parser.h"

String extractName(const String& input) {
    String result;
    int start = 0;
    int end = input.indexOf('(');
    if (end == -1) {
        return result;
    }
    result = input.substring(start, start + end);
    return result;
}

String extractArgs(const String& input) {
    int start = input.indexOf('(');
    int end = input.indexOf(')');

    String result;
    if (start == -1 || end == -1) {
        return result;
    }
    int count = end - start - 1;
    result = input.substring(start + 1, start + 1 + count);
    return result;
}

ParsedFunction parseFunction(const String& input) {
    ParsedFunction result;
    result.argCount = 0;

    result.name = extractName(input);

    String args = extractArgs(input);

    int argStart = 0;
    int argEnd;
    int eqPos;
    int length;
    while ((eqPos = args.indexOf('=', argStart)) != -1) {
        argEnd = args.indexOf(',', argStart);
        if (argEnd == -1) {
            argEnd = args.length();
        }
        length = argEnd - argStart;

        String arg = args.substring(argStart, argStart + length);
        if (eqPos == -1) {
            return result;
        }
        eqPos = arg.indexOf('=');
        result.arguments[result.argCount].key = arg.substring(0, 0 + eqPos);
        result.arguments[result.argCount].value = arg.substring(eqPos + 1);
        result.argCount++;

        argStart = argEnd + 1;
  }

  return result;
}
