# AIDataReady documentation

AIDataReady checks local data against contracts for AI applications.
Version 0.1.0 is the initial library and CLI MVP.

Visit the [official AIDataReady website](https://aidataready.lynvera.ai).

## Start here

| Goal | Guide |
| --- | --- |
| Install and run a first check | [Getting started](getting-started.md) |
| Start in Spanish | [Guía rápida](es/getting-started.md) |
| Understand commands and exit codes | [CLI reference](cli.md) |
| Call assessments from Python | [Python API](python-api.md) |
| Select rules for an application | [Profiles](profiles.md) |
| Connect a PostgreSQL table | [PostgreSQL](postgresql.md) |
| Diagnose a failed check | [Troubleshooting](troubleshooting.md) |
| Update, roll back, or uninstall | [Maintenance](maintenance.md) |

Run the RAG example first. Then try the known duplicate failure and open both
HTML reports. Choose a profile before connecting a small real dataset.

## Contracts and operation

[The YAML reference](contracts.md) defines sources, rule keys, statuses, counts,
and limits. [Architecture](architecture.md) explains the assessment lifecycle
and extension points. [Examples](../examples/README.md) provide small fixtures.

[Validation](validation.md) records tested environments and coverage.
[Releases](releases.md) explains local builds and compatibility expectations.
No PyPI publication is implied.

## Project

Read [contributing](../CONTRIBUTING.md), [security](../SECURITY.md), and the
[code of conduct](../CODE_OF_CONDUCT.md). The [tool review](tool-review.md)
explains the use-case focus. [Dependency licenses](dependencies.md) records
the reviewed lock graph.

[Return to the overview](../README.md).
