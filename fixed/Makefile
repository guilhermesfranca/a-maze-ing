PYTHON ?= python3
CONFIG ?= config.txt
MLX_WHEEL ?= vendor/mlx-2.2-py3-none-any.whl

.PHONY: install run debug clean lint lint-strict test package

install:
	$(PYTHON) -m pip install -r requirements.txt
	$(PYTHON) -m pip install "$(MLX_WHEEL)"

run:
	$(PYTHON) a_maze_ing.py "$(CONFIG)"

debug:
	$(PYTHON) -m pdb a_maze_ing.py "$(CONFIG)"

lint:
	$(PYTHON) -m flake8 .
	$(PYTHON) -m mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	$(PYTHON) -m flake8 .
	$(PYTHON) -m mypy . --strict

test:
	$(PYTHON) -m unittest discover -s tests -v

package:
	$(PYTHON) -m build --wheel --outdir .

clean:
	find . -type d \( -name __pycache__ -o -name .mypy_cache -o -name build -o -name '*.egg-info' \) -prune -exec rm -r {} +
