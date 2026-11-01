from enum import StrEnum
from pathlib import Path
from typing import Annotated

import typer
from pydantic import ValidationError
from rich.console import Console
from rich.table import Table
from rich.text import Text

from lynvera_aidataready import Assessment, Status, __version__
from lynvera_aidataready.core.models import Result
from lynvera_aidataready.reporting.writers import read_result, write_report

app = typer.Typer(
    help="Assess local data readiness for AI.",
    no_args_is_help=True,
    pretty_exceptions_enable=False,
    rich_markup_mode=None,
    add_completion=False,
)
console = Console(highlight=False)
ConfigOption = Annotated[Path, typer.Option("--config", "-c", help="YAML contract path.")]


class Format(StrEnum):
    json = "json"
    html = "html"
    junit = "junit"


def run(config: Path) -> Result:
    try:
        return Assessment.from_config(config).run()
    except ValidationError as error:
        fields = ", ".join(".".join(map(str, item["loc"])) for item in error.errors())
        console.print(f"Invalid configuration: {fields}", markup=False)
    except Exception:
        console.print("Cannot read configuration. Check its path and YAML syntax.")
    raise typer.Exit(2)


def summarize(result: Result) -> None:
    console.print(
        f"{result.project}: {result.status.value}. Records: {result.rows_examined}.", markup=False
    )
    table = Table(box=None, show_edge=False, pad_edge=False)
    for name in ["Status", "Check", "Field", "Violations"]:
        table.add_column(name)
    for finding in result.findings:
        table.add_row(
            finding.status.value,
            finding.code,
            Text(str(finding.evidence.get("field", ""))),
            str(finding.violations),
        )
    console.print(table)


@app.command()
def version() -> None:
    """Show the installed version."""
    console.print(__version__)


@app.command()
def init(path: Path = Path("aidataready.yaml")) -> None:
    """Create a small contract without overwriting files."""
    content = """project:
  name: my-project
source:
  type: csv
  path: data.csv
profile: general
rules:
  required_fields: [id]
  unique_fields: [id]
"""
    try:
        with path.open("x", encoding="utf-8") as stream:
            stream.write(content)
    except OSError:
        console.print("Cannot create contract. Check the path or existing file.")
        raise typer.Exit(2) from None
    console.print(f"Created {path}", markup=False)


@app.command()
def profile(config: ConfigOption = Path("aidataready.yaml")) -> None:
    """Show counts without record samples."""
    result = run(config)
    console.print_json(data=result.statistics)
    if not result.complete:
        raise typer.Exit(2)


@app.command()
def check(
    config: ConfigOption = Path("aidataready.yaml"),
    output: Path = Path("aidataready-result.json"),
) -> None:
    """Run readiness checks and save JSON."""
    result = run(config)
    try:
        write_report(result, output)
    except OSError:
        console.print("Cannot write report. Check the output path.")
        raise typer.Exit(2) from None
    summarize(result)
    if result.status in {Status.ERROR, Status.INCONCLUSIVE}:
        raise typer.Exit(2)
    if result.status == Status.FAIL:
        raise typer.Exit(1)


@app.command()
def report(
    input: Path = Path("aidataready-result.json"),
    format: Format = Format.html,
    output: Path | None = None,
) -> None:
    """Convert a saved result to JSON, HTML, or JUnit."""
    suffix = "xml" if format == Format.junit else format.value
    target = output or Path(f"aidataready-report.{suffix}")
    try:
        result = read_result(input)
        write_report(result, target, format.value)
    except Exception:
        console.print("Cannot create report. Check the input result and output path.")
        raise typer.Exit(2) from None
    console.print(f"Created {target}", markup=False)
