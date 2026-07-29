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
