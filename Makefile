# Makefile for project setup and testing

PYTHONPATH := $(shell pwd)
export PYTHONPATH

setup:
	python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt

test:
	source .venv/bin/activate && pytest tests/

lint:
	source .venv/bin/activate && pylint src/

format:
	source .venv/bin/activate && black src/
