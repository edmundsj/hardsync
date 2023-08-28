#include <WString.h>
#include "parser.h"

String extractName(const String& input) {
    String result;
    int start = 0;
    int end = input.indexOf(ARGUMENT_BEGINNER);
    if (end == -1) {
        return result;
    }
    result = input.substring(start, start + end);
    return result;
}

String extractArgs(const String& input) {
    int start = input.indexOf(ARGUMENT_BEGINNER);
    int end = input.indexOf(ARGUMENT_ENDER);

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
    while ((eqPos = args.indexOf(ARGUMENT_ASSIGNER, argStart)) != -1) {
        argEnd = args.indexOf(ARGUMENT_DELIMITER, argStart);
        if (argEnd == -1) {
            argEnd = args.length();
        }
        length = argEnd - argStart;

        String arg = args.substring(argStart, argStart + length);
        if (eqPos == -1) {
            return result;
        }
        eqPos = arg.indexOf(ARGUMENT_ASSIGNER);
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

String encode(Argument *args, int len, String name, bool is_request) {
    String return_string = "";
    if (is_request == true) {
        return_string += name + "Request" + ARGUMENT_BEGINNER;
    } else {
        return_string += name + "Response" + ARGUMENT_BEGINNER;
    }
    for (int i = 0; i < len; i++) {
        return_string += args[i].key + ARGUMENT_ASSIGNER + args[i].value;
        if (i < len - 1) {
            return_string += ARGUMENT_DELIMITER;
        }
    }
    return_string += ARGUMENT_ENDER;
    return_string += EXCHANGE_TERMINATOR;
    return return_string;
}