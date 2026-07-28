# NT V2 Rust Cutover Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close every confirmed NT V2 Rust cutover audit finding and replace static readiness claims with executable, content-bound evidence for all 18 skills.

**Architecture:** Keep policy, executable examples, and validation aligned through focused pytest regressions and stdlib-only checker changes. Use the pinned upstream checkout for reproducible Rust/API evidence, a separate freshness reporter for moving upstream state, and generated readiness artifacts only after validation succeeds.

**Tech Stack:** Markdown skills, Python 3 standard library, pytest, Ruff, basedpyright, Cargo/Rust 1.97.1, Git.

## Global Constraints

- Rust development and conversion correctness has highest priority.
- Official latest/nightly docs and upstream NautilusTrader source override local guidance.
- Reproducible baseline is `6e59fd74eaacacbb7410936f1766bd89fcce6f59`; V2 `2.0.0rc2`; Rust workspace `0.61.0`; Rust `1.97.1`.
- Only the AI/EvoMap advisory lane defaults to Python; it cannot place orders or block execution.
- No new dependencies.
- Every behavior change follows RED, observed failure, minimal GREEN, and targeted verification.
- Commit one logical segment at a time with conventional commit messages.
- Push only after full verification, post-fix reconciliation, code-review approval, and architecture clearance.

---

### Task 1: Rust-first routing and inventory

**Files:**
- Modify: `tests/test_v2_guidance_hardening.py`
- Modify: `skills/nt/SKILL.md`
- Modify: `skills/nt-implement/SKILL.md`
- Modify: `AGENTS.md`
- Modify: `skills/AGENTS.md`
- Modify: `README.md`

**Interfaces:**
- Produces: the canonical 18-skill inventory and deterministic Rust-first routing language consumed by later G2 tests.

- [ ] Add tests requiring ambiguous production/general strategy work to route to `nt-strategy-builder-rust`, explicit Python intent to route to `nt-strategy-builder`, and inventories to contain exactly 18 skill names.
- [ ] Run `uv run pytest -q tests/test_v2_guidance_hardening.py -k 'routing or inventory'` and record the expected assertion failures.
- [ ] Make the smallest routing and inventory edits that satisfy the policy while retaining explicit supported-Python wording where factually required.
- [ ] Re-run the targeted tests and `uv run python tools/check_dev_guide_sync.py`.
- [ ] Commit as `fix: default nautilus workflows to rust`.

### Task 2: Compile-checked Rust strategy and current V2 APIs

**Files:**
- Modify: `tests/test_rust_first_end_to_end.py`
- Modify: `tests/test_v2_guidance_hardening.py`
- Modify: `skills/nt-strategy-builder-rust/SKILL.md`
- Modify: `skills/nt-architect/SKILL.md`
- Modify: `skills/nt-implement/SKILL.md`
- Modify: `skills/nt-adapters/SKILL.md`

**Interfaces:**
- Produces: a named extractable Rust fence and current API/version wording used by G2 harnesses.

- [ ] Add an extraction/Cargo-check regression for the strategy fence and static assertions rejecting `subscribe_order_fills`, `subscribe_order_cancels`, hard-coded crate `0.57`, and a fixed adapter count.
- [ ] Run those tests and record compile/static failures.
- [ ] Replace the broken fragments with a self-contained upstream-shaped example, current event handling guidance, workspace-derived dependency guidance, and count-free adapter wording.
- [ ] Re-run targeted tests, Cargo check, and developer-guide sync.
- [ ] Commit as `fix: align rust examples with nautilus v2`.

### Task 3: Quarantine legacy executable surfaces

**Files:**
- Modify: `tests/test_template_classification.py`
- Modify: `tools/check_dev_guide_sync.py`
- Modify or remove: `skills/nt-strategy-builder/templates/*.py`
- Modify: `skills/nt-strategy-builder/AGENTS.md`
- Modify: `skills/nt-dex-adapter/AGENTS.md`
- Modify: `skills/nt-dex-adapter/rules/compliance_checklist.md`
- Modify or remove: `skills/nt-dex-adapter/templates/dex_factory.py`
- Modify/move: `skills/nt-adapters/references/examples/**/*.py`

**Interfaces:**
- Produces: a classifier that scans templates and executable examples and an explicit legacy/migration namespace for any retained Python live code.

- [ ] Extend tests to enumerate executable Python reference roots and reject default/live `TradingNode` files even when they have a generic classification banner.
- [ ] Run the classifier tests and capture the unclassified/stale surface failures.
- [ ] Remove redundant legacy executables or move/rename retained material into explicit legacy/migration locations; replace default guidance with Rust `LiveNode` references.
- [ ] Harden the checker so file banners cannot bless stale default/live executable APIs.
- [ ] Re-run classification, guide sync, and affected skill tests.
- [ ] Commit as `fix: quarantine legacy nautilus executables`.

### Task 4: Complete and content-bind all 18 G2 harnesses

**Files:**
- Modify: `tests/test_skill_g2_harnesses.py`
- Modify: `tools/check_skill_g2_harnesses.py`
- Modify/regenerate: `references/g2-evidence/*.json`
- Modify: readiness-card sections in `skills/nt*/SKILL.md`

**Interfaces:**
- Produces: exact 18-skill registry, non-empty owned paths, provenance validation, and targeted `nt-live`, `nt-trading`, and `nt-strategy-builder-rust` harnesses.

- [ ] Add tests requiring exactly 18 skills, non-empty owned paths including each `SKILL.md`, complete hash validation, expected upstream commit, and the three missing Rust harnesses.
- [ ] Run the G2 tests and record the expected manifest/provenance failures.
- [ ] Implement minimal registry, hashing, validation, and targeted harness changes without self-referential repository-commit cycles.
- [ ] Execute every harness and regenerate artifacts/readiness evidence.
- [ ] Re-run G2 tests and artifact validation.
- [ ] Commit as `feat: validate all nautilus g2 harnesses`.

### Task 5: Enforce the AI advisory boundary

**Files:**
- Modify: `tests/test_skill_g2_harnesses.py`
- Modify: `tests/test_v2_guidance_hardening.py`
- Modify: `tools/check_skill_g2_harnesses.py`
- Modify: `skills/nt-evomap-integration/SKILL.md`
- Modify: EvoMap templates/examples if present.

**Interfaces:**
- Produces: structural checks for forbidden execution authority and required non-blocking/approval/fallback semantics.

- [ ] Add tests rejecting order submission APIs, execution-client authority, and synchronous hot-handler networking in AI/EvoMap executable surfaces.
- [ ] Run tests and record the missing enforcement failure.
- [ ] Add the smallest checker and skill-contract changes necessary; do not invent a runtime implementation absent from the repository.
- [ ] Re-run targeted G2 and guidance tests.
- [ ] Commit as `fix: enforce advisory-only ai lane`.

### Task 6: Upstream freshness and archival cleanup

**Files:**
- Create: `tools/check_upstream_freshness.py`
- Create or modify: `tests/test_upstream_freshness.py`
- Modify: `tools/upstream_baseline.py`
- Modify: `tools/check_dev_guide_snapshot_sync.py`
- Modify: `skills/nt-signals/references/guides/indicators_guide.md`
- Modify: `skills/nt-data/references/guides/databento.md`
- Modify: historical `docs/superpowers/specs/*.md` and plans containing V1 instructions.

**Interfaces:**
- Produces: a read-only JSON/text freshness report that never mutates the pinned baseline.

- [ ] Add tests for pinned-versus-current reporting and archival headers for historical/Cython/TradingNode guidance.
- [ ] Run them and record failures.
- [ ] Implement the stdlib-only reporter and move/remove prominent legacy sections or label them archival.
- [ ] Re-run freshness, snapshot, and legacy checks.
- [ ] Commit as `feat: report nautilus upstream freshness`.

### Task 7: Reconcile, review, verify, and ship

**Files:**
- Modify: readiness cards and follow-up TODO only if fresh evidence requires it.

**Interfaces:**
- Consumes: all prior segment outputs.
- Produces: final verified branch merged to `main` and pushed to `origin/main`.

- [ ] Re-run the original Phase 1 searches and list each finding as closed or residual with file:line evidence.
- [ ] Regenerate all 18 readiness cards with only `Pass`, `Pending`, or `Blocked (+ reason)` and measurable evidence.
- [ ] Request independent code review and architecture review; fix all P0/P1 or BLOCK findings using failing tests first.
- [ ] Run `uv run pytest -q --ignore=tests/test_quality_gates.py`, `uv run pytest -q tests/test_quality_gates.py`, `uv run --with ruff ruff check .`, basedpyright/static analysis, guide and snapshot sync, all 18 G2 executions/validation, freshness report, `python3 -m compileall -q tools tests`, and `git diff --check`.
- [ ] Merge the feature branch into local `main`, rerun the full verification on the merged tree, and push `origin/main` without force.
- [ ] Report review summary, readiness tables, commit SHAs, validation evidence, and any residual Pending/Blocked gates.

## Self-review

- Spec coverage: all confirmed Segments A-G, progressive gates, reconciliation, commits, merge, and push have an owning task.
- Placeholder scan: no `TBD`, deferred implementation placeholder, or undefined interface remains.
- Type/path consistency: the 18-skill G2 registry, named Rust fence, freshness reporter, evidence directory, and readiness-card paths are consistent across tasks.
