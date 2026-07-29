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

## Review fix Round 2/5

### RED evidence

Executable tests were added before implementation for derived precision safety,
the exact mass-status fail-closed override, and direct construction through the
current live-client base contracts:

```text
uv run pytest skills/nt-dex-adapter/tests/test_legacy_migration_fail_closed.py skills/nt-dex-adapter/tests/test_nonproduction_migration_templates.py -q
...............F..........FFF.F......F                                   [100%]
6 failed, 32 passed in 2.77s
```

The failures showed that inherited mass status entered framework logic instead
of failing immediately, tiny/overflowing derived values reached Nautilus value
construction, and the migration clients did not accept the required event loop.
One construction test initially referenced the provider config from the wrong
dynamically loaded module; that test wiring error was corrected before using the
remaining constructor failures as implementation evidence. The next RED run
then reached the live base constructor and proved the provider was not a current
`InstrumentProvider`, followed by an execution-config serialization failure.

### GREEN implementation

- Swap conversion now validates the raw input and output, derived execution
  price, and six/eight-decimal serialized price/size before constructing
  `Price`, `Quantity`, or `TradeTick`.
- Tests cover a price quantizing to zero, a ratio overflowing to infinity, a
  size quantizing to zero, and an ordinary positive trade that constructs.
- The exact pinned `generate_mass_status(self, lookback_mins: int | None = None)
  -> ExecutionMassStatus | None` override now raises immediately. Its executable
  test proves the reconciliation flag remains false.
- Data and execution constructors now accept and pass `loop` and
  `instrument_provider`; the data constructor passes its compatible config.
  The execution base receives `config=None` because the migration config's
  `SecretStr` is not serializable by the pinned Nautilus component config
  encoder; the complete migration config remains retained on the client.
- The migration provider now subclasses the pinned `InstrumentProvider`, and
  the factory forwards its existing loop to both clients.
- The existing migration harness now imports and constructs both clients with
  real test-kit clock, message bus, cache, provider, and configs.

### Validation evidence

```text
uv run pytest skills/nt-dex-adapter/tests/test_legacy_migration_fail_closed.py skills/nt-dex-adapter/tests/test_nonproduction_migration_templates.py -q
38 passed in 2.53s

uv run pytest skills/nt-dex-adapter/tests -q
70 passed in 11.38s

uv run pytest tests/test_template_classification.py -q
14 passed in 0.37s

uv run pytest tests/test_v2_guidance_hardening.py -q
22 passed in 0.10s

uv run python tools/check_dev_guide_sync.py
Developer guide sync checks passed.

uv run ruff check <six changed Python files>
All checks passed!

python3 -m compileall -q <six changed Python files>
exit 0

git diff --check
exit 0
```

Normal repository type checking was run without ignores or alternate config:

```text
uv run basedpyright --outputjson
276 errors, 6358 warnings, 0 notes
exit 1
```

This remains a repository-wide red gate and is not claimed as a pass. The normal
run has no error in either changed test and no data/execution constructor call
error, task generic error, or execution-client reconciliation override error.
It reports 25 errors across the changed templates: 14 existing dynamic
standalone/package sibling-import diagnostics, 10 strict typing diagnostics in
the migration provider's pre-existing dynamic fallback/raw metadata surface,
and one pre-existing factory execution `create` override mismatch involving its
extra `account_id` argument. Runtime import and construction are covered by the
38-test GREEN run. The remaining diagnostics are recorded explicitly rather
than hidden with basedpyright configuration or ignores.
## Review fix Round 3/5

### RED evidence

Executable tests were added before implementation for fixed-point range errors,
canonical factory invocation, framework account identity, clean package imports,
secret-safe component config, provider cache isolation, and the real
`reconciliation_active` state. After correcting test-loader wiring so
package-relative imports reached their intended modules, the focused feature RED
included:

```text
6 failed, 40 passed in 3.65s
```

The failures showed clean subprocess imports and secret-safe base configuration
were not yet satisfied. Earlier RED runs in the same cycle also demonstrated
out-of-range Nautilus fixed-point exceptions escaping without a template-domain
error, a seventh required factory argument, parallel account identity, an
RPC-only provider cache key, and mass-status verification against an invented
flag.

### GREEN implementation

- Finite but out-of-range serialized price/size values are parsed before tick
  creation; Nautilus range failures become `InvalidSwapEventError`, with no tick.
- Execution factory has the pinned six-argument signature and derives
  `AccountId(f"{name}-001")` without credentials.
- Execution construction calls `_set_account_id(account_id)` and runtime asserts
  the framework `client.account_id`.
- Legacy executables use package-relative imports without `sys.path` mutation;
  each imports in a clean subprocess.
- The live base receives a serializable empty `NautilusConfig`; operational
  `SecretStr` config remains private. Serialization/repr checks exclude secrets.
- Provider caching keys on RPC URL, ordered pools, and sandbox mode.
- Mass status proves the actual `reconciliation_active` property remains false.

### Validation evidence

```text
focused: 46 passed in 12.37s
full DEX: 78 passed in 18.66s
classification: 14 passed in 0.37s
V2 guidance: 22 passed in 0.11s
developer guide sync: passed
Ruff: passed
compileall: exit 0
git diff --check: exit 0
```

Normal basedpyright ran without ignores or alternate config:

```text
uv run basedpyright --outputjson
261 errors, 6368 warnings, 0 notes
exit 1
```

This remains a repository-wide red gate. There are no errors in the changed
tests or legacy data, execution, and factory templates: constructor, canonical
factory, reconciliation, and package-import errors are gone. The only 10 errors
among changed files are in the retained migration provider's pre-existing
dynamic fallback and raw metadata typing surface: three unchecked `ModuleSpec`
errors, one dynamic config type-expression error, three raw-dict generic errors,
and three narrowed-config attribute/raw metadata errors. They are reported, not
suppressed.
