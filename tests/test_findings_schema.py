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
  file: docs/a.md:1
  evidence: reproduced
  fix: repair it
  acceptance-test: command exits zero

[NT-2026-08-28-01] [P1] [OPEN] Duplicate two.
  file: docs/b.md:1
  evidence: reproduced
  fix: repair it
  acceptance-test: command exits zero
""",
        encoding="utf-8",
    )

    errors = validate_findings(ledger)

    assert any("invalid finding header" in error for error in errors)
    assert any("duplicate finding ID" in error for error in errors)


def test_findings_schema_requires_open_acceptance_and_closed_proof(
    tmp_path: Path,
) -> None:
    ledger = tmp_path / "Findings.md"
    ledger.write_text(
        """# Findings

## Open findings

[NT-2026-08-28-01] [P1] [OPEN] Missing acceptance.
  file: docs/a.md:1
  evidence: reproduced
  fix: repair it

[NT-2026-08-28-02] [P2] [CLOSED] Missing closure.
  file: docs/b.md:1
  evidence: reproduced
  fix: repaired
""",
        encoding="utf-8",
    )

    errors = validate_findings(ledger)

    assert any("acceptance-test" in error for error in errors)
    assert any("closure" in error for error in errors)
