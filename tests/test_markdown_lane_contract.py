from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.markdown_lane_contract import LANE_ORDER, validate_rust_skill_lanes

REPO_ROOT = Path(__file__).resolve().parents[1]
RUST_ROOT_SKILLS = (
    "nt-trading",
    "nt-backtest",
    "nt-signals",
    "nt-live",
    "nt-data",
    "nt-implement",
)


def test_rust_root_skills_have_structurally_valid_lanes() -> None:
    errors = [
        error
        for skill in RUST_ROOT_SKILLS
        for error in validate_rust_skill_lanes(
            REPO_ROOT / "skills" / skill / "SKILL.md",
            REPO_ROOT,
        )
    ]

    assert errors == []


def test_four_visible_lanes_are_required_in_rust_first_order(tmp_path: Path) -> None:
    path = tmp_path / "skills/nt-data/SKILL.md"
    _write(path, _document(tuple(reversed(LANE_ORDER))))

    errors = validate_rust_skill_lanes(path, tmp_path)

    assert any("not in Rust-first order" in error for error in errors)


def test_rust_production_rejects_python_fences(tmp_path: Path) -> None:
    path = tmp_path / "skills/nt-data/SKILL.md"
    text = _document(LANE_ORDER).replace(
        "## Rust production lane\n",
        "## Rust production lane\n```python\nprint('wrong lane')\n```\n",
    )
    _write(path, text)

    errors = validate_rust_skill_lanes(path, tmp_path)

    assert any("Rust production lane contains a Python fence" in error for error in errors)


def test_migration_lane_must_be_pointer_only(tmp_path: Path) -> None:
    path = tmp_path / "skills/nt-data/SKILL.md"
    text = _document(LANE_ORDER).replace(
        "migration_reference/python\n",
        "migration_reference/python\n```python\nprint('copyable')\n```\n",
    )
    _write(path, text)

    errors = validate_rust_skill_lanes(path, tmp_path)

    assert any("migration lane must be pointer-only" in error for error in errors)


def test_source_pinned_lane_requires_snapshot_link_and_sha(tmp_path: Path) -> None:
    path = tmp_path / "skills/nt-data/SKILL.md"
    text = _document(LANE_ORDER).replace(
        "references/developer_guide/rust.md at " + "a" * 40,
        "current upstream notes",
    )
    _write(path, text)

    errors = validate_rust_skill_lanes(path, tmp_path)

    assert any("developer-guide link" in error for error in errors)
    assert any("immutable source metadata" in error for error in errors)


def test_pyo3_python_control_plane_rejects_execution_authority(tmp_path: Path) -> None:
    path = tmp_path / "skills/nt-data/SKILL.md"
    text = _document(LANE_ORDER).replace(
        "## PyO3 control-plane lane\n",
        "## PyO3 control-plane lane\n```python\nself.submit_order(order)\n```\n",
    )
    _write(path, text)

    errors = validate_rust_skill_lanes(path, tmp_path)

    assert any("execution authority" in error for error in errors)


def _document(lanes: tuple[str, ...]) -> str:
    lines = ["# Data", "", "## NT V2 Rust readiness gates", "", "gates", ""]
    for lane in lanes:
        lines.extend((f"## {lane}", ""))
        if lane == "Migration/reference lane":
            lines.extend(("migration_reference/python", ""))
        elif lane == "Source-pinned upstream lane":
            lines.extend(("references/developer_guide/rust.md at " + "a" * 40, ""))
    return "\n".join(lines)


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
