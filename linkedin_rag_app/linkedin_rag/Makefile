.PHONY: run test install shell dev entity

run:
	uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

install:
	uv venv && uv pip install -e .

test:
	uv run pytest

shell:
	uv run ipython

dev:
	uv run fastforge run

entity:
	fastforge make:entity $(name) $(fields)

dbt-run:
	uv run --env-file .env dbt run --project-dir src/analytics --profiles-dir src/analytics