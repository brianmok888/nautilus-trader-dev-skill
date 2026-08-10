# Mission: Harden and Improve `nautilus-trader-dev-skill`

## Required repository instructions

Before executing any part of this mission, read and apply the target repository's root `AGENTS.md`. Its project-scoped workflow, NT-only boundary, read-only upstream rule, validation requirements, and reporting requirements are mandatory for the entire mission. When work enters a subdirectory, also read and apply any deeper `AGENTS.md`; deeper instructions override broader ones.

**Target:** `/home/mok/projects/nautilus-trader-dev-skill`
**Mission output:** Improvements to this skill repository's skills, references, templates, tests, and validation tooling.
**Downstream purpose:** Make `nautilus-trader-dev-skill` reliably guide agents that architect, develop, test, integrate, operate, and review NautilusTrader Rust V2 components against current upstream APIs and standards.

## Scope boundary

- **This prompt hardens and improves `nautilus-trader-dev-skill`.** It does not develop NautilusTrader itself. Do not implement features in, modify, commit to, or prepare changes for the upstream `nautilus_trader` repository.
- **Upstream NautilusTrader is read-only ground truth.** Inspect its source, documentation, examples, tests, schemas, and toolchain standards only to correct and strengthen this repository's skill sets.
- **Only NautilusTrader development skills are in scope.** Audit and harden material that teaches agents to architect, implement, test, integrate, operate, or review NautilusTrader-related components.
- **AI/EvoMap work is out of scope.** Do not add, audit, modify, test, gate, or make readiness claims for AI/EvoMap skills, sidecars, templates, tests, evidence, or other AI-lane artifacts. That responsibility belongs to `nautilus-daedalus-dev-skill`; such artifacts must not exist in this repository.
- If an in-scope NT skill links to the excluded AI lane, preserve the boundary but do not follow the link into AI-lane review or changes. Record any unavoidable cross-repository dependency as `Pending` rather than expanding scope.

---

## Methodology skills (invoke these during execution)

The executing agent MUST load and apply these skills at the right phase. Do not skip — they encode the workflow discipline this mission requires.

| Skill                                  | When to invoke                                           | What it enforces                                                         |
| -------------------------------------- | -------------------------------------------------------- | ------------------------------------------------------------------------ |
| `$superpowers:requesting-code-review`               | **Phase 1** — deep review                                | Adversarial review pass; findings must cite file:line, not vibes         |
| best-practice-research                   | **Phase 1** — V2 compliance baseline                     | Pull current NT V2 docs/source as ground truth; no training-data guesses |
| `$superpowers:brainstorming`             | **Phase 2** — when fix approach is ambiguous             | Explore approach before coding; pick deliberately, not by default        |
| `$superpowers:test-driven-development`   | **Phase 2** — every fix segment                          | Test first → watch fail → implement → verify pass                        |
| `$superpowers:verification-before-completion` | **Phase 3 / Phase 5** — before claiming any gate `Pass` | Run the actual command; cite real output; "should pass" is not Pass      |
| `$superpowers:requesting-code-review`    | **Phase 4** — reconciliation                             | Independent review of post-fix tree before ship                          |

**Rule:** If a phase's skill is not available in the runtime, STOP and report — do not substitute unstructured work for a missing methodology skill.

---

## Authoritative sources (when findings conflict)

Resolve by priority:

NT v2 compatibility note: Cython, v1, and legacy terms in this mission are
audit targets or migration/reference-only history. They never authorize a
production path; new in-scope guidance remains Rust-first and PyO3-oriented.

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

NT v2 compatibility note: legacy-labelling below is a migration audit control,
not implementation guidance.

1. **Current findings update** — evidence-backed changes in `docs/tracking/Findings.md`, without session plans or historical reports.
2. **Legacy lint gate** — `tools/check_legacy_labelling.py` remains green for retained Cython/v1 migration references.
3. **Per-skill gate checklist** — G0-G7 readiness cards for all retained NT-development skills, indexed by `docs/tracking/Components.md`.
4. **Skill repository corrections** — source-backed changes to current skills, references, templates, tests, and validators only.
5. **Closure summary** — verification evidence, residual NT-development risks, and confirmation that upstream was not modified.

Do not create tracked session plans, handoffs, generated agent state, historical reconciliation reports, or external attestations. AI/EvoMap artifacts are outside every deliverable and must remain absent.

---

## Phase 1 — Deep Skill-Set Review (READ-ONLY, no edits)

**Invoke:** `$superpowers:requesting-code-review` + `best-practice-research` (use `web_search`/`webfetch` against the Source URLs below).
Treat upstream NautilusTrader source and official docs as read-only evidence;
do not treat the upstream repository as an implementation target.

Before reviewing, build an explicit in-scope inventory of NT-development skill
artifacts and a proof that AI/EvoMap artifacts are absent. Do not report
findings against excluded files.

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

### Record current findings

Record source-backed findings in `docs/tracking/Findings.md` using the format above. Do not create a dated audit plan or session artifact.

**Do not edit skill content in this phase.** Phase 1 produces only the current findings update.

---

## Phase 2 — Skill-Set Fix Implementation (segment-by-segment, TDD)

**Invoke:** `$superpowers:brainstorming` (when ambiguous) + `$superpowers:test-driven-development` (every segment).

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

- Scans in-scope NT-development `skills/**/SKILL.md`, `references/**/*.md`, and `templates/**/*.md`; AI/EvoMap artifacts must be absent from the repository.
- Fails (exit 1) if any of these appear WITHOUT an explicit `legacy:` label or migration note within 5 lines:
  - Cython keywords: `cdef`, `cpdef`, `cimport`, `.pyx`
  - v1-only API markers: version-pinned removed symbols
- Add a pytest wrapper in `tests/test_legacy_labelling.py`.
- This prevents future unlabelled legacy guidance from sneaking back in.

---

## Phase 3 — Progressive Gate Checklist (PRIMARY DELIVERABLE)

**Invoke:** `$superpowers:verification-before-completion` — every `Pass` status must cite real command output, not assertion.

For each in-scope NT-development skill, maintain a G0-G7 cutover readiness card in that skill's `SKILL.md`; keep `docs/tracking/Components.md` as the index. AI-lane artifacts must remain absent from the checklist, summary counts, and repository tree.

### Gate card contract

NT v2 compatibility note: G1 below measures migration/reference-only Cython/v1
labelling; it does not make those paths current production guidance.

```markdown
### Cutover readiness — <skill-name>

NT v2 compatibility note: G1 measures migration/reference-only Cython/v1
labelling; current implementation guidance remains Rust/PyO3-oriented.

| Gate | Description | Status | Evidence |
|------|-------------|--------|----------|
| G0   | Scope and ownership are explicit | Pass/Pending/Blocked | file:line |
| G1   | No Cython/v1 references remain unlabelled | Pass/Pending/Blocked | command or file:line |
| G2   | Examples compile against the pinned NT V2 baseline | Pass/Pending/Blocked | `python tools/check_skill_g2_harnesses.py --execute --skill <skill>` output |
| G3   | Rust bindings / PyO3 paths match current upstream contracts | Pass/Pending/Blocked | file:line or upstream URL |
| G4   | Skill-specific functional gates pass | Pass/Pending/Blocked | command or URL |
| G5   | References and templates are synchronized | Pass/Pending/Blocked | command or file:line |
| G6   | Operational and migration boundaries are explicit | Pass/Pending/Blocked | command or file:line |
| G7   | Durable evidence records the verified result | Pass/Pending/Blocked | evidence artifact |
```

**Rules:**
- Status values: `Pass` / `Pending` / `Blocked` (+ reason on next line).
- Every `Pass` MUST cite a measurable command, file, or URL that proves it.
- A skill is "cutover-ready" only when ALL gates are `Pass`.
- `Pending` gates carry into a follow-up TODO list at the end of Phase 4.

---

## Phase 4 — Reconciliation

**Invoke:** `$superpowers:requesting-code-review` for independent post-fix review.

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

- **Skill repository only.** Modify `/home/mok/projects/nautilus-trader-dev-skill`; never modify or prepare upstream NautilusTrader changes.
- **Upstream is evidence, not a deliverable.** Source, docs, examples, tests, and standards from `nautilus_trader` are read-only inputs used to improve this repository's skill artifacts.
- **NT-development scope only.** Every finding, edit, test, and gate must improve skills for developing NautilusTrader-related components.
- **AI/EvoMap excluded.** Do not add, inspect beyond boundary identification, modify, validate, gate, or claim readiness for AI-lane artifacts; route that work to `nautilus-daedalus-dev-skill` and keep those artifacts absent here.
- **Rust-first default.** All new in-scope guidance routes through `skills/nt-strategy-builder-rust/`. Python `skills/nt-strategy-builder/` is reference-only.
- **All in-scope legacy content must be labelled.** Per `docs/tracking/Handguard.md` invariant #3.
- **Applicable sync checkers must stay green.** `check_dev_guide_sync.py`, `check_rust_trading_reference_sync.py`, `check_upstream_freshness.py`.
- **No fabricated content.** If a finding can't cite a real file:line, it's not a finding.
