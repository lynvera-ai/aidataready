# Python API

The distribution is `lynvera-aidataready`. The import package is
`lynvera_aidataready`. Examples below use only implemented interfaces.

## Assess a YAML contract

From the source checkout:

```python
from lynvera_aidataready import Assessment, Status

result = Assessment.from_config("examples/rag.yaml").run()
print(result.status)
print(result.rows_examined)

if result.status == Status.FAIL:
    for finding in result.findings:
        if finding.status == Status.FAIL:
            print(finding.code, finding.violations)
```

`from_config` validates YAML and resolves source paths relative to that file.
Invalid configuration raises a validation or file error. Source failures during
`run` become ERROR findings with sensitive details withheld.

## Assess in-memory records

```python
from lynvera_aidataready import Assessment
from lynvera_aidataready.config import Config
from lynvera_aidataready.sources import MemorySource

config = Config.model_validate(
    {
        "project": {"name": "customer-data"},
        "source": {"type": "memory", "name": "customers"},
        "rules": {
            "required_fields": ["id"],
            "unique_fields": ["id"],
        },
        "limits": {"batch_size": 1},
    }
)
source = MemorySource([{"id": 1}, {"id": 1}])
result = Assessment(config, source=source).run()
print(result.status)
```

Expected result: FAIL. The duplicate is found across batches.
MemorySource accepts an iterable of dictionaries. A list can be read again;
a generator is consumed. Supply a fresh generator for another assessment.

## Inspect results

| Property | Meaning |
| --- | --- |
| `status` | Overall status using the documented precedence. |
| `complete` | Whether the source scan completed within its limits. |
| `rows_examined` | Number of scanned records. |
| `findings` | Check results, counts, recommendations, and limitations. |
| `statistics` | Aggregate column statistics without record values. |

Each finding has a stable `code`, `category`, `severity`, `status`, `resource`,
`evidence`, `examined`, `violations`, `recommendation`, and `limitations`.
`result.as_dict()` returns JSON-compatible data with the derived overall status.
`model_dump()` alone does not add that status property.

## Write and read reports

After either assessment above:

```python
from lynvera_aidataready.reporting.writers import read_result, write_report

write_report(result, "result.json")
write_report(result, "report.html", "html")
write_report(result, "report.xml", "junit")
restored = read_result("result.json")
print(restored.status)
```

Formats are `json`, `html`, and `junit`. Parent directories must exist.
Writing a report does not rescan the original source.

## Reuse a Pandera schema

Install the optional extra from the source checkout:

```bash
python -m pip install '.[pandera]'
```

```python
import pandas as pd
import pandera.pandas as pa
from lynvera_aidataready.integrations.pandera import PanderaRule

schema = pa.DataFrameSchema({"id": pa.Column(int, pa.Check.ge(1))})
finding = PanderaRule(schema).validate(pd.DataFrame({"id": [1, 2]}))
print(finding.status)
```

This validates a caller-managed batch. It is separate from YAML and returns
counts without Pandera failure samples. A batch cannot prove uniqueness across
other batches. Runtime errors in a supplied schema may raise to the caller.

## Add a source or rule

A source implements `Source.batches(size)` as a generator of pandas DataFrames.
Pass it through `Assessment(config, source=your_source)`. The engine closes the
generator when a scan stops. Extensions must release their resources in cleanup.

An aggregate rule implements `Rule.evaluate(config, stats)` and returns a list
of Finding objects. Pass it as `extra_rules=[your_rule]`. It receives bounded
statistics, including internal digests, rather than original records.
Custom rule errors become `rule.execution` findings.

Extensions are trusted Python code and must preserve privacy. See
[architecture](architecture.md) and [limits](contracts.md#results-and-budgets).
