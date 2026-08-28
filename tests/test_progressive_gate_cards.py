from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / "skills"

REQUIRED_GATES = (
    "Architecture Consistency",
    "Dependency and Build Health",
    "API and Binding Contract",
    "Correctness Test Pyramid",
    "Performance Regression Control",
    "Resilience and Failure Recovery",
    "Observability and Operability",
    "Security Safety and Governance",
    "Release and Rollback Readiness",
    "Integration and Acceptance",
    "Continuous Improvement",
)


def test_progressive_gate_template_declares_complete_contract() -> None:
    template = (REPO_ROOT / "docs/tracking/CutoverGateTemplate.md").read_text(
        encoding="utf-8"
    )

    for gate in REQUIRED_GATES:
        assert gate in template
    for field in (
        "Objective",
        "Applicability",
        "Evidence",
        "Status",
        "Owner",
        "Last verified",
        "Next action",
        "Blocker",
    ):
        assert field in template
    assert "Pass" in template
    assert "Pending" in template
    assert "Blocked" in template


def test_every_skill_routes_to_progressive_gate_template() -> None:
    skill_files = sorted(SKILL_ROOT.glob("*/SKILL.md"))

    assert len(skill_files) == 17
    for path in skill_files:
        text = path.read_text(encoding="utf-8")
        assert "docs/tracking/CutoverGateTemplate.md" in text, path


def test_end_to_end_guide_requires_progressive_gate_review() -> None:
    guide = (REPO_ROOT / "docs/end_to_end_guide.md").read_text(encoding="utf-8")

    assert "Progressive Cutover Gates" in guide
    for gate in REQUIRED_GATES:
        assert gate in guide
