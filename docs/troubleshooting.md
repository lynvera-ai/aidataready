# Troubleshooting

Start with `aidataready version` and `aidataready --help` in the same Python
environment used for installation. Use synthetic data when sharing a problem.

## Common problems

| Symptom | Check |
| --- | --- |
| Command not found | Activate `.venv`, use its executable directly, or use `uv run aidataready`. |
| Import fails | Confirm Python 3.12 or newer and install with that interpreter's pip. |
| Invalid configuration | Review the named fields, spelling, thresholds, and YAML indentation. Unknown keys are rejected. |
| Cannot read configuration | Check the path, permissions, and YAML syntax. |
| `source.execution` | Check source access, format, optional driver, and file or memory budgets. Details are withheld to protect values and credentials. |
| `source.row_limit` | Increase max_rows or assess smaller partitions. The scan is incomplete. |
| Cannot write report | Create the parent directory and check write permissions. |
| Report does not reflect new data | Rerun `check`, then rerun `report` against the new JSON. |

## Why does a check return FAIL?

A contract violation was found. Inspect its code, field, and violation count in
the saved JSON or HTML. Examples include missing required fields, duplicate IDs,
invalid formats, and stale dates. Exit code 1 is a data result.

Required values must be nonempty. CSV uses pandas inference and default missing
value handling. Tokens such as `NA` can be interpreted as missing. Numeric type
checks accept numeric strings; boolean type checks require actual booleans.

## Why is a result inconclusive?

An empty source, incomplete scan, missing target, or exhausted distinct budget
can prevent a conclusion. Lack of evidence cannot produce PASS. A known failure
can still take precedence over INCONCLUSIVE in the overall result.

Distinct counts become lower bounds at `max_distinct`. Increase that limit only
with a suitable memory budget. Memory checks happen after batch decoding and
do not cap the entire process. See [budgets](contracts.md#results-and-budgets).

## Why does freshness fail on a sample?

Freshness rejects invalid dates, future dates, and ages above the limit. Dates
are interpreted in UTC. The RAG fixture uses a fixed date and a documented window;
your clock and data must fall within that contract. Use current data for pilots.

## Why does PostgreSQL return ERROR?

Confirm the named environment variable is set in the terminal running the CLI.
Do not print or share its value. Confirm the psycopg extra is installed and the
URL uses `postgresql` or `postgresql+psycopg`.

Check the host, authentication, database, schema, allowed table, and SELECT grants
with your database client privately. Review the statement timeout for a slow view.
Missing tables, unknown filter columns, and denied access cannot produce PASS.
See [PostgreSQL setup](postgresql.md).

## Why does JUnit show skipped tests?

WARN and INCONCLUSIVE findings map to skipped. JUnit does not retain the full
status vocabulary. Use the JSON report and `check` exit code for your CI policy.
`report` exits 0 when conversion succeeds, even for a saved failed assessment.

## Report a reproducible issue

Include the installed version, Python version, operating system, command,
expected status, actual status, and a small synthetic contract and dataset.
Remove credentials and private names. For security issues, use
[the private reporting address](../SECURITY.md).
