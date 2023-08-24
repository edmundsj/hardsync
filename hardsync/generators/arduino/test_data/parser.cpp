#include <WString.h>
#include "parser.h"

Encoding ascii_encoding = Encoding("(", ")", "=", ",", "\n");


String extractName(const String& input) {
    String result;
    int start = 0;
    int end = input.indexOf(ascii_encoding.argument_beginner);
    if (end == -1) {
        return result;
    }
    result = input.substring(start, start + end);
    return result;
}

String extractArgs(const String& input) {
    int start = input.indexOf(ascii_encoding.argument_beginner);
    int end = input.indexOf(ascii_encoding.argument_ender);

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
    while ((eqPos = args.indexOf(ascii_encoding.argument_assigner, argStart)) != -1) {
        argEnd = args.indexOf(ascii_encoding.argument_delimiter, argStart);
        if (argEnd == -1) {
            argEnd = args.length();
        }
        length = argEnd - argStart;

        String arg = args.substring(argStart, argStart + length);
        if (eqPos == -1) {
            return result;
        }
        eqPos = arg.indexOf(ascii_encoding.argument_assigner);
        result.arguments[result.argCount].key = arg.substring(0, 0 + eqPos);
        result.arguments[result.argCount].value = arg.substring(eqPos + 1);
        result.argCount++;

        argStart = argEnd + 1;
  }

  return result;
}

int extractInt(ParsedFunction* parsed_function, String arg_name) {
    for (int i = 0; i < MAX_ARGS; i++) {
        if (parsed_function->arguments[i].key == arg_name) {
            return parsed_function->arguments[i].value.toInt();
        }
    }
    return -1;
}

double extractDouble(ParsedFunction* parsed_function, String arg_name) {
    for (int i = 0; i < MAX_ARGS; i++) {
        if (parsed_function->arguments[i].key == arg_name) {
            return parsed_function->arguments[i].value.toDouble();
        }
    }
    return -1.0;
}

float extractFloat(ParsedFunction* parsed_function, String arg_name) {
    for (int i = 0; i < MAX_ARGS; i++) {
        if (parsed_function->arguments[i].key == arg_name) {
            return parsed_function->arguments[i].value.toFloat();
        }
    }
    return -1.0;
}

String extractString(ParsedFunction* parsed_function, String arg_name) {
    for (int i = 0; i < MAX_ARGS; i++) {
        if (parsed_function->arguments[i].key == arg_name) {
            return parsed_function->arguments[i].value;
        }
    }
    return "";

}
