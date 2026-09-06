# TEMPLATE_CLASSIFICATION: migration/reference-only; not a production default
# -------------------------------------------------------------------------------------------------
#  Copyright (C) 2015-2026 Nautech Systems Pty Ltd. All rights reserved.
#  https://nautechsystems.io
#
#  Licensed under the GNU Lesser General Public License Version 3.0 (the "License");
#  You may not use this file except in compliance with the License.
#  You may obtain a copy of the License at https://www.gnu.org/licenses/lgpl-3.0.en.html
#
#  Unless required by applicable law or agreed to in writing, software distributed under
#  the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
#  KIND, either express or implied.  See the License for the specific language governing
#  permissions and limitations under the License.
# -------------------------------------------------------------------------------------------------

# v1 contrast: venues used to be configured with ImportableFillModelConfig /
# ImportableFeeModelConfig / ImportableLatencyModelConfig (class-path strings).
# Those config types are gone at the pinned baseline; BacktestVenueConfig now
# takes model instances directly from nautilus_trader.execution.

from nautilus_trader.backtest import BacktestDataConfig
from nautilus_trader.backtest import BacktestEngineConfig
from nautilus_trader.backtest import BacktestNode
from nautilus_trader.backtest import BacktestRunConfig
from nautilus_trader.backtest import BacktestVenueConfig
from nautilus_trader.config import ImportableStrategyConfig
from nautilus_trader.config import LoggerConfig
from nautilus_trader.execution import DefaultFillModel
from nautilus_trader.execution import FixedFeeModel
from nautilus_trader.execution import MakerTakerFeeModel
from nautilus_trader.execution import PerContractFeeModel
from nautilus_trader.execution import StaticLatencyModel
from nautilus_trader.model import Currency, InstrumentId, Money, TraderId

if __name__ == "__main__":
    # Example strategy configuration
    strategy_config = ImportableStrategyConfig(
        strategy_path="nautilus_trader.examples.strategies.ema_cross:EMACross",
        config={
            "instrument_id": "AAPL.NASDAQ",
            "bar_type": "AAPL.NASDAQ-1-MINUTE-LAST-EXTERNAL",
            "fast_ema_period": 10,
            "slow_ema_period": 20,
            "trade_size": 100,
        },
    )

    # Configure backtest engine
    engine_config = BacktestEngineConfig(
        trader_id=TraderId("BACKTESTER-001"),
        logging=LoggerConfig(stdout_level="INFO"),
    )

    USD = Currency.from_str("USD")

    # Built-in fill model instance
    fill_model = DefaultFillModel(
        prob_fill_on_limit=0.95,  # 95% chance of limit orders filling
        prob_slippage=0.05,  # 5% chance of slippage
        random_seed=42,  # For reproducibility
    )

    # Built-in latency model instance (static latencies)
    latency_model = StaticLatencyModel(
        base_latency_nanos=5_000_000,  # 5 milliseconds base latency
        insert_latency_nanos=2_000_000,  # Additional 2ms for inserts
        update_latency_nanos=3_000_000,  # Additional 3ms for updates
        cancel_latency_nanos=1_000_000,  # Additional 1ms for cancels
    )

    # Built-in fee model instances
    maker_taker_fee_model = MakerTakerFeeModel()
    fixed_fee_model = FixedFeeModel(Money(2.00, USD))  # 2.00 USD per trade
    per_contract_fee_model = PerContractFeeModel(Money(0.01, USD))  # 0.01 USD per contract

    # Create venue configs with different model instances
    venue_config1 = BacktestVenueConfig(
        name="NASDAQ",
        oms_type="NETTING",
        account_type="CASH",
        base_currency=USD,
        starting_balances=["1000000 USD"],
        book_type="L1_MBP",
        fill_model=fill_model,
        latency_model=latency_model,
        fee_model=maker_taker_fee_model,
    )

    venue_config2 = BacktestVenueConfig(
        name="NYSE",
        oms_type="NETTING",
        account_type="CASH",
        base_currency=USD,
        starting_balances=["1000000 USD"],
        book_type="L1_MBP",
        fill_model=fill_model,
        latency_model=latency_model,
        fee_model=fixed_fee_model,
    )

    venue_config3 = BacktestVenueConfig(
        name="CME",
        oms_type="NETTING",
        account_type="MARGIN",
        base_currency=USD,
        starting_balances=["1000000 USD"],
        book_type="L1_MBP",
        fill_model=fill_model,
        latency_model=latency_model,
        fee_model=per_contract_fee_model,
    )

    # Create data config (this is just a placeholder - you would need actual data)
    data_config = BacktestDataConfig(
        catalog_path="./data",
        data_type="QuoteTick",
        instrument_id=InstrumentId.from_str("AAPL.NASDAQ"),
    )

    # Create BacktestRunConfig
    run_config = BacktestRunConfig(
        engine=engine_config,
        venues=[venue_config1, venue_config2, venue_config3],
        data=[data_config],
    )

    # Create and build the backtest node, then attach the strategy from its config
    node = BacktestNode(configs=[run_config])
    node.build()
    node.add_strategy_from_config(run_config.id, strategy_config)

    # Note: This example won't actually run without proper data
    # results = node.run()

    print("Example of configuring BacktestVenueConfig with model instances")
    print(f"Venue 1 fee model: {venue_config1.fee_model}")
    print(f"Venue 2 fee model: {venue_config2.fee_model}")
    print(f"Venue 3 fee model: {venue_config3.fee_model}")
    print(f"Fill model: {venue_config1.fill_model}")
    print(f"Latency model: {venue_config1.latency_model}")
