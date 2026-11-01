from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass
from dataclasses import field as dc_field
from datetime import datetime
from typing import Any, Protocol, cast

import pandas as pd

from lynvera_aidataready.config.models import Config
from lynvera_aidataready.core.models import Finding, Status
from lynvera_aidataready.profiling.collector import Collector, present

FORMATS = {
    "email": r"[^\s@]+@[^\s@]+\.[^\s@]+",
    "uuid": r"[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}",
    "iso-date": r"\d{4}-\d{2}-\d{2}(?:T.*)?",
}
SENSITIVE = re.compile(
    r"[^\s@]+@[^\s@]+\.[^\s@]+|(?<!\w)\+?\d[\d ()-]{7,}\d(?!\w)|\b\d{3}-\d{2}-\d{4}\b"
)


class Rule(Protocol):
    def evaluate(self, config: Config, stats: Collector) -> list[Finding]: ...


@dataclass
class CounterRule:
    code: str
    category: str
    field: str
    predicate: Callable[[pd.DataFrame], pd.Series[Any]]
    recommendation: str
    severity: str = "error"
    dependencies: list[str] = dc_field(default_factory=list)
    examined: int = 0
    violations: int = 0
    missing_fields: bool = False

    def update(self, frame: pd.DataFrame) -> None:
        self.examined += len(frame)
        if self.field != "*" and any(
            name not in frame for name in [self.field, *self.dependencies]
        ):
            self.missing_fields = True
            self.violations += len(frame)
        else:
            self.violations += int((~self.predicate(frame).fillna(False)).sum())

    def finding(self, resource: str) -> Finding:
        status = Status.PASS
        if self.violations:
            status = Status.WARN if self.severity == "warning" else Status.FAIL
        if not self.examined:
            status = Status.INCONCLUSIVE
        return Finding(
            code=self.code,
            category=self.category,
            severity=self.severity,
            status=status,
            resource=resource,
            examined=self.examined,
            violations=self.violations,
            evidence={"field": self.field, "missing_fields": self.missing_fields},
            recommendation=self.recommendation,
            limitations=["Heuristic detection can miss sensitive data and produce false positives."]
            if self.code == "privacy.possible_sensitive_data"
            else [],
        )


def valid_type(series: pd.Series[Any], kind: str) -> pd.Series[Any]:
    if kind in {"number", "integer"}:
        numeric = pd.to_numeric(series, errors="coerce")
        valid = numeric.notna() & ~numeric.isin([float("inf"), float("-inf")])
        if kind == "integer":
            valid &= numeric.mod(1).eq(0)
        return valid & ~series.map(lambda value: isinstance(value, bool))
    if kind == "datetime":
        return pd.to_datetime(series, errors="coerce", utc=True, format="mixed").notna()
    if kind == "boolean":
        return series.map(lambda value: isinstance(value, bool))
    return series.map(lambda value: isinstance(value, str)) & present(series)


def build_rules(config: Config, now: datetime) -> list[CounterRule]:
    rules: list[CounterRule] = []

    def add(
        code: str,
        category: str,
        name: str,
        predicate: Callable[[pd.DataFrame], pd.Series[Any]],
        recommendation: str,
        severity: str = "error",
        dependencies: list[str] | None = None,
    ) -> None:
        rules.append(
            CounterRule(
                code, category, name, predicate, recommendation, severity, dependencies or []
            )
        )

    required = list(config.rules.required_fields)
    if config.profile == "rag":
        rag = config.rag
        required += [rag.id_field, rag.text_field, rag.provenance_field, rag.version_field]
        required += rag.filter_fields
        if rag.permission_field:
            required.append(rag.permission_field)
        add(
            "rag.text_quality",
            "rag",
            rag.text_field,
            lambda df: (
                df[rag.text_field].map(lambda value: isinstance(value, str))
                & df[rag.text_field].astype(str).str.strip().str.len().ge(rag.min_text_length)
            ),
            "Provide usable document text.",
        )
    if config.profile == "agent-tools":
        agent = config.agent
        required += [agent.id_field, agent.authorization_field, *agent.tool_fields]
        if agent.action_field:
            required.append(agent.action_field)
            add(
                "agent.allowed_actions",
                "agent",
                agent.action_field,
                lambda df: df[agent.action_field or ""].isin(agent.allowed_actions),
                "Use actions allowed by the contract.",
            )
    if config.profile == "machine-learning" and config.rules.target:
        required.append(config.rules.target)
    for name in dict.fromkeys(required):

        def required_value(df: pd.DataFrame, n: str = name) -> pd.Series[Any]:
            return present(df[n])

        add(
            "structure.required",
            "structure",
            name,
            required_value,
            "Provide a nonempty required field.",
        )
    for name, kind in config.rules.types.items():

        def typed_value(df: pd.DataFrame, n: str = name, k: str = kind) -> pd.Series[Any]:
            return valid_type(df[n], k)

        add(
            "structure.type",
            "structure",
            name,
            typed_value,
            "Match the contracted type.",
        )
    for name, bounds in config.rules.ranges.items():

        def in_range(
            df: pd.DataFrame,
            n: str = name,
            lo: float | None = bounds.min,
            hi: float | None = bounds.max,
        ) -> pd.Series[Any]:
            values = pd.to_numeric(df[n], errors="coerce")
            valid = values.notna()
            if lo is not None:
                valid &= values.ge(lo)
            if hi is not None:
                valid &= values.le(hi)
            return valid

        add("structure.range", "structure", name, in_range, "Use values within the range.")
    for name, fmt in config.rules.formats.items():

        def matches(df: pd.DataFrame, n: str = name, f: str = fmt) -> pd.Series[Any]:
            valid = df[n].astype(str).str.fullmatch(FORMATS[f], na=False)
            if f == "iso-date":
                valid &= valid_type(df[n], "datetime")
            return valid

        add("structure.format", "structure", name, matches, "Use the contracted format.")
    for name, allowed in config.rules.references.items():

        def referenced_value(
            df: pd.DataFrame,
            n: str = name,
            values: list[str | int] = allowed,
        ) -> pd.Series[Any]:
            return df[n].isin(values)

        add(
            "structure.reference",
            "structure",
            name,
            referenced_value,
            "Use an identifier in the supplied reference set.",
        )
    freshness = config.rules.freshness
    if freshness:

        def fresh(df: pd.DataFrame) -> pd.Series[Any]:
            dates = pd.to_datetime(df[freshness.field], errors="coerce", utc=True, format="mixed")
            age = (pd.Timestamp(now) - dates).dt.total_seconds() / 86400
            return dates.notna() & age.ge(0) & age.le(freshness.max_age_days)

        add(
            "operations.freshness",
            "operations",
            freshness.field,
            fresh,
            "Refresh old records and correct invalid or future dates.",
        )
    split = config.rules.temporal_split
    if split:

        def temporal(df: pd.DataFrame) -> pd.Series[Any]:
            dates = pd.to_datetime(df[split.field], errors="coerce", utc=True, format="mixed")
            cutoff = pd.to_datetime(split.cutoff, utc=True)
            return cast(
                "pd.Series[Any]",
                (df[split.split_field].eq(split.train_value) & dates.lt(cutoff))
                | (df[split.split_field].eq(split.test_value) & dates.ge(cutoff)),
            )

        add(
            "ml.temporal_split",
            "ml",
            split.field,
            temporal,
            "Keep training records before the cutoff and test records after it.",
            dependencies=[split.split_field],
        )
    if config.rules.sensitive_data:

        def no_sensitive(df: pd.DataFrame) -> pd.Series[Any]:
            detected = pd.Series(False, index=df.index)
            for column in df.columns:
                detected |= df[column].astype(str).str.contains(SENSITIVE, na=False)
            return ~detected

        rules.append(
            CounterRule(
                "privacy.possible_sensitive_data",
                "privacy",
                "*",
                no_sensitive,
                "Review access and remove unnecessary sensitive data.",
                "warning",
            )
        )
    return rules


def aggregate_findings(config: Config, stats: Collector, source: str) -> list[Finding]:
    findings: list[Finding] = []

    def add(
        code: str,
        category: str,
        bad: int,
        evidence: dict[str, Any],
        *,
        inconclusive: bool = False,
        warning: bool = False,
    ) -> None:
        status = Status.WARN if bad and warning else Status.FAIL if bad else Status.PASS
        if inconclusive or not stats.total:
            status = Status.INCONCLUSIVE
        findings.append(
            Finding(
                code=code,
                category=category,
                severity="warning" if warning else "error",
                status=status,
                resource=source,
                evidence=evidence,
                examined=stats.total,
                violations=bad,
                recommendation="Review the data and contract.",
                limitations=["Distinct value limit reached."] if inconclusive else [],
            )
        )

    add("source.nonempty", "structure", int(stats.total == 0), {}, inconclusive=not stats.total)
    add(
        "operations.batch_schema",
        "operations",
        stats.schema_changes,
        {"changed_batches": stats.schema_changes},
    )
    unique = list(config.rules.unique_fields)
    if config.profile == "rag":
        unique += [config.rag.id_field, config.rag.text_field]
    elif config.profile == "agent-tools":
        unique.append(config.agent.id_field)
    for name in dict.fromkeys(unique):
        column = stats.columns.get(name)
        if column is None:
            add("structure.unique", "structure", stats.total, {"field": name})
        else:
            missing = column.missing + stats.total - column.observed
            add(
                "structure.unique",
                "structure",
                column.duplicates + missing,
                {"field": name},
                inconclusive=column.overflow and not column.duplicates,
            )
    for name, threshold in config.rules.max_null_fraction.items():
        column = stats.columns.get(name)
        missing = column.missing + stats.total - column.observed if column else stats.total
        fraction = missing / stats.total if stats.total else 0
        add(
            "structure.null_fraction",
            "structure",
            missing if fraction > threshold else 0,
            {"field": name, "fraction": fraction, "threshold": threshold},
        )
    if config.rules.expected_fields is not None:
        actual, expected = set(stats.columns), set(config.rules.expected_fields)
        add(
            "operations.schema",
            "operations",
            len(actual ^ expected),
            {
                "missing_fields": sorted(expected - actual),
                "extra_fields": sorted(actual - expected),
            },
        )
    baseline = config.rules.baseline_rows
    if baseline:
        change = abs(stats.total - baseline) / baseline
        add(
            "operations.row_change",
            "operations",
            int(change > config.rules.max_row_change),
            {"relative_change": change},
            warning=True,
        )
    for name, maximum in config.rules.max_cardinality.items():
        column = stats.columns.get(name)
        distinct = len(column.counts) if column else 0
        add(
            "ml.cardinality",
            "ml",
            max(0, distinct - maximum),
            {"field": name, "distinct": distinct},
            inconclusive=column is None or (column.overflow and distinct <= maximum),
        )
    if config.profile == "machine-learning":
        target = config.rules.target
        column = stats.columns.get(target or "")
        largest = max(column.counts.values(), default=0) if column else 0
        nonmissing = column.observed - column.missing if column else 0
        fraction = largest / nonmissing if nonmissing else 0
        add(
            "ml.class_balance",
            "ml",
            int(fraction > config.rules.max_class_fraction),
            {"target": target, "largest_class_fraction": fraction},
            inconclusive=column is None or column.overflow or nonmissing == 0,
            warning=True,
        )
        for name in config.rules.forbidden_features:
            add("ml.forbidden_feature", "ml", int(name in stats.columns), {"field": name})
    if config.profile == "agent-tools":
        agent = config.agent
        add("agent.contract_version", "agent", int(not agent.version), {})
        add("agent.action_definitions", "agent", int(not agent.allowed_actions), {})
        undocumented = [
            name for name in agent.tool_fields if not agent.field_descriptions.get(name, "").strip()
        ]
        add("agent.documented_schema", "agent", len(undocumented), {"fields": undocumented})
    return findings
