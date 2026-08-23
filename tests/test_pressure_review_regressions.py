from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

def read(relative: str) -> str:
    return (REPO_ROOT / relative).read_text(encoding="utf-8")

def test_backtest_fill_model_uses_current_trait_and_venue_wrapper() -> None:
    text = read("skills/nt-backtest/SKILL.md")
    assert "impl FillModel for MyFillModel" in text
    assert "FillModelHandle" in text
    assert "anyhow::Result<bool>" in text

def test_data_skill_avoids_invented_backend_and_removed_decorator() -> None:
    text = read("skills/nt-data/SKILL.md")
    assert "MyStorageBackend" not in text
    assert "@customdataclass" not in text
    assert "register_custom_data_class" in text

def test_architect_publication_example_uses_real_data_type_constructor() -> None:
    text = read("skills/nt-architect/SKILL.md")
    assert "DataType::new::<" not in text
    assert "publish_signal(" in text

def test_adapter_provider_guidance_uses_current_required_methods() -> None:
    for path in (
        "skills/nt-adapters/SKILL.md",
        "references/developer_guide/contracts/adapter_contract.md",
    ):
        text = read(path)
        assert "load_all_async" not in text
        for method in ("load_all", "load_ids", "load"):
            assert method in text

def test_active_guidance_does_not_recommend_unsupported_msgspec() -> None:
    assert "msgspec" not in read("skills/nt-strategy-builder/SKILL.md")
    assert "msgspec" not in read("docs/serialization.md")

def test_router_and_dev_skill_protect_pinned_upstream_cache() -> None:
    router = read("skills/nt/SKILL.md")
    dev = read("skills/nt-dev/SKILL.md")
    for text in (router, dev):
        assert "disposable writable" in text
        assert "pinned cache" in text

def test_router_captures_version_and_routes_legacy_runtime_requests() -> None:
    text = read("skills/nt/SKILL.md")
    assert "runtime version" in text
    assert "legacy runtime" in text
    assert "migration/reference" in text

def test_router_quarantine_claim_matches_inline_legacy_policy() -> None:
    router = read("skills/nt/SKILL.md")
    implement = read("skills/nt-implement/SKILL.md")
    assert "physically quarantined" in router
    assert "legacy Cython/v1" in implement and "migration/reference-only" in implement

def test_pinned_runtime_tests_reject_wrong_nautilus_version() -> None:
    for path in (
        "skills/nt-strategy-builder/tests/conftest.py",
        "skills/nt-dex-adapter/tests/test_backtest_integration.py",
    ):
        text = read(path)
        assert "nautilus_trader._libnautilus.common" in text
        assert "pytest.importorskip" in text

def test_remaining_pressure_review_prose_defects_are_fixed() -> None:
    implement = read("skills/nt-implement/SKILL.md")
    backtest = read("skills/nt-backtest/SKILL.md")
    assert "Rust, / remain" not in implement
    assert "Develop-only" not in backtest or "d2b62d35a7" in backtest


def test_testing_guidance_covers_current_timestamp_scale_contract() -> None:
    testing = read("skills/nt-testing/SKILL.md")

    assert "Unix nanoseconds" in testing
    assert "10^16" in testing
    assert "Treat a timestamp-scale warning as a failure" in testing
    assert "reconstructed books" in testing


def test_adapter_guidance_rejects_wrong_timestamp_scales() -> None:
    adapters = read("skills/nt-adapters/SKILL.md")

    assert "ts_event" in adapters and "ts_init" in adapters
    assert "Unix nanoseconds" in adapters
    assert "seconds, milliseconds, or microseconds" in adapters


def test_architect_actor_example_returns_result() -> None:
    architect = read("skills/nt-architect/SKILL.md")

    assert 'self.publish_signal(\n            "regime",' in architect
    assert ");\n        Ok(())" in architect
    assert "self.publish_signal(RegimeSignal" not in architect


def test_dev_make_targets_exist_in_pinned_makefile() -> None:
    dev = read("skills/nt-dev/SKILL.md")

    assert "make pytest-v2" not in dev
    assert "make test-performance" not in dev
    assert "make pytest" in dev
    assert "make cargo-ci-benches" in dev


def test_implementation_guidance_uses_upstream_log_facade() -> None:
    implement = read("skills/nt-implement/SKILL.md")

    assert "`tracing::*`" not in implement
    assert "fully qualified `log::" in implement


def test_model_inventory_uses_exact_instrument_discriminant() -> None:
    model = read("skills/nt-model/SKILL.md")

    inventory = model.split("**18 `InstrumentAny` variants:**", 1)[1].split("##", 1)[0]
    assert "`Betting` - payload type `BettingInstrument`" in inventory
    assert "- `BettingInstrument`" not in inventory


def test_backtest_custom_fill_model_uses_current_handle_contract() -> None:
    backtest = read("skills/nt-backtest/SKILL.md")

    assert "get_orderbook_for_fill_simulation" in backtest
    assert "FillModelHandle::new" in backtest
    assert "FillModelAny::Custom" not in backtest


def test_signals_custom_data_uses_current_registration_api() -> None:
    signals = read("skills/nt-signals/SKILL.md")
    guide = read("skills/nt-signals/references/guides/custom_data_patterns.md")

    assert "register_custom_data_class" in signals
    assert "register_custom_data_class" in guide
    assert "customdataclass" not in signals
    assert "customdataclass" not in guide
    assert "encode_record_batch_py" in guide
    assert "decode_record_batch_py" in guide


def test_dex_canonical_rules_are_rust_first_and_pool_unique() -> None:
    skill = read("skills/nt-dex-adapter/SKILL.md")
    rules = read("skills/nt-dex-adapter/rules/dos_and_donts.md")

    assert "migration/reference-only" in "\n".join(rules.splitlines()[0:8])
    assert "signer_private_key_env" in skill
    assert "pool contract address or protocol pool ID" in skill
    assert "taker_fee" in skill
    assert "maker_fee = taker_fee" not in rules
    assert "AMM swap fee tier to `taker_fee`" in skill


def test_live_reconciliation_uses_current_rust_owners() -> None:
    guide = read("skills/nt-live/references/guides/reconciliation.md")

    assert "crates/execution/src/reconciliation" in guide
    assert "crates/network/src/retry.rs" in guide
    assert "LiveNodeConfig" in guide
    assert "aborts startup" in guide
    assert "nautilus_trader/live/reconciliation.py" not in guide
    assert "nautilus_trader/live/retry.py" not in guide


def test_indicator_example_rejects_zero_period() -> None:
    signals = read("skills/nt-signals/SKILL.md")

    assert 'assert!(period > 0, "period must be positive")' in signals


def test_data_custom_persistence_uses_model_registry() -> None:
    data = read("skills/nt-data/SKILL.md")

    assert "nautilus_model::data::register_arrow" in data
    assert "CustomDataBatch" in data
    assert "write_custom_data_batch" in data
    assert "crates/serialization/src/arrow" not in data


def test_testing_preferred_async_pattern_awaits_exact_signal() -> None:
    guide = read("skills/nt-testing/references/guides/testing.md")
    section = guide.split("### Deterministic async completion", 1)[1].split("##", 1)[0]

    assert "subscribe" in section
    assert "trigger" in section
    assert "bounded timeout" in section
    assert "wait_until_async" not in section
    assert "eventually" not in section
    assert "sleep(" not in section
