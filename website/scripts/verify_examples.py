"""Verify the site's commands against the real CLI and save synthetic report artifacts."""

import json
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "website/public/examples"
OUTPUT.mkdir(parents=True, exist_ok=True)
ENV = {**os.environ, "PYTHONPATH": str(ROOT / "src"), "NO_COLOR": "1", "TERM": "dumb"}
PREFIX = [sys.executable, "-c", "from lynvera_aidataready.cli import app; app()"]


def run(*args: str, expected: int = 0) -> str:
    result = subprocess.run(
        [*PREFIX, *args], cwd=ROOT, env=ENV, capture_output=True, text=True, check=False
    )
    assert result.returncode == expected, (args, result.returncode, result.stdout, result.stderr)
    return result.stdout.strip()


version = run("version")
run("--help")
for command in ("init", "check", "profile", "report"):
    run(command, "--help")

summaries = {}
for name, config, status, count, code in (
    ("rag", "rag", "PASS", 2, 0),
    ("duplicates", "duplicate-ids", "FAIL", 2, 1),
    ("ml", "machine-learning", "PASS", 4, 0),
    ("agent", "agent-tools", "PASS", 2, 0),
):
    target = OUTPUT / f"{name}.json"
    summary = run(
        "check", "--config", f"examples/{config}.yaml", "--output", str(target), expected=code
    )
    data = json.loads(target.read_text())
    assert data["status"] == status
    assert data["rows_examined"] == count
    if name == "duplicates":
        finding = next(f for f in data["findings"] if f["code"] == "structure.unique")
        assert finding["violations"] == 1
    summaries[name] = {"summary": summary.splitlines()[0], "exitCode": code, "records": count}
    for format_name, suffix in (("html", "html"), ("junit", "xml"), ("json", "json")):
        run(
            "report",
            "--input",
            str(target),
            "--format",
            format_name,
            "--output",
            str(OUTPUT / f"{name}-report.{suffix}"),
        )

stats = json.loads(run("profile", "--config", "examples/rag.yaml"))
assert stats
record = {
    "version": version,
    "verifiedAt": datetime.now(UTC).isoformat(),
    "sourceCommit": subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip(),
    "synthetic": True,
    "examples": summaries,
}
(OUTPUT / "verification.json").write_text(json.dumps(record, indent=2) + "\n")
print(json.dumps(record, indent=2))
