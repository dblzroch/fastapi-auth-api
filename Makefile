.PHONY: install test lint format migrate

install:
	uv sync --dev

test:
	uv run pytest

lint:
	uv run ruff check
	uv run ruff format --check
	uv run mypy .

format:
	uv run ruff format
	uv run ruff check --fix

migrate:
	uv run alembic upgrade head
