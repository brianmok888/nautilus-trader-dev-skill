from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def test_exec_tester_guidance_uses_current_python_keywords_and_rust_builder() -> None:
    text = read("skills/nt-testing/references/guides/spec_exec_testing.md")
    api_text = read("skills/nt-testing/references/api/exec_tester_config.md")

    for keyword in [
        "strategy_id=",
        "instrument_id=",
        "client_id=",
        "order_qty=",
        "enable_limit_buys=",
        "enable_limit_sells=",
    ]:
        assert keyword in text

    assert "ExecTesterConfig::builder()" in text
    assert "ExecTesterConfig::builder()" in api_text
    assert "ExecTesterConfig::new(" not in text
    assert ".with_risk_engine_config(" in text
    assert ".with_exec_engine_config(" in text
    assert ".risk_engine_config(" not in text
    assert ".exec_engine_config(" not in text


def test_data_tester_guidance_uses_current_bon_builder_names() -> None:
    api_text = read("skills/nt-testing/references/api/data_tester_config.md")
    guide_text = read("skills/nt-testing/references/guides/spec_data_testing.md")
    skill_text = read("skills/nt-testing/SKILL.md")

    assert "DataTesterConfig::builder()" in api_text
    assert ".subscribe_trades(bool)" in api_text
    assert ".with_subscribe_trades(" not in api_text + guide_text
    assert "NonZeroUsize" not in api_text + guide_text
    assert ").with_subscribe_" not in skill_text
    assert ").with_request_" not in skill_text


def test_python_v2_callbacks_must_use_live_runner_channels_not_tokio_attach() -> None:
    text = read("skills/nt-live/SKILL.md") + read("skills/nt-review/SKILL.md")

    assert "no `Python::attach` from Tokio worker tasks" in text
    assert "live runner channels" in text


def test_current_pyo3_registration_uses_owning_crate_module() -> None:
    texts = [
        read("skills/nt-data/SKILL.md"),
        read("skills/nt-model/SKILL.md"),
        read("skills/nt-signals/SKILL.md"),
        read("skills/nt-trading/SKILL.md"),
        read("skills/nt-live/SKILL.md"),
        read("skills/nt-backtest/SKILL.md"),
        read("skills/nt-strategy-builder-rust/SKILL.md"),
    ]

    for text in texts:
        assert "src/python/mod.rs" in text
        assert "crates/pyo3/src/lib.rs" in text
        assert "aggregates" in text


def test_nightly_migration_guidance_covers_current_v2_features() -> None:
    text = "\n".join(
        read(path)
        for path in [
            "skills/nt-live/SKILL.md",
            "skills/nt-trading/SKILL.md",
            "skills/nt-review/SKILL.md",
            "skills/nt-testing/SKILL.md",
        ]
    )

    required_terms = [
        "OrderFillVoided",
        "VOIDED",
        "use_mark_prices",
        "carry_replay_events_on_reopen",
        "RedisMessageBusBacking",
        "SQL/catalog migration",
        "deferred V2 limits",
        "shared adapter task tracking",
        "#![deny(unsafe_op_in_unsafe_fn)]",
    ]
    missing = [term for term in required_terms if term not in text]
    assert missing == []


def test_rust_strategy_builder_does_not_present_builtin_examples_as_extension_api() -> None:
    text = read("skills/nt-strategy-builder-rust/SKILL.md")

    assert "is not a general extension path" in text
    assert "node.add_builtin_strategy(\"YourStrategy\", config)" not in text
    assert "core: StrategyCore" in text
    assert "StrategyCore::new(config)" in text
    assert "nautilus_strategy!(MyStrategy)" in text


def test_repository_cutover_restricts_python_to_ai_advisory_and_migration() -> None:
    upstream_python = read("references/developer_guide/python.md")
    router = read("skills/nt/SKILL.md")
    python_builder = read("skills/nt-strategy-builder/SKILL.md")
    implement = read("skills/nt-implement/SKILL.md")
    architect = read("skills/nt-architect/SKILL.md")
    trading = read("skills/nt-trading/SKILL.md")

    assert "ideal for strategy development" in upstream_python
    assert "Upstream NT V2 supports Python strategies" in router
    assert "this repository applies a stricter cutover policy" in router
    assert "migration/reference-only" in python_builder
    assert "AI/advisory lane stays Python through `nt-evomap-integration`" in python_builder
    assert "Explicit Python strategy requests still route to Rust" in implement

    misleading_claims = [
        "Python and Rust strategies are both supported NT V2 extension surfaces",
        "supported NT V2 Python strategy",
        "Explicit Python strategy or AI/advisory lane -> `nt-strategy-builder`",
        "Python strategy (\"build a strategy in Python\") -> `nt-strategy-builder` ONLY",
    ]
    combined = router + python_builder + implement + architect + trading
    for claim in misleading_claims:
        assert claim not in combined

    assert (
        "Python strategy (\"build a strategy in Python\") -> `nt-strategy-builder-rust` ONLY"
        in router
    )
    assert "AI/advisory request -> `nt-evomap-integration` ONLY" in router

    forbidden_active_python = [
        "Treat Python as the user strategy/configuration surface",
        "User orchestration, config, research strategy, AI lane | **Python**",
        "user-facing strategy/config or the AI lane it stays in Python",
        "Python is limited to research/config and AI/advisory sidecars",
    ]
    for claim in forbidden_active_python:
        assert claim not in combined


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
        "Explicit Python or AI/advisory strategy work | `skills/nt-strategy-builder/`",
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
        "| Backtests, fill models, simulated venues, backtest configs | `nt-backtest` "
        "| `nt-strategy-builder-rust`, `nt-testing` |"
    ) in router
    assert (
        "Routing to nt-strategy-builder-rust with nt-backtest and\n"
        "nt-testing because the task is backtest wiring plus validation."
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
    evomap = read("skills/nt-evomap-integration/SKILL.md")

    assert "## Appendix: Python Migration Reference and Active AI/Advisory Lane" in guide
    assert "New strategy research and rapid prototyping route to `nt-strategy-builder-rust`" in guide
    assert "Only AI/advisory through `nt-evomap-integration` remains active Python" in guide
    assert "Python remains supported for V2 strategy research" not in guide
    contradictory_python_guidance = [
        phrase
        for phrase in [
            "supported Python V2 strategy/research work",
            "current Python-only integration guidance",
        ]
        if phrase in guide
    ]
    assert contradictory_python_guidance == []

    combined_dex = dex_skill + dex_agents
    assert "`nt-strategy-builder-rust`" in combined_dex
    assert "Rust `LiveNode` or backtest wiring" in combined_dex
    assert "nt-strategy-builder/dex_venue_input.py" not in combined_dex
    assert "`nt-strategy-builder` skill's `dex_venue_input.py`" not in combined_dex

    assert "`nt-strategy-builder-rust` for Rust `LiveNode` or backtest runtime wiring" in evomap
    assert "`nt-strategy-builder` for runtime wiring" not in evomap


def test_component_registration_uses_current_native_and_bundled_apis() -> None:
    texts = [
        read("skills/nt-trading/SKILL.md"),
        read("skills/nt-live/references/concepts/rust.md"),
    ]
    combined = "\n".join(texts)

    assert "node.add_strategy(strategy)?" in combined
    assert "node.add_actor(actor)?" in combined
    assert "add_builtin_strategy(type_name, config)" in combined
    assert "add_builtin_actor(type_name, config)" in combined
    assert "examples feature" in combined
    assert "not a first-class extension API" in combined
    assert "add_native_strategy" not in combined
    assert "add_native_actor" not in combined


def test_visualization_guidance_uses_current_tearsheet_api() -> None:
    paths = [
        "docs/visualization.md",
        "references/README.md",
        "skills/nt-implement/templates/legacy_migration/backtest_viz.py",
        "skills/nt-strategy-builder/SKILL.md",
        "skills/nt-strategy-builder/templates/legacy_migration/backtest_node.py",
        "skills/nt-dex-adapter/SKILL.md",
    ]
    combined = "\n".join(read(path) for path in paths)

    assert "BacktestVisualizer" not in combined
    assert "from nautilus_trader.analysis import TearsheetConfig, create_tearsheet" in combined
    assert 'create_tearsheet(engine, output_path="tearsheet.html", config=' in combined
    assert "visualization" in combined
    assert "migration/reference-only" in read("skills/nt-implement/templates/legacy_migration/backtest_viz.py")
    assert "migration/reference-only" in read("skills/nt-strategy-builder/templates/legacy_migration/backtest_node.py")


def test_backtest_template_uses_typed_logging_config() -> None:
    text = read("skills/nt-strategy-builder/templates/legacy_migration/backtest_node.py")

    assert "from nautilus_trader.common.config import LoggingConfig" in text
    assert 'logging=LoggingConfig(log_level="WARNING")' in text
    assert 'logging={"log_level": "WARNING"}' not in text


def test_instrument_any_inventory_matches_exact_v2_variants() -> None:
    text = read("skills/nt-model/SKILL.md")
    expected = {
        "BettingInstrument",
        "BinaryOption",
        "Cfd",
        "Commodity",
        "CryptoFuture",
        "CryptoFuturesSpread",
        "CryptoOption",
        "CryptoOptionSpread",
        "CryptoPerpetual",
        "CurrencyPair",
        "Equity",
        "FuturesContract",
        "FuturesSpread",
        "IndexInstrument",
        "OptionContract",
        "OptionSpread",
        "PerpetualContract",
        "TokenizedAsset",
    }
    inventory = re.search(
        r"\*\*18 `InstrumentAny` variants:\*\*\n(?P<body>(?:- `[^`]+`.*\n)+)",
        text,
    )
    assert inventory is not None
    documented = set(re.findall(r"^- `([^`]+)`", inventory.group("body"), re.MULTILINE))
    assert documented == expected
    assert "SyntheticInstrument is separate from `InstrumentAny`" in text
    assert "**14 instrument types:**" not in text
    assert "All 14 instrument types" not in text


def test_pinned_nautilus_rust_dependencies_use_exact_workspace_version() -> None:
    paths = [
        "skills/nt-backtest/references/guides/run_rust_backtest.md",
        "skills/nt-live/references/guides/run_rust_live_trading.md",
        "docs/end_to_end_guide.md",
        "skills/nt-backtest/SKILL.md",
        "skills/nt-live/SKILL.md",
        "skills/nt-live/references/concepts/rust.md",
    ]
    dependency_pattern = re.compile(
        r'^nautilus-[a-z-]+\s*=\s*(?:"(?P<plain>[^"]+)"|\{[^\n]*version\s*=\s*"(?P<table>[^"]+)")',
        re.MULTILINE,
    )
    dependencies: list[tuple[str, str]] = []
    for path in paths:
        text = read(path)
        for match in dependency_pattern.finditer(text):
            version = match.group("plain") or match.group("table")
            assert version is not None
            dependencies.append((path, version))

    assert dependencies
    assert [(path, version) for path, version in dependencies if version != "0.61.0"] == []
    assert "Rust 1.97.1" in read("docs/end_to_end_guide.md")


def test_documented_inventory_lists_all_eighteen_nt_skills() -> None:
    expected = {
        path.parent.name
        for path in (REPO_ROOT / "skills").glob("nt*/SKILL.md")
    }
    assert len(expected) == 18

    for path in ["README.md", "skills/AGENTS.md"]:
        text = read(path)
        documented = set(re.findall(r"\| \*\*(nt(?:-[a-z0-9]+)*)\*\* \|", text))
        if path == "README.md":
            documented = set(re.findall(r"\| `(nt(?:-[a-z0-9]+)*)` \|", text))
        assert "18 skills" in text
        assert documented == expected


def test_pyo3_ownership_guidance_matches_current_cycle_handling() -> None:
    text = "\n".join(
        read(path)
        for path in [
            "skills/nt-implement/SKILL.md",
            "skills/nt-review/SKILL.md",
        ]
    )

    required_terms = [
        "`Py<T>` / `Py<PyAny>` owns a Python object reference",
        "`Arc<Py<T>>` is normally redundant",
        "plain `Py<T>` does not itself break Python reference cycles",
        "Use Python weak references for back-references",
        "For PyO3 pyclasses that own Python references or other GC-traceable objects which can participate in cycles",
        "implement `__traverse__` and `__clear__`",
        "explicit callback cleanup",
    ]
    missing = [term for term in required_terms if term not in text]
    assert missing == []

    misleading_claims = [
        "Arc wrapper causes reference cycles",
        "Arc<PyObject>` anywhere (causes reference cycles)",
        "Never use `Arc<PyObject>` (causes reference cycles)",
    ]
    for claim in misleading_claims:
        assert claim not in text


def test_current_v2_guidance_rejects_removed_order_subscriptions_and_brittle_versions() -> None:
    architect = read("skills/nt-architect/SKILL.md")
    implement = read("skills/nt-implement/SKILL.md")
    adapters = read("skills/nt-adapters/SKILL.md")
    actor_guidance = "\n".join(
        read(path)
        for path in [
            "skills/nt-architect/AGENTS.md",
            "references/concepts/actors.md",
            "skills/nt-trading/references/concepts/actors.md",
        ]
    )

    combined = architect + actor_guidance
    assert "subscribe_order_fills" not in combined
    assert "subscribe_order_cancels" not in combined
    assert "unsubscribe_order_fills" not in combined
    assert "unsubscribe_order_cancels" not in combined
    assert "on_order_filled(&OrderFilled)" in architect
    assert "on_order_canceled(&OrderCanceled)" in architect
    assert "message bus" in actor_guidance.lower()
    assert "on_order_filled" in actor_guidance
    assert "on_order_canceled" in actor_guidance
    assert "Read the target workspace version" in implement
    assert "Use Rust crate version `0.57`" not in implement
    assert "All 16 adapters" not in adapters
    assert "Do not hard-code an adapter count" in adapters
