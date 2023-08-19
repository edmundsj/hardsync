cmake_minimum_required(VERSION 3.14)
project(my_project)

# GoogleTest requires at least C++14
set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include(FetchContent)
FetchContent_Declare(
  googletest
  URL https://github.com/google/googletest/archive/03597a01ee50ed33e9dfd640b249b4be3799d395.zip
)
# For Windows: Prevent overriding the parent project's compiler/linker settings
set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
FetchContent_MakeAvailable(googletest)

enable_testing()

add_library(parser src/parser.cpp)

add_executable(
  hello_test
  tests/hello_test.cpp
)
add_executable(
  parser_test 
  tests/parser_test.cpp
)
target_link_libraries(
  hello_test
  GTest::gtest_main
)
target_link_libraries(
  parser_test 
  GTest::gtest_main
  parser
)

include(GoogleTest)
include_directories(${CMAKE_SOURCE_DIR}/src)

gtest_discover_tests(hello_test)
gtest_discover_tests(parser_test)
