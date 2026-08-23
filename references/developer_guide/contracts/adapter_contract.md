NT v2 compatibility note: legacy Cython/v1 and Python live `TradingNode` references in this file are retained for migration/reference-only context. Prefer Rust v2/PyO3 guidance and `LiveNode` for new Rust-backed live work.

# Adapter Contract

Sources:

- `references/developer_guide/adapters.md`
- `references/developer_guide/spec_data_testing.md`
- `references/developer_guide/spec_exec_testing.md`

## Required guidance

- Keep Rust-core and Python-integration boundaries explicit.
- Use `nautilus_network::http::HttpClient` for Rust HTTP client examples unless
  official source evidence requires another client.
- Use `get_runtime().spawn()` for Python-runtime-sensitive async Rust paths; do
  not teach `tokio::spawn()` as the default from Python-driven adapter code.
- Align Python adapter methods with current command/request object signatures.
- Treat the required `InstrumentProvider` methods `load_all`, `load_ids`, and `load` for
  current v1.227-era guidance; override targeted load methods only for venue
  semantics or efficiency.
- Require order status reports, fill reports, position status reports, and mass
  status generation where the official execution client contract requires them.
- Queue `SetClient` before publishing a replacement WebSocket command channel
  or active-state flag when handlers receive their connected client by command.
- Keep expiring auth-token rotation in the outer client and stop refresh loops
  with `CancellationToken`; handlers send supplied tokens but do not sign.
- Treat transport, timeout, send, retry, parse, and whole-batch failures as
  ambiguous outcomes unless the venue returns explicit per-order results.
- Preserve the local prepare-failure carve-out from ExecTester policy: local
  cancel/modify prepare failures that prove the command was not sent may emit
  `OrderCancelRejected` or `OrderModifyRejected` when attributable to exactly
  one command.

## Review rule

An adapter is not ready when it only has provider/data/exec class shells. It must
prove command handling, subscriptions, reconciliation, account state, and factory
wiring for the claimed venue scope. Rejection events require venue evidence, not
client-side uncertainty.
