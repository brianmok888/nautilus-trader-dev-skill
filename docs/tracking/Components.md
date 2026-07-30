# Components — nautilus-trader-dev-skill

<!-- CHARTER -->
<!-- Role: Per-skill detail — what each skill does, Rust-vs-Python orientation, readiness status, known gaps. -->
<!-- Read when: answering "what does skill X do?", "what's the readiness of Y?", "is Z reviewed?". -->
<!-- Updated when: a skill changed (new skill, readiness shift, review update). -->
<!-- Does NOT contain: invariants, structural inventory, issue tracking, plans. -->
<!-- Write-target rule: only update this file if a skill changed. -->

Review date: 2026-07-30
Audit commit: ceb53702d5c493406fe8976232df8843088b625e
Cutover gates: 18 skills × G0-G7 = 144 Pass, 0 Pending, 0 Blocked; the measurable cards remain in each `skills/nt*/SKILL.md` and are validated by `uv run python tools/check_skill_g2_harnesses.py --check-cards`.

## Rust-first tier (primary skills)

### nt-strategy-builder-rust

**Purpose:** Default production strategy and LiveNode wiring using Rust-first NT V2 patterns.
**Readiness:** review-ready (flagship Rust skill).
**Integration surfaces:** `nt` router dispatches here for production/live-node work; `nt-architect` feeds into it.
**Known gaps:** Historical audit found 2 migration-reference binding-generator mentions; post-fix reconciliation is in `docs/superpowers/reports/2026-07-29-nt-v2-rust-cutover-reconciliation.md`.
**Lane signal:** Rust-first; migration references remain quarantined and labelled.

### nt-architect

**Purpose:** Architecture decomposition (Actor/Indicator/Strategy). Starting point for new projects.
**Readiness:** review-ready.
**Integration surfaces:** Feeds `nt-implement`, `nt-strategy-builder-rust`.
**Known gaps:** Historical audit found 2 migration-reference binding-generator mentions; post-fix reconciliation is recorded in the cutover report.
**Lane signal:** Rust-first; migration references remain quarantined and labelled.

### nt-implement

**Purpose:** Strategy/Actor/Indicator implementation with templates + conventions.
**Readiness:** review-ready.
**Integration surfaces:** Has `templates/`; receives from `nt-architect`; feeds `nt-strategy-builder-rust`.
**Known gaps:** Historical audit found 7 migration-reference binding-generator mentions; post-fix reconciliation is recorded in the cutover report.
**Lane signal:** Rust-first; migration references remain quarantined and labelled.

### nt-review

**Purpose:** Pre-deployment code review skill.
**Readiness:** review-ready.
**Integration surfaces:** Consumed after implementation passes `nt-testing`.
**Known gaps:** Historical audit found 8 migration-reference binding-generator mentions; post-fix reconciliation is recorded in the cutover report.
**Lane signal:** Rust-first; migration references remain quarantined and labelled.

### nt-live

**Purpose:** Live trading runtime — LiveNode, execution, adapters.
**Readiness:** review-ready.
**Integration surfaces:** Pairs with `nt-adapters`, `nt-strategy-builder-rust`.
**Known gaps:** No P0/P1 cutover finding remains; see the reconciliation report for P2 maintenance follow-ups.
**Lane signal:** Rust-first; migration references remain quarantined and labelled.

### nt-dev

**Purpose:** Development environment setup.
**Readiness:** review-ready.
**Integration surfaces:** Entry for onboarding; pairs with `references/developer_guide/contracts/environment_tooling.md`.
**Known gaps:** Historical audit found 9 migration-reference binding-generator mentions; post-fix reconciliation is recorded in the cutover report.
**Lane signal:** Rust-first; migration references remain quarantined and labelled.

### nt-adapters

**Purpose:** Adapter development (CEX/venue) with spec exec testing contract.
**Readiness:** review-ready.
**Integration surfaces:** Pairs with `nt-live`; follows `references/developer_guide/contracts/adapter_contract.md`.
**Known gaps:** No P0/P1 cutover finding remains; see the reconciliation report for P2 maintenance follow-ups.
**Lane signal:** Rust-first; migration references remain quarantined and labelled.

### nt-dex-adapter

**Purpose:** Custom DEX adapter development.
**Readiness:** review-ready.
**Integration surfaces:** Has `rules/` + `tests/`; pairs with `nt-adapters`.
**Known gaps:** No P0/P1 cutover finding remains; see the reconciliation report for P2 maintenance follow-ups.
**Lane signal:** Rust-first; migration references remain quarantined and labelled.

### nt-backtest

**Purpose:** Backtesting skill.
**Readiness:** review-ready.
**Integration surfaces:** Has `templates/` + `references/`.
**Known gaps:** Historical audit found 5 migration-reference binding-generator mentions; post-fix reconciliation is recorded in the cutover report.
**Lane signal:** Rust-first; migration references remain quarantined and labelled.

### nt-testing

**Purpose:** Testing policies.
**Readiness:** review-ready.
**Integration surfaces:** Pairs with `references/developer_guide/contracts/testing_policy.md`.
**Known gaps:** Historical audit found 5 migration-reference binding-generator mentions; post-fix reconciliation is recorded in the cutover report.
**Lane signal:** Rust-first; migration references remain quarantined and labelled.

### nt-data

**Purpose:** Data handling and serialization.
**Readiness:** review-ready.
**Integration surfaces:** Feeds into most other skills.
**Known gaps:** No P0/P1 cutover finding remains; see the reconciliation report for P2 maintenance follow-ups.
**Lane signal:** Rust-first; migration references remain quarantined and labelled.

### nt-model

**Purpose:** Model definitions.
**Readiness:** review-ready.
**Integration surfaces:** Feeds into `nt-implement`, `nt-strategy-builder-rust`.
**Known gaps:** No P0/P1 cutover finding remains; see the reconciliation report for P2 maintenance follow-ups.
**Lane signal:** Rust-first; migration references remain quarantined and labelled.

### nt-signals

**Purpose:** Signal generation.
**Readiness:** review-ready.
**Integration surfaces:** Has `templates/` + `references/`; feeds `nt-trading`.
**Known gaps:** No P0/P1 cutover finding remains; see the reconciliation report for P2 maintenance follow-ups.
**Lane signal:** Rust-first; migration references remain quarantined and labelled.

### nt-trading

**Purpose:** Trading workflows.
**Readiness:** review-ready.
**Integration surfaces:** Has `templates/` + `references/`.
**Known gaps:** No P0/P1 cutover finding remains; see the reconciliation report for P2 maintenance follow-ups.
**Lane signal:** Rust-first; migration references remain quarantined and labelled.

### nt-learn

**Purpose:** Learning curriculum.
**Readiness:** review-ready.
**Integration surfaces:** Has `curriculum/`.
**Known gaps:** No P0/P1 cutover finding remains; see the reconciliation report for P2 maintenance follow-ups.
**Lane signal:** Rust-first; migration references remain quarantined and labelled.

## Router

### nt

**Purpose:** Entry-point router for all NautilusTrader tasks.
**Readiness:** review-ready.
**Integration surfaces:** Dispatches to all `nt-*` skills based on task classification.
**Known gaps:** No P0/P1 cutover finding remains; see the reconciliation report for P2 maintenance follow-ups.
**Lane signal:** Rust-first router; migration references remain quarantined and labelled.

## Python lane (reference/migration-only)

### nt-strategy-builder

**Purpose:** Python strategy workflows.
**Readiness:** reference-only (NOT for new work).
**Integration surfaces:** Migration reference; new work routes to `nt-strategy-builder-rust`.
**Known gaps:** By design — Python-first; kept for migration context only.
**Lane signal:** Migration/reference-only Python; not a production default.

### nt-evomap-integration

**Purpose:** EvoMap advisory sidecar integration.
**Readiness:** review-ready (sole permitted active Python lane).
**Integration surfaces:** Advisory only; never execution authority.
**Known gaps:** No P0/P1 cutover finding remains; see the reconciliation report for P2 maintenance follow-ups.
**Lane signal:** Sole active Python advisory lane; Rust retains execution authority.

### brainstorming_evomap

**Purpose:** EvoMap brainstorming prototypes.
**Readiness:** review-ready.
**Integration surfaces:** Has `tests/`.
**Known gaps:** No P0/P1 cutover finding remains; see the reconciliation report for P2 maintenance follow-ups.
**Lane signal:** Python advisory prototype under the sole active AI lane.
