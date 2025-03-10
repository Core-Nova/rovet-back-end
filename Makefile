.PHONY: help build up down logs ps test lint format migrate seed shell restart clean monitoring

help:
	@echo "Available commands:"
	@echo "  build        Build all Docker containers"
	@echo "  up           Start all containers in detached mode"
	@echo "  down         Stop all containers"
	@echo "  logs         View container logs"
	@echo "  ps           List running containers"
	@echo "  test         Run tests"
	@echo "  lint         Run linting checks"
	@echo "  format       Format code using black and isort"
	@echo "  migrate      Run database migrations"
	@echo "  seed         Seed the database with initial data"
	@echo "  shell        Open a shell in the API container"
	@echo "  restart      Restart all containers"
	@echo "  clean        Remove all containers and volumes"
	@echo "  monitoring   Open Grafana monitoring dashboard"

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

ps:
	docker-compose ps

test:
	docker-compose exec api poetry run pytest

lint:
	docker-compose exec api poetry run flake8 app
	docker-compose exec api poetry run black --check app
	docker-compose exec api poetry run isort --check-only app

format:
	docker-compose exec api poetry run black app
	docker-compose exec api poetry run isort app

migrate:
	docker-compose exec api poetry run alembic upgrade head

seed:
	docker-compose exec api poetry run python -m app.scripts.seed_db

shell:
	docker-compose exec api sh

restart:
	docker-compose restart

clean:
	docker-compose down -v
	docker system prune -f

monitoring:
	@echo "Opening Grafana dashboard at http://localhost:3000"
	@echo "Default credentials: admin/admin"
	@open http://localhost:3000 