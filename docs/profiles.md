# Assessment profiles

Choose `general`, `rag`, `machine-learning`, or `agent-tools` in YAML.
Each assessment uses one profile. Add shared checks through `rules`.
All profiles check for nonempty data and column-set changes between batches.

## General

Use `general` for source quality contracts. Configure required fields, unique
IDs, logical types, null fractions, ranges, formats, references, or freshness.
These constraints are not inferred automatically.

```yaml
project:
  name: customers
source:
  type: csv
  path: customers.csv
profile: general
rules:
  required_fields: [id, name]
  unique_fields: [id]
  types:
    id: integer
  max_null_fraction:
    name: 0
```

Try [the duplicate ID fixture](../examples/duplicate-ids.yaml) for a known FAIL.

## RAG

The default RAG contract requires `document_id`, `content`, `source`, and
`version`. IDs and exact document text are checked for duplicates. Text must
be a string with at least 20 trimmed characters.

| Contract option | Default or behavior |
| --- | --- |
| `id_field` | `document_id` |
| `text_field` | `content` |
| `provenance_field` | `source` |
| `version_field` | `version` |
| `min_text_length` | 20 |
| `filter_fields` | Extra required fields. |
| `permission_field` | An extra required field when configured. |

These options go under `rag`. Use them to map an existing document schema.
Try [the RAG fixture](../examples/rag.yaml).

Text length and exact duplicates are mechanical checks. They do not measure
semantic quality, embeddings, retrieval relevance, or complete permissions.

## Machine learning

Set `rules.target` to enable classification balance checks. The target must
exist and be nonempty. Without a target, class balance is INCONCLUSIVE.

`max_class_fraction` defaults to 0.9 and warns when the largest nonmissing
class exceeds that share. `max_cardinality` sets limits for selected fields.
`forbidden_features` lists fields the data owner knows can leak information.
`temporal_split` checks dates against an explicit training/test cutoff.

Try [the ML fixture](../examples/machine-learning.yaml). It has two balanced
classes and training dates before the test cutoff.

Class balance is for classification. No automatic leakage inference,
statistical drift test, or model performance evaluation is performed.

## Agent tools

The default required fields are `id` and `authorization`. The `agent` section
adds a contract version, tool fields, field descriptions, and allowed actions.

| Contract option | Purpose |
| --- | --- |
| `id_field` | ID field, default `id`. |
| `authorization_field` | Required metadata, default `authorization`. |
| `version` | A declared contract version. |
| `tool_fields` | Fields required by the tool. |
| `field_descriptions` | Descriptions keyed by tool field. |
| `allowed_actions` | Declared permitted action names. |
| `action_field` | If set, each value must be in allowed_actions. |

Try [the agent fixture](../examples/agent-tools.yaml). It declares one read
action and provides two authorized record shapes.

The checks establish presence and declared membership. They do not prove that
IDs are stable over time or that an authorization system enforces these values.

## Tune the contract

Choose the fields and thresholds your application actually needs. Review WARN
and INCONCLUSIVE results before use. The [YAML reference](contracts.md) defines
all available rule keys and limits. No readiness score is calculated.
