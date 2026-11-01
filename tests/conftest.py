from datetime import UTC, datetime
from typing import Any

from lynvera_aidataready import Assessment, Result
from lynvera_aidataready.config import Config
from lynvera_aidataready.sources import MemorySource

NOW = datetime(2026, 11, 1, tzinfo=UTC)


def assess(records: list[dict[str, Any]], **options: Any) -> Result:
    data: dict[str, Any] = {"project": {"name": "test"}, "source": {"type": "memory"}}
    data.update(options)
    return Assessment(Config.model_validate(data), MemorySource(records)).run(now=NOW)
