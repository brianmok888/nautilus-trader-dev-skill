# ExecTesterConfig API (current V2 guidance)

`ExecTesterConfig` validates venue order-lifecycle behavior through the
`ExecTester` strategy. Treat this page as the API guardrail for new adapter
execution-test guidance.

## Python constructor-keyword API

Python `ExecTesterConfig` is constructed with keyword arguments. Do not use
legacy `with_*` mutator examples in new Python guidance.

```python
from decimal import Decimal

from nautilus_trader.model import ClientId, InstrumentId, Quantity, StrategyId
from nautilus_trader.testkit import ExecTesterConfig

config = ExecTesterConfig(
    strategy_id=StrategyId("EXEC-TESTER-001"),
    instrument_id=InstrumentId.from_str("BTCUSDT-PERP.BINANCE"),
    client_id=ClientId("BINANCE"),
    order_qty=Quantity.from_str("0.001"),
    open_position_on_start_qty=Decimal("0.001"),
    enable_limit_buys=True,
    enable_limit_sells=True,
    use_post_only=True,
    limit_aggressive=False,
    use_quote_quantity=False,
    cancel_orders_on_stop=True,
    close_positions_on_stop=True,
    can_unsubscribe=True,
)
```

Common constructor keywords include `strategy_id=`, `order_id_tag=`,
`use_hyphens_in_client_order_ids=`, `use_uuid_client_order_ids=`,
`external_order_claims=`, `instrument_id=`, `client_id=`, `order_qty=`,
`subscribe_book=`, `subscribe_quotes=`, `subscribe_trades=`,
`open_position_on_start_qty=`, `open_position_on_first_quote=`,
`open_position_time_in_force=`, `enable_limit_buys=`, `enable_limit_sells=`,
`enable_stop_buys=`, `enable_stop_sells=`, `tob_offset_ticks=`,
`limit_time_in_force=`, `use_post_only=`, `limit_aggressive=`,
`use_quote_quantity=`, `use_individual_cancels_on_stop=`,
`cancel_orders_on_stop=`, `close_positions_on_stop=`,
`close_positions_time_in_force=`, `reduce_only_on_stop=`, `dry_run=`,
`log_data=`, `can_unsubscribe=`, `clamp_to_instrument_price_range=`,
`log_events=`, and `log_commands=`.

## Rust builder API

Rust `nautilus_testkit::testers::ExecTesterConfig` uses
`ExecTesterConfig::builder()` and `.build()?`. NT v2 compatibility note: legacy positional-constructor examples are migration/reference-only; do not copy them into new Rust adapter docs.

```rust
use nautilus_model::{identifiers::InstrumentId, types::Quantity};
use nautilus_trading::strategy::StrategyConfig;
use nautilus_testkit::testers::{ExecTester, ExecTesterConfig};

let tester_config = ExecTesterConfig::builder()
    .base(StrategyConfig {
        strategy_id: Some(strategy_id),
        ..Default::default()
    })
    .instrument_id(instrument_id)
    .client_id(client_id)
    .order_qty(Quantity::from("0.001"))
    .enable_limit_buys(true)
    .enable_limit_sells(true)
    .use_post_only(true)
    .build()?;

let tester = ExecTester::new(tester_config);
```

## Review rule

NT v2 compatibility note: Python live TradingNode fallback and legacy positional constructors are migration/reference-only anti-patterns; prefer Rust `ExecTesterConfig::builder()` for new Rust-backed V2 adapters.

Fail new execution-test guidance if Python examples omit constructor keywords,
Rust examples use migration/reference-only legacy positional constructors, or examples imply that Python
live `TradingNode` is the preferred path for new Rust-backed V2 adapters.
