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

## 2026-03-28 — Guardrail goal clarified
- The desired behavior is now explicit: on vague resume prompts, a fresh agent must orient from the canonical docs, summarize state, and wait for explicit instruction before making changes.
