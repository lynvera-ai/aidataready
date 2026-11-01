from __future__ import annotations

import hashlib
import json
from collections import Counter
from dataclasses import dataclass, field
from typing import Any

import pandas as pd


def fingerprint(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, default=str, ensure_ascii=True)
    return hashlib.sha256(payload.encode()).hexdigest()


def present(series: pd.Series[Any]) -> pd.Series[Any]:
    return series.notna() & series.astype(str).str.strip().ne("")


@dataclass
class ColumnStats:
    observed: int = 0
    missing: int = 0
    counts: Counter[str] = field(default_factory=Counter)
    overflow: bool = False
    kinds: set[str] = field(default_factory=set)

    def update(self, series: pd.Series[Any], max_distinct: int) -> None:
        self.observed += len(series)
        mask = present(series)
        self.missing += int((~mask).sum())
        for value in series[mask]:
            self.kinds.add(type(value).__name__)
            key = fingerprint(value)
            if key in self.counts or len(self.counts) < max_distinct:
                self.counts[key] += 1
            else:
                self.overflow = True

    @property
    def duplicates(self) -> int:
        return sum(count - 1 for count in self.counts.values())

    def summary(self, total: int) -> dict[str, Any]:
        return {
            "missing": self.missing + total - self.observed,
            "distinct": len(self.counts),
            "distinct_complete": not self.overflow,
            "types": sorted(self.kinds),
        }


@dataclass
class Collector:
    max_distinct: int
    total: int = 0
    batches: int = 0
    schema_changes: int = 0
    columns: dict[str, ColumnStats] = field(default_factory=dict)
    first_schema: set[str] | None = None

    def update(self, frame: pd.DataFrame) -> None:
        schema = set(frame.columns)
        if self.first_schema is None:
            self.first_schema = schema
        elif schema != self.first_schema:
            self.schema_changes += 1
        self.total += len(frame)
        self.batches += 1
        for name in frame.columns:
            self.columns.setdefault(name, ColumnStats()).update(frame[name], self.max_distinct)

    def summary(self) -> dict[str, Any]:
        return {
            "rows": self.total,
            "batches": self.batches,
            "columns": {name: stats.summary(self.total) for name, stats in self.columns.items()},
        }
