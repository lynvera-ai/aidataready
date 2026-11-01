# Contributing

Open an issue for substantial changes. Keep pull requests focused and use a
branch other than main. Use synthetic fixtures and document behavior changes.

## Local checks

With Python 3.12 or newer and uv installed:

```bash
uv sync --locked --all-extras
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov --cov-report=term-missing
```

The coverage minimum is 85%, including branches. Database tests are skipped
unless `AIDATAREADY_TEST_DATABASE_URL` points to a disposable database whose
administrator can create roles. Tests create and remove `aidataready_test`
and temporary reader roles. See [database tests](docs/postgresql.md#integration-tests).

## Documentation and examples

Start at [the documentation index](docs/README.md). Keep prose short and describe
implemented behavior. Check local links and run any changed command or example.
A deliberate failing example should state its expected exit code.

Preserve external license notices. Do not commit credentials, private records,
local reports, caches, or temporary notes. Source extensions must close their
resources and report incomplete scans honestly.

Use short messages such as `feat: add a source adapter` or
`docs: clarify profile configuration`. Review the staged diff before committing.
Contributions are under Apache License 2.0. Follow the
[code of conduct](CODE_OF_CONDUCT.md) and [security policy](SECURITY.md).
