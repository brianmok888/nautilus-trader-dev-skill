from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def test_pyo3_custom_data_injection_is_develop_only_and_non_authoritative() -> None:
    text = read("skills/nt-backtest/SKILL.md")

    required = [
        "998005124e298e9b0c2f6c60be21e581f3426da1",
        "develop/nightly only",
        "BacktestEngine.add_data",
        "CustomData",
        "bounded control/data injection",
        "matching and execution remain Rust-owned",
        "not available in the pinned baseline or stable releases",
    ]

    assert [term for term in required if term not in text] == []


def test_rust_state_persistence_guidance_covers_component_and_kernel_lifecycle() -> None:
    texts = {
        path: read(path)
        for path in [
            "skills/nt-live/SKILL.md",
            "skills/nt-trading/SKILL.md",
        ]
    }

    common = [
        "9a9e5fe7b762410229b380d5af92d32c13169c3a",
        "develop/nightly only",
        "DataActor",
        "Strategy",
        "on_load",
        "on_save",
        "load_actor_state",
        "load_strategy_state",
        "save_trader_state",
        "finalize_stop",
        "not available in the pinned baseline or stable releases",
        "execution ownership remains in Rust",
    ]

    for path, text in texts.items():
        assert [term for term in common if term not in text] == [], path


def test_state_guidance_distinguishes_backtest_and_live_shutdown_paths() -> None:
    live = read("skills/nt-live/SKILL.md")
    trading = read("skills/nt-trading/SKILL.md")

    assert "after residual event processing" in live
    assert "before cache teardown" in live
    assert "backtest and live" in trading
    assert "load before component startup" in trading
    assert "save once during shutdown" in trading
