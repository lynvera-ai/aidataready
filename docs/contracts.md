# YAML contracts

Unknown keys and invalid thresholds are rejected. YAML cannot run Python.
Configuration files are limited to 1 MB. Paths resolve from the YAML directory.
Use non-sensitive project, source, and field names because reports include them.

```yaml
project:
  name: customer-knowledge
source:
  type: csv
  path: data/documents.csv
  name: documents
profile: rag
limits:
  batch_size: 1000
  max_rows: 100000
  max_file_bytes: 100000000
  max_batch_bytes: 64000000
  max_distinct: 100000
rules:
  required_fields: [document_id, content, updated_at]
  unique_fields: [document_id]
  freshness:
    field: updated_at
    max_age_days: 30
rag:
  permission_field: access
```

## Sources

`type` accepts csv, json, jsonl, parquet, postgres, and memory. Files require
`path`. JSON must be an array of objects. JSONL uses one object per line.
The memory source is passed explicitly through the SDK.

PostgreSQL requires `table` in `allowed_tables`. `schema_name` defaults to public.
`url_env` defaults to AIDATAREADY_DATABASE_URL. Set it to a PostgreSQL URL with
psycopg installed. `filters` maps column names to scalar equality values. Values
are bound parameters. Arbitrary SQL is not accepted. Identifiers are restricted
to letters, digits, and underscores, beginning with a letter or underscore.

`timeout_ms` defaults to 10000. A connect timeout and transaction-local statement
timeout are applied. Use a role granted only SELECT on the intended tables.
Read-only transactions also reject writes attempted by a view function. A SQL
source reads at most max_rows plus one record to detect truncation. Tables can
change during a scan under PostgreSQL's default transaction isolation.

## General rules

| Key | Meaning |
| --- | --- |
| required_fields | Fields must exist and have nonempty values on each record. |
| unique_fields | No repeated nonempty values across examined batches. Missing values fail. |
| types | Field to string, integer, number, boolean, or datetime. Nulls fail. |
| max_null_fraction | Field to allowed missing fraction, from 0 to 1. |
| ranges | Field to min and/or max, inclusive. Nulls and nonnumeric values fail. |
| formats | Field to email, uuid, or iso-date. Nulls fail. |
| references | Field to a supplied list of allowed string or integer values. |
| freshness | Field and max_age_days. Invalid and future dates fail. |
| expected_fields | Exact set of expected column names. |
| baseline_rows | Positive reference row count. |
| max_row_change | Allowed relative count change. Default 0.2. |
| sensitive_data | Optional heuristic email, phone, and US SSN detection. Default false. |
| target | Target field for classification checks. |
| max_class_fraction | Largest allowed nonmissing class share. Default 0.9. |
| max_cardinality | Field to a positive distinct value limit. |
| forbidden_features | Fields known by the owner to leak target information. |
| temporal_split | Date field, split_field, cutoff, train_value, and test_value. |

Integer and number checks accept numeric strings and reject booleans and
nonfinite values. Boolean checks require actual boolean values. CSV inference
uses pandas. Use JSON for unambiguous boolean data. Datetimes are parsed in UTC;
naive datetimes are treated as UTC. An ISO date must also parse as a real date.
Blank strings count as missing. No custom regex or Python expressions run from
YAML. Reference checks prove membership only in the supplied reference set.

A temporal split requires training dates before `cutoff` and test dates at or
after it. Other split labels fail. Defaults are train and test. This does not
verify that the training process actually uses those partitions.

## Profiles

`general` runs configured rules, a nonempty check, and batch schema checks.

`rag` also requires document_id, content, source, and version. Override names
through `rag.id_field`, text_field, provenance_field, and version_field.
`filter_fields` adds required metadata. `permission_field` adds a required field.
`min_text_length` defaults to 20 trimmed characters. Text must be a string.
Document IDs and exact document text are checked for duplicates.

`machine-learning` requires the configured target and measures class balance.
Without a target it reports INCONCLUSIVE. Class balance is intended for
classification, not regression. No automatic leakage inference is performed.

`agent-tools` requires id, authorization, and configured tool_fields. The `agent`
section accepts id_field, authorization_field, version, tool_fields,
field_descriptions, allowed_actions, and action_field. Version and allowed
operation definitions must be present. Each tool field needs a description.
An action_field, if set, must contain allowed_actions. Nonempty authorization
metadata does not establish that an authorization policy is valid.

## Results and budgets

Overall status precedence is ERROR, FAIL, INCONCLUSIVE, WARN, PASS. Source errors
are execution failures. Empty datasets are inconclusive. WARN does not fail the
CLI. JUnit maps FAIL to failure, ERROR to error, WARN and INCONCLUSIVE to skipped.
JSON preserves all statuses and has the full evidence.

`examined` counts records examined by a check. Most violation counts are records
or duplicate occurrences. Schema checks count mismatched fields or changed
batches. Row change, class balance, forbidden features, and contract checks use
one violation per failed condition. Evidence provides the relevant measure.

The batch schema check compares column sets between batches; it cannot locate
per-record optional-field changes normalized into a dataframe. Type changes are
caught only by configured logical type checks. Row change is the absolute
relative difference from baseline_rows. No statistical drift test is implied.

Each column retains up to max_distinct SHA-256 digests and counts internally.
Digests and values are excluded from reports. Distinct counts become lower
bounds when the budget is reached. Exact duplicate checks distinguish serialized
types and text, without normalization or semantic similarity.

A scan stops at max_rows. Passing checks become INCONCLUSIVE for partial scans.
Observed violations remain failures. A row-count baseline requires a complete
scan. max_file_bytes limits local file size. max_batch_bytes checks pandas deep
memory size after each batch is decoded. Nested objects, decoder buffers, tracking
state, and library overhead can consume extra memory. Limit individual record
sizes upstream; use operating system resource controls when a hard cap is needed.

Built-in reports omit all record samples. Sensitive detection counts flagged
rows, with false positives and false negatives. It is not a privacy audit.
Custom extensions and caller-managed logs must follow the same privacy rules.
