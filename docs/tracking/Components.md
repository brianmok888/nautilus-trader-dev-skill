# Components — nautilus-trader-dev-skill

<!-- CHARTER -->
<!-- Role: Per-skill detail — what each skill does, Rust-vs-Python orientation, readiness status, known gaps. -->
<!-- Read when: answering "what does skill X do?", "what's the readiness of Y?", "is Z reviewed?". -->
<!-- Updated when: a skill changed (new skill, readiness shift, review update). -->
<!-- Does NOT contain: invariants, structural inventory, issue tracking, plans. -->
<!-- Write-target rule: only update this file if a skill changed. -->

Review date: 2026-07-30
Audit commit: 6260468

## Rust-first tier (primary skills)

### nt-strategy-builder-rust

**Purpose:** Default production strategy and LiveNode wiring using Rust-first NT V2 patterns.
**Readiness:** review-ready (flagship Rust skill).
**Integration surfaces:** `nt` router dispatches here for production/live-node work; `nt-architect` feeds into it.
**Known gaps:** Awaiting Phase 1 audit for remaining Cython references (2 hits in SKILL.md).
**Rust/Cython signal:** 43 Rust mentions, 2 Cython mentions, 8 legacy mentions.

### nt-architect

**Purpose:** Architecture decomposition (Actor/Indicator/Strategy). Starting point for new projects.
**Readiness:** review-ready.
**Integration surfaces:** Feeds `nt-implement`, `nt-strategy-builder-rust`.
**Known gaps:** Awaiting Phase 1 audit for remaining Cython references (2 hits).
**Rust/Cython signal:** 26 Rust, 2 Cython, 9 legacy.

### nt-implement

**Purpose:** Strategy/Actor/Indicator implementation with templates + conventions.
**Readiness:** review-ready.
**Integration surfaces:** Has `templates/`; receives from `nt-architect`; feeds `nt-strategy-builder-rust`.
**Known gaps:** Highest Cython mention count among skills (7 hits) — needs Phase 1 audit to confirm all are labelled legacy.
**Rust/Cython signal:** 85 Rust, 7 Cython, 18 legacy.

### nt-review

**Purpose:** Pre-deployment code review skill.
**Readiness:** review-ready.
**Integration surfaces:** Consumed after implementation passes `nt-testing`.
**Known gaps:** 8 Cython mentions — needs Phase 1 audit.
**Rust/Cython signal:** 64 Rust, 8 Cython, 14 legacy.

### nt-live

**Purpose:** Live trading runtime — LiveNode, execution, adapters.
**Readiness:** review-ready.
**Integration surfaces:** Pairs with `nt-adapters`, `nt-strategy-builder-rust`.
**Known gaps:** Awaiting Phase 1 audit for V2 LiveNode API drift.
**Rust/Cython signal:** 44 Rust, 3 Cython, 10 legacy.

### nt-dev

**Purpose:** Development environment setup.
**Readiness:** review-ready.
**Integration surfaces:** Entry for onboarding; pairs with `references/developer_guide/contracts/environment_tooling.md`.
**Known gaps:** 9 Cython mentions — needs Phase 1 audit.
**Rust/Cython signal:** 53 Rust, 9 Cython, 12 legacy.

### nt-adapters

**Purpose:** Adapter development (CEX/venue) with spec exec testing contract.
**Readiness:** review-ready.
**Integration surfaces:** Pairs with `nt-live`; follows `references/developer_guide/contracts/adapter_contract.md`.
**Known gaps:** Awaiting Phase 1 audit.
**Rust/Cython signal:** 44 Rust, 3 Cython, 6 legacy.

### nt-dex-adapter

**Purpose:** Custom DEX adapter development.
**Readiness:** review-ready.
**Integration surfaces:** Has `rules/` + `tests/`; pairs with `nt-adapters`.
**Known gaps:** Awaiting Phase 1 audit.
**Rust/Cython signal:** 21 Rust, 3 Cython, 5 legacy.

### nt-backtest

**Purpose:** Backtesting skill.
**Readiness:** review-ready.
**Integration surfaces:** Has `templates/` + `references/`.
**Known gaps:** 5 Cython mentions — needs Phase 1 audit.
**Rust/Cython signal:** 21 Rust, 5 Cython, 6 legacy.

### nt-testing

**Purpose:** Testing policies.
**Readiness:** review-ready.
**Integration surfaces:** Pairs with `references/developer_guide/contracts/testing_policy.md`.
**Known gaps:** 5 Cython mentions — needs Phase 1 audit.
**Rust/Cython signal:** 34 Rust, 5 Cython, 9 legacy.

### nt-data

**Purpose:** Data handling and serialization.
**Readiness:** review-ready.
**Integration surfaces:** Feeds into most other skills.
**Known gaps:** Awaiting Phase 1 audit.
**Rust/Cython signal:** 19 Rust, 3 Cython, 5 legacy.

### nt-model

**Purpose:** Model definitions.
**Readiness:** review-ready.
**Integration surfaces:** Feeds into `nt-implement`, `nt-strategy-builder-rust`.
**Known gaps:** Awaiting Phase 1 audit.
**Rust/Cython signal:** 26 Rust, 3 Cython, 5 legacy.

### nt-signals

**Purpose:** Signal generation.
**Readiness:** review-ready.
**Integration surfaces:** Has `templates/` + `references/`; feeds `nt-trading`.
**Known gaps:** Awaiting Phase 1 audit.
**Rust/Cython signal:** 25 Rust, 3 Cython, 5 legacy.

### nt-trading

**Purpose:** Trading workflows.
**Readiness:** review-ready.
**Integration surfaces:** Has `templates/` + `references/`.
**Known gaps:** Awaiting Phase 1 audit.
**Rust/Cython signal:** 37 Rust, 3 Cython, 6 legacy.

### nt-learn

**Purpose:** Learning curriculum.
**Readiness:** review-ready.
**Integration surfaces:** Has `curriculum/`.
**Known gaps:** Awaiting Phase 1 audit.
**Rust/Cython signal:** 12 Rust, 2 Cython, 5 legacy.

## Router

### nt

**Purpose:** Entry-point router for all NautilusTrader tasks.
**Readiness:** review-ready.
**Integration surfaces:** Dispatches to all `nt-*` skills based on task classification.
**Known gaps:** Awaiting Phase 1 audit.
**Rust/Cython signal:** 19 Rust, 3 Cython, 9 legacy.

## Python lane (reference/migration-only)

### nt-strategy-builder

**Purpose:** Python strategy workflows.
**Readiness:** reference-only (NOT for new work).
**Integration surfaces:** Migration reference; new work routes to `nt-strategy-builder-rust`.
**Known gaps:** By design — Python-first; kept for migration context only.
**Rust/Cython signal:** 29 Rust, 4 Cython, 13 legacy.

### nt-evomap-integration

**Purpose:** EvoMap advisory sidecar integration.
**Readiness:** review-ready (sole permitted active Python lane).
**Integration surfaces:** Advisory only; never execution authority.
**Known gaps:** Awaiting Phase 1 audit.
**Rust/Cython signal:** 6 Rust, 2 Cython, 4 legacy.

### brainstorming_evomap

**Purpose:** EvoMap brainstorming prototypes.
**Readiness:** review-ready.
**Integration surfaces:** Has `tests/`.
**Known gaps:** Awaiting Phase 1 audit.
**Rust/Cython signal:** Python-only (prototype skill).
