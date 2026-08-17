from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REMOVED_PATHS = (
    "tests/test_cutover_attestation.py",
    "tools/check_cutover_attestation.py",
    ".superpowers",
    "docs/plans",
    "docs/superpowers",
    "docs/handoffs",
    "docs/cleanup-plan.md",
    "docs/cleanup-design.md",
    "docs/tracking/AGENTS.md.scaffold",
)

def test_non_nt_and_historical_artifacts_are_removed() -> None:
    for relative_path in REMOVED_PATHS:
        assert not (ROOT / relative_path).exists(), relative_path

def test_main_router_states_master_prompt_boundaries() -> None:
    router = (ROOT / "skills/nt" / "SKILL.md").read_text(encoding="utf-8")

    assert "NautilusTrader development only" in router
    assert "read-only ground truth" in router
    assert "Do not modify the upstream" in router
