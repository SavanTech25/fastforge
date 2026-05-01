.PHONY: install install-reqs build clean format test

install:
	uv venv && uv pip install -e .

install-reqs:
	uv pip install -r requirements.txt

build: clean
	uv build

clean:
	rm -rf dist/ build/ *.egg-info/ .venv/
	find . -type d -name __pycache__ -exec rm -rf {} +

format:
	uvx ruff format fastforge/

test:
	uv run pytest


git-push:
	@echo "Enter commit message:"
	@read -p "Message: " msg; \
	git add .; \
	git commit -m "$$msg"; \
	git push

