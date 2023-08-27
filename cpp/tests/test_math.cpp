// test_math.cpp

#include <gtest/gtest.h>
#include "math.h"

TEST(MathTest, PositiveNos) {
    EXPECT_EQ(2, add(1, 1));
    EXPECT_EQ(6, add(3, 3));
}

TEST(MathTest, NegativeNos) {
    EXPECT_EQ(-2, add(-1, -1));
    EXPECT_EQ(0, add(-1, 1));
}

int main(int argc, char **argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
