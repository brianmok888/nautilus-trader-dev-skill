import hashlib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_PATH = REPO_ROOT / "skills/nt-testing/SKILL.md"
PINNED_SPEC_PATH = REPO_ROOT / "references/developer_guide/spec_exec_testing.md"
PINNED_SPEC_SHA256 = "6984b46a8f845603a53bf88890b5e173d62722c0d461e6fcc30090ddada6c5e5"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def execution_freshness_section() -> str:
    skill = read(SKILL_PATH)
    start = skill.index("## Execution specification freshness")
    end = skill.index("## V2 nightly migration regression coverage", start)
    return skill[start:end]


def test_pinned_execution_spec_snapshot_remains_immutable() -> None:
    digest = hashlib.sha256(PINNED_SPEC_PATH.read_bytes()).hexdigest()

    assert digest == PINNED_SPEC_SHA256


def test_current_overlay_versions_the_execution_spec_delta() -> None:
    section = execution_freshness_section()

    assert "baa667bc3c57cd3f639d9722b6fd592e4fcde36f" in section
    assert "45903fc8" in section
    assert "184e231f192ea7410aeb7730d6118fedfdf2c4d7" in section
    assert "pinned" in section.lower()
    assert "differs" in section.lower()
    assert "unchanged between the pinned snapshot" not in section


def test_current_overlay_requires_exact_precision_residual_and_no_open_orders() -> None:
    section = execution_freshness_section()

    assert "TC-E06" in section
    assert "TC-E82" in section
    assert "close_positions_qty_precision" in section
    assert "exact sub-precision residual" in section
    assert "determined by\n`close_positions_qty_precision`" in section
    assert "no open orders" in section
    assert "arbitrary residual" not in section
