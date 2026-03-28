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

## 2026-03-28 — Documentation reorganization
- Introduced canonical takeover docs: `doc/START_HERE.md`, `doc/CURRENT_STATE.md`, `doc/NEXT_ACTIONS.md`, and `doc/WORK_LOG.md`.
- Refactored `AGENTS.md` into a routing and maintenance file.
- Archived stale operational docs so short takeover prompts can resolve to a single documentation chain.

## 2026-03-28 — Backlog fixes (client form, duplication, start date)
- Fixed duplicate `client_destination_name` in task creation form (`views.xml` line 65 removed, kept inheritance view with `required="1"`).
- Added `copy=False` to `created_at` and `created_by_id` on `GrInternalInventory` so all copy paths (not just custom buttons) reset these fields.
- Added `views_simple.xml` to `__manifest__.py` to expose `planned_date_begin` (operation start date) in task form and tree views.
- Verified lot name max-length constraints were already in place.
