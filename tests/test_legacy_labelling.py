from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_clean_tree_passes_legacy_labelling_gate() -> None:
    result = subprocess.run(
        [sys.executable, "tools/check_legacy_labelling.py"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize(
    "relative_path, guidance",
    [
        ("skills/nt-example/SKILL.md", "Use cdef and cimport in a .pyx wrapper.\n"),
        ("references/example.md", "Call the removed v1 LegacyApi directly.\n"),
        ("templates/example.md", "Implement this wrapper with cpdef.\n"),
    ],
)
def test_unlabelled_scoped_legacy_guidance_fails(
    tmp_path: Path,
    relative_path: str,
    guidance: str,
) -> None:
    path = tmp_path / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(guidance, encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "tools/check_legacy_labelling.py"),
            "--root",
            str(tmp_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert f"unlabelled legacy/Cython/v1 guidance in {relative_path}" in result.stdout


@pytest.mark.parametrize("status", ["Pass", "Blocked"])
def test_readiness_card_does_not_suppress_unlabelled_guidance(
    tmp_path: Path,
    status: str,
) -> None:
    path = tmp_path / "skills/nt-example/SKILL.md"
    path.parent.mkdir(parents=True)
    path.write_text(
        "# Example\n\n"
        "## NT V2 Rust readiness gates\n\n"
        "| Gate | Criterion | Status | Evidence |\n"
        "| --- | --- | --- | --- |\n"
        "| G0 Scope | Rust-first | Pass | evidence |\n"
        f"| G1 Legacy labelling | Label old APIs | {status} | evidence |\n\n"
        "Use v1 LegacyApi directly in current work.\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "tools/check_legacy_labelling.py"),
            "--root",
            str(tmp_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "unlabelled legacy/Cython/v1 guidance" in result.stdout


def test_nested_skill_reference_is_in_mandatory_scope(tmp_path: Path) -> None:
    path = tmp_path / "skills/nt-example/references/example.md"
    path.parent.mkdir(parents=True)
    path.write_text("Use cdef and cimport in a .pyx wrapper.\n", encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "tools/check_legacy_labelling.py"),
            "--root",
            str(tmp_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "skills/nt-example/references/example.md" in result.stdout


def test_migration_note_within_five_lines_passes(tmp_path: Path) -> None:
    path = tmp_path / "templates/example.md"
    path.parent.mkdir(parents=True)
    path.write_text(
        "legacy: migration/reference-only; prefer Rust/PyO3 for new work.\n"
        "\n"
        "This retained example uses cdef in a historical .pyx wrapper.\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "tools/check_legacy_labelling.py"),
            "--root",
            str(tmp_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
