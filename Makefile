# Deliberately minimal: two targets, as an example of the pattern (a "get me set up"
# target and a "prove it works" target), not a wrapper around every command in the
# project. Everything else — training, evaluating, the demo, linting, tests — is run
# directly (see README.md's Quick start / Development sections for the exact
# commands); add more targets here only if your team actually wants the shortcut.

PYTHON ?= python3.13
VENV   := .venv
BIN    := $(VENV)/bin

.PHONY: setup reproduce

setup: ## Create .venv, install runtime+dev deps and this package, install pre-commit hooks
	$(PYTHON) -m venv $(VENV)
	$(BIN)/pip install --upgrade pip
	$(BIN)/pip install -r requirements.txt -r requirements-dev.txt
	$(BIN)/pip install -e .
	$(BIN)/pre-commit install

reproduce: ## data -> train -> evaluate; prints the same metric as README.md's results table
	$(BIN)/python scripts/download_data.py
	$(BIN)/python -m wine_origin train
	$(BIN)/python -m wine_origin evaluate
