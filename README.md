# Lynvera AIDataReady

Know your data. Build reliable AI.

Local Python toolkit for data readiness checks for AI, RAG, machine learning,
and agent tools. Python 3.12 or later. Apache License 2.0.

## Install

From this checkout:

```bash
uv sync --all-extras
uv run aidataready --help
```

For a local package installation:

```bash
python -m pip install .
python -m pip install '.[postgres,pandera]'
```

The package has not been published to PyPI.

## Quickstart

```bash
uv run aidataready check --config examples/rag.yaml
uv run aidataready profile --config examples/rag.yaml
uv run aidataready report --format html
uv run aidataready report --format junit
uv run aidataready version
```

Open `aidataready-report.html` locally. It has severity, category, and source
filters. No external scripts, models, or AI services are used.

Create your own contract with `aidataready init`. File paths are relative to the
contract. `check` writes JSON by default. `report` converts a saved JSON result.

```python
from lynvera_aidataready import Assessment

result = Assessment.from_config("examples/rag.yaml").run()
print(result.status)
```

## Implemented

CSV, JSON arrays, JSONL, Parquet, PostgreSQL, and in-memory sources support batch
processing. PostgreSQL uses allowed tables, bound filter values, read-only
transactions, and timeouts. Credentials come from an environment variable.

The `general`, `rag`, `machine-learning`, and `agent-tools` profiles combine
contract checks. These cover required fields, logical types, nulls, duplicates,
ranges, known formats, supplied reference sets, freshness, schema changes, row
count changes, RAG metadata, text length, class balance, cardinality, temporal
splits, forbidden features, and agent contract metadata.

Results use PASS, WARN, FAIL, ERROR, and INCONCLUSIVE. Each finding includes a
code, severity, category, evidence, examined count, violations, recommendation,
and limitations. Reports support JSON, local HTML, JUnit XML, and plain terminal
summaries. There is no readiness score.

Exit codes: 0 for PASS or WARN, 1 for FAIL, 2 for ERROR or INCONCLUSIVE.

## Limits

Checks assess the supplied contract. They do not establish model quality,
retrieval quality, valid permissions, stable IDs over time, or complete privacy
coverage. Personal data detection is optional and heuristic. Reports contain
counts and field names, without record samples or values. Dataset values and
SQL credentials are withheld from execution errors.

Row limits make the scan incomplete. Distinct limits make affected checks
inconclusive unless a violation is already proven. Memory budgets check batches
after decoding; they are not a hard process memory cap. See the
[contract reference](docs/contracts.md) for exact semantics.

No telemetry is sent. Examples run offline after dependencies are installed.
MySQL, Oracle, object storage, model evaluation, and semantic text scoring are
not implemented.

## Development

```bash
uv sync --locked --all-extras
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov --cov-report=term-missing
uv build
```

PostgreSQL tests need a disposable database. They create and remove the
`aidataready_test` schema. Never point them at production.

```bash
export AIDATAREADY_TEST_DATABASE_URL='postgresql+psycopg://user:password@localhost/test'
uv run pytest -m postgres
```

The CI workflow supplies PostgreSQL and requires 85% coverage, including branches.

See [architecture](docs/architecture.md), [tool review](docs/tool-review.md),
and [dependency licenses](docs/dependencies.md).

Created and maintained by Dr. Felipe Castillo Rendón.

Lynvera Open Source.

https://lynvera.ai
