# Releases and compatibility

Version 0.1.0 is the initial MVP. It is available from source. No PyPI upload,
automatic publication, or public package release is implied.

## Current scope

The supported implementation is a local Python library and CLI. File readers,
PostgreSQL access, four profiles, and JSON, HTML, and JUnit reports are implemented.
See [the overview](../README.md) and [validation record](validation.md).

The API and YAML format are early interfaces. Review the changelog and rerun
representative contracts before adopting updates. A long-term compatibility
policy has not yet been established. No formal versioned JSON Schema is shipped.

## Build locally

From a reviewed checkout, with uv installed:

```bash
uv sync --locked --all-extras
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov --cov-report=term-missing
uv build
```

PostgreSQL tests are skipped without a disposable test URL. Run the documented
[database tests](postgresql.md#integration-tests) before declaring full validation.
The configured coverage minimum is 85%, including branches.

For version 0.1.0, a successful build creates:

```text
dist/lynvera_aidataready-0.1.0-py3-none-any.whl
dist/lynvera_aidataready-0.1.0.tar.gz
```

The wheel includes the typed library and CLI entry point. The source archive
also includes docs, examples, and tests. Building creates local files only.

## Before distribution

Check the package name and executable name again before publication. Review
dependency licenses and preserve upstream notices. Install the built wheel in
a clean environment and run a documented example. Record the platform, Python
version, test results, and limitations.

A package-index upload, GitHub release, or tag is a separate maintainer action.
The CI workflow builds packages but does not publish them.

Read [CHANGELOG.md](../CHANGELOG.md), [maintenance](maintenance.md), and
[dependency licenses](dependencies.md).
