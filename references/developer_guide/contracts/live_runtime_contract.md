NT v2 compatibility note: legacy Cython/v1 and Python live `TradingNode` references in this file are retained for migration/reference-only context. Prefer Rust v2/PyO3 guidance and `LiveNode` for new Rust-backed live work.

# Live Runtime Contract

Sources:

- `references/concepts/live.md`
- Official developer guide testing and adapter pages

## Required guidance

NT v2 compatibility note: legacy Cython/v1 reference-only; prefer Rust v2/PyO3 for new work.

- Prefer `nautilus_trader.live.LiveNode` for new Rust-backed PyO3 adapter and v2
  live-runtime examples.
- Treat `nautilus_trader.live.node.TradingNode` as legacy v1/Cython-oriented
  guidance unless the skill is documenting an existing integration that still
  uses it.
- Keep reconciliation enabled for production live execution unless a documented
  adapter limitation makes it impossible.
- Refresh account state and satisfy startup reconciliation before announcing a
  production live client as connected.

## Review rule

NT v2 compatibility note: Python live/integration-specific TradingNode; use LiveNode for Rust v2/Rust-backed work.

Unqualified “use TradingNode” guidance in new adapter work is stale. Either use
`LiveNode` or label the example as legacy/integration-specific.
