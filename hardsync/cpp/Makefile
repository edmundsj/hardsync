# Variables

# Targets
all: build/test_math

build/test_math: build/math.o tests/build/test_math.o $(GTEST_LIBS)
	g++ -o $@ $^ $(LDFLAGS)

build/math.o: src/math.cpp
	g++ -c $(CPPFLAGS) $< -o $@

tests/build/test_math.o: tests/src/test_math.cpp
	g++ -c $(CPPFLAGS) $< -o $@

$(GTEST_LIBS):
	mkdir -p $(GTEST_BUILD_DIR) && cd $(GTEST_BUILD_DIR) && cmake .. && make

test: 
	cmake -S . -B build
	cmake --build build
	cd build && ctest --verbose

clean:
	rm -rf build

