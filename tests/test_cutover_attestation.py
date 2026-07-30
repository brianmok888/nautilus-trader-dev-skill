from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def _repo_sha() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _write_attestation(path: Path, manifest: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "repo_sha": _repo_sha(),
                "manifest": {
                    "path": manifest.relative_to(REPO_ROOT).as_posix(),
                    "sha256": hashlib.sha256(manifest.read_bytes()).hexdigest(),
                },
                "commands": [
                    {"command": "uv run pytest tests/", "returncode": 0},
                    {"command": "uv run ruff check .", "returncode": 0},
                ],
                "code_reviewer": {"verdict": "APPROVE"},
                "architect": {"status": "CLEAR"},
            },
        ),
        encoding="utf-8",
    )


def _run(attestation: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "tools/check_cutover_attestation.py",
            "--attestation",
            str(attestation),
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def test_external_attestation_accepts_exact_sha_manifest_and_green_reviews(
    tmp_path: Path,
) -> None:
    manifest = REPO_ROOT / "references" / "upstream-delta-review.json"
    attestation = tmp_path / "attestation.json"
    _write_attestation(attestation, manifest)

    result = _run(attestation)

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Cutover attestation valid" in result.stdout


def test_external_attestation_rejects_wrong_repo_sha(tmp_path: Path) -> None:
    manifest = REPO_ROOT / "references" / "upstream-delta-review.json"
    attestation = tmp_path / "attestation.json"
    _write_attestation(attestation, manifest)
    payload = json.loads(attestation.read_text(encoding="utf-8"))
    payload["repo_sha"] = "0" * 40
    attestation.write_text(json.dumps(payload), encoding="utf-8")

    result = _run(attestation)

    assert result.returncode == 1
    assert "repo_sha" in result.stderr


def test_external_attestation_rejects_changed_manifest(tmp_path: Path) -> None:
    manifest = tmp_path / "manifest.json"
    manifest.write_text("{}\n", encoding="utf-8")
    attestation = tmp_path / "attestation.json"
    payload = {
        "schema_version": 1,
        "repo_sha": _repo_sha(),
        "manifest": {
            "path": str(manifest),
            "sha256": "0" * 64,
        },
        "commands": [{"command": "pytest", "returncode": 0}],
        "code_reviewer": {"verdict": "APPROVE"},
        "architect": {"status": "CLEAR"},
    }
    attestation.write_text(json.dumps(payload), encoding="utf-8")

    result = _run(attestation)

    assert result.returncode == 1
    assert "manifest.sha256" in result.stderr


def test_external_attestation_rejects_failed_command_or_review(tmp_path: Path) -> None:
    manifest = REPO_ROOT / "references" / "upstream-delta-review.json"
    attestation = tmp_path / "attestation.json"
    _write_attestation(attestation, manifest)
    payload = json.loads(attestation.read_text(encoding="utf-8"))
    payload["commands"][0]["returncode"] = 1
    payload["code_reviewer"]["verdict"] = "REQUEST_CHANGES"
    payload["architect"]["status"] = "BLOCKED"
    attestation.write_text(json.dumps(payload), encoding="utf-8")

    result = _run(attestation)

    assert result.returncode == 1
    assert "commands[0].returncode" in result.stderr
    assert "code_reviewer.verdict" in result.stderr
    assert "architect.status" in result.stderr
