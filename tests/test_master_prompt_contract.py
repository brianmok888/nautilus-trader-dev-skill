from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER_PROMPT = ROOT / "docs/prompts/master-prompt.md"


def read_master_prompt() -> str:
    return MASTER_PROMPT.read_text(encoding="utf-8")


def test_master_prompt_preserves_required_execution_sections() -> None:
    prompt = read_master_prompt()

    required_sections = (
        "## Execution contract",
        "### Preflight and ownership",
        "### Upstream currency prerequisite",
        "### States and stop conditions",
        "### Finding format (every finding)",
        "## Phase 3 — Post-Implementation Verification Approval Gate",
        "## Phase 4 — Progressive Gate Checklist (PRIMARY DELIVERABLE)",
        "## Phase 5 — Reconciliation",
        "## Phase 6 — Shipping Approval Gate",
        "### Mission-owned changes exist",
        "### No mission-owned changes",
        "### Final report",
    )

    positions = [prompt.index(section) for section in required_sections]
    assert positions == sorted(positions)


def test_master_prompt_declares_machine_consumed_commands() -> None:
    prompt = read_master_prompt()

    commands = (
        "python3 tools/check_skill_g2_harnesses.py --execute --skill <skill>",
        "python3 tools/check_skill_g2_harnesses.py --check-cards",
        "python3 tools/check_skill_g2_harnesses.py --check-card-declarations",
        "python3 tools/check_upstream_freshness.py --format json",
        "git merge --ff-only <mission-branch>",
        "git push origin main",
    )

    for command in commands:
        assert f"`{command}`" in prompt


def test_master_prompt_defines_complete_finding_record() -> None:
    prompt = read_master_prompt()

    finding_template = (
        "[NT-###] [P0|P1|P2] [OPEN] <category>: <one-line description>",
        "file: <path>:<line>",
        "evidence: <upstream source, pinned revision, test result, or docs URL>",
        "fix: <specific change required>",
        "closure: <command, file:line, or URL required to mark CLOSED>",
    )

    for field in finding_template:
        assert field in prompt


def test_master_prompt_requires_upstream_currency_prerequisite() -> None:
    prompt = read_master_prompt()

    assert "references/upstream-delta-review.json" in prompt
    assert "tools/upstream_baseline.py" in prompt
    assert "must exit 0 before the mission may ship" in prompt
    assert "Deferring the pin move requires an OPEN P2 finding" in prompt
    assert prompt.index("### Upstream currency prerequisite") < prompt.index(
        "### States and stop conditions"
    )

def test_master_prompt_exposes_both_shipping_outcomes() -> None:
    prompt = read_master_prompt()

    assert "### Mission-owned changes exist" in prompt
    assert "### No mission-owned changes" in prompt
    assert "git merge --ff-only <mission-branch>" in prompt
    assert "git push origin main" in prompt
    assert "create no empty commit" in prompt
