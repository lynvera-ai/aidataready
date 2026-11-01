import json
import os
from collections.abc import Generator, Iterable, Iterator
from pathlib import Path
from typing import Any, Protocol

import ijson
import pandas as pd
import pyarrow.parquet as pq
from sqlalchemy import MetaData, Table, create_engine, select, text
from sqlalchemy.engine import make_url
from sqlalchemy.pool import NullPool

from lynvera_aidataready.config.models import Limits, SourceConfig


class Source(Protocol):
    def batches(self, size: int) -> Generator[pd.DataFrame, None, None]: ...


class MemorySource:
    def __init__(self, records: Iterable[dict[str, Any]]) -> None:
        self.records = records

    def batches(self, size: int) -> Generator[pd.DataFrame, None, None]:
        rows = []
        for record in self.records:
            rows.append(record)
            if len(rows) == size:
                yield pd.DataFrame(rows)
                rows = []
        if rows:
            yield pd.DataFrame(rows)


class FileSource:
    def __init__(self, config: SourceConfig, limits: Limits) -> None:
        self.config, self.limits = config, limits

    def batches(self, size: int) -> Generator[pd.DataFrame, None, None]:
        path = self.config.path
        if path is None:
            raise ValueError("Missing source path.")
        if path.stat().st_size > self.limits.max_file_bytes:
            raise ValueError("File size limit exceeded.")
        if self.config.type == "csv":
            with pd.read_csv(path, chunksize=size) as reader:
                yield from reader
        elif self.config.type == "parquet":
            with pq.ParquetFile(path) as parquet:
                for batch in parquet.iter_batches(batch_size=size):
                    yield batch.to_pandas()
        else:
            yield from MemorySource(self._records(path)).batches(size)

    def _records(self, path: Path) -> Iterator[dict[str, Any]]:
        with path.open("rb") as stream:
            if self.config.type == "jsonl":
                records = (json.loads(line) for line in stream if line.strip())
            else:
                first = stream.read(1)
                while first and first.isspace():
                    first = stream.read(1)
                if first != b"[":
                    raise ValueError("JSON source must contain an array of records.")
                stream.seek(0)
                records = ijson.items(stream, "item", use_float=True)
            for record in records:
                if not isinstance(record, dict) or not all(isinstance(k, str) for k in record):
                    raise ValueError("Records must be objects with string keys.")
                yield record


class PostgresSource:
    def __init__(self, config: SourceConfig, limits: Limits) -> None:
        self.config = SourceConfig.model_validate(config.model_dump())
        self.limits = limits

    def batches(self, size: int) -> Generator[pd.DataFrame, None, None]:
        url = make_url(os.environ[self.config.url_env])
        if url.drivername not in {"postgresql", "postgresql+psycopg"}:
            raise ValueError("Only PostgreSQL with psycopg is supported.")
        url = url.set(drivername="postgresql+psycopg")
        engine = create_engine(
            url,
            poolclass=NullPool,
            hide_parameters=True,
            connect_args={"connect_timeout": max(1, self.config.timeout_ms // 1000)},
        )
        try:
            with engine.connect() as connection, connection.begin():
                connection.execute(text("SET TRANSACTION READ ONLY"))
                connection.execute(
                    text("SELECT set_config('statement_timeout', :timeout, true)"),
                    {"timeout": str(self.config.timeout_ms)},
                )
                table = Table(
                    self.config.table or "",
                    MetaData(),
                    schema=self.config.schema_name,
                    autoload_with=connection,
                )
                query = select(table)
                for field, value in self.config.filters.items():
                    query = query.where(table.c[field] == value)
                query = query.limit(self.limits.max_rows + 1)
                with connection.execution_options(stream_results=True).execute(query) as result:
                    while rows := result.fetchmany(size):
                        yield pd.DataFrame(rows, columns=list(result.keys()))
        finally:
            engine.dispose()


def make_source(config: SourceConfig, limits: Limits) -> Source:
    if config.type == "memory":
        raise ValueError("Pass MemorySource explicitly for in-memory data.")
    if config.type == "postgres":
        return PostgresSource(config, limits)
    return FileSource(config, limits)
