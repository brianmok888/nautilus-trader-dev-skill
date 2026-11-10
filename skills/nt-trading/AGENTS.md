# Trading Skill Guidance

## OVERVIEW
Order handling, execution, positions, risk and Rust strategy examples; score 9,
with a distinct trading domain spanning concepts and executable reference code.

## WHERE TO LOOK
| Need | Location |
|------|----------|
| Current trading readiness and event contracts | `SKILL.md` |
| Orders, execution and risk API pages | `references/api/` |
| Actors, strategies and position concepts | `references/concepts/` |
| Rust construction and lifecycle guides | `references/guides/` |
| Rust strategy reference implementations | `references/examples/rust_trading/examples/strategies/` |
| Historical Python templates and examples | `migration_reference/python/` |

## CONVENTIONS
- Use the event contracts in `SKILL.md` at their stated source versions.
- `OrderFillVoided` and terminal `VOIDED` handling include replay and reopen
  considerations; check the referenced fill before reasoning about recovery.
- The skill labels command-denial hooks at develop commit
  `77d785c69205c4326e6aadb46d03fb45357a78f2` and their absence from RC8
  `d53849b216e20f2c122ca01b4dd0da377638b186`; keep that distinction explicit.
- `OrderModifyDenied` and `OrderCancelDenied` mean the command was proven not
  sent; clear relevant local command bookkeeping without inventing a venue
  rejection or terminal order state.
- Read example configuration, state, strategy and tests together when porting.
- Portfolio and position pages carry their own historical migration labels.

## ANTI-PATTERNS
- Applying develop command-denial hooks to a release that lacks them.
- Treating a command denial as a successful cancel or a venue rejection.
- Inferring profitability or production readiness from a strategy example.
- Substituting historical Python order-management examples for current Rust
  strategy ownership and execution contracts.
