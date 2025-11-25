# Skill Taxonomy Pipeline - Project Structure

## Recommended Folder Structure for VS Code

```
skill_taxonomy_pipeline/
│
├── .vscode/                      # VS Code configuration
│   ├── settings.json            # Project-specific settings
│   ├── launch.json              # Debug configurations
│   └── extensions.json          # Recommended extensions
│
├── src/                         # Source code (main package)
│   ├── __init__.py
│   ├── data_processing/         # Data processing module
│   │   ├── __init__.py
│   │   ├── processor.py        # Main data processor
│   │   ├── validator.py        # Data validation
│   │   └── cleaner.py          # Data cleaning utilities
│   │
│   ├── embeddings/              # Embedding generation module
│   │   ├── __init__.py
│   │   ├── embedding_manager.py # Embedding generation & caching
│   │   ├── similarity.py       # Similarity computations
│   │   └── deduplicator.py     # Deduplication logic
│   │
│   ├── clustering/              # Clustering module
│   │   ├── __init__.py
│   │   ├── hierarchical_clustering.py
│   │   ├── cluster_analyzer.py # Cluster evaluation
│   │   └── refinement.py       # Cluster refinement
│   │
│   ├── llm_integration/         # LLM integration module
│   │   ├── __init__.py
│   │   ├── openai_refiner.py   # OpenAI API integration
│   │   ├── prompts.py          # LLM prompt templates
│   │   └── validator.py        # LLM-based validation
│   │
│   ├── taxonomy_builder/        # Taxonomy construction module
│   │   ├── __init__.py
│   │   ├── builder.py          # Main taxonomy builder
│   │   ├── hierarchy.py        # Hierarchy management
│   │   └── optimizer.py        # Structure optimization
│   │
│   └── utils/                   # Utility functions
│       ├── __init__.py
│       ├── logging_config.py   # Logging configuration
│       ├── cache_manager.py    # Cache management
│       └── visualization.py    # Visualization utilities
│
├── config/                      # Configuration files
│   ├── __init__.py
│   ├── settings.py             # Main configuration
│   ├── settings.dev.py         # Development settings
│   ├── settings.prod.py        # Production settings
│   └── constants.py            # Project constants
│
├── data/                        # Data directory
│   ├── raw/                    # Raw input data
│   ├── processed/              # Processed data
│   └── sample/                 # Sample data for testing
│
├── output/                      # Output directory
│   ├── taxonomies/             # Generated taxonomies
│   ├── reports/                # Analysis reports
│   └── visualizations/         # Charts and graphs
│
├── cache/                       # Cache directory
│   ├── embeddings/             # Cached embeddings
│   ├── clustering/             # Cached clustering results
│   └── llm_cache/              # Cached LLM responses
│
├── tests/                       # Test suite
│   ├── __init__.py
│   ├── unit/                   # Unit tests
│   │   ├── test_processor.py
│   │   ├── test_embeddings.py
│   │   └── test_clustering.py
│   ├── integration/            # Integration tests
│   │   └── test_pipeline.py
│   └── fixtures/               # Test data
│       └── sample_skills.csv
│
├── notebooks/                   # Jupyter notebooks
│   ├── 01_data_exploration.ipynb
│   ├── 02_embedding_analysis.ipynb
│   ├── 03_clustering_experiments.ipynb
│   └── 04_taxonomy_visualization.ipynb
│
├── scripts/                     # Utility scripts
│   ├── setup_environment.py    # Environment setup
│   ├── download_models.py      # Download required models
│   └── validate_data.py        # Data validation script
│
├── docs/                        # Documentation
│   ├── api/                    # API documentation
│   ├── guides/                 # User guides
│   └── architecture.md         # Architecture documentation
│
├── .env.example                 # Example environment variables
├── .env                        # Environment variables (gitignored)
├── .gitignore                  # Git ignore file
├── .dockerignore               # Docker ignore file
├── .pylintrc                   # Pylint configuration
├── .pre-commit-config.yaml     # Pre-commit hooks
│
├── requirements.txt            # Production dependencies
├── requirements-dev.txt        # Development dependencies
├── setup.py                    # Package setup file
├── pyproject.toml             # Modern Python project config
│
├── main.py                     # Main pipeline entry point
├── run_pipeline.py            # CLI interface
├── example_usage.py           # Usage examples
│
├── Dockerfile                  # Docker configuration
├── docker-compose.yml         # Docker compose file
│
├── Makefile                    # Build automation
├── LICENSE                     # License file
└── README.md                   # Project documentation
```

## File Contents to Create

### 1. VS Code Settings (.vscode/settings.json)
```json
{
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "python.testing.unittestEnabled": false,
    "python.testing.pytestArgs": ["tests"],
    "python.envFile": "${workspaceFolder}/.env",
    "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    },
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        ".pytest_cache": true,
        "*.egg-info": true
    },
    "python.analysis.extraPaths": [
        "${workspaceFolder}/src"
    ]
}
```

### 2. VS Code Launch Config (.vscode/launch.json)
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Run Pipeline",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/main.py",
            "args": ["data/sample/sample_skills.csv", "-o", "output/debug"],
            "console": "integratedTerminal",
            "env": {
                "PYTHONPATH": "${workspaceFolder}"
            }
        },
        {
            "name": "Debug Current File",
            "type": "python",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal"
        },
        {
            "name": "Run Tests",
            "type": "python",
            "request": "launch",
            "module": "pytest",
            "args": ["-v", "tests/"],
            "console": "integratedTerminal"
        }
    ]
}
```

### 3. VS Code Extensions (.vscode/extensions.json)
```json
{
    "recommendations": [
        "ms-python.python",
        "ms-python.vscode-pylance",
        "ms-python.black-formatter",
        "ms-toolsai.jupyter",
        "ms-vscode.makefile-tools",
        "streetsidesoftware.code-spell-checker",
        "yzhang.markdown-all-in-one",
        "gruntfuggly.todo-tree",
        "njpwerner.autodocstring",
        "visualstudioexptteam.vscodeintellicode"
    ]
}
```

### 4. Project Configuration (pyproject.toml)
```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "skill-taxonomy-pipeline"
version = "1.0.0"
description = "A scalable pipeline for building skill taxonomies"
readme = "README.md"
requires-python = ">=3.8"
dependencies = [
    "pandas>=2.0.0",
    "numpy>=1.24.0",
    "scikit-learn>=1.3.0",
    "sentence-transformers>=2.2.0",
    "hdbscan>=0.8.33",
    "umap-learn>=0.5.4",
    "faiss-cpu>=1.7.4",
    "openai>=1.0.0",
    "tqdm>=4.65.0",
    "python-dotenv>=1.0.0"
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "black>=23.0.0",
    "pylint>=2.17.0",
    "mypy>=1.0.0",
    "pre-commit>=3.0.0"
]

[tool.black]
line-length = 100
target-version = ['py38', 'py39', 'py310', 'py311']

[tool.pylint.messages_control]
max-line-length = 100
disable = ["C0111", "R0903"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
addopts = "-v --cov=src --cov-report=html"
```

### 5. Makefile
```makefile
.PHONY: help setup install test clean run

help:
	@echo "Available commands:"
	@echo "  make setup    - Set up development environment"
	@echo "  make install  - Install dependencies"
	@echo "  make test     - Run tests"
	@echo "  make clean    - Clean cache and temporary files"
	@echo "  make run      - Run example pipeline"
	@echo "  make format   - Format code with black"
	@echo "  make lint     - Run linting"

setup:
	python -m venv venv
	./venv/bin/pip install --upgrade pip
	./venv/bin/pip install -r requirements.txt
	./venv/bin/pip install -r requirements-dev.txt
	./venv/bin/python -m spacy download en_core_web_sm

install:
	pip install -r requirements.txt

test:
	pytest tests/ -v --cov=src

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf cache/*
	rm -rf output/*

run:
	python example_usage.py

format:
	black src/ tests/ *.py

lint:
	pylint src/
	mypy src/

docker-build:
	docker build -t skill-taxonomy-pipeline .

docker-run:
	docker-compose up
```

### 6. .gitignore
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
.venv

# IDE
.vscode/
.idea/
*.swp
*.swo
.DS_Store

# Project specific
.env
cache/
output/
data/raw/*
data/processed/*
!data/sample/
*.log
*.pkl
*.npy

# Testing
.coverage
htmlcov/
.pytest_cache/
.tox/

# Documentation
docs/_build/
site/

# Distribution
build/
dist/
*.egg-info/
```

### 7. Docker Configuration (Dockerfile)
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY config/ ./config/
COPY main.py .
COPY run_pipeline.py .

# Create necessary directories
RUN mkdir -p data output cache

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["python", "main.py"]
```

## Setup Instructions for VS Code

1. **Clone/Create the project structure**:
```bash
mkdir skill_taxonomy_pipeline
cd skill_taxonomy_pipeline
```

2. **Initialize Git** (optional):
```bash
git init
```

3. **Create virtual environment**:
```bash
python -m venv venv
```

4. **Activate virtual environment**:
- Windows: `venv\Scripts\activate`
- Mac/Linux: `source venv/bin/activate`

5. **Install dependencies**:
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development
```

6. **Open in VS Code**:
```bash
code .
```

7. **Install recommended extensions** (VS Code will prompt)

8. **Configure Python interpreter**:
- Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
- Type "Python: Select Interpreter"
- Choose the interpreter from `./venv/`

## Development Workflow

1. **Start development**:
```bash
make setup  # One-time setup
make install  # Install dependencies
```

2. **Run tests**:
```bash
make test
```

3. **Format code**:
```bash
make format
```

4. **Run pipeline**:
```bash
python main.py data/your_skills.csv -o output/
```

5. **Debug in VS Code**:
- Set breakpoints in code
- Press `F5` to run with debugger
- Use debug console for inspection

## Best Practices

1. **Use separate `__init__.py` files** to make modules importable
2. **Keep configuration in `config/` folder**
3. **Use `.env` for sensitive data** (never commit)
4. **Write tests in `tests/` folder**
5. **Document code with docstrings**
6. **Use type hints** for better IDE support
7. **Follow PEP 8** style guide
8. **Use meaningful commit messages**
