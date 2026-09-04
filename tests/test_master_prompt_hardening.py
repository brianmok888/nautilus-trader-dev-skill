from __future__ import annotations

from pathlib import Path

from tools.upstream_baseline import UPSTREAM_COMMIT

ROOT = Path(__file__).resolve().parents[1]


def test_in_scope_artifacts_exclude_ai_framework_guidance() -> None:
    offenders: list[str] = []
    for scoped_root in (ROOT / "skills", ROOT / "references", ROOT / "templates"):
        if not scoped_root.exists():
            continue
        for path in scoped_root.rglob("*.md"):
            text = path.read_text(encoding="utf-8").lower()
            if any(marker in text for marker in ("langchain", "langgraph")):
                offenders.append(str(path.relative_to(ROOT)))

    assert offenders == []


def test_inventory_claims_and_signal_paths_resolve() -> None:
    signal_skill = (ROOT / "skills/nt-signals/SKILL.md").read_text(encoding="utf-8")

    assert len(list((ROOT / "references/api_reference").rglob("*.md"))) == 45
    assert (ROOT / "skills/nt-signals/migration_reference/python/python/analysis").is_dir()
    assert (ROOT / "skills/nt-signals/migration_reference/python/templates").is_dir()
    assert "migration_reference/python/python/analysis/" in signal_skill
    assert "migration_reference/python/templates/" in signal_skill


def test_live_curriculum_identifies_the_actual_pinned_baseline() -> None:
    curriculum = (ROOT / "skills/nt-learn/curriculum/07-live-trading.md").read_text(
        encoding="utf-8"
    )

    assert "pinned upstream examples at develop commit `45903fc8`" not in curriculum
    assert UPSTREAM_COMMIT in curriculum


def test_master_prompt_contains_no_host_specific_absolute_path() -> None:
    prompt = (ROOT / "docs/prompts/master-prompt.md").read_text()

    assert "/home/" not in prompt
    assert "/Users/" not in prompt
    assert "git rev-parse --show-toplevel" in prompt
