# Components — nautilus-trader-dev-skill

<!-- CHARTER -->
<!-- Role: Per-skill detail — what each skill does, Rust-vs-Python orientation, readiness status, known gaps. -->
<!-- Read when: answering "what does skill X do?", "what's the readiness of Y?", "is Z reviewed?". -->
<!-- Updated when: a skill changed (new skill, readiness shift, review update). -->
<!-- Does NOT contain: invariants, structural inventory, issue tracking, plans. -->
<!-- Write-target rule: only update this file if a skill changed. -->

Review date: 2026-08-07
Reviewed tree: current audited working tree; exact-SHA attestation remains pending until these changes are committed and an independent reviewer supplies artifacts for that final commit and reports its SHA and evidence path.
Cutover gates: 18 skills × G0-G7 = **144 Pass, 0 Pending, 0 Blocked** in a clean standard environment. The measurable per-skill G0-G7 cards remain in each `skills/nt*/SKILL.md` and are validated by `uv run python tools/check_skill_g2_harnesses.py --check-cards`. `nt-implement` G2 now passes with Cap'n Proto `capnp 1.0.1` available in the standard verification environment; durable evidence is recorded in `references/g2-evidence/nt-implement.json` (`status: pass`).
Evidence boundary: G2 Cargo checks prove compilation only. Adapter conformance, controlled-venue, resilience, fuzz, and operations acceptance remain change-specific delivery obligations and are not implied by the card summary.

## Per-skill readiness card index

The full measurable G0-G7 checklist for each NT skill is linked below from its
existing component entry. The linked `SKILL.md` table is the single authority;
this tracker intentionally indexes rather than duplicates the evidence rows.
The `#nt-v2-rust-readiness-gates` links resolve to the shared readiness heading
(the heading is positioned after skill-specific introductory sections where
needed).

| Skill | Authoritative readiness card | Current summary |
| --- | --- | --- |
| nt | [`skills/nt/SKILL.md`](../../skills/nt/SKILL.md#nt-v2-rust-readiness-gates) | review-ready |
| nt-adapters | [`skills/nt-adapters/SKILL.md`](../../skills/nt-adapters/SKILL.md#nt-v2-rust-readiness-gates) | review-ready |
| nt-architect | [`skills/nt-architect/SKILL.md`](../../skills/nt-architect/SKILL.md#nt-v2-rust-readiness-gates) | review-ready |
| nt-backtest | [`skills/nt-backtest/SKILL.md`](../../skills/nt-backtest/SKILL.md#nt-v2-rust-readiness-gates) | review-ready |
| nt-data | [`skills/nt-data/SKILL.md`](../../skills/nt-data/SKILL.md#nt-v2-rust-readiness-gates) | review-ready |
| nt-dev | [`skills/nt-dev/SKILL.md`](../../skills/nt-dev/SKILL.md#nt-v2-rust-readiness-gates) | review-ready |
| nt-dex-adapter | [`skills/nt-dex-adapter/SKILL.md`](../../skills/nt-dex-adapter/SKILL.md#nt-v2-rust-readiness-gates) | review-ready |
| nt-evomap-integration | [`skills/nt-evomap-integration/SKILL.md`](../../skills/nt-evomap-integration/SKILL.md#nt-v2-rust-readiness-gates) | review-ready |
| nt-implement | [`skills/nt-implement/SKILL.md`](../../skills/nt-implement/SKILL.md#nt-v2-rust-readiness-gates) | review-ready |
| nt-learn | [`skills/nt-learn/SKILL.md`](../../skills/nt-learn/SKILL.md#nt-v2-rust-readiness-gates) | review-ready |
| nt-live | [`skills/nt-live/SKILL.md`](../../skills/nt-live/SKILL.md#nt-v2-rust-readiness-gates) | review-ready |
| nt-model | [`skills/nt-model/SKILL.md`](../../skills/nt-model/SKILL.md#nt-v2-rust-readiness-gates) | review-ready |
| nt-review | [`skills/nt-review/SKILL.md`](../../skills/nt-review/SKILL.md#nt-v2-rust-readiness-gates) | review-ready |
| nt-signals | [`skills/nt-signals/SKILL.md`](../../skills/nt-signals/SKILL.md#nt-v2-rust-readiness-gates) | review-ready |
| nt-strategy-builder | [`skills/nt-strategy-builder/SKILL.md`](../../skills/nt-strategy-builder/SKILL.md#nt-v2-rust-readiness-gates) | reference-only |
| nt-strategy-builder-rust | [`skills/nt-strategy-builder-rust/SKILL.md`](../../skills/nt-strategy-builder-rust/SKILL.md#nt-v2-rust-readiness-gates) | review-ready |
| nt-testing | [`skills/nt-testing/SKILL.md`](../../skills/nt-testing/SKILL.md#nt-v2-rust-readiness-gates) | review-ready |
| nt-trading | [`skills/nt-trading/SKILL.md`](../../skills/nt-trading/SKILL.md#nt-v2-rust-readiness-gates) | review-ready |

## Rust-first tier (primary skills)

### nt-strategy-builder-rust

**Purpose:** Default production strategy and LiveNode wiring using Rust-first NT V2 patterns.
**Readiness:** review-ready (flagship Rust skill).
**Integration surfaces:** `nt` router dispatches here for production/live-node work; `nt-architect` feeds into it.
**Known gaps:** Historical audit found 2 migration-reference binding-generator mentions; post-fix reconciliation is in `docs/superpowers/reports/2026-07-30-nt-v2-rust-cutover-reconciliation.md`.
**Lane signal:** Rust-first; migration references remain quarantined and labelled.

### nt-architect

**Purpose:** Architecture decomposition (Actor/Indicator/Strategy). Starting point for new projects.
**Readiness:** review-ready.
**Integration surfaces:** Feeds `nt-implement`, `nt-strategy-builder-rust`.
**Known gaps:** Historical audit found 2 migration-reference binding-generator mentions; post-fix reconciliation is recorded in the cutover report.
**Lane signal:** Rust-first; migration references remain quarantined and labelled.

### nt-implement

**Purpose:** Strategy/Actor/Indicator implementation with templates + conventions.
**Readiness:** review-ready (`nt-implement` G2 passes with Cap'n Proto `capnp 1.0.1` in the standard verification environment on 2026-08-07).
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
