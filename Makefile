# Makefile for Oodaloo Project

.PHONY: init test test-e2e record task-new task-archive run-auto

init:
	pip install -U pip ruff black mdformat pytest pyyaml vcrpy

test:
	pytest -q -k "not e2e and not qbo_real_api"

test-e2e:
	QBO_LIVE=1 pytest -q -m "e2e or qbo_real_api"

record:
	# Refresh VCR cassettes using sandbox credentials in env
	pytest -q -k "qbo and not e2e" --record-mode=once

task-new:
	@read -p "Enter task description: " desc; \
	python scripts/task.py create "$$desc"

task-archive:
	python scripts/task.py archive

run-auto:
	python dev/agent/auto.py --taskfile dev/agent/TASK.md