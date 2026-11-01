import html
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Literal

from lynvera_aidataready.core.models import Result, Status

ReportFormat = Literal["json", "html", "junit"]


def xml_safe(value: str) -> str:
    return "".join(
        char
        for char in value
        if char in "\t\n\r"
        or 32 <= ord(char) <= 0xD7FF
        or 0xE000 <= ord(char) <= 0xFFFD
        or 0x10000 <= ord(char) <= 0x10FFFF
    )


def write_report(result: Result, path: str | Path, format: ReportFormat = "json") -> Path:
    path = Path(path)
    if format == "json":
        content = json.dumps(result.as_dict(), indent=2, ensure_ascii=True)
    elif format == "junit":
        root = ET.Element(
            "testsuite", name=xml_safe(result.project), tests=str(len(result.findings))
        )
        failures = errors = skipped = 0
        for finding in result.findings:
            case = ET.SubElement(
                root,
                "testcase",
                name=xml_safe(f"{finding.code}:{finding.evidence.get('field', '')}"),
                classname=xml_safe(finding.resource),
            )
            detail = xml_safe(f"{finding.violations} violations. {finding.recommendation}")
            if finding.status == Status.FAIL:
                ET.SubElement(case, "failure", message=detail)
                failures += 1
            elif finding.status == Status.ERROR:
                ET.SubElement(case, "error", message=detail)
                errors += 1
            elif finding.status in {Status.INCONCLUSIVE, Status.WARN}:
                ET.SubElement(case, "skipped", message=finding.status.value)
                skipped += 1
        root.set("failures", str(failures))
        root.set("errors", str(errors))
        root.set("skipped", str(skipped))
        content = ET.tostring(root, encoding="unicode")
    elif format == "html":
        content = render_html(result)
    else:
        raise ValueError("Unsupported report format.")
    path.write_text(content, encoding="utf-8")
    return path


def read_result(path: str | Path) -> Result:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    data.pop("status", None)
    return Result.model_validate(data)


def render_html(result: Result) -> str:
    escape = html.escape
    rows = []
    for finding in result.findings:
        detail = json.dumps(
            {"evidence": finding.evidence, "limitations": finding.limitations}, ensure_ascii=True
        )
        rows.append(
            f'<tr data-severity="{escape(finding.severity, quote=True)}" '
            f'data-category="{escape(finding.category, quote=True)}" '
            f'data-source="{escape(finding.resource, quote=True)}">'
            f"<td>{escape(finding.status.value)}</td><td>{escape(finding.code)}</td>"
            f"<td>{escape(finding.resource)}</td><td>{finding.examined}</td>"
            f"<td>{finding.violations}</td><td>{escape(finding.recommendation)}"
            f"<details><summary>Details</summary><pre>{escape(detail)}</pre></details></td></tr>"
        )
    filters = []
    for key in ("severity", "category", "source"):
        values = {getattr(f, "resource" if key == "source" else key) for f in result.findings}
        options = "".join(
            f'<option value="{escape(value, quote=True)}">{escape(value)}</option>'
            for value in sorted(values)
        )
        filters.append(
            f'<label>{key.title()} <select id="{key}"><option value="">All</option>'
            f"{options}</select></label>"
        )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>AIDataReady report</title><style>
body{{font:16px system-ui;max-width:1200px;margin:32px auto;padding:0 16px;color:#17312d}}
table{{width:100%;border-collapse:collapse}}th,td{{padding:12px;border-bottom:1px solid #ddd;
text-align:left;vertical-align:top}}label{{display:inline-block;margin:12px 20px 20px 0}}
select{{padding:6px}}pre{{white-space:pre-wrap;overflow-wrap:anywhere}}summary{{cursor:pointer}}
</style></head><body><h1>{escape(result.project)}</h1>
<p>{escape(result.profile)}: {result.status.value}. Records examined: {result.rows_examined}.</p>
<p>Complete scan: {str(result.complete).lower()}. Checks do not certify model performance.</p>
{"".join(filters)}<table><thead><tr><th>Status</th><th>Check</th><th>Source</th>
<th>Examined</th><th>Violations</th><th>Recommendation</th></tr></thead>
<tbody>{"".join(rows)}</tbody></table><script>
const keys = ['severity', 'category', 'source'];
function filter() {{ document.querySelectorAll('tbody tr').forEach(row => {{
row.hidden = !keys.every(key => !document.getElementById(key).value ||
row.dataset[key] === document.getElementById(key).value); }}); }}
keys.forEach(key => document.getElementById(key).addEventListener('change', filter));
</script></body></html>"""
