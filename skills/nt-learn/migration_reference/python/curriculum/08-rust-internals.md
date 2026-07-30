NT v2 compatibility note: this file is a migration/reference-only Python/Cython
curriculum snapshot. Do not use it for new non-AI work; current binding guidance
is Rust/PyO3-oriented, and the only active Python lane is AI/advisory.

The historical Stage 08 Cython/FFI walkthrough was removed from the active
curriculum during the V2 Rust cutover. Use repository history only for migration
analysis; verify every new binding against the current `crates/*/src/python/`
and `crates/pyo3/` source paths.
