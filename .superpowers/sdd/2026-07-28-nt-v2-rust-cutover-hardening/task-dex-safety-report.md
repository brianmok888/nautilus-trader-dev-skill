# DEX fail-closed safety report

## Scope

- Hardened only the quarantined `legacy_migration` DEX execution and data templates.
- Added source-contract regression tests under `skills/nt-dex-adapter/tests/`.
- Did not modify the G2 harness/evidence or AI actor.
- Added no dependency and retained exact legacy template classification and location.

## RED evidence

Tests were added before template changes and run with:

```text
uv run pytest skills/nt-dex-adapter/tests/test_legacy_migration_fail_closed.py -q
FFFFFF.                                                                  [100%]
6 failed, 1 passed in 0.22s
```

The six expected failures showed that submission, cancellation, account state,
reconciliation, receipt handling, and non-positive swap input did not yet fail
closed. Each failed because the required `NotImplementedError` or positive-input
guard was absent, not because of test setup or import errors.

## GREEN implementation

- `_submit_order` now raises before any lifecycle event because signing and
  broadcast are unimplemented. Its documented flow requires a validated,
  non-empty transaction hash before submission can be emitted.
- Cancel and cancel-all paths raise explicitly and cannot silently succeed.
- Account-state refresh raises rather than claiming an unqueried state.
- All unimplemented reconciliation methods raise rather than returning fake
  `None` or empty authoritative results. Guidance names TC-E84–87.
- Receipt monitoring raises without classifying unknown transport, receipt,
  parse, timeout, retry, or batch outcomes. Fabricated receipt, fill price,
  commission, trade ID, venue ID, quantity, and terminal events were removed.
  Guidance names TC-E74–78.
- Swap conversion rejects `amount_in <= 0` before constructing a `TradeTick`.

Targeted GREEN result:

```text
uv run pytest skills/nt-dex-adapter/tests/test_legacy_migration_fail_closed.py -q
.......                                                                  [100%]
7 passed in 0.06s
```

## Required validation

```text
uv run pytest skills/nt-dex-adapter/tests -q
44 passed in 11.66s

uv run pytest tests/test_template_classification.py -q
14 passed in 0.37s

uv run pytest tests/test_v2_guidance_hardening.py -q
22 passed in 0.07s

uv run python tools/check_dev_guide_sync.py
Developer guide sync checks passed.

uv run ruff check <three changed Python files>
All checks passed!

uv run basedpyright --project /tmp/basedpyright-dex.json
0 errors, 0 warnings, 0 notes

python3 -m compileall -q <three changed Python files>
exit 0

git diff --check
exit 0
```

The repository has no checked-in basedpyright configuration. A direct strict
invocation reports pre-existing template integration diagnostics involving the
standalone/package import bridge, legacy base-constructor shape, generic task
annotation, and legacy method override signature. The recorded successful
changed-file run used a temporary basic-mode config with both template paths in
`extraPaths` and disabled only those known legacy integration categories; it
reported no diagnostics in the changed safety logic or new tests.

## Result

The executable legacy DEX references now fail closed wherever authoritative
broadcast, cancellation, receipt parsing, reconciliation, or account queries are
not implemented, and cannot emit a zero-price trade for non-positive input.

## Review fix Round 1/5

### RED evidence

The source-substring tests were replaced first with executable unbound-method
tests using lifecycle/state probes, real async invocation, swap-construction
spies, and runtime signature inspection. Before implementation:

```text
uv run pytest skills/nt-dex-adapter/tests/test_legacy_migration_fail_closed.py -q
...FF......FFFFF..F..FFFF..                                              [100%]
12 failed, 15 passed in 2.97s
```

The failures reproduced all open findings: modify/query did not raise, all four
reconciliation signatures differed from the pinned contract, mass status was
unnecessarily overridden, infinite input reached quantity construction, and
zero, negative, or non-finite output reached price/tick construction. The async
probe tests also demonstrated that existing unsupported paths emitted no
lifecycle or account-state callbacks before raising.

### GREEN implementation

- Both `amount_in` and `amount_out` must now be finite and greater than zero
  before price, quantity, or `TradeTick` construction.
- Submit, cancel, cancel-all, modify, query, account refresh, receipt monitoring,
  and all retained reconciliation paths raise `NotImplementedError` before any
  lifecycle or state callback when their authoritative venue operation is absent.
- Reconciliation overrides now exactly accept `GenerateOrderStatusReport`,
  `GenerateOrderStatusReports`, `GenerateFillReports`, and
  `GeneratePositionStatusReports`, with the pinned return annotations.
- The stale `generate_mass_status` override was removed so the inherited local
  contract is used.
- Legacy classification and `legacy_migration` paths remain unchanged; no
  dependency was added.

### Validation evidence

```text
uv run pytest skills/nt-dex-adapter/tests/test_legacy_migration_fail_closed.py -q
27 passed in 2.44s

uv run pytest skills/nt-dex-adapter/tests -q
64 passed in 11.10s

uv run pytest tests/test_template_classification.py -q
14 passed in 0.37s

uv run pytest tests/test_v2_guidance_hardening.py -q
22 passed in 0.07s

uv run python tools/check_dev_guide_sync.py
Developer guide sync checks passed.

uv run ruff check skills/nt-dex-adapter/templates/legacy_migration/dex_exec_client.py skills/nt-dex-adapter/templates/legacy_migration/dex_data_client.py skills/nt-dex-adapter/tests/test_legacy_migration_fail_closed.py
All checks passed!

python3 -m compileall -q skills/nt-dex-adapter/templates/legacy_migration/dex_exec_client.py skills/nt-dex-adapter/templates/legacy_migration/dex_data_client.py skills/nt-dex-adapter/tests/test_legacy_migration_fail_closed.py
exit 0

git diff --check
exit 0
```

Normal repository type checking was run exactly as requested, without a
temporary config or suppressed override diagnostics:

```text
uv run basedpyright
275 errors, 6297 warnings, 0 notes
exit 1
```

This is an explicit repository-wide validation gap, not a pass. JSON filtering
of that same normal run found no error in the new behavioral test and no
`reportIncompatibleMethodOverride` error after signature alignment. It found 11
errors in the two retained legacy templates: eight unresolved/implicit sibling
import diagnostics from their existing standalone/package import bridge, two
existing base-constructor call-shape diagnostics, and one existing unparameterized
`asyncio.Task` diagnostic. These integration diagnostics predate the Round 1
safety logic and were left scoped out rather than hidden with ignores or config.

The earlier report section's temporary basic-config basedpyright result must not
be interpreted as repository type-check cleanliness; this Round 1 normal-command
result supersedes that claim.
