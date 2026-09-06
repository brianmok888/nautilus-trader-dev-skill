# Portfolio

> **NT v2 compatibility note:** Python examples in this file are retained pre-V2 migration/reference-only content (whole file); current V2 APIs are the flat `nautilus_trader.model` / `nautilus_trader.testkit` surfaces documented in the pinned upstream docs.

The Portfolio is the central hub for managing and tracking all positions across active strategies for the trading node or backtest.
It consolidates position data from multiple instruments, providing a unified view of your holdings, risk exposure, and overall performance.
Explore this section to understand how NautilusTrader aggregates and updates portfolio state to support effective trading and risk management.

## Currency conversion

The Portfolio supports automatic currency conversion for PnL and exposure calculations,
allowing you to view results in your preferred currency. This is particularly useful when
trading across multiple instruments with different settlement currencies or managing multiple
accounts with different base currencies.

### Supported conversions

Currency conversion is available for the following portfolio queries:

- `realized_pnl()` / `realized_pnls()` - Convert realized PnL to target currency.
- `unrealized_pnl()` / `unrealized_pnls()` - Convert unrealized PnL to target currency.
- `total_pnl()` / `total_pnls()` - Convert total PnL to target currency.
- `net_exposure()` / `net_exposures()` - Convert net exposure to target currency.

All methods accept an optional `target_currency` parameter to specify the desired output
currency.

### Single account behavior

When querying a single account without specifying `target_currency`, the Portfolio
automatically converts values to that account's base currency:

```python
# Returns exposure in the account's base currency (e.g., USD)
exposure = portfolio.net_exposures(venue=BINANCE, account_id=account_id)
```

### Multi-account behavior

When querying multiple accounts simultaneously, behavior depends on whether you query
all instruments (`net_exposures()`) or a single instrument (`net_exposure()`):

**For `net_exposures()` (all instruments):**

- **Same base currency**: Automatically converts to the common base currency.
- **Different base currencies**: Returns a dict with multiple currencies, each converted
  to its account's base currency. Provide `target_currency` for single-currency results.

**For `net_exposure()` (single instrument across accounts):**

- **Different base currencies**: Returns `None` unless you provide `target_currency`.

```python
# Scenario 1: Multiple accounts, all with USD base currency
exposures = portfolio.net_exposures(venue=BINANCE)
# Returns {USD: Money(...)}

# Scenario 2: Multiple accounts with different base currencies (USD and EUR)
exposures = portfolio.net_exposures(venue=BINANCE)
# Returns {USD: Money(...), EUR: Money(...)}

# Force single currency across accounts
exposures = portfolio.net_exposures(venue=BINANCE, target_currency=USD)
# Returns {USD: Money(...)}
```

### Conversion failures

When `target_currency` is provided and currency conversion fails, behavior depends on
the method type:

- **Single-value methods** (`realized_pnl`, `unrealized_pnl`, `total_pnl`, `net_exposure`):
  Return `None` and log an error to prevent incorrect values.
- **Dict-returning methods** (`realized_pnls`, `unrealized_pnls`, `total_pnls`, `net_exposures`):
  Omit instruments that fail conversion but return results for successful conversions.

:::warning
Ensure exchange rate data is available when using `target_currency` for cross-currency
aggregation.
:::

### Conversion price types

When converting exposures to a target currency, the Portfolio uses different price types
depending on the position composition:

- **All long positions**: Uses `BID` prices (conservative for long exposure).
- **All short positions**: Uses `ASK` prices (conservative for short exposure).
- **Mixed positions**: Uses `MID` prices (neutral when both long and short exist).

This ensures conversions reflect realistic market conditions where you would liquidate
long positions at bid and cover short positions at ask. For mixed positions, mid-pricing
provides a neutral valuation.

If `use_mark_xrates` is enabled in the portfolio configuration, `MARK` prices replace
`MID` prices for mixed positions and general conversions.

## Portfolio statistics

There are a variety of [built-in portfolio statistics](https://github.com/nautechsystems/nautilus_trader/tree/develop/crates/analysis/src/statistics)
which are used to analyse a trading portfolios performance for both backtests and live trading.

The statistics are generally categorized as follows.

- PnLs based statistics (per currency)
- Returns based statistics
- Positions based statistics
- Orders based statistics

It's also possible to call a traders `PortfolioAnalyzer` and calculate statistics at any arbitrary
time, including *during* a backtest, or live trading session.

PnL-based statistics and `trade_pnl_records` resolve the query currency through
`resolve_pnl_currency` (`crates/analysis/src/analyzer.rs`): an explicit currency wins;
otherwise a single account-balance currency resolves it; otherwise a single realized-PnL
currency (across analyzer-held and recorded PnLs) resolves it; otherwise the query fails
with "Currency must be specified for multi-currency portfolio" -- pass an explicit
currency for genuinely multi-currency portfolios.

## Custom statistics

The current V2 path for custom statistics is the Rust `PortfolioStatistic` trait
(pinned source `crates/analysis/src/statistic.rs`): implement `name()` and the
`calculate_` method matching the input data (`calculate_from_returns`,
`calculate_from_realized_pnls`, `calculate_from_positions`, plus the optional
`calculate_from_returns_with_benchmark`, which defaults to `None`), then register
the type with `PortfolioAnalyzer::register_statistic(Arc::new(...))`. The
analyzer accepts `Arc<dyn PortfolioStatistic<Item = f64> + Send + Sync>` (pinned
source `crates/analysis/src/analyzer.rs`), and built-in examples live in
`crates/analysis/src/statistics/` (Sharpe ratio, Sortino, max drawdown, etc.).
The analyzer invokes `calculate_from_returns`, `calculate_from_realized_pnls`,
and `calculate_from_positions` on every registered statistic, and the trait
defaults panic, so an implementation must override all three and return `None`
for any category it does not support.

For example, a custom win-rate statistic:

```rust
use std::sync::Arc;

use nautilus_analysis::analyzer::PortfolioAnalyzer;
use nautilus_analysis::statistic::PortfolioStatistic;
use nautilus_analysis::Returns;
use nautilus_model::position::Position;

#[derive(Debug, Default)]
struct SessionWinRate;

impl PortfolioStatistic for SessionWinRate {
    type Item = f64;

    fn name(&self) -> String {
        "Session Win Rate".to_string()
    }

    fn calculate_from_realized_pnls(&self, realized_pnls: &[f64]) -> Option<f64> {
        if realized_pnls.is_empty() {
            return Some(f64::NAN);
        }
        let winners = realized_pnls.iter().filter(|&&pnl| pnl > 0.0).count();
        Some(winners as f64 / realized_pnls.len() as f64)
    }

    fn calculate_from_returns(&self, _returns: &Returns) -> Option<f64> {
        None // not a returns-based statistic
    }

    fn calculate_from_positions(&self, _positions: &[Position]) -> Option<f64> {
        None // not a positions-based statistic
    }
}

// Register with the portfolio analyzer
analyzer.register_statistic(Arc::new(SessionWinRate));
```

The analyzer calls all three `calculate_` methods on every registered statistic
(`crates/analysis/src/analyzer.rs` in the pinned tree), and the trait defaults
panic when a method is not overridden (`crates/analysis/src/statistic.rs:32-34`),
so always override all three and return `None` for categories the statistic does
not support, as above.

Python v2 path (current, not migration-only): subclass
`nautilus_trader.analysis.statistic.PortfolioStatistic` (exported as
`nautilus_trader.analysis.PortfolioStatistic` in the pinned
`python/nautilus_trader/analysis/__init__.pyi:29`) and override the same
`calculate_` methods; register instances via `Portfolio.register_statistic(...)`
(`python/nautilus_trader/portfolio/__init__.pyi:136`). See the pinned
docs/concepts/portfolio.md "Custom statistics" section for the current
subclassing example.

:::tip
Ensure your statistic is robust to degenerate inputs such as empty slices or insufficient data.
Return `None` for unknown/incalculable values, or a reasonable default like `0.0` when semantically appropriate (e.g., win rate with no trades).
For built-in returns-based statistics the degenerate-input convention is `NaN`, not `None`:
`SharpeRatio` derives dispersion via `calculate_std`, and `SortinoRatio` has an explicit
`returns.len() < 2` guard after daily binning ("a single observation cannot estimate
dispersion"), so both yield `NaN` for samples with fewer than two daily observations
(`crates/analysis/src/statistics/sortino_ratio.rs`).
:::

## Portfolio snapshots

`PortfolioSnapshot` (pinned source `crates/model/src/events/portfolio/snapshot.rs`)
is a point-in-time mark-to-market event for a single account. Unlike `AccountState`,
which fires only on balance or margin changes, a snapshot folds open-position
valuations into the totals: per-currency `unrealized_pnls`, session
`realized_pnls`, mark-to-market `total_equity`, and optionally
`base_currency_equity`, plus staleness diagnostics (`is_stale`, `stale_instruments`,
`stale_currencies`, `unpriced_instruments`).

Emission is configured through `PortfolioConfig` (pinned source
`crates/portfolio/src/config.rs`):

- `equity_curve` (default `true`) records one snapshot at account registration, at
  every UTC midnight (including while flat), and at shutdown.
- `snapshot_interval_ms` (default `None`) opts into a fine-grained stream: while
  the account holds at least one open position, an additional snapshot is emitted
  at this cadence.

Snapshots are published on the message bus under `events.portfolio.{account_id}`;
subscribe to that topic to consume the equity-curve stream. Totals span every
venue the account holds positions on, so multi-venue accounts produce a single
account-wide snapshot. `Portfolio::build_snapshot(account_id)` builds a snapshot
on demand, and `Portfolio::snapshots(account_id)` reads the recorded buffer
(pinned source `crates/portfolio/src/portfolio.rs`).

## Backtest analysis

Following a backtest run, a performance analysis will be carried out by passing realized PnLs, returns, positions and orders data to each registered
statistic in turn. Any output is then displayed in the tear sheet under the `Portfolio Performance` heading, grouped as:

- Realized PnL statistics (per currency)
- Returns statistics (for the entire portfolio)
- General statistics derived from position and order data (for the entire portfolio)

## Related guides

- [Positions](https://nautilustrader.io/docs/latest/concepts/positions/) - Position tracking within portfolios.
- [Reports](https://nautilustrader.io/docs/latest/concepts/reports/) - Generate portfolio analysis reports.
- [Visualization](https://nautilustrader.io/docs/latest/concepts/visualization/) - Visualize portfolio performance.
