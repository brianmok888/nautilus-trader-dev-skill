from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.upstream_baseline import DEFAULT_UPSTREAM_ROOT, UPSTREAM_COMMIT

REPO_ROOT = Path(__file__).resolve().parents[1]
GUIDE = REPO_ROOT / "docs/end_to_end_guide.md"
README = REPO_ROOT / "README.md"
NT_LIVE = REPO_ROOT / "skills/nt-live/SKILL.md"
NT_TESTING = REPO_ROOT / "skills/nt-testing/SKILL.md"
UPSTREAM_ROOT = DEFAULT_UPSTREAM_ROOT
EXPECTED_UPSTREAM_COMMIT = UPSTREAM_COMMIT


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def section(text: str, heading: str) -> str:
    pattern = rf"^## {re.escape(heading)}\n(?P<body>.*?)(?=^## |\Z)"
    match = re.search(pattern, text, flags=re.MULTILINE | re.DOTALL)
    assert match, f"missing section: {heading}"
    return match.group("body")


def rust_fence(text: str) -> str:
    match = re.search(r"^```rust\n(?P<body>.*?)^```", text, flags=re.MULTILINE | re.DOTALL)
    assert match, "missing Rust source fence"
    return match.group("body")


def test_primary_end_to_end_path_is_rust_project_cargo_and_native_live_node() -> None:
    text = read(GUIDE)
    primary = section(text, "Primary Path: Rust Strategy to LiveNode")

    required = [
        "cargo new my-strategy --bin",
        "Cargo.toml",
        "nautilus-live",
        "nautilus-backtest",
        "nautilus-trading",
        "nautilus-okx",
        "GridMarketMaker",
        "GridMarketMakerConfig",
        "LiveNode::builder",
        ".add_data_client(",
        ".add_exec_client(",
        "node.add_strategy(strategy)?;",
        "node.run().await?;",
        "#[tokio::main]",
        "run_rust_backtest.md",
        "cargo run -p nautilus-backtest --features examples --example engine-ema-cross",
        "cargo run --release",
    ]
    missing = [term for term in required if term not in primary]
    assert missing == []

    assert "official upstream `docs/how_to/run_rust_live_trading.md`" in text


def test_primary_path_does_not_teach_python_strategy_backtest_or_tradingnode() -> None:
    primary = section(read(GUIDE), "Primary Path: Rust Strategy to LiveNode")

    forbidden = [
        "uv init",
        "uv add",
        "strategy.py",
        "run_backtest.py",
        "backtest_node.py",
        "my_strategy.py",
        "def on_bar",
        "TradingNode",
        "TradingNodeConfig",
    ]
    present = [term for term in forbidden if term in primary]
    assert present == []


def test_primary_live_node_source_compiles_against_pinned_upstream(tmp_path: Path) -> None:
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=UPSTREAM_ROOT,
        capture_output=True,
        check=False,
        text=True,
    )
    assert commit.returncode == 0, commit.stderr
    assert commit.stdout.strip() == EXPECTED_UPSTREAM_COMMIT

    crate = tmp_path / "guide-smoke"
    (crate / "src").mkdir(parents=True)
    (crate / "src/main.rs").write_text(rust_fence(read(GUIDE)), encoding="utf-8")
    (crate / "Cargo.toml").write_text(
        """[package]
name = "nt-guide-smoke"
version = "0.1.0"
edition = "2024"
rust-version = "1.97.1"

[dependencies]
anyhow = "1"
dotenvy = "0.15"
log = "0.4"
tokio = { version = "1", features = ["full"] }
nautilus-common = { path = "UPSTREAM/crates/common" }
nautilus-live = { path = "UPSTREAM/crates/live" }
nautilus-model = { path = "UPSTREAM/crates/model" }
nautilus-okx = { path = "UPSTREAM/crates/adapters/okx" }
nautilus-trading = { path = "UPSTREAM/crates/trading", features = ["examples"] }
""".replace("UPSTREAM", UPSTREAM_ROOT.as_posix()),
        encoding="utf-8",
    )

    cargo = ["rustup", "run", "1.97.1", "cargo"] if shutil.which("rustup") else ["cargo"]
    result = subprocess.run(
        [*cargo, "check", "--manifest-path", str(crate / "Cargo.toml")],
        capture_output=True,
        check=False,
        env={**os.environ, "CARGO_TARGET_DIR": str(UPSTREAM_ROOT / "target")},
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_rust_guidance_has_no_stale_057_or_removed_grid_constructor() -> None:
    rust_guidance = [
        REPO_ROOT / "docs/end_to_end_guide.md",
        REPO_ROOT / "skills/nt-backtest/SKILL.md",
        REPO_ROOT / "skills/nt-backtest/references/guides/run_rust_backtest.md",
        REPO_ROOT / "skills/nt-implement/SKILL.md",
        REPO_ROOT / "skills/nt-learn/curriculum/09-full-rust-trading.md",
        REPO_ROOT / "skills/nt-live/SKILL.md",
        REPO_ROOT / "skills/nt-live/references/concepts/rust.md",
        REPO_ROOT / "skills/nt-live/references/guides/run_rust_live_trading.md",
        REPO_ROOT / "skills/nt-adapters/references/examples/rust_adapters/bitmex/node_grid_mm.rs",
        REPO_ROOT / "skills/nt-adapters/references/examples/rust_adapters/dydx/node_grid_mm.rs",
    ]

    stale = [path.relative_to(REPO_ROOT).as_posix() for path in rust_guidance if '"0.57"' in read(path)]
    removed_api = [
        path.relative_to(REPO_ROOT).as_posix()
        for path in rust_guidance
        if "GridMarketMakerConfig::new(" in read(path)
    ]

    assert stale == []
    assert removed_api == []


def test_python_supported_v2_strategy_research_appendix_is_explicitly_labelled() -> None:
    appendix = section(read(GUIDE), "Appendix: Supported Python V2 Strategy and Research Lane")

    assert "Python remains supported for V2 strategy research" in appendix
    assert "research" in appendix.lower()
    assert "appendix" in appendix.lower()
    assert "not the default production live path" in appendix
    assert "legacy `TradingNode`" in appendix
    assert "migration/reference-only" in appendix
    assert "AI/advisory lane remains Python" in appendix
    assert "off execution-critical paths" in appendix
    assert "must not place orders" in appendix


def test_readme_developer_guide_count_is_two() -> None:
    text = read(README)
    assert "### Developer Guide Skills (2)" in text
    assert "### Developer Guide (3)" not in text


def test_owned_skill_files_do_not_repeat_top_level_compatibility_notes() -> None:
    for path in [NT_LIVE, NT_TESTING]:
        text = read(path)
        body = text.split("---", 2)[-1]
        pre_heading = body.split("# ", 1)[0]
        assert "NT v2 compatibility note:" not in pre_heading


def test_python_appendix_keeps_one_local_legacy_label() -> None:
    appendix = section(read(GUIDE), "Appendix: Supported Python V2 Strategy and Research Lane")
    assert appendix.count("NT v2 compatibility note:") == 1
    assert "legacy `TradingNode` material is migration/reference-only" in appendix
