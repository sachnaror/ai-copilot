.PHONY: poet install lint test run dev dev-open open evaluate ingest docker-build docker-run

POETRY ?= poetry
APP_MODULE ?= app.main:app
HOST ?= 127.0.0.1
PORT ?= 8000

poet:
	bash ./poet_install_make_dev.sh

install:
	$(POETRY) config --local virtualenvs.in-project true
	$(POETRY) install

lint:
	$(POETRY) run ruff check app scripts

test:
	$(POETRY) run pytest

run:
	$(POETRY) run uvicorn $(APP_MODULE) --host $(HOST) --port $(PORT)

dev:
	$(POETRY) run uvicorn $(APP_MODULE) --reload --host $(HOST) --port $(PORT)

dev-open:
	(sleep 2 && $(POETRY) run python -m webbrowser http://$(HOST):$(PORT)/) & \
	$(POETRY) run uvicorn $(APP_MODULE) --reload --host $(HOST) --port $(PORT)

open:
	$(POETRY) run python -m webbrowser http://$(HOST):$(PORT)/

evaluate:
	$(POETRY) run python scripts/evaluate.py

ingest:
	$(POETRY) run python scripts/ingest.py

docker-build:
	docker build -t enterprise-ai-copilot:local .

docker-run:
	docker run --rm -p 8000:8000 --env-file .env enterprise-ai-copilot:local
