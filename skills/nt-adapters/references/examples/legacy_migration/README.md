NT v2 compatibility note: all legacy/v1 and Python `TradingNode` files below
are migration/reference-only; prefer Rust V2/PyO3 and `LiveNode`.

# Python TradingNode migration/reference examples

These files are preserved only for migration and historical comparison. They
are not production defaults and are intentionally quarantined from the active
adapter reference tree. New adapter, data tester, execution tester, and live-node
work must use the Rust examples under `../rust_adapters/`, current `LiveNode`
wiring, and the official adapter specification.
