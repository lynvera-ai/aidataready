from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path

from lynvera_aidataready.config import Config, load_config
from lynvera_aidataready.core.models import Finding, Result, Status
from lynvera_aidataready.profiling.collector import Collector
from lynvera_aidataready.rules.engine import Rule, aggregate_findings, build_rules
from lynvera_aidataready.sources import Source, make_source


class Assessment:
    def __init__(
        self,
        config: Config,
        source: Source | None = None,
        extra_rules: Sequence[Rule] = (),
    ) -> None:
        self.config = config
        self.source = source
        self.extra_rules = extra_rules

    @classmethod
    def from_config(cls, path: str | Path) -> "Assessment":
        return cls(load_config(path))

    def run(self, *, now: datetime | None = None) -> Result:
        config = self.config
        now = now or datetime.now(UTC)
        if now.tzinfo is None:
            raise ValueError("Assessment time must include a timezone.")
        resource = config.source.name
        result = Result(project=config.project.name, source=resource, profile=config.profile)
        stats = Collector(config.limits.max_distinct)
        rules = build_rules(config, now)
        iterator = None
        try:
            source = (
                self.source
                if self.source is not None
                else make_source(config.source, config.limits)
            )
            iterator = source.batches(config.limits.batch_size)
            for frame in iterator:
                if not all(isinstance(name, str) for name in frame.columns):
                    raise ValueError("Column names must be strings.")
                if frame.columns.has_duplicates:
                    raise ValueError("Duplicate column names.")
                if frame.memory_usage(index=True, deep=True).sum() > config.limits.max_batch_bytes:
                    raise ValueError("Batch memory budget exceeded.")
                remaining = config.limits.max_rows - stats.total
                truncated = len(frame) > remaining
                frame = frame.iloc[:remaining]
                if len(frame):
                    stats.update(frame)
                    for rule in rules:
                        rule.update(frame)
                if truncated:
                    result.complete = False
                    result.findings.append(
                        Finding(
                            code="source.row_limit",
                            category="operations",
                            status=Status.INCONCLUSIVE,
                            resource=resource,
                            examined=stats.total,
                            recommendation="Raise max_rows or assess smaller partitions.",
                            limitations=["Only the first max_rows records were examined."],
                        )
                    )
                    break
        except Exception:
            result.complete = False
            result.findings.append(
                Finding(
                    code="source.execution",
                    category="execution",
                    status=Status.ERROR,
                    resource=resource,
                    examined=stats.total,
                    recommendation="Check source access, data format, dependencies, and limits.",
                    limitations=[
                        "Source error details are withheld to protect credentials and values."
                    ],
                )
            )
        finally:
            if iterator is not None:
                iterator.close()
        result.findings += [rule.finding(resource) for rule in rules]
        result.findings += aggregate_findings(config, stats, resource)
        for custom_rule in self.extra_rules:
            try:
                result.findings += custom_rule.evaluate(config, stats)
            except Exception:
                result.findings.append(
                    Finding(
                        code="rule.execution",
                        category="execution",
                        status=Status.ERROR,
                        resource=resource,
                        recommendation="Check the custom rule.",
                    )
                )
        result.rows_examined = stats.total
        result.statistics = stats.summary()
        if not result.complete:
            for finding in result.findings:
                if finding.status == Status.PASS or finding.code == "operations.row_change":
                    finding.status = Status.INCONCLUSIVE
                    finding.limitations.append("The source was not fully examined.")
        return result
