setup:
	python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt

test:
	pytest tests/

lint:
	flake8 src/

format:
	black src/ tests/
