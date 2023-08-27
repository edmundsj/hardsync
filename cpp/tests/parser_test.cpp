#include <gtest/gtest.h>
#include "parser.h"


TEST(ParseZeroArguments, BasicAssertions) {
    ParsedFunction parsed = parseFunction("identify()");
    EXPECT_EQ(parsed.name, "identify");
    EXPECT_EQ(parsed.argCount, 0);
}

std::string ZERO_ARG_COMMAND="identify()";
std::string SINGLE_ARG_COMMAND="measure_voltage(channel=1)";
std::string DOUBLE_ARG_COMMAND = "measure_current(channel=2,integration_time=0.5)";


TEST(ParseOneArgumentName, BasicAssertions) {
    std::string name = extractName(SINGLE_ARG_COMMAND);
    EXPECT_EQ(name, "measure_voltage");
}

TEST(ParseTwoArgumentNames, basicAssertion) {
    std::string name = extractName(DOUBLE_ARG_COMMAND);
    EXPECT_EQ(name, "measure_current");
}

TEST(ExtractZeroArgumentArgs, basicAssertion) {
    std::string args = extractArgs(ZERO_ARG_COMMAND);
    EXPECT_EQ(args, "");
}

TEST(ExtractOneArgumentArgs, basicAssertion) {
    std::string args = extractArgs(SINGLE_ARG_COMMAND);
    EXPECT_EQ(args, "channel=1");
}

TEST(ExtractTwoArgumentArgs, basicAssertion) {
    std::string args = extractArgs(DOUBLE_ARG_COMMAND);
    EXPECT_EQ(args, "channel=2,integration_time=0.5");
}

TEST(ParseOneArgumentNumberArgs, BasicAssertions) {
    ParsedFunction parsed = parseFunction(SINGLE_ARG_COMMAND);
    EXPECT_EQ(parsed.argCount, 1);
}

TEST(ParseOneArgumentArgName, BasicAssertions) {
    ParsedFunction parsed = parseFunction(SINGLE_ARG_COMMAND);
    EXPECT_EQ(parsed.arguments[0].key, "channel");
}

TEST(ParseOneArgumentArgValue, BasicAssertions) {
    ParsedFunction parsed = parseFunction(SINGLE_ARG_COMMAND);
    EXPECT_EQ(parsed.arguments[0].value, "1");
}


TEST(ParseTwoArgumentNumberArgs, BasicAssertions) {
    ParsedFunction parsed = parseFunction(DOUBLE_ARG_COMMAND);
    EXPECT_EQ(parsed.argCount, 2);
}

TEST(ParseTwoArgumentArgName, BasicAssertions) {
    ParsedFunction parsed = parseFunction(DOUBLE_ARG_COMMAND);
    EXPECT_EQ(parsed.arguments[1].key, "integration_time");
}

TEST(ParseTwoArgumentArgValue, BasicAssertions) {
    ParsedFunction parsed = parseFunction(DOUBLE_ARG_COMMAND);
    EXPECT_EQ(parsed.arguments[1].value, "0.5");
}


