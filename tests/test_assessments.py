from datetime import datetime

import pandas as pd
import pytest
from conftest import NOW, assess

from lynvera_aidataready import Assessment, Finding, Status
from lynvera_aidataready.config import Config
from lynvera_aidataready.profiling.collector import Collector
from lynvera_aidataready.sources import MemorySource


def statuses(result, code):
    return [finding.status for finding in result.findings if finding.code == code]


def test_general_contract_and_global_duplicates():
    result = assess(
        [{"id": 1, "n": 2}, {"id": 2, "n": 3}, {"id": 1, "n": 4}],
        limits={"batch_size": 1},
        rules={
            "required_fields": ["id"],
            "unique_fields": ["id"],
            "types": {"id": "integer"},
            "ranges": {"n": {"min": 0, "max": 10}},
        },
    )
    assert result.status == Status.FAIL
    unique = next(f for f in result.findings if f.code == "structure.unique")
    assert unique.violations == 1
    assert unique.examined == 3
    assert result.statistics["batches"] == 3


@pytest.mark.parametrize("records", [[{"id": None}], [{"other": 1}], [{"id": " "}]])
def test_required_missing_values(records):
    result = assess(records, rules={"required_fields": ["id"], "unique_fields": ["id"]})
    assert statuses(result, "structure.required") == [Status.FAIL]
    assert statuses(result, "structure.unique") == [Status.FAIL]


def test_structural_rules_and_privacy_do_not_export_values():
    secret = "private.person@example.com"
    result = assess(
        [{"id": "bad", "email": secret, "day": "2026-02-30", "ref": 9, "score": 99, "flag": "yes"}],
        rules={
            "types": {"id": "integer", "flag": "boolean", "day": "datetime"},
            "formats": {"email": "email", "day": "iso-date"},
            "references": {"ref": [1, 2]},
            "ranges": {"score": {"max": 10}},
            "sensitive_data": True,
        },
    )
    assert result.status == Status.FAIL
    assert statuses(result, "privacy.possible_sensitive_data") == [Status.WARN]
    assert secret not in str(result.as_dict())
    assert secret not in str(result.statistics)
    assert statuses(result, "structure.reference") == [Status.FAIL]


def test_sensitive_detection_clean_and_null_fraction():
    result = assess(
        [{"a": "documentation"}, {"a": None}],
        rules={"sensitive_data": True, "max_null_fraction": {"a": 0.4, "missing": 0.1}},
    )
    assert statuses(result, "privacy.possible_sensitive_data") == [Status.PASS]
    assert statuses(result, "structure.null_fraction") == [Status.FAIL, Status.FAIL]


@pytest.mark.parametrize(
    "kind,value",
    [
        ("string", "ok"),
        ("number", 1.5),
        ("boolean", True),
        ("integer", 2),
        ("datetime", "2026-10-31T00:00:00Z"),
    ],
)
def test_valid_types(kind, value):
    assert assess([{"a": value}], rules={"types": {"a": kind}}).status == Status.PASS


@pytest.mark.parametrize("value", [True, "abc", float("inf"), float("-inf"), 1.5])
def test_invalid_integer(value):
    assert assess([{"a": value}], rules={"types": {"a": "integer"}}).status == Status.FAIL


def test_formats_and_reference_pass():
    result = assess(
        [{"id": "b3b49bf7-2d61-4bfc-a774-5b8a00ee77ad", "day": "2026-10-31", "ref": 1}],
        rules={
            "formats": {"id": "uuid", "day": "iso-date"},
            "references": {"ref": [1]},
            "ranges": {"ref": {"min": 1}},
        },
    )
    assert result.status == Status.PASS


def test_freshness_rejects_old_invalid_and_future_dates():
    result = assess(
        [{"updated": value} for value in ["2026-10-31", "2020-01-01", "bad", "2027-01-01"]],
        rules={"freshness": {"field": "updated", "max_age_days": 30}},
    )
    finding = next(f for f in result.findings if f.code == "operations.freshness")
    assert finding.violations == 3


def test_schema_changes_missing_fields_and_baseline():
    result = assess(
        [{"id": 1}, {"id": 2, "extra": 3}],
        limits={"batch_size": 1},
        rules={
            "required_fields": ["extra"],
            "expected_fields": ["id", "required"],
            "max_null_fraction": {"extra": 0},
            "baseline_rows": 100,
        },
    )
    assert statuses(result, "operations.batch_schema") == [Status.FAIL]
    assert statuses(result, "operations.schema") == [Status.FAIL]
    assert statuses(result, "operations.row_change") == [Status.WARN]
    assert result.statistics["columns"]["extra"]["missing"] == 1


def test_rag_profile_valid_and_missing_metadata():
    record = {
        "document_id": "doc1",
        "content": "Useful instructions for account setup.",
        "source": "manual",
        "version": 1,
        "access": "team",
        "region": "mx",
    }
    options = {"profile": "rag", "rag": {"permission_field": "access", "filter_fields": ["region"]}}
    assert assess([record], **options).status == Status.PASS
    assert assess([{"document_id": "1", "content": "short"}], **options).status == Status.FAIL
    assert assess([record, {**record, "document_id": "doc2"}], **options).status == Status.FAIL


def test_ml_balance_leakage_cardinality_and_time_split():
    records = [
        {"id": i, "target": "a" if i < 9 else "b", "leak": 1, "day": "2026-10-31", "split": "train"}
        for i in range(10)
    ]
    result = assess(
        records,
        profile="machine-learning",
        rules={
            "target": "target",
            "max_class_fraction": 0.8,
            "max_cardinality": {"id": 5},
            "forbidden_features": ["leak"],
            "temporal_split": {"field": "day", "split_field": "split", "cutoff": "2026-10-01"},
        },
    )
    assert statuses(result, "ml.class_balance") == [Status.WARN]
    assert statuses(result, "ml.cardinality") == [Status.FAIL]
    assert statuses(result, "ml.temporal_split") == [Status.FAIL]
    assert statuses(result, "ml.forbidden_feature") == [Status.FAIL]
    assert assess(records, profile="machine-learning").status == Status.INCONCLUSIVE


def test_valid_temporal_split_and_absent_dependencies():
    rule = {"temporal_split": {"field": "date", "split_field": "split", "cutoff": "2026-10-01"}}
    records = [{"date": "2026-09-30", "split": "train"}, {"date": "2026-10-01", "split": "test"}]
    assert assess(records, rules=rule).status == Status.PASS
    assert assess([{"date": "2026-09-30"}], rules=rule).status == Status.FAIL


def test_agent_contract_and_actions():
    record = {"id": 1, "authorization": "staff", "query": "status", "action": "read"}
    agent = {
        "version": "1",
        "tool_fields": ["query"],
        "field_descriptions": {"query": "Lookup"},
        "allowed_actions": ["read"],
        "action_field": "action",
    }
    assert assess([record], profile="agent-tools", agent=agent).status == Status.PASS
    assert (
        assess([{**record, "action": "delete"}], profile="agent-tools", agent=agent).status
        == Status.FAIL
    )
    assert (
        assess([record], profile="agent-tools", agent={"tool_fields": ["query"]}).status
        == Status.FAIL
    )


def test_empty_data_never_passes():
    result = assess([], rules={"required_fields": ["id"], "max_null_fraction": {"id": 0}})
    assert result.status == Status.INCONCLUSIVE
    assert all(f.status != Status.PASS for f in result.findings)


def test_row_limit_marks_passes_inconclusive_but_preserves_failures():
    result = assess(
        [{"id": i} for i in range(5)],
        limits={"batch_size": 2, "max_rows": 3},
        rules={"required_fields": ["id", "absent"]},
    )
    assert result.rows_examined == 3
    assert not result.complete
    assert Status.PASS not in [f.status for f in result.findings]
    assert Status.FAIL in statuses(result, "structure.required")
    assert assess([{"id": 1}], limits={"max_rows": 1}).complete


def test_distinct_limit_never_proves_uniqueness():
    result = assess(
        [{"id": i} for i in range(3)],
        limits={"max_distinct": 1},
        rules={"unique_fields": ["id"], "max_cardinality": {"id": 2}},
    )
    assert statuses(result, "structure.unique") == [Status.INCONCLUSIVE]
    assert statuses(result, "ml.cardinality") == [Status.INCONCLUSIVE]
    assert (
        assess(
            [{"id": "a"}, {"id": "a"}, {"id": "b"}],
            limits={"max_distinct": 1},
            rules={"unique_fields": ["id"]},
        ).status
        == Status.FAIL
    )


def test_memory_budget_and_missing_memory_source_are_errors():
    assert assess([{"id": "long text"}], limits={"max_batch_bytes": 1}).status == Status.ERROR
    config = Config.model_validate({"project": {"name": "x"}, "source": {"type": "memory"}})
    assert Assessment(config).run().status == Status.ERROR
    with pytest.raises(ValueError, match="timezone"):
        Assessment(config, MemorySource([])).run(now=datetime(2026, 1, 1))


def test_custom_rule_extension_and_failure():
    class Custom:
        def evaluate(self, config: Config, stats: Collector) -> list[Finding]:
            return [
                Finding(
                    code="custom",
                    category="custom",
                    resource="dataset",
                    status=Status.WARN,
                    examined=stats.total,
                )
            ]

    class Broken:
        def evaluate(self, config: Config, stats: Collector) -> list[Finding]:
            raise RuntimeError("private value")

    config = Config.model_validate({"project": {"name": "x"}, "source": {"type": "memory"}})
    result = Assessment(config, MemorySource([{"id": 1}]), [Custom(), Broken()]).run(now=NOW)
    assert result.status == Status.ERROR
    assert statuses(result, "custom") == [Status.WARN]
    assert "private value" not in str(result.as_dict())


def test_custom_source_closes_after_limit():
    closed = []

    class CustomSource:
        def batches(self, size):
            try:
                yield pd.DataFrame({"a": [1, 2, 3]})
            finally:
                closed.append(True)

    config = Config.model_validate(
        {"project": {"name": "x"}, "source": {"type": "memory"}, "limits": {"max_rows": 1}}
    )
    assert not Assessment(config, CustomSource()).run().complete
    assert closed == [True]


def test_reject_invalid_column_names():
    class BadSource:
        def batches(self, size):
            yield pd.DataFrame([[1, 2]], columns=["id", "id"])

    config = Config.model_validate({"project": {"name": "x"}, "source": {"type": "memory"}})
    assert Assessment(config, BadSource()).run().status == Status.ERROR


def test_partial_scan_cannot_establish_baseline_row_decrease():
    result = assess(
        [{"id": i} for i in range(100)], limits={"max_rows": 3}, rules={"baseline_rows": 100}
    )
    assert statuses(result, "operations.row_change") == [Status.INCONCLUSIVE]
    assert result.status == Status.INCONCLUSIVE


def test_large_generator_stays_lazy_and_tracks_bounded_distinct_values():
    consumed = []

    def records():
        for i in range(100001):
            consumed.append(i)
            yield {"id": i}

    config = Config.model_validate(
        {
            "project": {"name": "large"},
            "source": {"type": "memory"},
            "limits": {"batch_size": 512, "max_rows": 100000, "max_distinct": 64},
        }
    )
    result = Assessment(config, MemorySource(records())).run()
    assert result.rows_examined == 100000
    assert len(consumed) == 100001
    assert result.statistics["batches"] == 196
    assert result.statistics["columns"]["id"]["distinct"] == 64
    assert not result.statistics["columns"]["id"]["distinct_complete"]
    assert not result.complete
