from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

def read(relative: str) -> str:
    return (REPO_ROOT / relative).read_text(encoding="utf-8")

def test_backtest_fill_model_uses_current_trait_and_venue_wrapper() -> None:
    text = read("skills/nt-backtest/SKILL.md")
    assert "impl FillModel for MyFillModel" in text
    assert "FillModelAny" in text
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
    assert "legacy Cython/v1 reference-only" in implement and "Cython interop" in implement

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
    assert "Develop-only" not in backtest or "f725e184db" in backtest
