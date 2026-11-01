import json

import pandas as pd
import pytest
from pydantic import ValidationError
from yaml.constructor import ConstructorError

from lynvera_aidataready import Assessment, Status
from lynvera_aidataready.config import Config, load_config
from lynvera_aidataready.config.models import Limits, SourceConfig
from lynvera_aidataready.sources import FileSource, PostgresSource


@pytest.mark.parametrize("kind", ["csv", "json", "jsonl", "parquet"])
def test_files_processed_in_batches(tmp_path, kind):
    records = [{"id": i, "content": f"record {i}"} for i in range(2505)]
    path = tmp_path / f"data.{kind}"
    if kind == "csv":
        pd.DataFrame(records).to_csv(path, index=False)
    elif kind == "json":
        path.write_text(json.dumps(records))
    elif kind == "jsonl":
        path.write_text("\n".join(json.dumps(record) for record in records))
    else:
        pd.DataFrame(records).to_parquet(path)
    config = Config.model_validate(
        {
            "project": {"name": "test"},
            "source": {"type": kind, "path": str(path)},
            "limits": {"batch_size": 100},
            "rules": {"unique_fields": ["id"]},
        }
    )
    result = Assessment(config).run()
    assert result.status == Status.PASS
    assert result.rows_examined == 2505
    assert result.statistics["batches"] == 26


@pytest.mark.parametrize(
    "kind,content",
    [("json", "{}"), ("json", "[1]"), ("jsonl", "{bad}"), ("csv", ""), ("json", '[{"id":1},')],
)
def test_malformed_files_return_execution_error(tmp_path, kind, content):
    path = tmp_path / "data"
    path.write_text(content)
    config = Config.model_validate(
        {"project": {"name": "x"}, "source": {"type": kind, "path": str(path)}}
    )
    assert Assessment(config).run().status == Status.ERROR


def test_missing_and_oversized_source(tmp_path):
    path = tmp_path / "data.json"
    config = Config.model_validate(
        {
            "project": {"name": "x"},
            "source": {"type": "json", "path": str(path)},
            "limits": {"max_file_bytes": 1},
        }
    )
    assert Assessment(config).run().status == Status.ERROR
    path.write_text('[{"id":1}]')
    assert Assessment(config).run().status == Status.ERROR
    with pytest.raises(ValueError):
        list(FileSource(SourceConfig(type="memory"), Limits()).batches(1))


def test_empty_json(tmp_path):
    path = tmp_path / "data.json"
    path.write_text(" \n []")
    config = Config.model_validate(
        {"project": {"name": "x"}, "source": {"type": "json", "path": str(path)}}
    )
    assert Assessment(config).run().status == Status.INCONCLUSIVE


def test_relative_paths_resolve_against_contract(tmp_path, monkeypatch):
    (tmp_path / "data.csv").write_text("id\n1\n")
    contract = tmp_path / "test.yaml"
    contract.write_text("project: {name: test}\nsource: {type: csv, path: data.csv}\n")
    monkeypatch.chdir("/tmp")
    assert load_config(contract).source.path == tmp_path / "data.csv"
    assert Assessment.from_config(contract).run().status == Status.PASS


@pytest.mark.parametrize(
    "patch",
    [
        {"source": {"type": "csv"}},
        {"profile": "unknown"},
        {"unknown": True},
        {"rules": {"max_null_fraction": {"id": 2}}},
        {"limits": {"batch_size": 0}},
        {"rules": {"ranges": {"id": {"min": 2, "max": 1}}}},
        {"rules": {"ranges": {"id": {}}}},
        {"rules": {"max_cardinality": {"id": 0}}},
        {"source": {"type": "postgres", "table": "documents", "allowed_tables": []}},
        {
            "source": {
                "type": "postgres",
                "table": "a; DROP TABLE a",
                "allowed_tables": ["a; DROP TABLE a"],
            }
        },
        {"rules": {"temporal_split": {"field": "date", "split_field": "split", "cutoff": "bad"}}},
        {
            "rules": {
                "temporal_split": {
                    "field": "d",
                    "split_field": "s",
                    "cutoff": "2026-01-01",
                    "train_value": "same",
                    "test_value": "same",
                }
            }
        },
    ],
)
def test_invalid_configs(patch):
    data = {"project": {"name": "test"}, "source": {"type": "memory"}}
    data.update(patch)
    with pytest.raises(ValidationError):
        Config.model_validate(data)


def test_yaml_does_not_execute_python(tmp_path):
    path = tmp_path / "bad.yaml"
    path.write_text('!!python/object/apply:os.system ["touch should-not-exist"]')
    with pytest.raises(ConstructorError):
        load_config(path)
    path.write_text("x" * 1_000_001)
    with pytest.raises(ValueError, match="1 MB"):
        load_config(path)


def test_postgres_missing_credentials_and_wrong_driver(monkeypatch):
    config = Config.model_validate(
        {
            "project": {"name": "x"},
            "source": {
                "type": "postgres",
                "table": "docs",
                "allowed_tables": ["docs"],
                "url_env": "TEST_DB",
            },
        }
    )
    monkeypatch.delenv("TEST_DB", raising=False)
    assert Assessment(config).run().status == Status.ERROR
    monkeypatch.setenv("TEST_DB", "sqlite://")
    with pytest.raises(ValueError, match="PostgreSQL"):
        list(PostgresSource(config.source, config.limits).batches(1))
    monkeypatch.setenv("TEST_DB", "postgresql+psycopg://user:secret@127.0.0.1:1/test")
    result = Assessment(config).run()
    assert result.status == Status.ERROR
    assert "secret" not in str(result.as_dict())


def test_postgres_revalidates_table_allowlist_after_config_changes():
    config = SourceConfig(type="postgres", table="documents", allowed_tables=["documents"])
    config.table = "other"
    with pytest.raises(ValidationError, match="allowed_tables"):
        PostgresSource(config, Limits())
