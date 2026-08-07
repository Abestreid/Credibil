.PHONY: help install dev test lint format docker-up docker-down migrate

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install all dependencies
	cd backend && uv pip install -e ".[dev]"
	cd frontend && npm install

dev: ## Start all services in development
	docker-compose up -d postgres redis meilisearch
	cd backend && uvicorn credibil.main:app --reload --host 0.0.0.0 --port 8000 &
	cd frontend && npm run dev

test: ## Run all tests
	cd backend && make test

lint: ## Run linting
	cd backend && make lint
	cd frontend && npm run lint

format: ## Format code
	cd backend && make format
	cd frontend && npm run format

docker-up: ## Start all Docker services
	docker-compose up -d

docker-down: ## Stop all Docker services
	docker-compose down

docker-build: ## Build Docker images
	docker-compose build

migrate: ## Run database migrations
	cd backend && alembic upgrade head

migration: ## Create new migration (msg="description")
	cd backend && alembic revision --autogenerate -m "$(msg)"
