from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path

_HEADER = re.compile(
    r"^\[(?P<id>NT-\d{4}-\d{2}-\d{2}-\d{2,3})\] "
    r"\[(?P<priority>P[0-2])\] "
    r"\[(?P<status>OPEN|CLOSED(?: \d{4}-\d{2}-\d{2})?)\] "
    r"(?P<title>\S.*)$"
)
_FIELD = re.compile(r"^  (?P<name>[a-z][a-z0-9-]*): (?P<value>\S.*)$")
_FIELD_LIKE = re.compile(r"^\s+[a-z][a-z0-9-]*( \d{4}-\d{2}-\d{2})?: \S")
_CANDIDATE = re.compile(r"^\[[^\]]+\] \[")
_PATH_LINE = re.compile(r"(?<![\w./-])(?P<path>[A-Za-z0-9._][\w./+-]*?):(?P<line>\d+)(?!\d)")
_CURRENT_DATE = "2026-08-28"
_CURRENT_FIELDS = frozenset(
    {"file", "evidence", "fix", "closure", "closure-proof", "acceptance-test", "correction"}
)


@dataclass(frozen=True)
class Finding:
    identifier: str
    priority: str
    status: str
    title: str
    line: int
    fields: dict[str, str]


def _uses_current_schema(identifier: str) -> bool:
    return identifier.removeprefix("NT-").rsplit("-", 1)[0] >= _CURRENT_DATE


def _repo_root(ledger: Path) -> Path:
    for ancestor in ledger.resolve().parents:
        if (ancestor / ".git").exists():
            return ancestor
    return ledger.resolve().parent


def _citation_is_valid(root: Path, citation: re.Match[str]) -> bool:
    path = root / citation["path"]
    if not path.is_file():
        return False
    try:
        line_count = len(path.read_text(encoding="utf-8", errors="replace").splitlines())
    except OSError:
        return False
    return 1 <= int(citation["line"]) <= max(line_count, 1)


def _parse_findings(path: Path) -> tuple[list[Finding], list[str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    findings: list[Finding] = []
    errors: list[str] = []
    current: Finding | None = None
    for line_number, line in enumerate(lines, 1):
        if _CANDIDATE.match(line):
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
            name = field["name"]
            is_current = _uses_current_schema(current.identifier)
            duplicate = name in current.fields
            if duplicate and is_current:
                errors.append(
                    f"line {line_number}: duplicate field {name} in {current.identifier}"
                )
            current.fields.setdefault(name, field["value"])
            if not duplicate and is_current and name not in _CURRENT_FIELDS:
                errors.append(
                    f"line {line_number}: unknown field {name} in {current.identifier}"
                )
            continue
        if (
            current is not None
            and _uses_current_schema(current.identifier)
            and _FIELD_LIKE.match(line) is not None
            and field is None
        ):
            errors.append(
                f"line {line_number}: malformed field line in {current.identifier}"
            )
    if not findings:
        errors.append("ledger contains no findings")
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
        is_current_schema = _uses_current_schema(finding.identifier)
        if finding.status == "OPEN":
            required.update({"file", "acceptance-test"})
        elif is_current_schema:
            required.add("closure")
        missing = sorted(required - finding.fields.keys())
        if missing:
            errors.append(
                f"line {finding.line}: {finding.identifier} missing {', '.join(missing)}"
            )
        if is_current_schema and "file" in finding.fields:
            citations = list(_PATH_LINE.finditer(finding.fields["file"]))
            if not citations:
                errors.append(
                    f"line {finding.line}: {finding.identifier} file field has no path:line citation"
                )
            else:
                root = _repo_root(path)
                if not any(_citation_is_valid(root, c) for c in citations):
                    errors.append(
                        f"line {finding.line}: {finding.identifier} file field cites no resolvable repository path:line"
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
