PYTHON=python
VENV=.venv
PYTHON_VENV=$(VENV)/Scripts/python.exe
PIP_VENV=$(VENV)/Scripts/pip.exe

setup:
	$(PYTHON) -m venv $(VENV)
	$(PYTHON_VENV) -m pip install --upgrade pip
	$(PIP_VENV) install -r requirements-dev.txt

test:
	$(PYTHON_VENV) -m pytest tests -q

lint:
	$(PYTHON_VENV) -m ruff check src tests

format:
	$(PYTHON_VENV) -m black src tests
