from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from lynvera_aidataready.core.models import Finding, Status


@dataclass
class PanderaRule:
    """Reuse a trusted Pandera schema on a batch without exporting failure samples."""

    schema: Any

    def validate(self, frame: pd.DataFrame, resource: str = "dataset") -> Finding:
        from pandera.errors import SchemaErrors

        try:
            self.schema.validate(frame, lazy=True)
            status, violations = Status.PASS, 0
        except SchemaErrors as error:
            status, violations = Status.FAIL, len(error.failure_cases)
        return Finding(
            code="integration.pandera",
            category="structure",
            status=status,
            resource=resource,
            examined=len(frame),
            violations=violations,
            recommendation="Match the Pandera schema.",
            limitations=["Batch validation cannot establish uniqueness across batches."],
        )
