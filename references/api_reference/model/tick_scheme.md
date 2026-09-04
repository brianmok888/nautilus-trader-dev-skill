# Tick Scheme

The legacy `nautilus_trader.model.tick_scheme` module does not exist in the pinned V2 tree: the
`nautilus_trader.model` package is a flat PyO3 re-export surface with no submodule pages. Tick
schemes are implemented in Rust at `crates/model/src/instruments/tick_scheme.rs`. The surviving
Python surface is the optional `tick_scheme: str | None` constructor field and matching property
on instrument classes exported from flat `nautilus_trader.model` (for example `BettingInstrument`).

Owning Rust crate: `crates/model/src/instruments/`.
