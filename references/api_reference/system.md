# System

The `nautilus_trader.system` Python package does not exist in the pinned V2 tree: there is no
`python/nautilus_trader/system/` directory at the pin. The kernel is implemented in Rust at
`crates/system/src/kernel.rs` (`NautilusKernel`, `NautilusKernelDependencies`). Its Python-facing
entry points are re-exported through the node packages instead:

- `LiveNode`, `LiveNodeBuilder`, `LiveNodeConfig`, `LiveNodeHandle` from flat `nautilus_trader.live`
- `BacktestEngine`, `BacktestNode`, `BacktestRunConfig` from flat `nautilus_trader.backtest`

Owning Rust crate: `crates/system/`.
