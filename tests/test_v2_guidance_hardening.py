from __future__ import annotations

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
    assert "pub base: StrategyConfig" in text
    assert "StrategyCore::new(config.base)" in text


def test_rust_first_policy_preserves_supported_python_v2_strategies() -> None:
    upstream_python = read("references/developer_guide/python.md")
    router = read("skills/nt/SKILL.md")
    python_builder = read("skills/nt-strategy-builder/SKILL.md")
    implement = read("skills/nt-implement/SKILL.md")

    assert "ideal for strategy development" in upstream_python
    assert "Python and Rust strategies are both supported NT V2 extension surfaces" in router
    assert "supported NT V2 Python strategy" in python_builder
    assert "supported NT V2 Python strategy" in implement

    misleading_claims = [
        "Python strategy migration example",
        "Python research/config/AI lane -> `nt-strategy-builder`",
        "this skill is for Python research/config, paper exploration, and AI/advisory orchestration only",
    ]
    combined = router + python_builder + implement
    for claim in misleading_claims:
        assert claim not in combined
