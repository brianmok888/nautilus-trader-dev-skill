from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

def read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")

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
