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

## Legacy Python timeout configuration (migration/reference-only)

v1 configured the four connection timeouts on the Python node config; the same fields live on the Rust `LiveNodeConfig` at v2.

```python
# NT v2 compatibility note: v1-only snippet; v2 uses Rust LiveNodeConfig timeouts. Python live migration/reference-only.
config = TradingNodeConfig(
    timeout_connection=30.0,
    timeout_reconciliation=10.0,
    timeout_portfolio=10.0,
    timeout_disconnection=10.0,
)
```

## Legacy Python live configuration for custom DEX migration

```python
# NT v2 compatibility note: Python live migration/reference-only configuration.
config = TradingNodeConfig(
    data_clients={
        "MYDEX": MyDEXDataClientConfig(rpc_url="https://...", wallet_address="0x...")
    },
    exec_clients={
        "MYDEX": MyDEXExecClientConfig(
            rpc_url="https://...", private_key=SecretStr(...)
        )
    },
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

## v1 to v2 `StrategyConfig` subclass mapping

NT v2 compatibility note: the v1 pattern below is migration/reference-only;
new Python config subclasses use the v2 shape, and new production work uses the
Rust v2 lane (`nt-strategy-builder-rust`).

The legacy lane (`templates/legacy_migration/multi_venue_strategy.py`) shows the
v1 `frozen=True` annotated-struct subclass (migration/reference-only): declared
fields are consumed directly by the legacy base. v2 simplified Python config
subclass definitions (bed07c6c3e):

- Declare custom fields as keyword-only arguments on `__init__`, so no
  positional argument is matched against a base field.
- Accept `**_kwargs` so base keywords pass through the subclass signature.
- Call `super().__init__()` with no arguments, then assign the custom fields;
  the PyO3 base reads its own fields in `__new__` and ignores unrecognized
  keywords, so no `__new__` override is needed.
- Do not reuse a base field name (`strategy_id`, `order_id_tag`, `oms_type`,
  ...) for a custom field, and keep a `__new__` override only where a custom
  field widens a base field's type.

v1 (frozen annotated struct, migration/reference-only):

```python
# NT v2 compatibility note: v1 shape retained for migration reference only.
class MultiVenueStrategyConfig(StrategyConfig, frozen=True):
    primary_instrument_id: str
    secondary_instrument_id: str
    min_spread_bps: float = 10.0
    max_position_size: float = 1.0
    trade_primary: bool = True
```

maps to the v2 keyword-only subclass shape:

```python
from nautilus_trader.config import StrategyConfig

class MultiVenueStrategyConfig(StrategyConfig):
    def __init__(
        self,
        *,
        primary_instrument_id: str,
        secondary_instrument_id: str,
        min_spread_bps: float = 10.0,
        max_position_size: float = 1.0,
        trade_primary: bool = True,
        **_kwargs,
    ) -> None:
        super().__init__()
        self.primary_instrument_id = primary_instrument_id
        self.secondary_instrument_id = secondary_instrument_id
        self.min_spread_bps = min_spread_bps
        self.max_position_size = max_position_size
        self.trade_primary = trade_primary
```

Source: `docs/concepts/strategies.md` (strategy configuration) and
`MIGRATION_V2.md` (config subclass rule) at bed07c6c3e, present at the pinned
commit 6df237382eb1d8411906f9b1790fa06f8ba7aad4.
