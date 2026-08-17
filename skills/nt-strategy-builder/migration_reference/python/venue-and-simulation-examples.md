# Python venue and simulation migration reference

NT v2 compatibility note: every `TradingNode` and Python live example in this
file is legacy migration/reference-only; new production wiring uses Rust
`LiveNode`.

These examples document historical Python wiring only. They are not production defaults. New work routes to `nt-strategy-builder-rust`; these examples stay off execution-critical paths.

## Legacy Python live configuration for CeFi migration

```python
# NT v2 compatibility note: Python live migration/reference-only example.
from nautilus_trader.adapters.binance.config import BinanceDataClientConfig
from nautilus_trader.config import TradingNodeConfig

config = TradingNodeConfig(
    data_clients={
        "BINANCE": BinanceDataClientConfig(
            api_key=os.environ["BINANCE_API_KEY"],
            api_secret=os.environ["BINANCE_API_SECRET"],
            testnet=False,
        ),
    },
)
```

## Legacy Python live configuration for custom DEX migration

```python
# NT v2 compatibility note: Python live migration/reference-only configuration.
config = TradingNodeConfig(
    data_clients={"MYDEX": MyDEXDataClientConfig(rpc_url="https://...", wallet_address="0x...")},
    exec_clients={"MYDEX": MyDEXExecClientConfig(rpc_url="https://...", private_key=SecretStr(...))},
    data_client_factories={"MYDEX": MyDEXLiveDataClientFactory},
    exec_client_factories={"MYDEX": MyDEXLiveExecClientFactory},
)
```

## Catalog data

```python
from nautilus_trader.config import BacktestDataConfig
from nautilus_trader.persistence.catalog import ParquetDataCatalog

catalog = ParquetDataCatalog("/path/to/catalog")
data_config = BacktestDataConfig(
    catalog_path=str(catalog.path),
    data_cls="nautilus_trader.model.data:Bar",
    instrument_id="WETH-USDC.UNISWAP_V3",
    start_time="2024-01-01",
    end_time="2024-12-31",
)
```

## Fill and venue models

```python
from decimal import Decimal

from nautilus_trader.backtest.config import BacktestVenueConfig
from nautilus_trader.backtest.models import FillModel

dex_fill_model = FillModel(prob_fill_on_limit=0.3, prob_slippage=0.7, random_seed=42)
cefi_fill_model = FillModel(prob_fill_on_limit=0.5, prob_slippage=0.2, random_seed=42)

dex_venue_config = BacktestVenueConfig(
    name="UNISWAP_V3",
    oms_type="NETTING",
    account_type="CASH",
    base_currency="USDT",
    starting_balances=["10_000 USDT"],
    fill_model=dex_fill_model,
)
perp_venue_config = BacktestVenueConfig(
    name="BYBIT",
    oms_type="NETTING",
    account_type="MARGIN",
    base_currency="USDT",
    starting_balances=["10_000 USDT"],
    default_leverage=Decimal("10"),
    fill_model=cefi_fill_model,
)
```
