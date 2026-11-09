# NautilusTrader References

This directory contains reference documentation for NautilusTrader concepts, APIs, and development guides.

> [!IMPORTANT]
> **Modern Tooling**: For current workflows including `uv`, `msgspec`, and `create_tearsheet`, please see the [docs/](../docs/) directory. Non-AI Python examples are migration/reference-only.
>
> - [End-to-End Guide](../docs/end_to_end_guide.md)
> - [uv Guide](../docs/uv_guide.md)
> - [Visualization](../docs/visualization.md)
> - [Serialization](../docs/serialization.md)

## Contents

- **concepts/**: Core architectural concepts (Data, Architecture, Execution, etc.)
- **developer_guide/**: Guides for implementing adapters, indicators, and strategies.
- **api_reference/**: Detailed API documentation.
- **integrations/**: Specifics for various exchange integrations.

## Upstream version boundary

The reproducible Rust V2 source baseline is develop commit
`77d785c69205c4326e6aadb46d03fb45357a78f2` (2026-11-08), synchronized on
2026-11-09. `tools/upstream_baseline.py` is the pin authority. Set
`NT_UPSTREAM_ROOT` to a clean checkout of that commit for repository validators;
the default cache may still contain an earlier pin.

The latest published release candidate is `v2.0.0rc8`, whose annotated tag
resolves to commit `d53849b216e20f2c122ca01b4dd0da377638b186` (2026-10-28).
Current develop is 300 commits ahead and identifies itself as `v2.0.0rc9` in
`version.json`; that version is unreleased. Current source guidance must not
be represented as available in rc8 without checking that tag's source.

Source synchronization and host-Python checks do not prove Rust compilation or
PyO3 runtime readiness. G2 evidence must be regenerated against the new pin;
earlier evidence remains historical until the harness records a fresh result.
