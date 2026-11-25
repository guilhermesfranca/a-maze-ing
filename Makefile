PY           = python3
COMFIG       = config.txt
MAIN         = a_maze_ing.py
PIP          = pip
INSTALL      = install
REQUIREMENTS = requirements.txt
MAIN         = a_maze_ing.py

.PHONY: install run debug clean lint lint-strict

all: install

install:
	$(PIP) $(INSTALL) --upgrade $(PIP)
	$(PIP) $(INSTALL) -r $(REQUIREMENTS)
	tar -xzf mlx-2.2.tgz ubuntu/mlx-2.2-py3-none-any.whl
	$(PIP) $(INSTALL) ubuntu/mlx-2.2-py3-none-any.whl
	rm -rf ubuntu

run:
	$(PY) $(MAIN) $(COMFIG)

debug:
	$(PY) -m pdb $(MAIN) $(COMFIG)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 .
	mypy . --strict