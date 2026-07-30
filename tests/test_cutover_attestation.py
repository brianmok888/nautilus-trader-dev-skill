from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
REQUIRED_COMMANDS = (
    "uv run pytest -q --ignore=tests/test_quality_gates.py",
    "uv run pytest -q tests/test_quality_gates.py",
    "uv run --with ruff ruff check .",
    "uv run python tools/check_legacy_labelling.py",
    "uv run python tools/check_dev_guide_sync.py",
    "uv run python tools/check_dev_guide_snapshot_sync.py",
    "uv run python tools/check_upstream_freshness.py",
    "uv run python tools/check_skill_g2_harnesses.py --check-cards",
    "python3 -m compileall -q tools tests skills/nt-evomap-integration/python_sidecar/brainstorming_evomap",
    "git diff --check",
)


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
                    {"command": command, "returncode": 0, "output_sha256": "1" * 64}
                    for command in REQUIRED_COMMANDS
                ],
                "code_reviewer": {"verdict": "APPROVE", "artifact": "/tmp/reviewer.txt"},
                "architect": {"status": "CLEAR", "artifact": "/tmp/architect.txt"},
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
        "commands": [
            {"command": command, "returncode": 0, "output_sha256": "1" * 64}
            for command in REQUIRED_COMMANDS
        ],
        "code_reviewer": {"verdict": "APPROVE", "artifact": "/tmp/reviewer.txt"},
        "architect": {"status": "CLEAR", "artifact": "/tmp/architect.txt"},
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


def test_external_attestation_requires_full_command_inventory_and_review_artifacts(
    tmp_path: Path,
) -> None:
    manifest = REPO_ROOT / "references" / "upstream-delta-review.json"
    attestation = tmp_path / "attestation.json"
    _write_attestation(attestation, manifest)
    payload = json.loads(attestation.read_text(encoding="utf-8"))
    payload["commands"].pop()
    payload["code_reviewer"].pop("artifact")
    payload["architect"].pop("artifact")
    attestation.write_text(json.dumps(payload), encoding="utf-8")

    result = _run(attestation)

    assert result.returncode == 1
    assert "commands: missing required commands" in result.stderr
    assert "code_reviewer.artifact" in result.stderr
    assert "architect.artifact" in result.stderr
