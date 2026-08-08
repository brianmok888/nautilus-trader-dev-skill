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


def test_repository_scope_routes_python_only_as_nt_migration_reference() -> None:
    upstream_python = read("references/developer_guide/python.md")
    router = read("skills/nt/SKILL.md")
    python_builder = read("skills/nt-strategy-builder/SKILL.md")
    implement = read("skills/nt-implement/SKILL.md")

    assert "ideal for strategy development" in upstream_python
    assert "migration/reference-only" in router
    assert "migration/reference-only" in python_builder
    assert "Explicit Python strategy requests still route to Rust" in implement
    assert "AI work is out of scope" in router
    assert "AI work is out of scope" in router


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

    assert "## Appendix: Python Migration Reference" in guide
    assert "New strategy research and rapid prototyping route to `nt-strategy-builder-rust`" in guide
    assert "AI and advisory work are outside this repository" in guide
    assert "Python remains supported for V2 strategy research" not in guide

    combined_dex = dex_skill + dex_agents
    assert "`nt-strategy-builder-rust`" in combined_dex
    assert "Rust `LiveNode` or backtest wiring" in combined_dex
    assert "nt-strategy-builder/dex_venue_input.py" not in combined_dex
    assert "`nt-strategy-builder` skill's `dex_venue_input.py`" not in combined_dex


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


def test_dex_python_live_templates_are_quarantined_and_not_approvable() -> None:
    agents = read("skills/nt-dex-adapter/AGENTS.md")
    checklist = read("skills/nt-dex-adapter/rules/compliance_checklist.md")

    assert "legacy_migration/dex_data_client.py" in agents
    assert "legacy_migration/dex_exec_client.py" in agents
    assert "Rust `LiveNodeBuilder`" in agents
    assert "Rust Core (if applicable)" not in checklist
    assert "N/A if Python-only" not in checklist
    assert "Python-only" in checklist
    assert "cannot receive APPROVED FOR USE" in checklist


def test_dex_canonical_skill_is_unconditionally_rust_first() -> None:
    text = read("skills/nt-dex-adapter/SKILL.md")
    canonical = text.split("## Migration/reference-only Python architecture", 1)[0]

    assert "Rust Core Infrastructure (if Rust-first)" not in canonical
    assert "Phase 1: Define scope" in canonical
    assert "Phase 2: Build the protocol core" in canonical
    assert "Rust `InstrumentProvider`, data and execution client" in canonical
    assert "LiveNodeBuilder" in canonical
    assert "registered with `TradingNode`" not in canonical
    assert "nautilus_trader/adapters/my_dex/" not in canonical


def test_dex_current_compliance_does_not_import_migration_executables() -> None:
    current = read("skills/nt-dex-adapter/tests/test_dex_compliance.py")
    migration = read(
        "skills/nt-dex-adapter/tests/test_nonproduction_migration_templates.py"
    )
    checklist = read("skills/nt-dex-adapter/rules/compliance_checklist.md")

    assert "legacy_migration" not in current
    assert "MyDEXLiveDataClientFactory" not in current
    assert "MyDEXLiveExecClientFactory" not in current
    assert "legacy_migration" in migration
    assert "non-production migration smoke" in checklist
    assert "does not gate production approval" in checklist


def test_dex_current_compliance_loads_no_classified_python_templates() -> None:
    current = read("skills/nt-dex-adapter/tests/test_dex_compliance.py")
    migration = read(
        "skills/nt-dex-adapter/tests/test_nonproduction_migration_templates.py"
    )

    classified_templates = {
        path.name
        for path in (REPO_ROOT / "skills/nt-dex-adapter/templates").rglob("*.py")
        if path.read_text(encoding="utf-8").startswith("# TEMPLATE_CLASSIFICATION:")
    }
    loaded_by_current = {
        template
        for template in classified_templates
        if template.removesuffix(".py") in current
    }

    assert loaded_by_current == set()
    assert "dex_config" in migration
    assert "dex_instrument_provider" in migration


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


def test_documented_inventory_lists_all_seventeen_nt_skills() -> None:
    expected = {
        path.parent.name
        for path in (REPO_ROOT / "skills").glob("nt*/SKILL.md")
    }
    assert len(expected) == 17

    for path in ["README.md", "skills/AGENTS.md"]:
        text = read(path)
        documented = set(re.findall(r"\| \*\*(nt(?:-[a-z0-9]+)*)\*\* \|", text))
        if path == "README.md":
            documented = set(re.findall(r"\| `(nt(?:-[a-z0-9]+)*)` \|", text))
        assert "17 skills" in text
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


def test_post_pin_develop_features_are_version_scoped_and_source_backed() -> None:
    data = read("skills/nt-data/SKILL.md")
    model = read("skills/nt-model/SKILL.md")
    backtest = read("skills/nt-backtest/SKILL.md")
    live = read("skills/nt-live/SKILL.md")
    testing = read("skills/nt-testing/SKILL.md")

    assert "aabb824cb377d62ea7ff6a7ce9489a92c705580a" in data
    for accessor in [
        "mark_price_count",
        "index_price_count",
        "funding_rate_count",
        "instrument_status_count",
        "has_mark_prices",
        "has_index_prices",
        "has_funding_rates",
        "has_instrument_statuses",
    ]:
        assert accessor in data

    assert "d46f56505" in model
    assert "OrderInitialized::new_checked" in model
    assert "contingent order" in model
    assert "execution spawn ID" in model

    assert "501ebe4a8" in backtest
    assert "BacktestResult.returns_series" in backtest
    assert "dict[int, float]" in backtest
    assert "result-only tearsheet" in backtest

    assert "32bc6b680" in live
    for invariant in [
        "exactly once",
        "post-halt",
        "embedded `seq`",
        "undecodable",
        "filesystem order",
    ]:
        assert invariant in live

    assert "spec_exec_testing.md" in testing
    assert "groups 1–5" in testing
    assert "184e231f192ea7410aeb7730d6118fedfdf2c4d7" in testing
    assert "close_positions_qty_precision" in testing
    assert "exact sub-precision residual" in testing
    assert "no open orders" in testing


def test_version_guidance_distinguishes_pins_from_support_policy() -> None:
    readme = read("README.md")
    dev = read("skills/nt-dev/SKILL.md")

    for text in [readme, dev]:
        assert "Python 3.12-3.14" in text
        assert "repository toolchain is pinned to Rust 1.97.1" in text
        assert "not a permanent MSRV promise" in text

    assert "Current release baseline: NautilusTrader v1.230.0 latest release" not in readme
    assert "Pinned reproducible baseline" in readme
    assert "Current develop observation" in readme
