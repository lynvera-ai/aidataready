# Installation maintenance

Use the same Python environment for installation and commands. Save contracts
and reports separately from package files before replacing an environment.

## Inspect an installation

```bash
aidataready version
python -m pip show lynvera-aidataready
```

The distribution name differs from the command. A source checkout also contains
docs and examples; an installed wheel contains the CLI and library.

## Update from source

Use a clean source checkout of a reviewed commit. Install it into a new environment
first, then run a synthetic check before using real data:

```bash
python3 -m venv .venv-review
source .venv-review/bin/activate
python -m pip install .
aidataready version
aidataready check --config examples/rag.yaml
```

Use the Windows executable paths described in [getting started](getting-started.md)
when activation is unavailable. Choose a different directory if `.venv-review`
already exists. Existing contracts are not migrated automatically.

For uv development, use `uv sync --locked --all-extras` in the reviewed checkout.
Avoid `uv lock --upgrade` unless you intend to review dependency updates.

## Replace a wheel

Install the reviewed local file into the selected environment:

```bash
python -m pip install --force-reinstall ./lynvera_aidataready-0.1.0-py3-none-any.whl
```

Use the file's actual version and name. Include optional extras again if needed.
Dependency resolution may require network access. There is no published PyPI
release assumed by this workflow.

## Roll back

Keep the previous reviewed wheel or source commit. Reinstall it in a separate
environment and rerun your small contract. Preserve the JSON that explains a
previous result; report conversion does not rerun or modify the dataset.

## Uninstall

```bash
python -m pip uninstall lynvera-aidataready
```

Uninstalling removes the library and command from that environment. It does not
remove your YAML, datasets, reports, source checkout, or separately installed
dependencies. There is no background service or fixed application data directory.
Review and remove those files separately when they are no longer needed.
