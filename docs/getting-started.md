# Getting started

Install AIDataReady, run a passing assessment, then inspect a known failure.
You need Python 3.12 or newer. The local examples need no database or AI service.

## Installation

| Method | Use when |
| --- | --- |
| Source with pip | You want the library, CLI, docs, and examples. |
| Source with uv | You also want the locked development environment. |
| Local wheel | You have a reviewed package file. |

Dependencies usually need network access to install. Once installed, the
included examples run offline. No background service or account is created.

### Source with pip

```bash
git clone https://github.com/lynvera-ai/aidataready.git
cd aidataready
python3 -m venv .venv
source .venv/bin/activate
python -m pip install .
aidataready version
```

Expected version: `0.1.0`.

On Windows PowerShell, replace the environment steps with:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install .
.venv\Scripts\aidataready.exe version
```

Use `.venv\Scripts\aidataready.exe` instead of `aidataready` below if the
environment is not activated. Windows instructions are provided; a clean
Windows installation has not been independently verified.

### Source with uv

From the checkout, with uv already installed:

```bash
uv sync --locked --all-extras
uv run aidataready version
uv run aidataready check --config examples/rag.yaml
```

This installs development tools plus the PostgreSQL and Pandera extras.
Use `uv run` before subsequent commands, or activate `.venv`.

### Local package

Install an actual reviewed file in an isolated Python environment:

```bash
python -m pip install ./lynvera_aidataready-0.1.0-py3-none-any.whl
```

A source archive can be installed with
`python -m pip install ./lynvera_aidataready-0.1.0.tar.gz`.
A wheel contains the library and CLI. The source archive also includes docs
and examples. These instructions do not imply a published release or PyPI upload.
Use [local build instructions](releases.md#build-locally) to create the files.

## Run a passing check

From the source checkout:

```bash
aidataready check --config examples/rag.yaml
aidataready report --format html
```

The summary starts with `local-knowledge: PASS. Records: 2.` and exits 0.
Open `aidataready-report.html` in your browser. The input result is saved as
`aidataready-result.json`. Reports are written to your working directory.

The fixture dates are fixed. Its freshness rule accepts records from
2026-10-31 for 3,650 days. Future dates also fail, so use a current dataset
and a suitable freshness window in your own contracts.

## Inspect a failure

```bash
aidataready check --config examples/duplicate-ids.yaml --output duplicates.json
aidataready report --input duplicates.json --output duplicates.html
```

Expected summary: `duplicate-ids: FAIL. Records: 2.` The `structure.unique`
finding has one violation. Exit code 1 is expected. Run the report command
separately even when the check exits 1.

## Create your own contract

Use a new working directory. Keep your installed environment active.

```bash
aidataready init
```

Create `data.csv` beside the generated YAML file:

```csv
id,name
1,Ana
2,Luis
```

Then run:

```bash
aidataready check --config aidataready.yaml
aidataready profile --config aidataready.yaml
```

The generated contract requires unique, nonempty IDs. It does not require
`name` until you add that field to `rules.required_fields`.
`init` refuses to overwrite files. Choose another name with
`aidataready init --path another.yaml`.

File paths are relative to the YAML file. Output paths are relative to the
working directory. Create output directories before writing reports.

## Choose the next guide

Use [profiles](profiles.md) to choose RAG, ML, or agent rules.
Use the [Python API](python-api.md) for in-memory data and existing applications.
Use [PostgreSQL](postgresql.md) for an allowed database table.
See [troubleshooting](troubleshooting.md) if a command cannot complete.
