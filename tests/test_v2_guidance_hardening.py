from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

def read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")

def test_current_guidance_rejects_verified_obsolete_paths_and_defaults() -> None:
    combined = "\n".join(
        read(path)
        for path in (
            "skills/nt-dex-adapter/SKILL.md",
            "skills/nt-implement/SKILL.md",
            "skills/nt-backtest/SKILL.md",
            "skills/nt-adapters/references/guides/rust.md",
            "skills/nt-dev/references/guides/rust_conventions.md",
            "skills/nt-model/references/concepts/instruments.md",
            "skills/nt-architect/references/concepts/instruments.md",
            "skills/nt-implement/references/concepts/instruments.md",
            "skills/nt-review/references/concepts/instruments.md",
            "skills/nt-signals/references/guides/custom_data_patterns.md",
        )
    )

    for obsolete in (
        "nautilus_trader/adapters/_template/",
        "crates/exec-algo/",
        "crates/execution/src/matching_core/",
        "crates/live/src/manager.rs",
        "nautilus_trader/accounting/accounts/margin.pyx",
        "Custom data types are a **Python-only** feature",
        "prefer Python `@customdataclass`",
    ):
        assert obsolete not in combined

    for current in (
        "crates/trading/src/algorithm/",
        "crates/execution/src/matching_core.rs",
        "crates/model/src/accounts/margin.rs",
        "crates/model/src/python/account/margin.rs",
        "CustomDataTrait",
        "register_custom_data_class",
    ):
        assert current in combined

def test_copy_paste_rust_guidance_uses_current_v2_api_shapes() -> None:
    backtest = read("skills/nt-backtest/SKILL.md")
    adapters = read("skills/nt-adapters/SKILL.md")
    data = read("skills/nt-data/SKILL.md")
    implement = read("skills/nt-implement/SKILL.md")
    model = read("skills/nt-model/SKILL.md")
    signals = read("skills/nt-signals/SKILL.md")
    trading = read("skills/nt-trading/SKILL.md")

    assert "SimulatedVenueConfig::builder()" in backtest
    assert "31 args" not in backtest
    assert ".add_adapter(" not in adapters
    assert "trait AdapterFactory" not in adapters
    assert "InvalidBackoff" not in adapters
    assert "RetryExhausted" not in adapters
    assert "nautilus_persistence::backend::catalog::ParquetDataCatalog" in data
    assert "ArrowSerializer" not in data
    assert "use nautilus_core::ffi::abort_on_panic;" in implement
    assert "use ustr::Ustr;" in model
    assert "nautilus_indicators::momentum::rsi::RelativeStrengthIndex" in signals
    assert "self.order().market(" in trading
    assert "self.submit_order(order, None, None, None)?;" in trading
    assert "Deref<Target = DataActorCore>" not in trading

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
