.PHONY: install lint typecheck test test-cov run migrate migration format

install:
	uv pip install -e ".[dev]"

lint:
	ruff check src/ tests/
	ruff format --check src/ tests/

format:
	ruff check --fix src/ tests/
	ruff format src/ tests/

typecheck:
	mypy src/

test:
	python -m pytest tests/ -v

test-cov:
	python -m pytest tests/ -v --cov=credibil --cov-report=term-missing

run:
	uvicorn credibil.main:app --reload --host 0.0.0.0 --port 8000

migrate:
	alembic upgrade head

migration:
	alembic revision --autogenerate -m "$(msg)"
