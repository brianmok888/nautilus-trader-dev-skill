# Signal Reference Snapshots

## OVERVIEW
Indicators, custom-data contracts and a copied Rust analysis crate; score 12,
with a distinct source-reference domain below the signal workflow.

## WHERE TO LOOK
| Need | Location |
|------|----------|
| Rust analysis public modules | `rust/analysis/src/lib.rs` |
| Analyzer registration and calculation | `rust/analysis/src/analyzer.rs` |
| Statistic extension contract | `rust/analysis/src/statistic.rs` |
| Individual statistic implementations | `rust/analysis/src/statistics/` |
| PyO3 statistic registration | `rust/analysis/src/python/mod.rs` |
| Custom-data persistence requirements | `guides/custom_data_patterns.md` |
| Indicator scale and initialization | `guides/indicators_guide.md` |
| Arrow schema and IPC guidance | `guides/serialization_patterns.md` |

## CONVENTIONS
- The analysis manifest inherits workspace dependencies and metadata; this
  copied tree does not establish a standalone build command.
- `default` features are empty; `python` enables bindings and
  `extension-module` includes `python` in the copied manifest.
- `PortfolioStatistic` implementations used by the analyzer override returns,
  realized-PnL and position calculations; unsupported categories return `None`.
- Benchmark calculation is optional and defaults to `None` in that trait.
- Keep JSON and Arrow round-trip evidence separate for custom data.

## ANTI-PATTERNS
- Relying on the three panicking default statistic calculation methods.
- Applying indicator thresholds before initialization or without their scale.
- Inventing Arrow layouts instead of checking `get_arrow_schema_map`.
- Reintroducing removed `serialization.arrow`, `ArrowSerializer` or
  `register_arrow()` interfaces from historical examples.
- Interpreting copied bindings or tests as proof that a runtime was exercised.
