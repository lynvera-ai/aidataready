# Architecture

Assessment loads a validated Config, streams a Source, collects bounded
statistics, runs readiness rules, and returns a Result. Writers render that
result without reading the source again.

| Module | Responsibility |
| --- | --- |
| cli | Typer commands and terminal summaries. |
| core | Finding, Result, and Status models. |
| config | Pydantic models and safe YAML loading. |
| sources | Source protocol and local or PostgreSQL readers. |
| profiling | Counts and bounded digest tracking. |
| rules | Vectorized predicates and aggregate readiness checks. |
| contracts | Public profile contract types. |
| assessments | Evaluation lifecycle and error handling. |
| reporting | JSON, HTML, and JUnit writers. |
| integrations | Optional Pandera batch validation. |

Pandas was selected for its schema ecosystem and direct Pandera integration.
Polars offers a strong lazy engine, but adds conversion work for that integration.
PyArrow reads Parquet batches. ijson streams JSON arrays. SQLAlchemy constructs
PostgreSQL queries and manages connections. General dataframe operations reuse
pandas; AI profiles supply contract-specific checks.

Implement `Source.batches(size)` as a generator of pandas DataFrames to add a
source. Supply it to `Assessment(config, source=my_source)`. Generator cleanup
runs when the scan stops. MySQL, Oracle, and object storage are future adapters.

Extra aggregate rules implement `Rule.evaluate(config, stats)` and return
findings. Pass them through `Assessment(..., extra_rules=[rule])`. Collector
contains internal digests, not raw records. Extensions are trusted Python code.

`integrations.pandera.PanderaRule(schema).validate(frame)` reuses an existing
Pandera schema directly. It returns counts without failure samples. This API is
separate from YAML and is for caller-managed batches. Global uniqueness needs
cross-batch tracking in the assessment.
