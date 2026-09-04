NT v2 compatibility note: this file is a migration/reference-only Python/Cython
curriculum snapshot. Do not use it for new work; current binding guidance
is Rust/PyO3-oriented. For the authoritative v1-to-v2 migration guide, see `MIGRATION_V2.md` at the root of the pinned upstream checkout.

The historical Stage 08 Cython/FFI walkthrough was removed from the active
curriculum during the V2 Rust cutover. Use repository history only for migration
analysis; verify every new binding against the current `crates/*/src/python/`
and `crates/pyo3/` source paths.
