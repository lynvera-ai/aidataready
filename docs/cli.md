# CLI reference

Run `aidataready --help` for installed command names. These commands are also
available as `uv run aidataready` from a source checkout with uv.

## Commands

| Command | Purpose |
| --- | --- |
| `aidataready init` | Create a contract without overwriting a file. |
| `aidataready profile` | Print record and column statistics. |
| `aidataready check` | Evaluate a contract, print findings, and save JSON. |
| `aidataready report` | Convert saved JSON to JSON, HTML, or JUnit. |
| `aidataready version` | Print the installed version. |

## Create a contract

```bash
aidataready init
aidataready init --path customer-data.yaml
```

`--path` defaults to `aidataready.yaml`. The contract points to `data.csv`
and requires unique, nonempty IDs. Create or choose the dataset before checking.
An existing file or invalid destination exits 2.

## Profile data

```bash
aidataready profile --config examples/rag.yaml
```

`--config` also accepts `-c` and defaults to `aidataready.yaml`.
The JSON output includes rows, batches, missing counts, distinct counts,
observed Python types, and whether distinct tracking is complete.
No record values or internal digests are printed.

`profile` runs the assessment but prints only statistics. It exits 0 for a
complete scan even if data checks fail. It exits 2 for invalid configuration
or an incomplete scan. Use `check` for a data quality gate.

## Check data

```bash
aidataready check --config examples/rag.yaml --output result.json
```

| Option | Default |
| --- | --- |
| `--config`, `-c` | `aidataready.yaml` |
| `--output` | `aidataready-result.json` |

`check` prints the overall status and finding counts. JSON is saved before
returning a data failure or inconclusive status. Configuration and output errors
can prevent JSON from being written. Existing output files are overwritten.

| Result | Exit code |
| --- | ---: |
| PASS or WARN | 0 |
| FAIL | 1 |
| ERROR or INCONCLUSIVE | 2 |

Status precedence is ERROR, FAIL, INCONCLUSIVE, WARN, PASS. An empty dataset
is inconclusive. A malformed file is an execution error. Missing required data
is a failed check. See [contract semantics](contracts.md#results-and-budgets).

## Render a report

```bash
aidataready report --input result.json --format html --output report.html
aidataready report --input result.json --format junit --output report.xml
aidataready report --input result.json --format json --output report.json
```

| Option | Default |
| --- | --- |
| `--input` | `aidataready-result.json` |
| `--format` | `html`; accepts `json`, `html`, or `junit` |
| `--output` | `aidataready-report.html`, `.json`, or `.xml` |

The command reads a saved result; it does not rerun the source.
The HTML report works as a local file and includes three filters.
JUnit maps FAIL to failure, ERROR to error, and WARN or INCONCLUSIVE to skipped.
JSON preserves each original status. Use JSON or the `check` exit code when
warnings and inconclusive checks must remain distinct.

A successful conversion exits 0 even if the saved assessment failed.
Unreadable input, unsupported formats, and invalid output paths exit 2.
Parent directories must already exist. Existing reports are overwritten.
