PYTHON := .\\venv\\Scripts\\python
PIP := .\\venv\\Scripts\\pip
MANAGE := $(PYTHON) manage.py
IMAGE := smartseason-backend
CONTAINER := smartseason-backend

.PHONY: help install migrate makemigrations createsuperuser shell run test check docker-build docker-run docker-stop

help:
	@echo Available targets:
	@echo   make install         - Install Python dependencies
	@echo   make migrate         - Apply database migrations
	@echo   make makemigrations  - Create migrations from model changes
	@echo   make createsuperuser - Create Django superuser
	@echo   make shell           - Open Django shell
	@echo   make run             - Run development server on port 8000
	@echo   make test            - Run Django tests
	@echo   make check           - Run Django system checks
	@echo   make docker-build    - Build Docker image
	@echo   make docker-run      - Run app container with .env and port 8000
	@echo   make docker-stop     - Stop and remove running app container

install:
	$(PIP) install -r requirements.txt

migrate:
	$(MANAGE) migrate

makemigrations:
	$(MANAGE) makemigrations

createsuperuser:
	$(MANAGE) createsuperuser

shell:
	$(MANAGE) shell

run:
	$(MANAGE) runserver

test:
	$(MANAGE) test

check:
	$(MANAGE) check

docker-build:
	docker build -t $(IMAGE) .

docker-run:
	docker run --rm --name $(CONTAINER) -p 8000:8000 --env-file .env $(IMAGE)

docker-stop:
	docker stop $(CONTAINER)
