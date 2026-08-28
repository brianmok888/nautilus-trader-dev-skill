from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path

_HEADER = re.compile(
    r"^\[(?P<id>NT-\d{4}-\d{2}-\d{2}-\d{2})\] "
    r"\[(?P<priority>P[0-2])\] "
    r"\[(?P<status>OPEN|CLOSED(?: \d{4}-\d{2}-\d{2})?)\] "
    r"(?P<title>\S.*)$"
)
_FIELD = re.compile(r"^  (?P<name>[a-z][a-z0-9-]*): (?P<value>\S.*)$")


@dataclass(frozen=True)
class Finding:
    identifier: str
    priority: str
    status: str
    title: str
    line: int
    fields: dict[str, str]


def _parse_findings(path: Path) -> tuple[list[Finding], list[str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    findings: list[Finding] = []
    errors: list[str] = []
    current: Finding | None = None
    for line_number, line in enumerate(lines, 1):
        if line.startswith("[") and "] [P" in line:
            match = _HEADER.fullmatch(line)
            if match is None:
                errors.append(f"line {line_number}: invalid finding header")
                current = None
                continue
            current = Finding(
                identifier=match["id"],
                priority=match["priority"],
                status=match["status"],
                title=match["title"],
                line=line_number,
                fields={},
            )
            findings.append(current)
            continue
        field = _FIELD.fullmatch(line)
        if field is not None and current is not None:
            current.fields[field["name"]] = field["value"]
    return findings, errors


def validate_findings(path: Path) -> list[str]:
    findings, errors = _parse_findings(path)
    seen: dict[str, int] = {}
    for finding in findings:
        previous = seen.get(finding.identifier)
        if previous is not None:
            errors.append(
                f"line {finding.line}: duplicate finding ID {finding.identifier}; first declared at line {previous}"
            )
        else:
            seen[finding.identifier] = finding.line
        required = {"evidence", "fix"}
        is_current_schema = finding.identifier.startswith("NT-2026-08-28-")
        if finding.status == "OPEN":
            required.update({"file", "acceptance-test"})
        elif is_current_schema:
            required.add("closure")
        missing = sorted(required - finding.fields.keys())
        if missing:
            errors.append(
                f"line {finding.line}: {finding.identifier} missing {', '.join(missing)}"
            )
        if (
            is_current_schema
            and finding.status.startswith("CLOSED")
            and "closure" not in finding.fields
        ):
            errors.append(
                f"line {finding.line}: {finding.identifier} missing closure proof"
            )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current Findings ledger schema"
    )
    parser.add_argument(
        "path",
        nargs="?",
        type=Path,
        default=Path("docs/tracking/Findings.md"),
    )
    args = parser.parse_args()
    errors = validate_findings(args.path)
    if errors:
        print("Findings schema check failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Findings schema check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
