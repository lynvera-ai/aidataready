import re
from pathlib import Path
from typing import Any, Literal, Self

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class Project(StrictModel):
    name: str = Field(min_length=1, max_length=200)


class SourceConfig(StrictModel):
    type: Literal["csv", "json", "jsonl", "parquet", "postgres", "memory"]
    path: Path | None = None
    name: str = "dataset"
    url_env: str = "AIDATAREADY_DATABASE_URL"
    table: str | None = None
    schema_name: str = "public"
    allowed_tables: list[str] = Field(default_factory=list)
    filters: dict[str, str | int | float | bool] = Field(default_factory=dict)
    timeout_ms: int = Field(default=10000, ge=1, le=300000)

    @model_validator(mode="after")
    def valid_source(self) -> Self:
        if self.type in {"csv", "json", "jsonl", "parquet"} and self.path is None:
            raise ValueError("File sources require path.")
        if self.type == "postgres":
            if not self.table or self.table not in self.allowed_tables:
                raise ValueError("PostgreSQL table must be in allowed_tables.")
            for identifier in [self.table, self.schema_name, *self.filters]:
                if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", identifier):
                    raise ValueError("Invalid SQL identifier.")
        return self


class Limits(StrictModel):
    batch_size: int = Field(default=1000, ge=1, le=100000)
    max_rows: int = Field(default=100000, ge=1)
    max_file_bytes: int = Field(default=100_000_000, ge=1)
    max_batch_bytes: int = Field(default=64_000_000, ge=1)
    max_distinct: int = Field(default=100000, ge=1)


class Freshness(StrictModel):
    field: str
    max_age_days: float = Field(ge=0)


class Range(StrictModel):
    min: float | None = None
    max: float | None = None

    @model_validator(mode="after")
    def ordered(self) -> Self:
        if self.min is None and self.max is None:
            raise ValueError("Range requires min or max.")
        if self.min is not None and self.max is not None and self.min > self.max:
            raise ValueError("Range min exceeds max.")
        return self


class TemporalSplit(StrictModel):
    field: str
    split_field: str
    cutoff: str
    train_value: str = "train"
    test_value: str = "test"

    @model_validator(mode="after")
    def valid_cutoff(self) -> Self:
        from datetime import datetime

        datetime.fromisoformat(self.cutoff.replace("Z", "+00:00"))
        if self.train_value == self.test_value:
            raise ValueError("Split values must differ.")
        return self


class Rules(StrictModel):
    required_fields: list[str] = Field(default_factory=list)
    unique_fields: list[str] = Field(default_factory=list)
    types: dict[str, Literal["string", "integer", "number", "boolean", "datetime"]] = Field(
        default_factory=dict
    )
    max_null_fraction: dict[str, float] = Field(default_factory=dict)
    ranges: dict[str, Range] = Field(default_factory=dict)
    formats: dict[str, Literal["email", "uuid", "iso-date"]] = Field(default_factory=dict)
    references: dict[str, list[str | int]] = Field(default_factory=dict)
    freshness: Freshness | None = None
    expected_fields: list[str] | None = None
    baseline_rows: int | None = Field(default=None, ge=1)
    max_row_change: float = Field(default=0.2, ge=0)
    sensitive_data: bool = False
    target: str | None = None
    max_class_fraction: float = Field(default=0.9, gt=0, le=1)
    max_cardinality: dict[str, int] = Field(default_factory=dict)
    forbidden_features: list[str] = Field(default_factory=list)
    temporal_split: TemporalSplit | None = None

    @model_validator(mode="after")
    def valid_thresholds(self) -> Self:
        if any(not 0 <= value <= 1 for value in self.max_null_fraction.values()):
            raise ValueError("Null fractions must be between 0 and 1.")
        if any(value < 1 for value in self.max_cardinality.values()):
            raise ValueError("Cardinality limits must be positive.")
        return self


class RagContract(StrictModel):
    id_field: str = "document_id"
    text_field: str = "content"
    provenance_field: str = "source"
    version_field: str = "version"
    filter_fields: list[str] = Field(default_factory=list)
    permission_field: str | None = None
    min_text_length: int = Field(default=20, ge=1)


class AgentContract(StrictModel):
    id_field: str = "id"
    version: str | None = None
    tool_fields: list[str] = Field(default_factory=list)
    field_descriptions: dict[str, str] = Field(default_factory=dict)
    allowed_actions: list[str] = Field(default_factory=list)
    action_field: str | None = None
    authorization_field: str = "authorization"


class Config(StrictModel):
    project: Project
    source: SourceConfig
    profile: Literal["general", "rag", "machine-learning", "agent-tools"] = "general"
    rules: Rules = Field(default_factory=Rules)
    rag: RagContract = Field(default_factory=RagContract)
    agent: AgentContract = Field(default_factory=AgentContract)
    limits: Limits = Field(default_factory=Limits)


def load_config(path: str | Path) -> Config:
    path = Path(path).resolve()
    if path.stat().st_size > 1_000_000:
        raise ValueError("Configuration exceeds 1 MB.")
    data: Any = yaml.safe_load(path.read_text(encoding="utf-8"))
    config = Config.model_validate(data)
    if config.source.path is not None:
        config.source.path = (path.parent / config.source.path).resolve()
    return config
