PYTHON ?= .venv/bin/python
PIP ?= .venv/bin/pip

.PHONY: venv install generate run run-no-db test

venv:
	python3 -m venv .venv

install: venv
	$(PIP) install -r requirements.txt

generate:
	$(PYTHON) -m src.main generate

run:
	$(PYTHON) -m src.main run

run-no-db:
	$(PYTHON) -m src.main run --skip-db

test:
	$(PYTHON) -m pytest
