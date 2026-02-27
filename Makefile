.PHONY: help install test lint format clean train deploy api docker-build docker-up docker-down mlflow-ui monitor

help:
	@echo "Available commands:"
	@echo "  make install       - Install dependencies"
	@echo "  make test          - Run tests"
	@echo "  make lint          - Run linting"
	@echo "  make format        - Format code"
	@echo "  make clean         - Clean artifacts"
	@echo "  make train         - Train model"
	@echo "  make deploy        - Deploy model with conditional logic"
	@echo "  make api           - Start API server"
	@echo "  make docker-build  - Build Docker image"
	@echo "  make docker-up     - Start Docker containers"
	@echo "  make docker-down   - Stop Docker containers"
	@echo "  make mlflow-ui     - Start MLflow UI"
	@echo "  make monitor       - Show model registry status"

install:
	pip install --upgrade pip
	pip install -r requirements.txt

test:
	pytest tests/ -v --cov=src --cov-report=html

lint:
	flake8 src/ tests/ --max-line-length=127
	pylint src/ --disable=C0111,R0903

format:
	black src/ tests/
	isort src/ tests/

clean:
	rm -rf __pycache__ .pytest_cache .coverage htmlcov
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

train:
	python train.py --data-path NLP-Sentiment/data/aclImdb

deploy:
	python train.py --data-path NLP-Sentiment/data/aclImdb --deploy

api:
	uvicorn src.api:app --reload --host 0.0.0.0 --port 8000

docker-build:
	docker build -t sentiment-api:latest .

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

mlflow-ui:
	mlflow ui --backend-store-uri mlruns --port 5000

monitor:
	python -m src.monitoring --action status

# Development helpers
dev-setup:
	python -m venv venv
	. venv/bin/activate && make install

quick-test:
	pytest tests/ -v -k "not slow"

coverage:
	pytest tests/ --cov=src --cov-report=term-missing

# Docker helpers
docker-logs:
	docker-compose logs -f sentiment-api

docker-shell:
	docker-compose exec sentiment-api /bin/bash

docker-clean:
	docker-compose down -v
	docker system prune -f

# MLflow helpers
mlflow-clean:
	rm -rf mlruns/ mlartifacts/

# Full pipeline
full-pipeline: clean train deploy api

# CI/CD simulation
ci: lint test docker-build
