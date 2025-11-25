.PHONY: help setup install install-dev test test-cov clean clean-cache clean-output run run-sample format lint type-check pre-commit docker-build docker-run docs

# Variables
PYTHON := python
PIP := pip
VENV := venv
SRC := src
TESTS := tests
OUTPUT := output
CACHE := cache

# Colors for terminal output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(GREEN)Skill Taxonomy Pipeline - Make Commands$(NC)"
	@echo ""
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'

setup: ## Set up development environment from scratch
	@echo "$(GREEN)Setting up development environment...$(NC)"
	$(PYTHON) -m venv $(VENV)
	./$(VENV)/bin/$(PIP) install --upgrade pip setuptools wheel
	./$(VENV)/bin/$(PIP) install -r requirements.txt
	./$(VENV)/bin/$(PIP) install -r requirements-dev.txt
	./$(VENV)/bin/$(PYTHON) -m spacy download en_core_web_sm
	@mkdir -p $(OUTPUT) $(CACHE) data/raw data/processed data/sample
	@echo "$(GREEN)Setup complete! Activate venv with: source $(VENV)/bin/activate$(NC)"

install: ## Install production dependencies
	@echo "$(GREEN)Installing production dependencies...$(NC)"
	$(PIP) install -r requirements.txt
	$(PYTHON) -m spacy download en_core_web_sm

install-dev: ## Install development dependencies
	@echo "$(GREEN)Installing development dependencies...$(NC)"
	$(PIP) install -r requirements-dev.txt

test: ## Run all tests
	@echo "$(GREEN)Running tests...$(NC)"
	pytest $(TESTS) -v

test-cov: ## Run tests with coverage report
	@echo "$(GREEN)Running tests with coverage...$(NC)"
	pytest $(TESTS) -v --cov=$(SRC) --cov-report=html --cov-report=term

test-unit: ## Run unit tests only
	@echo "$(GREEN)Running unit tests...$(NC)"
	pytest $(TESTS)/unit -v

test-integration: ## Run integration tests only
	@echo "$(GREEN)Running integration tests...$(NC)"
	pytest $(TESTS)/integration -v

clean: clean-cache clean-output ## Clean all generated files
	@echo "$(GREEN)Cleaning all generated files...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache htmlcov .coverage *.egg-info build dist
	@echo "$(GREEN)Clean complete!$(NC)"

clean-cache: ## Clean cache directory
	@echo "$(YELLOW)Cleaning cache directory...$(NC)"
	rm -rf $(CACHE)/*

clean-output: ## Clean output directory
	@echo "$(YELLOW)Cleaning output directory...$(NC)"
	rm -rf $(OUTPUT)/*

run: ## Run the pipeline with sample data
	@echo "$(GREEN)Running pipeline with sample data...$(NC)"
	$(PYTHON) example_usage.py

run-sample: ## Run pipeline with small sample (quick test)
	@echo "$(GREEN)Running pipeline with small sample...$(NC)"
	$(PYTHON) main.py data/sample/sample_skills.csv -o $(OUTPUT)/sample --sample 100

run-full: ## Run full pipeline (requires data/raw/skills.csv)
	@echo "$(GREEN)Running full pipeline...$(NC)"
	$(PYTHON) main.py data/raw/skills.csv -o $(OUTPUT)/full

format: ## Format code with black and isort
	@echo "$(GREEN)Formatting code...$(NC)"
	black $(SRC) $(TESTS) *.py
	isort $(SRC) $(TESTS) *.py

lint: ## Run linting with pylint and flake8
	@echo "$(GREEN)Running linters...$(NC)"
	pylint $(SRC)
	flake8 $(SRC) --max-line-length=100 --ignore=E203,W503

type-check: ## Run type checking with mypy
	@echo "$(GREEN)Running type checking...$(NC)"
	mypy $(SRC) --ignore-missing-imports

pre-commit: format lint type-check test ## Run all pre-commit checks
	@echo "$(GREEN)All pre-commit checks passed!$(NC)"

docker-build: ## Build Docker image
	@echo "$(GREEN)Building Docker image...$(NC)"
	docker build -t skill-taxonomy-pipeline .

docker-run: ## Run pipeline in Docker container
	@echo "$(GREEN)Running pipeline in Docker...$(NC)"
	docker-compose up

docs: ## Generate documentation
	@echo "$(GREEN)Generating documentation...$(NC)"
	sphinx-build -b html docs docs/_build/html

notebook: ## Start Jupyter notebook server
	@echo "$(GREEN)Starting Jupyter notebook...$(NC)"
	jupyter notebook notebooks/

profile: ## Profile the pipeline execution
	@echo "$(GREEN)Profiling pipeline execution...$(NC)"
	$(PYTHON) -m cProfile -o profile.stats main.py data/sample/sample_skills.csv -o $(OUTPUT)/profile --sample 100
	$(PYTHON) -c "import pstats; p = pstats.Stats('profile.stats'); p.sort_stats('cumulative').print_stats(20)"

validate-data: ## Validate input data format
	@echo "$(GREEN)Validating data format...$(NC)"
	$(PYTHON) scripts/validate_data.py data/raw/skills.csv

download-models: ## Download required models
	@echo "$(GREEN)Downloading required models...$(NC)"
	$(PYTHON) scripts/download_models.py

check-env: ## Check environment and dependencies
	@echo "$(GREEN)Checking environment...$(NC)"
	@which $(PYTHON) || echo "$(RED)Python not found$(NC)"
	@$(PYTHON) --version
	@$(PIP) --version
	@echo ""
	@echo "$(YELLOW)Checking key dependencies:$(NC)"
	@$(PYTHON) -c "import pandas; print(f'  ✓ pandas {pandas.__version__}')" 2>/dev/null || echo "  $(RED)✗ pandas not installed$(NC)"
	@$(PYTHON) -c "import numpy; print(f'  ✓ numpy {numpy.__version__}')" 2>/dev/null || echo "  $(RED)✗ numpy not installed$(NC)"
	@$(PYTHON) -c "import sentence_transformers; print(f'  ✓ sentence-transformers {sentence_transformers.__version__}')" 2>/dev/null || echo "  $(RED)✗ sentence-transformers not installed$(NC)"
	@$(PYTHON) -c "import hdbscan; print('  ✓ hdbscan installed')" 2>/dev/null || echo "  $(RED)✗ hdbscan not installed$(NC)"
	@$(PYTHON) -c "import umap; print('  ✓ umap installed')" 2>/dev/null || echo "  $(RED)✗ umap not installed$(NC)"
	@$(PYTHON) -c "import openai; print(f'  ✓ openai {openai.__version__}')" 2>/dev/null || echo "  $(RED)✗ openai not installed$(NC)"

watch-logs: ## Watch pipeline logs in real-time
	@echo "$(GREEN)Watching logs...$(NC)"
	tail -f taxonomy_pipeline.log
