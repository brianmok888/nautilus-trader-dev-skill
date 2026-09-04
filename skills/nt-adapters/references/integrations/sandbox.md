# Sandbox

The sandbox adapter (`crates/adapters/sandbox/`, Python projection
`nautilus_trader.adapters.sandbox`) provides an execution client backed by a
local matching engine. Pair it with a real data adapter to paper-trade venue
market data without sending orders to the venue.

## Components

- `SandboxExecutionClientConfig`: Execution client configuration (starting
  balances, fee and fill models, matching-engine behavior switches).
- `SandboxExecutionClientFactory`: Execution client factory registered with the
  live node builder.

There is no sandbox data client; source market data from another adapter (for
example Databento).

## Configuration

`SandboxExecutionClientConfig` (pinned `crates/adapters/sandbox/src/config.rs`)
mirrors the backtest matching-engine options:

| Option                          | Default        | Description |
|---------------------------------|----------------|-------------|
| `account_id`                    | `SANDBOX-001`  | Account ID for this client. |
| `venue`                         | `SANDBOX`      | Venue for this sandbox execution client. |
| `starting_balances`             | `[]`           | Starting balances for the sandbox venue. |
| `base_currency`                 | `None`         | Base currency for the venue (`None` for multi-currency). |
| `oms_type`                      | `Netting`      | Order management system type. |
| `account_type`                  | `Margin`       | Account type for the client. |
| `default_leverage`              | `1`            | Default account leverage (margin accounts). |
| `leverages`                     | `{}`           | Per-instrument leverage overrides. |
| `book_type`                     | `L1_MBP`       | Order book type for the matching engine. |
| `fee_model`                     | `None`         | Fee model for the sandbox matching engine. |
| `fill_model`                    | `None`         | Fill model for the sandbox matching engine. |
| `frozen_account`                | `False`        | Freeze the account against balance changes. |
| `bar_execution`                 | `True`         | Process bars in the matching engine. |
| `trade_execution`               | `True`         | Process trades in the matching engine. |
| `reject_stop_orders`            | `True`         | Reject stop orders whose trigger is already in the market. |
| `support_gtd_orders`            | `True`         | Support GTD time in force. |
| `support_contingent_orders`     | `True`         | Respect contingent orders. |
| `use_position_ids`              | `True`         | Generate venue position IDs on fills. |
| `use_random_ids`                | `False`        | Use random UUID4 venue order/position IDs. |
| `use_reduce_only`               | `True`         | Honor the `reduce_only` execution instruction. |
| `queue_position`                | `False`        | Track limit order queue position during execution. |
| `liquidity_consumption`         | `False`        | Track order book liquidity consumption per level. |
| `bar_adaptive_high_low_ordering`| `False`        | Adapt bar high/low processing order to the bar shape. |
| `use_market_order_acks`         | `False`        | Generate `OrderAccepted` events for market orders. |
| `oto_full_trigger`              | `False`        | OTO children wait for a full parent fill before release. |

## Wiring

Register the sandbox execution factory alongside a data adapter factory on the
live node builder (pinned example:
`crates/adapters/sandbox/examples/databento_cme.rs`):

```rust
use nautilus_databento::{data::DatabentoDataClientConfig, factories::DatabentoDataClientFactory};
use nautilus_live::node::LiveNode;
use nautilus_model::{
    enums::{AccountType, BookType, OmsType},
    identifiers::{AccountId, TraderId, Venue},
    types::{Currency, Money},
};
use nautilus_sandbox::{SandboxExecutionClientConfig, SandboxExecutionClientFactory};

let sandbox_config = SandboxExecutionClientConfig {
    account_id: AccountId::from("XCME-SANDBOX-001"),
    venue: Venue::new("XCME"),
    starting_balances: vec![Money::new(1_000_000.0, Currency::USD())],
    oms_type: OmsType::Netting,
    account_type: AccountType::Margin,
    book_type: BookType::L1_MBP,
    trade_execution: false, // bars drive the matching engine instead
    ..Default::default()
};

let mut node = LiveNode::builder(trader_id, environment)?
    .with_name("DATABENTO-CME-SANDBOX")
    .with_load_state(false)
    .with_save_state(false)
    .add_data_client(
        None,
        Box::new(DatabentoDataClientFactory::new()),
        Box::new(databento_config),
    )?
    .add_simulated_exec_client(
        Some("XCME".to_string()),
        Box::new(SandboxExecutionClientFactory::new()),
        Box::new(sandbox_config),
    )?
    .with_delay_post_stop_secs(2)
    .build()?;
```

The same wiring is available from Python through the
`nautilus_trader.adapters.sandbox` projection
(`SandboxExecutionClientConfig`, `SandboxExecutionClientFactory`).

## Example

The pinned upstream example is
`crates/adapters/sandbox/examples/databento_cme.rs`, which runs the
`ExecTester` strategy against Databento CME market data with a sandbox
execution client. Set `DRY_RUN = true` in the example to connect without
submitting orders. A copy of the pinned file ships in this skill at
`references/examples/rust_adapters/sandbox/databento_cme.rs`.
