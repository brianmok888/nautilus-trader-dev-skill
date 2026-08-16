from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REMOVED_PATHS = (
    "skills/nt-evomap-integration",
    "references/g2-evidence/nt-evomap-integration.json",
    "skills/nt-implement/legacy_migration/evomap-sidecar-implementation-pattern-optional.md",
    "tests/test_ai_advisory_boundary.py",
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

CURRENT_SCOPE_FILES = (
    "README.md",
    "AGENTS.md",
    "skills/AGENTS.md",
    "skills/nt/SKILL.md",
    "skills/nt-strategy-builder/SKILL.md",
    "docs/end_to_end_guide.md",
    "docs/tracking/Handguard.md",
    "docs/tracking/Structure.md",
    "docs/tracking/Components.md",
    "tools/check_skill_g2_harnesses.py",
)

EXCLUDED_LANE_MARKERS = (
    "nt-evomap-integration",
    "nt-evomap-integration",
    "brainstorming_evomap",
    "advisory_actor",
)


def test_non_nt_and_historical_artifacts_are_removed() -> None:
    for relative_path in REMOVED_PATHS:
        assert not (ROOT / relative_path).exists(), relative_path


def test_pytest_config_has_no_removed_test_ignores() -> None:
    config = (ROOT / "pytest.ini").read_text(encoding="utf-8")

    assert "test_ai_advisory_boundary.py" not in config


def test_current_repository_surface_has_no_excluded_lane_route() -> None:
    for relative_path in CURRENT_SCOPE_FILES:
        text = (ROOT / relative_path).read_text(encoding="utf-8")
        for marker in EXCLUDED_LANE_MARKERS:
            assert marker not in text, f"{relative_path} contains {marker!r}"


def test_main_router_states_master_prompt_boundaries() -> None:
    router = (ROOT / "skills/nt/SKILL.md").read_text(encoding="utf-8")

    assert "NautilusTrader development only" in router
    assert "read-only ground truth" in router
    assert "Do not modify the upstream" in router
    assert "AI and advisory work are outside this repository" in router
