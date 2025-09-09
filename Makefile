# Makefile for LLM Assistant Telegram Bot

.PHONY: help build run stop clean test lint install dev-setup

# Default target
help:
	@echo "Available commands:"
	@echo "  help        - Show this help message"
	@echo "  install     - Install dependencies"
	@echo "  dev-setup   - Setup development environment"
	@echo "  run         - Run bot locally"
	@echo "  build       - Build Docker image"
	@echo "  up          - Start with docker-compose"
	@echo "  down        - Stop docker-compose"
	@echo "  logs        - Show docker logs"
	@echo "  test        - Run tests"
	@echo "  lint        - Run linting"
	@echo "  clean       - Clean up containers and images"

# Development setup
install:
	pip install -r requirements.txt

dev-setup: install
	@echo "Development environment setup complete"
	@echo "Don't forget to create .env file with your tokens!"

# Local development
run:
	python main.py

# Docker commands
build:
	docker build -t llm-telegram-bot .

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f bot

restart:
	docker-compose restart bot

# Testing and quality
test:
	pytest tests/ -v

lint:
	python -m py_compile *.py modules/*.py
	@echo "Basic syntax check completed"

# Cleanup
clean:
	docker-compose down --volumes --remove-orphans
	docker rmi llm-telegram-bot || true
	docker system prune -f

# Production deployment
deploy: build
	docker-compose up -d --force-recreate

# Health check
health:
	docker-compose exec bot python -c "print('Bot container is healthy')"


