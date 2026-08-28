from __future__ import annotations

from pathlib import Path

from tools.check_findings_schema import validate_findings


def test_current_findings_ledger_has_valid_schema() -> None:
    root = Path(__file__).resolve().parents[1]

    assert validate_findings(root / "docs/tracking/Findings.md") == []


def test_findings_schema_rejects_malformed_entries(tmp_path: Path) -> None:
    ledger = tmp_path / "Findings.md"
    ledger.write_text(
        """# Findings

## Open findings

[BROKEN] [P9] Finding without status.
  evidence: reproduced
  fix: repair it

[NT-2026-08-28-01] [P1] [OPEN] Duplicate one.
  file: a.md:1
  evidence: reproduced
  fix: repair it
  acceptance-test: command exits zero

[NT-2026-08-28-01] [P1] [OPEN] Duplicate two.
  file: b.md:1
  evidence: reproduced
  fix: repair it
  acceptance-test: command exits zero
""",
        encoding="utf-8",
    )
    _write_cited(tmp_path, "a.md")
    _write_cited(tmp_path, "b.md")

    errors = validate_findings(ledger)

    assert any("invalid finding header" in error for error in errors)
    assert any("duplicate finding ID" in error for error in errors)


def _write_cited(tmp_path: Path, name: str) -> None:
    (tmp_path / name).write_text("line0\n", encoding="utf-8")


def test_findings_schema_rejects_malformed_priority_that_bypasses_prefilter(
    tmp_path: Path,
) -> None:
    ledger = tmp_path / "Findings.md"
    ledger.write_text(
        """# Findings

[NT-2026-08-28-01] [Q1] [OPEN] Malformed priority bypass.
  file: docs/a.md:1
  evidence: reproduced
  fix: repair it
  acceptance-test: command exits zero
""",
        encoding="utf-8",
    )

    errors = validate_findings(ledger)

    assert any("invalid finding header" in error for error in errors)


def test_findings_schema_rejects_duplicate_fields(tmp_path: Path) -> None:
    ledger = tmp_path / "Findings.md"
    ledger.write_text(
        """# Findings

[NT-2026-08-28-01] [P1] [OPEN] Duplicate field.
  file: docs/a.md:1
  file: docs/b.md:1
  evidence: reproduced
  fix: repair it
  acceptance-test: command exits zero
""",
        encoding="utf-8",
    )

    errors = validate_findings(ledger)

    assert any("duplicate field" in error for error in errors)


def test_findings_schema_rejects_ledger_without_findings(tmp_path: Path) -> None:
    ledger = tmp_path / "Findings.md"
    ledger.write_text("# Findings\n\nNothing recorded.\n", encoding="utf-8")

    errors = validate_findings(ledger)

    assert any("no findings" in error for error in errors)


def test_findings_schema_rejects_malformed_current_field_lines(
    tmp_path: Path,
) -> None:
    ledger = tmp_path / "Findings.md"
    ledger.write_text(
        "# Findings\n\n"
        "[NT-2026-08-28-01] [P1] [OPEN] Malformed field.\n"
        "  file: a.md:1\n"
        "   evidence: wrong indent\n"
        "  fix: repair it\n"
        "  acceptance-test: command exits zero\n",
        encoding="utf-8",
    )
    (tmp_path / "a.md").write_text("line0\n", encoding="utf-8")

    errors = validate_findings(ledger)

    assert any("malformed field line" in error for error in errors)


def test_findings_schema_applies_current_rules_after_migration_date(
    tmp_path: Path,
) -> None:
    ledger = tmp_path / "Findings.md"
    ledger.write_text(
        "# Findings\n\n"
        "[NT-2026-08-29-01] [P1] [CLOSED] Future current-schema finding.\n"
        "  evidence: reproduced\n"
        "  fix: repair it\n"
        "  surprise: rejected\n",
        encoding="utf-8",
    )

    errors = validate_findings(ledger)

    assert any("unknown field surprise" in error for error in errors)
    assert any("missing closure proof" in error for error in errors)


def test_findings_schema_rejects_unknown_current_field(tmp_path: Path) -> None:
    ledger = tmp_path / "Findings.md"
    ledger.write_text(
        "# Findings\n\n"
        "[NT-2026-08-28-01] [P1] [OPEN] Unknown field.\n"
        "  file: a.md:1\n"
        "  evidence: reproduced\n"
        "  bogus: not a field\n"
        "  fix: repair it\n"
        "  acceptance-test: command exits zero\n",
        encoding="utf-8",
    )
    (tmp_path / "a.md").write_text("line0\n", encoding="utf-8")

    errors = validate_findings(ledger)

    assert any("unknown field" in error for error in errors)


def test_current_finding_requires_resolvable_path_line_citation(
    tmp_path: Path,
) -> None:
    missing = tmp_path / "Findings.md"
    missing.write_text(
        "# Findings\n\n"
        "[NT-2026-08-28-01] [P1] [OPEN] No citation.\n"
        "  file: docs/**\n"
        "  evidence: reproduced\n"
        "  fix: repair it\n"
        "  acceptance-test: command exits zero\n",
        encoding="utf-8",
    )
    (tmp_path / "a.md").write_text("line0\n", encoding="utf-8")

    errors = validate_findings(missing)

    assert any("path:line" in error for error in errors)

    wrong_line = tmp_path / "Findings2.md"
    wrong_line.write_text(
        "# Findings\n\n"
        "[NT-2026-08-28-01] [P1] [OPEN] Out-of-range line.\n"
        "  file: a.md:999\n"
        "  evidence: reproduced\n"
        "  fix: repair it\n"
        "  acceptance-test: command exits zero\n",
        encoding="utf-8",
    )

    errors = validate_findings(wrong_line)

    assert any("path:line" in error for error in errors)


def test_current_closed_finding_also_requires_path_line_citation(
    tmp_path: Path,
) -> None:
    ledger = tmp_path / "Findings.md"
    ledger.write_text(
        "# Findings\n\n"
        "[NT-2026-08-28-01] [P1] [CLOSED] Closed without citation.\n"
        "  file: references/developer_guide/\n"
        "  evidence: reproduced\n"
        "  fix: repaired\n"
        "  closure: command exits zero\n",
        encoding="utf-8",
    )

    errors = validate_findings(ledger)

    assert any("path:line" in error for error in errors)


def test_findings_schema_requires_open_acceptance_and_closed_proof(
    tmp_path: Path,
) -> None:
    ledger = tmp_path / "Findings.md"
    ledger.write_text(
        """# Findings

## Open findings

[NT-2026-08-28-01] [P1] [OPEN] Missing acceptance.
  file: a.md:1
  evidence: reproduced
  fix: repair it

[NT-2026-08-28-02] [P2] [CLOSED] Missing closure.
  file: b.md:1
  evidence: reproduced
  fix: repaired
""",
        encoding="utf-8",
    )
    _write_cited(tmp_path, "a.md")
    _write_cited(tmp_path, "b.md")

    errors = validate_findings(ledger)

    assert any("acceptance-test" in error for error in errors)
    assert any("closure" in error for error in errors)
