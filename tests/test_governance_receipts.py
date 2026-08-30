from __future__ import annotations

import hashlib
import json
from pathlib import Path

from tools.check_governance_receipts import main, validate_receipt


def _valid_receipt() -> dict[str, object]:
    output = "12 passed in 0.31s\n"
    return {
        "schema_version": 1,
        "mission": "examples",
        "receipt": "phase-3-verification",
        "finding_id": "NT-001",
        "owner_stage": "phase-3",
        "evidence_state": "verified",
        "severity": "none",
        "command": "python -m pytest -q tests/test_example.py",
        "exit_code": 0,
        "output_sha256": hashlib.sha256(output.encode()).hexdigest(),
        "output_excerpt": output,
        "redactions": [],
        "recorded_at": "2026-08-29T16:00:00Z",
    }


def test_validate_receipt_accepts_safe_versioned_receipt() -> None:
    assert validate_receipt(_valid_receipt(), Path("receipt.json")) == []


def test_validate_receipt_keeps_priority_independent_from_evidence() -> None:
    receipt = _valid_receipt()
    receipt["severity"] = "P0"
    receipt["evidence_state"] = "unverified"

    assert validate_receipt(receipt, Path("receipt.json")) == []


def test_validate_receipt_rejects_schema_digest_and_secret_failures() -> None:
    receipt = _valid_receipt()
    receipt["schema_version"] = 2
    receipt["output_excerpt"] = "-----BEGIN PRIVATE KEY-----"
    receipt["output_sha256"] = "0" * 64

    errors = validate_receipt(receipt, Path("receipt.json"))

    assert any("schema_version" in error for error in errors)
    assert any("output_sha256" in error for error in errors)
    assert any("secret-like content" in error for error in errors)


def test_validate_receipt_requires_redaction_metadata() -> None:
    receipt = _valid_receipt()
    receipt["command"] = "curl -H 'Authorization: Bearer [REDACTED]' example.test"

    errors = validate_receipt(receipt, Path("receipt.json"))

    assert any("redactions" in error for error in errors)


def test_main_validates_tree_and_binds_identity_to_path(
    capsys, tmp_path: Path
) -> None:
    receipts = tmp_path / "docs" / "tracking" / "receipts" / "examples"
    receipts.mkdir(parents=True)
    (receipts / "phase-3-verification.json").write_text(
        json.dumps(_valid_receipt()), encoding="utf-8"
    )

    assert main(["--root", str(tmp_path)]) == 0
    assert "validated 1 governance receipt" in capsys.readouterr().out

    mismatched = _valid_receipt()
    mismatched["receipt"] = "different-receipt"
    (receipts / "phase-3-verification.json").write_text(
        json.dumps(mismatched), encoding="utf-8"
    )

    assert main(["--root", str(tmp_path)]) == 1
    assert "does not match receipt mission/receipt" in capsys.readouterr().err


def test_main_rejects_legacy_free_form_receipts(capsys, tmp_path: Path) -> None:
    receipts = tmp_path / "docs" / "tracking" / "receipts" / "examples"
    receipts.mkdir(parents=True)
    (receipts / "NT-001.txt").write_text("12 passed", encoding="utf-8")

    assert main(["--root", str(tmp_path)]) == 1
    assert "unsupported receipt file" in capsys.readouterr().err
