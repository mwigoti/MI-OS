.PHONY: help setup build up down logs migrate superuser test check clean shell

help:
	@echo "MwohaOS Management Commands:"
	@echo "  make setup       - Initialize .env, build containers, run migrations, and prompt for superuser"
	@echo "  make build       - Build all Docker service images"
	@echo "  make up          - Start all Docker services in background"
	@echo "  make down        - Stop and remove all Docker containers"
	@echo "  make logs        - Follow Docker container logs"
	@echo "  make migrate     - Run Django database migrations"
	@echo "  make superuser   - Create Django admin superuser"
	@echo "  make test        - Run test suite with pytest"
	@echo "  make check       - Run Django system checks"
	@echo "  make shell       - Open Django interactive shell"
	@echo "  make clean       - Remove caches and build artifacts"

setup:
	@if [ ! -f .env ]; then cp .env.example .env && echo "[MwohaOS] Created .env from .env.example"; fi
	docker compose build
	docker compose up -d postgres redis
	@echo "[MwohaOS] Waiting for databases to become healthy..."
	docker compose up -d web celery celery-beat
	docker compose exec web python manage.py migrate
	@echo "[MwohaOS] Setup complete! Run 'make superuser' to create your admin account."

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

migrate:
	docker compose exec web python manage.py migrate

superuser:
	docker compose exec web python manage.py createsuperuser

test:
	docker compose exec web pytest

check:
	docker compose exec web python manage.py check

shell:
	docker compose exec web python manage.py shell

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage htmlcov staticfiles
