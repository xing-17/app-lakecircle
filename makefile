# Makefile for app-lakecircle
APP_NAME := $(shell grep '^name' pyproject.toml | head -1 | cut -d '"' -f2)
APP_ALIA := 湖堰
APP_VERS := $(shell grep '^version' pyproject.toml | head -1 | cut -d '"' -f2)
APP_PATH := $(abspath .)
CONDA_ENV := $(APP_NAME)
CONDA_ENV_FILE := environment.yml

clean: app/clean
lint: app/lint

conda/install:
	@if ! conda env list | grep -qE "^$(CONDA_ENV)[[:space:]]"; then \
		echo "[app][$(APP_NAME)@$(APP_ALIA)] create env '$(CONDA_ENV)'"; \
		conda env create -f $(CONDA_ENV_FILE); \
	else \
		echo "[app][$(APP_NAME)@$(APP_ALIA)] update env '$(CONDA_ENV)'"; \
		conda env update -n $(CONDA_ENV) -f $(CONDA_ENV_FILE); \
	fi
	@echo "[app][$(APP_NAME)@$(APP_ALIA)] installing deps via (pyproject.toml) ..."
	@conda run -n $(CONDA_ENV) python -m pip install --upgrade pip
	@conda run -n $(CONDA_ENV) sh -c 'python -m pip install ".[dev]"'
	@echo "[app][$(APP_NAME)@$(APP_ALIA)] 'conda' environment installed ✅ "

conda/activate:
	@echo "[app][$(APP_NAME)@$(APP_ALIA)] activate conda by 'conda activate $(APP_NAME)'"

conda/deactivate:
	@echo "[app][$(APP_NAME)@$(APP_ALIA)] deactivate conda by 'conda deactivate'"

app/install:
	@pip install .
	@pip install .[dev]
	@echo "[app][$(APP_NAME)@$(APP_ALIA)] 'dependencies' installed ✅ "

app/clean:
	@rm -rf build dist *.egg-info
	@echo "[app][$(APP_NAME)@$(APP_ALIA)] 'build artifacts' cleaned ✅ "

	@rm -rf .pytest_cache
	@echo "[app][$(APP_NAME)@$(APP_ALIA)] 'pytest caches' cleaned ✅ "

	@rm -rf .ruff_cache
	@rm -rf .benchmarks
	@echo "[app][$(APP_NAME)@$(APP_ALIA)] 'ruff/benchmarks caches' cleaned ✅ "

	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type d -name ".DS_Store" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@echo "[app][$(APP_NAME)@$(APP_ALIA)] 'python caches' cleaned ✅ "

app/lint:
	@ruff format .
	@ruff check . --fix
	@ruff check .
	@echo "[app][$(APP_NAME)@$(APP_ALIA)] 'app' lint checked ✅"
