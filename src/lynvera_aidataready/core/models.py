from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class Status(StrEnum):
    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"
    ERROR = "ERROR"
    INCONCLUSIVE = "INCONCLUSIVE"


class Finding(BaseModel):
    code: str
    category: str
    severity: str = "error"
    status: Status
    resource: str
    evidence: dict[str, Any] = Field(default_factory=dict)
    examined: int = 0
    violations: int = 0
    recommendation: str = "Review the data contract."
    limitations: list[str] = Field(default_factory=list)


class Result(BaseModel):
    project: str
    source: str
    profile: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    findings: list[Finding] = Field(default_factory=list)
    rows_examined: int = 0
    complete: bool = True
    statistics: dict[str, Any] = Field(default_factory=dict)

    @property
    def status(self) -> Status:
        for status in (Status.ERROR, Status.FAIL, Status.INCONCLUSIVE, Status.WARN):
            if any(f.status == status for f in self.findings):
                return status
        return Status.PASS if self.findings else Status.INCONCLUSIVE

    def as_dict(self) -> dict[str, Any]:
        return {**self.model_dump(mode="json"), "status": self.status.value}
