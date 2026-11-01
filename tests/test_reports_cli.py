import json
import xml.etree.ElementTree as ET

import pandas as pd
import pytest
from conftest import assess
from typer.testing import CliRunner

from lynvera_aidataready import Result, Status
from lynvera_aidataready.cli import app
from lynvera_aidataready.integrations.pandera import PanderaRule
from lynvera_aidataready.reporting.writers import read_result, write_report

runner = CliRunner()


def test_reports_roundtrip_escaping_privacy_and_junit(tmp_path):
    secret = "private@example.com"
    result = assess(
        [{"id": 1, "email": secret}, {"id": 1, "email": "clean"}],
        project={"name": '<script>alert("x")</script>\x01'},
        rules={"unique_fields": ["id"], "sensitive_data": True},
    )
    for format, suffix in [("json", "json"), ("html", "html"), ("junit", "xml")]:
        path = write_report(result, tmp_path / f"report.{suffix}", format)
        content = path.read_text()
        assert secret not in content
        if format == "html":
            assert '<script>alert("x")</script>' not in content
            assert "&lt;script&gt;" in content
            for key in ["severity", "category", "source"]:
                assert f'id="{key}"' in content
        elif format == "junit":
            xml = ET.fromstring(content)
            assert int(xml.attrib["failures"]) == 1
            assert int(xml.attrib["skipped"]) == 1
        else:
            assert json.loads(content)["status"] == "FAIL"
            assert read_result(path).status == result.status
    with pytest.raises(ValueError):
        write_report(result, tmp_path / "invalid", "pdf")


def test_junit_errors_and_inconclusive(tmp_path):
    result = assess([{"a": 1}], limits={"max_batch_bytes": 1})
    xml = ET.parse(write_report(result, tmp_path / "report.xml", "junit")).getroot()
    assert xml.attrib["errors"] == "1"
    assert int(xml.attrib["skipped"]) >= 1
    assert Result(project="x", source="x", profile="general").status == Status.INCONCLUSIVE


def test_cli_help_version_init_profile_and_reports(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    help_result = runner.invoke(app, ["--help"])
    assert help_result.exit_code == 0
    assert help_result.stdout.isascii()
    version = runner.invoke(app, ["version"])
    assert version.exit_code == 0
    assert "0.1.0" in version.stdout
    assert runner.invoke(app, ["init"]).exit_code == 0
    assert runner.invoke(app, ["init"]).exit_code == 2
    (tmp_path / "data.csv").write_text("id\n1\n2\n")
    assert runner.invoke(app, ["profile", "--config", "aidataready.yaml"]).exit_code == 0
    checked = runner.invoke(app, ["check", "--config", "aidataready.yaml"])
    assert checked.exit_code == 0, checked.output
    assert "PASS" in checked.output
    for format in ["html", "json", "junit"]:
        generated = runner.invoke(app, ["report", "--format", format])
        assert generated.exit_code == 0, generated.output
    (tmp_path / "data.csv").write_text("id\n1\n1\n")
    assert runner.invoke(app, ["check"]).exit_code == 1
    (tmp_path / "data.csv").unlink()
    assert runner.invoke(app, ["check"]).exit_code == 2
    assert runner.invoke(app, ["profile"]).exit_code == 2


def test_cli_invalid_config_and_output_errors_are_safe(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert runner.invoke(app, ["check"]).exit_code == 2
    path = tmp_path / "bad.yaml"
    path.write_text("project: {name: test}\nsource: {type: csv, password: secret}\n")
    error = runner.invoke(app, ["check", "-c", str(path)])
    assert error.exit_code == 2
    assert "secret" not in error.output
    path.write_text("[")
    assert runner.invoke(app, ["check", "-c", str(path)]).exit_code == 2
    assert runner.invoke(app, ["report"]).exit_code == 2
    assert runner.invoke(app, ["init", "missing/contract.yaml"]).exit_code == 2
    runner.invoke(app, ["init"])
    (tmp_path / "data.csv").write_text("id\n1\n")
    assert runner.invoke(app, ["check", "--output", "missing/result.json"]).exit_code == 2


def test_pandera_uses_existing_schema_without_failure_samples():
    pa = pytest.importorskip("pandera.pandas")
    schema = pa.DataFrameSchema({"id": pa.Column(int, pa.Check.ge(1))}, strict=True)
    adapter = PanderaRule(schema)
    assert adapter.validate(pd.DataFrame({"id": [1, 2]})).status == Status.PASS
    failure = adapter.validate(pd.DataFrame({"id": [-12345]}))
    assert failure.status == Status.FAIL
    assert "-12345" not in str(failure.model_dump())
