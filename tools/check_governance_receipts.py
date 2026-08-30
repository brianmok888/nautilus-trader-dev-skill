"""Validate versioned, secret-safe governance evidence receipts.

Usage:
    python3 tools/check_governance_receipts.py
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1
RECEIPTS_RELATIVE_PATH = Path("docs/tracking/receipts")
REQUIRED_FIELDS = {
    "schema_version",
    "mission",
    "receipt",
    "finding_id",
    "owner_stage",
    "evidence_state",
    "severity",
    "command",
    "exit_code",
    "output_sha256",
    "output_excerpt",
    "redactions",
    "recorded_at",
}
OWNER_STAGES = {"phase-2", "phase-3"}
EVIDENCE_STATES = {"verified", "verified-manual", "unverified"}
SEVERITIES = {"none", "P0", "P1", "P2"}
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FINDING_ID_RE = re.compile(r"^NT-(?:\d{3}|\d{4}-\d{2}-\d{2}-\d+)$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
RFC3339_UTC_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
SECRET_PATTERNS = (
    re.compile(r"(?i)authorization\s*:\s*(?:bearer|basic)\s+[^\s'\"]+"),
    re.compile(r"(?i)\bbearer\s+[^\s'\"]+"),
    re.compile(r"(?i)(?:api[_-]?key|token|secret|password)\s*[=:]\s*[^\s,;]+"),
    re.compile(r"(?i)\b(?:postgres(?:ql)?|mysql|redis)://[^\s/@:]+:[^\s/@]+@"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    re.compile(r"-----BEGIN (?:[A-Z0-9 ]+ )?PRIVATE KEY-----"),
)


def _field_text(receipt: dict[str, Any], name: str) -> str:
    value = receipt.get(name)
    return value if isinstance(value, str) else ""


def _contains_secret(value: str) -> bool:
    return any(
        "[REDACTED]" not in match.group(0)
        for pattern in SECRET_PATTERNS
        for match in pattern.finditer(value)
    )


def validate_receipt(receipt: object, path: Path) -> list[str]:
    """Return validation errors for one decoded receipt."""
    if not isinstance(receipt, dict):
        return [f"{path}: receipt root must be a JSON object"]

    errors: list[str] = []
    fields = set(receipt)
    missing = sorted(REQUIRED_FIELDS - fields)
    unknown = sorted(fields - REQUIRED_FIELDS)
    if missing:
        errors.append(f"{path}: missing fields: {', '.join(missing)}")
    if unknown:
        errors.append(f"{path}: unknown fields: {', '.join(unknown)}")

    if receipt.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"{path}: schema_version must equal {SCHEMA_VERSION}")

    for field in ("mission", "receipt"):
        value = _field_text(receipt, field)
        if not SLUG_RE.fullmatch(value):
            errors.append(f"{path}: {field} must be lowercase kebab-case")

    finding_id = _field_text(receipt, "finding_id")
    if not FINDING_ID_RE.fullmatch(finding_id):
        errors.append(f"{path}: finding_id must be a stable NT Finding ID")

    owner_stage = receipt.get("owner_stage")
    if owner_stage not in OWNER_STAGES:
        errors.append(f"{path}: owner_stage must be one of {sorted(OWNER_STAGES)}")
    evidence_state = receipt.get("evidence_state")
    if evidence_state not in EVIDENCE_STATES:
        errors.append(
            f"{path}: evidence_state must be one of {sorted(EVIDENCE_STATES)}"
        )
    severity = receipt.get("severity")
    if severity not in SEVERITIES:
        errors.append(f"{path}: severity must be one of {sorted(SEVERITIES)}")

    command = _field_text(receipt, "command")
    excerpt = _field_text(receipt, "output_excerpt")
    if not command:
        errors.append(f"{path}: command must be a non-empty string")
    if not excerpt:
        errors.append(f"{path}: output_excerpt must be a non-empty string")
    exit_code = receipt.get("exit_code")
    if not isinstance(exit_code, int) or isinstance(exit_code, bool):
        errors.append(f"{path}: exit_code must be an integer")

    digest = _field_text(receipt, "output_sha256")
    if not SHA256_RE.fullmatch(digest):
        errors.append(f"{path}: output_sha256 must be lowercase SHA-256")
    elif hashlib.sha256(excerpt.encode()).hexdigest() != digest:
        errors.append(f"{path}: output_sha256 does not match output_excerpt")

    redactions = receipt.get("redactions")
    if not isinstance(redactions, list) or not all(
        isinstance(item, str) and item for item in redactions
    ):
        errors.append(f"{path}: redactions must be an array of non-empty strings")
    elif "[REDACTED]" in f"{command}\n{excerpt}" and not redactions:
        errors.append(f"{path}: redactions must describe each redaction marker")

    if _contains_secret(command):
        errors.append(f"{path}: command contains secret-like content")
    if _contains_secret(excerpt):
        errors.append(f"{path}: output_excerpt contains secret-like content")

    recorded_at = _field_text(receipt, "recorded_at")
    if not RFC3339_UTC_RE.fullmatch(recorded_at):
        errors.append(f"{path}: recorded_at must be UTC YYYY-MM-DDTHH:MM:SSZ")

    return errors


def validate_tree(root: Path) -> tuple[int, list[str]]:
    """Validate every tracked receipt under the repository root."""
    receipts_root = root / RECEIPTS_RELATIVE_PATH
    if not receipts_root.exists():
        return 0, [f"{RECEIPTS_RELATIVE_PATH}: directory is missing"]

    errors: list[str] = []
    count = 0
    for path in sorted(receipts_root.rglob("*")):
        if not path.is_file() or path.name == "README.md":
            continue
        relative_path = path.relative_to(root)
        if path.suffix != ".json":
            errors.append(f"{relative_path}: unsupported receipt file; use JSON")
            continue
        count += 1
        try:
            receipt = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{relative_path}: invalid JSON: {exc}")
            continue
        errors.extend(validate_receipt(receipt, relative_path))
        if isinstance(receipt, dict):
            expected_mission = path.parent.name
            expected_receipt = path.stem
            if (
                receipt.get("mission") != expected_mission
                or receipt.get("receipt") != expected_receipt
            ):
                errors.append(
                    f"{relative_path}: path does not match receipt mission/receipt "
                    f"({expected_mission}/{expected_receipt})"
                )
    return count, errors


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate versioned, secret-safe governance evidence receipts."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="repository root (default: script parent repository)",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    count, errors = validate_tree(args.root.resolve())
    if errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        return 1
    print(f"validated {count} governance receipt{'s' if count != 1 else ''}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
