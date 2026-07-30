# Mission: NT V2 Rust Cutover Audit & Skill Hardening

**Target:** `/home/mok/projects/nautilus-trader-dev-skill`
**Goal:** Move skill set to NT V2 / Rust-first, as close to official docs as possible. Exception: AI Lane stays Python — everything else Rust-oriented.

---

## Authoritative sources (when findings conflict)

Resolve by priority:

NT v2 compatibility note: Cython, v1, and legacy terms in this mission are
audit targets or migration/reference-only history. They never authorize a
production path; new non-AI work remains Rust-first and PyO3-oriented.

1. **Rust conversion correctness** — highest. Python/Cython where Rust now exists in NT = P0.
2. **NT V2 compliance** — drift from current docs/API = P1.
3. **Gaps vs nightly/master** — newer NT features not covered = P2.
4. **Cython / v1 / legacy cleanup** — unlabelled legacy content = P1 (charter violation per `docs/tracking/Handguard.md` invariant #3).
5. **Cosmetic / docs polish** — lowest.

**Truth hierarchy:** NT source code (`nautilus_core` Rust, `nautilus_trader` Python on `develop`) > nautilustrader.io docs > `references/developer_guide/contracts/` > skill SKILL.md files > other references.

**Source URLs:**
- https://nautilustrader.io/docs/nightly/
- https://nautilustrader.io/docs/latest/
- https://nautilustrader.io/docs/latest/developer_guide
- https://nautilustrader.io/docs/latest/developer_guide/adapters/
- https://nautilustrader.io/docs/latest/developer_guide/spec_exec_testing/
- https://github.com/nautechsystems/nautilus_trader

---

## Deliverables (produced in order)

NT v2 compatibility note: legacy-labelling deliverables below are migration
and audit controls for Cython/v1 references, not implementation guidance.

1. **Phase 1 findings report** — `docs/plans/<date>-nt-v2-cutover-audit-phase1.md`
2. **Legacy lint gate** — `tools/check_legacy_labelling.py` (fails on unlabelled Cython/v1 content)
3. **Per-skill gate checklist** — cutover readiness cards appended to `docs/tracking/Components.md`
4. **Closure deltas** — one delta entry per segment in `docs/tracking/Findings.md`

---

## Phase 1 — Deep Code Review (READ-ONLY, no edits)

Audit every skill `SKILL.md`, reference file, and template. Produce a findings report grouped into four categories:

### Finding categories

NT v2 compatibility note: Cython/v1 entries in the audit taxonomy below are
migration/reference-only findings and must be replaced by current Rust/PyO3
guidance for new work.

| Category | What to flag | Default severity |
|---|---|---|
| Rust conversion gaps | Python/Cython where Rust now exists in NT | P0 |
| V2 compliance violations | API drift, removed/renamed symbols, wrong imports | P1 |
| Legacy unlabelled content | Cython (`cdef`/`cpdef`/`.pyx`), v1-only API, migration-history without `legacy:` label | P1 |
| Improvement opportunities | Newer NT features not yet covered | P2 |

### Finding format (every finding)

```
[P0/P1/P2] <category>: <one-line description>
  file: <path>:<line>
  fix: <one-line proposal>
```

### Write the report to

`docs/plans/<date>-nt-v2-cutover-audit-phase1.md` with YAML frontmatter:

```yaml
date: YYYY-MM-DD
status: draft
tier: C
write-targets: [docs/tracking/Findings.md, docs/tracking/Components.md]
```

**Do not edit skill content in this phase.** Phase 1 produces only the report.

---

## Phase 2 — Fix Implementation (segment-by-segment, TDD)

Work findings in priority order (P0 → P1 → P2). For each segment:

1. **When approach is ambiguous:** brainstorm the approach before coding.
2. **Write the test first.** Watch it fail. Then implement. Verify it passes.
3. **One commit per logical segment.** Do not batch unrelated fixes.
4. **Append a delta entry** to `docs/tracking/Findings.md` on each segment close:
   ```
   YYYY-MM-DD — [tier] — MODIFIED: <what changed> — files: a, b, c
   ```

### Mandatory: legacy lint gate

NT v2 compatibility note: the Cython/v1 syntax below is detection-only input
for the migration/reference gate; it is not executable or production guidance.

Before Phase 2 closes, ship `tools/check_legacy_labelling.py`:

NT v2 compatibility note: the following Cython/v1 tokens are
migration/reference-only detector inputs; prefer current Rust/PyO3 APIs for new
work.

- Scans all `skills/**/SKILL.md`, `references/**/*.md`, `templates/**/*.md`.
- Fails (exit 1) if any of these appear WITHOUT an explicit `legacy:` label or migration note within 5 lines:
  - Cython keywords: `cdef`, `cpdef`, `cimport`, `.pyx`
  - v1-only API markers: version-pinned removed symbols
- Add a pytest wrapper in `tests/test_legacy_labelling.py`.
- This prevents future unlabelled legacy guidance from sneaking back in.

---

## Phase 3 — Progressive Gate Checklist (PRIMARY DELIVERABLE)

For each NT-related skill, produce a cutover readiness card. Append each card to `docs/tracking/Components.md` under the skill's existing entry (or create the entry).

### Gate card template

NT v2 compatibility note: G1 below measures migration/reference-only Cython/v1
labelling; it does not make those paths current production guidance.

```markdown
### Cutover readiness — <skill-name>

NT v2 compatibility note: G1 measures migration/reference-only Cython/v1
labelling; current implementation guidance remains Rust/PyO3-oriented.

| Gate | Description | Status | Evidence |
|------|-------------|--------|----------|
| G1   | No Cython/v1 references remain unlabelled | Pass/Pending/Blocked | command or file:line |
| G2   | Examples compile against NT V2 master | Pass/Pending/Blocked | `tools/check_skill_g2_harnesses.py <skill>` output |
| G3   | Rust bindings / pyo3 paths match current nautilus_core | Pass/Pending/Blocked | file:line or upstream URL |
| G4   | Skill-specific gates (adapter spec tests, LiveNode boot, etc.) | Pass/Pending/Blocked | command or URL |
```

**Rules:**
- Status values: `Pass` / `Pending` / `Blocked` (+ reason on next line).
- Every `Pass` MUST cite a measurable command, file, or URL that proves it.
- A skill is "cutover-ready" only when ALL gates are `Pass`.
- `Pending` gates carry into a follow-up TODO list at the end of Phase 4.

---

## Phase 4 — Reconciliation

1. Re-run Phase 1 audit against the post-fix tree.
2. Confirm each Phase 1 finding is closed; carry residuals into a follow-up TODO list in `docs/tracking/Findings.md`.
3. Regenerate the gate checklist with updated statuses.
4. Verify the legacy lint gate passes on the full tree.

---

## Phase 5 — Ship

1. One commit per logical segment (conventional commits: `fix:`, `feat:`, `docs:`, `chore:`).
2. Merge to `main`.
3. Push to `origin/main`.
4. **Final report** (in chat, not committed):
   - Phase 1 findings count by severity (P0/P1/P2) and how many closed.
   - Gate checklist summary table (skill × gate → status).
   - Commit SHAs.
   - Anything still `Pending` or `Blocked`.

---

## Tracking system integration

This mission writes to the existing charter-scoped trackers. Follow the write-target routing rule:

| Change type | Write-target |
|---|---|
| Any segment closure | `docs/tracking/Findings.md` (ALWAYS — delta entry) |
| New invariant (e.g., legacy labelling rule) | `docs/tracking/Handguard.md` (ONLY IF new rule) |
| New skill, tool, or structural shift | `docs/tracking/Structure.md` (ONLY IF wiring changed) |
| Per-skill readiness/gate card | `docs/tracking/Components.md` (ONLY IF component changed) |

Do NOT duplicate content across trackers. One change → one write-target.

---

## Constraints

- **Rust-first default.** All new guidance routes through `skills/nt-strategy-builder-rust/`. Python `skills/nt-strategy-builder/` is reference-only.
- **AI/EvoMap lane is the sole permitted Python lane.** Advisory-only, never execution authority.
- **All legacy content must be labelled.** Per `docs/tracking/Handguard.md` invariant #3.
- **Sync checkers must stay green.** `check_dev_guide_sync.py`, `check_rust_trading_reference_sync.py`, `check_upstream_freshness.py`.
- **No fabricated content.** If a finding can't cite a real file:line, it's not a finding.
