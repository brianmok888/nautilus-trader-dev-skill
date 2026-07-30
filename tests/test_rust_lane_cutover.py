from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
ACTIVE_SKILLS = (
    "skills/nt-signals/SKILL.md",
    "skills/nt-backtest/SKILL.md",
    "skills/nt-dev/SKILL.md",
    "skills/nt-testing/SKILL.md",
    "skills/nt-learn/SKILL.md",
    "skills/nt-strategy-builder-rust/SKILL.md",
)
ACTIVE_LIVE_GUIDES = (
    "skills/nt-learn/curriculum/07-live-trading.md",
    "references/concepts/live.md",
    "references/integrations/okx.md",
    "skills/nt-adapters/references/integrations/ib.md",
)
NON_AI_PYTHON_AUTHORIZATIONS = (
    "Python may prototype",
    "keep Python research/config",
    "Python labs are labelled Python research/config",
    "Python tests only for research/config",
    "Python v2 controller subclassing and importable controller configs are supported",
    "Python v2 subclassable execution algorithms are supported",
    "Python v2 `FeeModel` and `FillModel` subclass support enables",
    "document any Python research/config",
)
PYTHON_FENCE = re.compile(r"^```python\n(?P<body>.*?)^```", re.MULTILINE | re.DOTALL)


def read(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


@pytest.mark.parametrize("relative_path", ACTIVE_SKILLS)
def test_active_skills_authorize_only_ai_advisory_python(relative_path: str) -> None:
    # Given: an active skill participates in the Rust/Python lane cutover.
    text = read(relative_path)

    # When: its current authorization language is inspected.
    present = [phrase for phrase in NON_AI_PYTHON_AUTHORIZATIONS if phrase in text]

    # Then: no non-AI Python lane is active and the sole exception is explicit.
    assert present == []
    assert "only active Python lane is AI/advisory" in text


def test_live_curriculum_teaches_rust_livenode() -> None:
    # Given: Stage 07 is the active live-trading curriculum.
    text = read("skills/nt-learn/curriculum/07-live-trading.md")

    # When: its runnable runtime guidance is inspected.
    required = [
        "LiveNode::builder",
        ".add_data_client(",
        ".add_exec_client(",
        ".with_reconciliation",
        "node.add_strategy(strategy)?;",
        "node.run().await?;",
    ]

    # Then: it teaches the current Rust live path, not Python TradingNode.
    assert [term for term in required if term not in text] == []
    assert "TradingNode" not in text
    assert PYTHON_FENCE.findall(text) == []


@pytest.mark.parametrize("relative_path", ACTIVE_LIVE_GUIDES)
def test_active_live_guides_quarantine_python_tradingnode_snippets(
    relative_path: str,
) -> None:
    # Given: active references previously exposed copyable Python live wiring.
    text = read(relative_path)

    # When: Python source fences and migration routing are inspected.
    trading_node_fences = [
        fence for fence in PYTHON_FENCE.findall(text) if "TradingNode" in fence
    ]

    # Then: Python TradingNode source is absent and migration users get a pointer.
    assert trading_node_fences == []
    assert "migration_reference" in text


def test_nt_testing_uses_public_v2_exectester_projection() -> None:
    # Given: ExecTesterConfig is projected by the V2 testkit package.
    text = read("skills/nt-testing/SKILL.md")

    # When: active PyO3 import guidance is inspected.
    public_import = "from nautilus_trader.testkit import ExecTesterConfig"

    # Then: users receive the public projection, never the compatibility root.
    assert public_import in text
    assert 'PyModule::import(py, "nautilus_trader.core.nautilus_pyo3")' not in text
