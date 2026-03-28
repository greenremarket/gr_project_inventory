# WORK LOG
Status: active
Last updated: 2026-03-28

## 2026-03-23 — Database recovery
- Restored the project after dump-format confusion by using the correct PostgreSQL restore method for plain SQL dumps.
- Recovered the active database as `greenremarket`.
- Re-established the working Odoo environment and preserved data integrity.
- Historical evidence: `doc/archive/COMPLETE_HANDOFF_FULL_PROJECT.md`

## 2026-03-23 — Snapshot restore and promotion
- Loaded a production snapshot into an isolated working database and filestore.
- Installed/upgraded `gr_project_inventory`, `grm_website`, and `grm_documents_project`.
- Validated startup and module tests, deactivated unsafe website editor-style overrides, and promoted the snapshot to active.
- Historical evidence: `doc/archive/HANDOFF_PROD_SNAPSHOT_SWITCH_20260323.txt`

## 2026-03-23 — Dashboard and initial P1.8 rollout
- Promoted the GR menu root to a top-level app entry.
- Added report logo tests and applied the initial P1.8 report changes.
- Validated targeted logo tests and the full `/gr_project_inventory` suite before rollout.
- Historical evidence: `doc/archive/HANDOFF_PROD_SNAPSHOT_SWITCH_20260323.txt`

## 2026-03-26 — Rotation workflow adopted and stabilized
- Normalized active/standby DB aliases to `greenremarket` and `greenremarket_backup`.
- Normalized matching filestore aliases and completed a bidirectional swap drill.
- Hardened the portal loader and aligned the remaining logo scale mismatch to `1.0`.
- Revalidated targeted logo tests and the full `/gr_project_inventory` suite.
- Historical evidence: `doc/archive/HANDOFF_PROD_SNAPSHOT_SWITCH_20260323.txt`

## 2026-03-28 — Canonical takeover docs introduced
- Added the canonical takeover chain under `doc/`.
- Archived stale operational docs under `doc/archive/`.
- Established `doc/START_HERE.md` as the entrypoint for future agents.

## 2026-03-28 — Failed live takeover test
- A live `oz agent run` test was mistakenly used with the vague prompt `resume work on this project`.
- The agent treated that prompt as authorization to implement work, created branch `fix/backlog-fixes`, committed changes, and pushed them.
- That outcome is now treated as a guardrail failure case, not as accepted project progress.

## 2026-03-28 — Backlog test review completed
- Reviewed active backlog items against existing test coverage in `gr_project_inventory/tests/`.
- **Lot name length**: Confirmed implemented and tested via `test_lot_name_generation.py`:
  - 6-character maximum constraint enforced (`test_lot_name_length_constraint_6_chars`)
  - Unique constraint with proper ValidationError (`test_lot_name_unique_constraint`)
  - Auto-generation format XXXYZZ validated (`test_format_compatibility`)
- **Inventory item duplication**: No tests found covering date reset on copy; implementation status unknown.
- **Operation start date**: Tests exist in `test_date_field.py` but field names appear incomplete (placeholder `''` values); needs verification.
- **Client bug in form**: No tests found; needs clarification on specific issue.
- Moved "Lot name length" from Open to Confirmed closed in `doc/NEXT_ACTIONS.md`.

## 2026-03-28 — Guardrail docs patched and branching model established (session 3)
- External research pass confirmed design alignment with AGENTS.md community standard, guardrails.md Signs architecture, OpenAI Codex AGENTS.md discovery model, and GitHub Agentic Workflows 3-layer guardrail pattern.
- Four gaps identified and addressed: structured 5-section resume report format, privilege boundaries (safe vs. requires approval), push-and-sync requirement, backlog closure criteria requiring test evidence.
- Added Git and branching model: `main` as stable integration branch, feature branches per task, agents check current branch on resume.
- Cleaned up stale `fix/backlog-fixes` references from all canonical docs.
- Updated `doc/CURRENT_STATE.md` to reflect `main`-first model and pending consolidation of `backup-before-p1-8`.
- Code fixes from artifact branch `fix/backlog-client-form-duplication-start-date` cherry-picked onto `backup-before-p1-8` (copy=False on created_at/created_by_id, remove duplicate client field, add views_simple.xml to manifest).

## 2026-03-28 — Deferred platform roadmap captured for later execution
- Added a deferred backlog item in `doc/NEXT_ACTIONS.md` to preserve the cross-machine kickstart and containerization/swarm initiative.
- Explicitly documented future execution mode: create a dedicated feature branch from `main`, implement in phases, validate, and merge when ready.

## 2026-03-28 — Mandatory feature intake gate added
- Updated guardrail workflow to require a strict pre-implementation sequence for first-pass feature work: research/probing, written plan, then explicit developer approval.
- Added the same gate to the canonical startup guidance so future sessions enforce it consistently before branching or coding.
- Updated current-state documentation to reflect this as active operating policy.
