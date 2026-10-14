# Tick Scheme

## Tick schemes at reviewed tip `52eef7955c`

The flat PyO3 model exports `FixedTickScheme`, `TieredTickScheme`,
`register_tick_scheme`, `get_tick_scheme` and `list_tick_schemes`.
Registered names cannot be replaced or removed. Legacy v1 tick-scheme
submodules are migration/reference-only; use the flat model exports.
Construct `FixedTickScheme(name, price_precision, price_increment: Price)`; the
increment must be positive and its precision cannot exceed price_precision.
`TieredTickScheme(name, price_precision, tiers, max_ticks_per_tier=10000)`
takes `(lower: float, upper: float, step: float)` tuples; positive infinity
is permitted as the final upper bound. Tiers must
be nonempty, ordered and nonoverlapping, with positive steps, representable
bounds and valid ranges; only the last tier may be open-ended, for which
max_ticks_per_tier bounds tick generation. Rust `TickScheme` is an enum.
Registration takes the scheme object; lookup takes its name, and listing
returns uppercase names sorted lexicographically. Names are trimmed and
case-insensitive. Duplicate registration and unknown lookup are errors.
Register before instruments resolve a
named scheme. Sources: upstream `crates/model/src/instruments/tick_scheme.rs`
and `crates/model/src/python/instruments/tick_scheme.rs`.

The legacy `nautilus_trader.model.tick_scheme` module does not exist in the pinned V2 tree: the
`nautilus_trader.model` package is a flat PyO3 re-export surface with no submodule pages. Tick
schemes are implemented in Rust at `crates/model/src/instruments/tick_scheme.rs`.
Instrument classes also expose an optional `tick_scheme: str | None` constructor
field and matching property, resolving the named registered scheme.

Owning Rust crate: `crates/model/src/instruments/`.
