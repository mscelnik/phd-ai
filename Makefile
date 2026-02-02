.PHONY: setup test lint format clean docs help

help:
	@echo "Available targets:"
	@echo "  setup   - Install dependencies and set up development environment"
	@echo "  test    - Run all tests"
	@echo "  lint    - Run linting checks"
	@echo "  format  - Format code with black and isort"
	@echo "  clean   - Clean build artifacts"
	@echo "  docs    - Build documentation"

setup:
	python -m venv .venv
	. .venv/bin/activate && pip install --upgrade pip
	. .venv/bin/activate && pip install -e ".[dev]"
	@echo "Setup complete. Activate with: source .venv/bin/activate"

test:
	. .venv/bin/activate && pytest tests/ -v

test-unit:
	. .venv/bin/activate && pytest tests/unit/ -v

test-integration:
	. .venv/bin/activate && pytest tests/integration/ -v -m integration

test-e2e:
	. .venv/bin/activate && pytest tests/e2e/ -v -m e2e

test-cov:
	. .venv/bin/activate && pytest tests/ --cov=src --cov-report=html --cov-report=term

lint:
	. .venv/bin/activate && ruff check src/ tests/
	. .venv/bin/activate && mypy src/

format:
	. .venv/bin/activate && black src/ tests/
	. .venv/bin/activate && isort src/ tests/

clean:
	rm -rf build/ dist/ *.egg-info .pytest_cache/ .mypy_cache/ .coverage htmlcov/
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

docs:
	. .venv/bin/activate && cd docs && make html

run-example:
	. .venv/bin/activate && python -m nanoparticle_simulator.cli examples/premixed_flame.yaml

verify:
	@echo "Running full verification..."
	$(MAKE) lint
	$(MAKE) test
	@echo "All checks passed!"
