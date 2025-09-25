PYTHON:=/Users/irfan/Development/Projects/dev_twin/venv/bin/python
PIP:=/Users/irfan/Development/Projects/dev_twin/venv/bin/pip

.PHONY: install dev run

install:
	$(PIP) install -r requirements.txt

run:
	$(PYTHON) -m uvicorn app.main:app --host 0.0.0.0 --port 8000

dev:
	$(PYTHON) scripts/dev.py
