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
        "### States and stop conditions",
        "### Finding format (every finding)",
        "## Phase 4 — Reconciliation",
        "## Phase 5 — Ship automatically",
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


def test_master_prompt_exposes_both_shipping_outcomes() -> None:
    prompt = read_master_prompt()

    assert "### Mission-owned changes exist" in prompt
    assert "### No mission-owned changes" in prompt
    assert "git merge --ff-only <mission-branch>" in prompt
    assert "git push origin main" in prompt
    assert "create no empty commit" in prompt
