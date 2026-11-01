# Examples

Run these from the source checkout after installation. They use synthetic data
and need no model, hosted service, or account. Output files below are local.

## RAG documents

```bash
aidataready check --config examples/rag.yaml --output rag-result.json
aidataready report --input rag-result.json --output rag-report.html
```

Expected summary: `local-knowledge: PASS. Records: 2.` The contract checks
text, IDs, provenance, version, access metadata, and freshness. Dates are fixed
at 2026-10-31 with a 3,650-day freshness window. Outside that window, or before
that date, freshness fails. Use current dates for your own data.

[Contract](rag.yaml) and [data](data/documents.csv).

## Duplicate IDs

```bash
aidataready check --config examples/duplicate-ids.yaml --output duplicates.json
aidataready report --input duplicates.json --output duplicates.html
```

Expected result: FAIL, exit 1. `structure.unique` reports one violation for `id`.
Run report conversion separately after the expected failing command.

[Contract](duplicate-ids.yaml) and [data](data/duplicate-ids.csv).

## Machine learning

```bash
aidataready check --config examples/machine-learning.yaml --output ml-result.json
```

Expected result: PASS, exit 0, four records. The classes are balanced. Training
dates precede 2026-10-01, and test dates are at or after it. The known forbidden
feature `future_outcome` is absent. These checks do not evaluate a model.

[Contract](machine-learning.yaml) and [data](data/training.jsonl).

## Agent tools

```bash
aidataready check --config examples/agent-tools.yaml --output agent-result.json
```

Expected result: PASS, exit 0, two records. The contract declares its version,
describes the query field, and allows only the read action. Authorization
metadata is present; enforcement of real permissions is outside the example.

[Contract](agent-tools.yaml) and [data](data/tool-records.jsonl).

## PostgreSQL

The [PostgreSQL guide](../docs/postgresql.md) shows a small table and a SELECT-only
role. [postgres.yaml](postgres.yaml) reads the table using an environment URL.
It needs your database and the optional driver. It is not an offline fixture.

Read [profiles](../docs/profiles.md), [contracts](../docs/contracts.md), and
[the Python API](../docs/python-api.md) before adapting examples to private data.
