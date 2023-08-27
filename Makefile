.PHONY: test
.PHONY: clean
.PHONY: install

test: clean
	poetry run pytest
	poetry run python -m hardsync hardsync/example/contract.py
	arduino-cli compile --fqbn arduino:avr:uno generated/firmware

clean:
	rm -rf generated

install:
	curl -sSL https://install.python-poetry.org | python3 -
	poetry install
	mkdir -p ~/.local/bin
	curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | BINDIR=~/.local/bin sh

