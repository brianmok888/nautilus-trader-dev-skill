from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

def read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")

def test_rust_strategy_builder_does_not_present_builtin_examples_as_extension_api() -> None:
    text = read("skills/nt-strategy-builder-rust/SKILL.md")

    assert "is not a general extension path" in text
    assert "node.add_builtin_strategy(\"YourStrategy\", config)" not in text
    assert "core: StrategyCore" in text
    assert "StrategyCore::new(config)" in text
    assert "nautilus_strategy!(MyStrategy)" in text

def test_repository_scope_routes_python_only_as_nt_migration_reference() -> None:
    upstream_python = read("references/developer_guide/python.md")
    router = read("skills/nt/SKILL.md")
    python_builder = read("skills/nt-strategy-builder/SKILL.md")
    implement = read("skills/nt-implement/SKILL.md")

    assert "ideal for strategy development" in upstream_python
    assert "migration/reference-only" in router
    assert "migration/reference-only" in python_builder
    assert "Explicit Python strategy requests still route to Rust" in implement

def test_ambiguous_strategy_requests_default_to_rust_builder() -> None:
    router = read("skills/nt/SKILL.md")
    implement = read("skills/nt-implement/SKILL.md")
    project = read("AGENTS.md")

    required = [
        "Ambiguous (\"build a strategy\", no language stated) -> `nt-strategy-builder-rust`",
        "Ambiguous strategy requests default to Rust",
        "Production strategy or live-node work | `skills/nt-strategy-builder-rust/`",
    ]
    combined = router + implement + project
    missing = [term for term in required if term not in combined]
    assert missing == []

    forbidden = [
        "ask which language before loading either skill",
        "or start in Python and port to Rust when profiling demands it",
        "Wire backtest or live node | `skills/nt-strategy-builder/templates/`",
    ]
    present = [term for term in forbidden if term in combined]
    assert present == []

def test_public_strategy_routing_uses_rust_builder_for_new_work() -> None:
    readme = read("README.md")
    router = read("skills/nt/SKILL.md")
    python_builder = read("skills/nt-strategy-builder/SKILL.md")
    guide = read("docs/end_to_end_guide.md")

    assert "nt-strategy-builder-rust ◄── nt-dex-adapter" in readme
    assert (
        "| Backtests, fill models, simulated venues, backtest configs | "
        "`nt-backtest`, `nt-strategy-builder-rust`, `nt-testing` |"
    ) in router
    assert (
        "Example: route backtest wiring plus validation to `nt-strategy-builder-rust`,\n"
        "`nt-backtest`, and `nt-testing` together."
    ) in router
    assert "description: Use when migrating or referencing existing Python" in python_builder
    assert "## Overview\n\nThis migration/reference-only skill" in python_builder
    assert (
        "especially `nt-architect`, `nt-implement`, `nt-strategy-builder-rust`, "
        "`nt-live`, `nt-testing`, and `nt-review`"
    ) in guide

def test_python_research_and_dex_runtime_routes_follow_rust_cutover() -> None:
    guide = read("docs/end_to_end_guide.md")
    dex_skill = read("skills/nt-dex-adapter/SKILL.md")
    dex_agents = read("skills/nt-dex-adapter/AGENTS.md")

    assert "## Appendix: Python Migration Reference" in guide
    assert "New strategy research and rapid prototyping route to `nt-strategy-builder-rust`" in guide
    assert "Python remains supported for V2 strategy research" not in guide

    combined_dex = dex_skill + dex_agents
    assert "`nt-strategy-builder-rust`" in combined_dex
    assert "Rust `LiveNode` or backtest wiring" in combined_dex
    assert "nt-strategy-builder/dex_venue_input.py" not in combined_dex
    assert "`nt-strategy-builder` skill's `dex_venue_input.py`" not in combined_dex
