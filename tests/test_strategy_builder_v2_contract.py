from __future__ import annotations

from importlib import import_module
from pathlib import Path

import pytest

pytest.importorskip("nautilus_trader")

backtest = import_module("nautilus_trader.backtest")
if not hasattr(backtest, "BacktestNode"):
    pytest.skip("requires the pinned NautilusTrader V2 module set", allow_module_level=True)
config_module = import_module("nautilus_trader.config")
model = import_module("nautilus_trader.model")
BacktestNode = backtest.BacktestNode
BacktestEngineConfig = config_module.BacktestEngineConfig
BacktestRunConfig = config_module.BacktestRunConfig
BacktestVenueConfig = config_module.BacktestVenueConfig
AccountType = model.AccountType
BookType = model.BookType
OmsType = model.OmsType


REPO_ROOT = Path(__file__).resolve().parents[1]
LEGACY_ROOT = REPO_ROOT / "skills/nt-strategy-builder"


def test_current_v2_backtest_node_contract_builds() -> None:
    venue = BacktestVenueConfig(
        name="SIM",
        oms_type=OmsType.NETTING,
        account_type=AccountType.CASH,
        book_type=BookType.L1_MBP,
        starting_balances=["10_000 USD"],
    )
    config = BacktestRunConfig(
        engine=BacktestEngineConfig(),
        venues=[venue],
        data=[],
    )

    assert BacktestNode([config]) is not None
    assert len(config.venues) == 1
    assert config.venues[0].name == "SIM"


def test_legacy_python_lane_is_static_migration_reference() -> None:
    skill = (LEGACY_ROOT / "SKILL.md").read_text()
    agents = (LEGACY_ROOT / "AGENTS.md").read_text()

    assert "migration/reference-only" in skill
    assert "migration/reference-only" in agents
    assert "nt-strategy-builder-rust" in skill
    assert "nt-strategy-builder-rust" in agents


def test_legacy_templates_are_not_presented_as_current_v2_examples() -> None:
    templates = sorted((LEGACY_ROOT / "templates/legacy_migration").glob("*.py"))

    assert templates
    for template in templates:
        text = template.read_text()
        assert "migration/reference-only" in text or "legacy" in text.lower(), template
