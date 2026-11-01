# Validation record

This records observed MVP validation, not independent acceptance or a guarantee
for every dataset. Documentation examples are also checked before review.

## MVP preparation

| Check | Observed result |
| --- | --- |
| Full suite with temporary PostgreSQL 16.2 | 70 passed, no skipped tests. |
| Total coverage, including branches | 99.22%. |
| Statement coverage | 99.57%. |
| Branch coverage | 98.00%. |
| Ruff and formatting | Passed. |
| Strict mypy checks on src | Passed. |
| Wheel and source build | Passed. |
| Clean wheel installation | Passed on macOS ARM64, Python 3.12.9. |
| Offline example after installation | Passed. |
| Linux CI | Python 3.12 and 3.13, with PostgreSQL 17. |

Validation used synthetic data. PostgreSQL tests covered streaming, bound
filters, timeouts, attempted writes, missing tables, and SELECT-only access.
A generator with 100,001 records exercised truncation and bounded distinct tracking.

See [the original validation run](https://github.com/lynvera-ai/aidataready/actions/runs/41356669239)
and [current CI](https://github.com/lynvera-ai/aidataready/actions/workflows/ci.yml).
Historical counts describe that preparation and may change as the suite grows.

## Documentation examples

The documentation refresh checked 18 Markdown files, 108 local links, and six
SVG assets. All four local profile examples returned their expected statuses.
JSON, HTML, and JUnit conversion ran for each result. Five Python snippets,
contract creation, and the documented CLI exit codes were also checked.

## Reproduce

Follow [contributing](../CONTRIBUTING.md) for code checks and
[PostgreSQL integration tests](postgresql.md#integration-tests) for database setup.
Without the test database URL, database tests are skipped; do not count that
as a complete PostgreSQL run.

Run the [documented examples](../examples/README.md) from the checkout. Passing
examples should exit 0. The duplicate fixture intentionally exits 1.

## Remaining evidence

A clean Windows installation and independent user acceptance remain pending.
Linux CI is automated test evidence, not an independent clean-host installation.
No fixed throughput or maximum supported dataset size is claimed. Batch budgets
are not hard memory limits. See [contract limits](contracts.md#results-and-budgets).
