"""Focused gate for the production-runtime vs deterministic-test-runtime spawn split.

NT-2026-08-16-25 — owned nt-dex-adapter guidance must state that production
adapter tasks use `get_runtime().spawn()` on the configured runtime while
deterministic tests that own their runtime may use `tokio::spawn()`, and must
cite the pinned upstream evidence for that split.
"""

from __future__ import annotations

import sys
from pathlib import Path

_SKILL_DIR = Path(__file__).resolve().parents[1]
_REPO_ROOT = _SKILL_DIR.parents[1]
sys.path.insert(0, str(_REPO_ROOT))

from tools.upstream_baseline import UPSTREAM_COMMIT, default_upstream_root  # noqa: E402

_SKILL = _SKILL_DIR / "SKILL.md"
_CHECKLIST = _SKILL_DIR / "rules" / "compliance_checklist.md"
_DOS_AND_DONTS = _SKILL_DIR / "rules" / "dos_and_donts.md"

OWNED_GUIDANCE = (
    ("skills/nt-dex-adapter/SKILL.md", _SKILL),
    ("skills/nt-dex-adapter/rules/compliance_checklist.md", _CHECKLIST),
    ("skills/nt-dex-adapter/rules/dos_and_donts.md", _DOS_AND_DONTS),
)

TEST_ALLOWANCE = "deterministic tests may use `tokio::spawn()`"

# Blanket spawn bans that conflate production and test runtimes; none may remain.
BLANKET_BANS = (
    "Never use `tokio::spawn()` in adapter Rust code",
    "`get_runtime().spawn()` for all async tasks (NOT `tokio::spawn()`)",
    "**DO** use `get_runtime().spawn()` for all async tasks in adapter code.",
    "**DON'T** use `tokio::spawn()` in adapter code (not in tests)",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_production_spawn_requirement_is_scoped_to_production_tasks() -> None:
    for name, path in OWNED_GUIDANCE:
        text = _read(path)
        scoped = [
            line
            for line in text.splitlines()
            if "get_runtime().spawn()" in line and "production" in line
        ]
        assert scoped, (
            f"{name} must scope the `get_runtime().spawn()` requirement to "
            "production adapter tasks instead of all async tasks"
        )


def test_deterministic_test_runtime_allows_tokio_spawn() -> None:
    for name, path in OWNED_GUIDANCE:
        text = _read(path)
        assert TEST_ALLOWANCE in text, (
            f"{name} must state that deterministic tests may use `tokio::spawn()` "
            "on their own runtime"
        )


def test_blanket_tokio_spawn_bans_are_gone() -> None:
    for name, path in OWNED_GUIDANCE:
        text = _read(path)
        for ban in BLANKET_BANS:
            assert ban not in text, f"{name} still contains the blanket ban: {ban!r}"


def test_guidance_cites_upstream_spawn_evidence() -> None:
    for name, path in OWNED_GUIDANCE:
        text = _read(path)
        assert UPSTREAM_COMMIT in text, f"{name} must cite the pinned upstream commit"
        assert ".pre-commit-hooks/check_tokio_usage.sh" in text, (
            f"{name} must cite the upstream Tokio usage hook"
        )


def test_pinned_upstream_hook_enforces_the_cited_split() -> None:
    upstream = default_upstream_root()

    hook = upstream / ".pre-commit-hooks" / "check_tokio_usage.sh"
    assert hook.is_file(), f"pinned upstream hook missing: {hook}"
    hook_text = _read(hook)
    assert "get_runtime().spawn() instead of tokio::spawn in adapters" in hook_text
    assert '[[ "$file" =~ /tests/ ]] && continue' in hook_text
    assert "#[cfg(test)]" in hook_text

    runtime = upstream / "crates" / "common" / "src" / "live" / "runtime.rs"
    assert runtime.is_file(), f"pinned upstream runtime missing: {runtime}"
    assert "pub fn get_runtime() -> &'static tokio::runtime::Runtime" in _read(runtime)

    betfair = upstream / "crates" / "adapters" / "betfair" / "tests" / "integration" / "data_client.rs"
    assert betfair.is_file(), f"pinned upstream adapter test missing: {betfair}"
    betfair_text = _read(betfair)
    assert "#[tokio::test]" in betfair_text
    assert "tokio::spawn(" in betfair_text
