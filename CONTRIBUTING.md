# Contributing

## Setup

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
```

This installs the project itself in editable mode (`-e .`) plus the dev
tooling, so `create_db`, `analyze_sales`, and `utils` are importable from
anywhere without path hacks.

## Quality gate

Every push and pull request runs the same checks locally and in CI
(`.github/workflows/ci.yml`):

```bash
ruff check .
black --check .
mypy
pytest --cov --cov-report=term-missing
```

All four must pass before merging. `ruff` and `black` also support
auto-fixing:

```bash
ruff check . --fix
black .
```

## Guidelines

- Keep changes minimal and focused; avoid unrelated renames or moves.
- Add or update tests for any behavior change, and keep coverage at or above
  the `fail_under` threshold in `pyproject.toml`.
- Match the existing style (typed signatures, docstrings, `pathlib.Path` over
  raw strings).
