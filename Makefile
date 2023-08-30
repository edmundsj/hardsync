AVR_TARGETS = arduino:avr
.PHONY: test
.PHONY: clean
.PHONY: install

publish: build
	poetry publish

build: sync
	poetry build

test: clean
	poetry run pytest
	poetry run python -m hardsync --contract hardsync/example/contract.py
	arduino-cli compile --fqbn arduino:avr:uno generated/firmware

sync:
	poetry run python sync.py --hash $$(git rev-parse HEAD)  # updates the version and hash

clean:
	rm -rf generated

install:
	curl -sSL https://install.python-poetry.org | python3 -
	poetry install
	mkdir -p ~/.local/bin
	curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | BINDIR=~/.local/bin sh
	arduino-cli core install $(AVR_TARGETS)

