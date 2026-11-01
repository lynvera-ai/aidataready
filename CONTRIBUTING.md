# Contributing

Open an issue for substantial changes. Keep pull requests focused and use a
branch other than main. Include tests for behavior changes and update the docs.

```bash
uv sync --locked --all-extras
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov --cov-report=term-missing
```

PostgreSQL integration tests require a disposable database as described in the
README. Use synthetic data. Never commit credentials or private records.

Use short commit messages such as `feat: add a source adapter`. Preserve license
notices. Contributions are under Apache License 2.0.
