# WORK LOG
Status: active
Last updated: 2026-03-30

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

## 2026-03-31 — migmi machine bootstrap (session 4)
- Repo refactored: `gr_project_inventory`, `grm_documents_project`, `grm_website` moved to `modules/`.
- `third_party_modules/` and `ebics_keys/` directories created with `.gitkeep`; contents gitignored.
- `portal_gr` removed from all references (no longer exists; replaced by `grm_*` in `modules/`).
- Git remote fixed from stale OneDrive path to `https://github.com/greenremarket/gr_project_inventory.git`.
- `doc/DECISIONS/2026-03-31-ebics-keys-location.md` created documenting EBICS key location.
- PostgreSQL 17.9 installed via winget. Role `odoo/odoo` with CREATEDB created.
- Cloned at `17.0 --depth 1`: `odoo`, `enterprise`, `third_party_modules/reporting-engine` (OCA), `third_party_modules/account_ebics_repo` (Noviat), `third_party_modules/account_reconcile_repo` (OCA), `third_party_modules/bank_statement_import_repo` (OCA), `third_party_modules/l10n_france_repo` (OCA).
- pip requirements installed from `odoo/requirements.txt` and `requirements.txt` into `.venv_odoo`.
- Production backup `greenremarket_2026-03-31_17-20-12.zip` received (PG 16.13 source, 69 MB SQL + 2252 filestore files).
- Savepoint 0: extracted to `dumps/savepoint_0_production_20260331/` (immutable baseline).
- DB `greenremarket_incoming` created and restored from `dump.sql`. Filestore copied to `odoo_data/filestore/greenremarket_incoming/`. 2252 files confirmed.
- Savepoint 1: `dumps/savepoint_1_restored_raw.dump` (pg_dump -Fc of raw restored DB).
- Next: website cleanup → savepoint 2 → module upgrade → savepoint 3 → promote to `greenremarket`.
- Website cleanup done: 4 editor-style overrides deactivated (template_header_default, header_text_element, footer_custom, footer_copyright_company_name). Count confirmed 0.
- Savepoint 2: `dumps/savepoint_2_cleaned.dump`.
- Missing pip dependencies discovered and installed: `pymysql>=1.1`, `fintech`, `pdfminer.six`. Added to `requirements.txt`.
- `views_simple.xml` commented out in manifest — `date_deadline` xpath fails on this enterprise version. Added as open backlog item.
- gr modules upgraded/installed: `gr_project_inventory` 17.0.1.2, `grm_website` 17.0.1.1.3, `grm_documents_project` 17.0.1.1.2. `account_ebics` and `account_ebics_oe` synced.
- Savepoint 3: `dumps/savepoint_3_upgraded.dump`.
- DB renamed `greenremarket_incoming` → `greenremarket`. Filestore promoted. Old March 30 filestore archived as `greenremarket_prior_march30`.
- Machine is now operational.
- Standby pair created: `greenremarket_backup` DB (240 installed modules confirmed) and `odoo_data/filestore/greenremarket_backup`. Active/standby rotation model is now fully operational on this machine.

## 2026-03-31 — EBICS full resolution + statement import (session 6, late)
- Root cause of "No financial journal found" identified: `sanitized_acc_number` is a stored computed field. SQL update to `acc_number` does NOT trigger a recompute. Both `acc_number` and `sanitized_acc_number` on `res_partner_bank` id=1 now set to `00021148802` on both DBs.
- EBICS 91116 on FDL with end date 2026-03-31: bank considers that delivery "consumed" (receipt acknowledged). Shifting end date to 2026-03-30 bypassed the block.
- Z53 (camt.053 CIC-specific) rejected with 91005 INVALID_ORDER_TYPE. C53 rejected with functional error. FDL/cfonb120 is the only working format at CIC for this EBICS contract.
- 16 bank statements imported: 2026-03-05 through 2026-03-27.
- Historical gap 2025-06-21 to 2026-03-04: confirmed unavailable via EBICS (code 90005 EBICS_NO_DOWNLOAD_DATA_AVAILABLE). CIC only retains ~30 days of CFONB in EBICS FDL. This gap must be imported manually from CIC online banking export.
- Shell scripts created in `scripts/` for reuse: `ebics_download_camt053.py`, `ebics_debug.py`, `ebics_try_formats.py`, `ebics_process_file.py`, `ebics_reprocess.py`, `ebics_missing_range.py`.
- Creation form date field: `planned_date_begin` replaces `date_deadline` in "Formulaire de lancement d'opération".

## 2026-03-31 — lot_name generation, view layout, EBICS, bank config (session 6 final)
- `lot_name` generation priority fixed: `_generate_client_hint` now tries `client_destination_name` first (the free-text destinataire field), then `order_giver_id.name`, then `partner_id.name`, then falls back to `UNK`. Logic, uniqueness, and 6-char constraints unchanged.
- `test_lot_name_generation.py` updated: `test_client_hint_from_client_destination_name` and `test_client_destination_overrides_order_giver` added. 25/25 tests passing.
- `lot_name` form layout fixed: xpath was targeting `//field[@name='date_deadline']` position=after which placed the field inside `div#date_deadline_and_recurring_task` (d-inline-flex), causing MOR601 to appear on the date row. Changed to target `//div[@id='date_deadline_and_recurring_task']` position=after — now a proper labeled row.
- `views_simple.xml` form view override removed: making `planned_date_begin` visible inside the flex div corrupted the entire date row. The enterprise daterange widget already exposes it. Tree column kept.
- Bank journal (BNK1): `acc_number` updated from IBAN `FR76 1027 8061 6400 0202 5770 259` to raw BBAN `00021148802` (what EBICS CFONB file sends). IBAN-to-BBAN mismatch was the root cause of "No financial journal found" errors on all 17 transactions. IBAN confirmation from CIC still pending.
- `bank_statements_source` set to `undefined`, `account_online_account_id`/`account_online_link_id` cleared — removes "Reconnecter la banque" button on both DBs.
- Startup command fixed with `--max-cron-threads=0` — prevents Windows cron thread crash (`pg_conn.poll()` incompatibility). HTTP server is unaffected.

## 2026-03-31 — Duplication performance fix, test skip, db indexes (session 6 continued)
- Root cause of ~15s duplication delay: `gr_internal_inventory` and `gr_client_inventory` had only primary-key indexes; lookups by `task_id` were full table scans.
- Added `index=True` on `gr.internal.inventory.task_id`, `client_inventory_id`, `created_at` and `gr.client.inventory.task_id`.
- `test_date_field.py` marked with `@unittest.skip` — the tests were broken placeholders (empty field names from cherry-pick) and were causing test run failures.
- Both DBs upgraded; 4 new indexes confirmed in `pg_indexes`.

## 2026-03-31 — views_simple.xml fix and icecat audit (session 6)
- `views_simple.xml` was disabled because both its views tried to add `planned_date_begin` to views where enterprise already added it (invisible), causing a duplicate-field conflict.
- Form view fixed: now inherits `project_enterprise.project_task_view_form`, uses xpath `//div[@id='date_deadline_and_recurring_task']/field[@name='planned_date_begin']` to flip `invisible=0` and set `string="Date de début"`.
- Tree view fixed: inherits `project.view_task_tree2`, uses xpath `//field[@name='planned_date_begin']` to set `column_invisible=0` and `optional=show` (field was added `column_invisible="True"` by enterprise to `project_task_view_tree_base`, which is the parent).
- `project_enterprise` added to `gr_project_inventory` depends in `__manifest__.py`.
- `views_simple.xml` re-enabled in manifest.
- Both `greenremarket_backup` and `greenremarket` upgraded cleanly (no errors, only known warnings).
- `odoo_icecat_connector` confirmed already `uninstalled` in both DBs — no action needed.

## 2026-03-31 — First functional validation session (session 5)
- First browser validation on `greenremarket_backup`. Core module features confirmed working.
- Menu fix: Project Inventory reverted to under Project app (`views.xml` `parent="project.menu_main_pm"` restored; incorrect standalone app change reverted and applied to both DBs).
- EBICS: HPB called, `#BANK` section written to `ebics_keys/greenremarket/120558690001_keys`. FDL file download confirmed working.
- Open Banking cron jobs (IDs 38, 39, 40, 41) disabled on both `greenremarket` and `greenremarket_backup` — were crashing every 5 minutes due to invalid PSD2 tokens from production.
- EBICS safe import start date established: 2025-06-21 (day after last Open Banking transaction).
- `pdfminer.six` removed from `requirements.txt` (cryptography conflict with Odoo's `==3.4.8` pin).
- CI workflow (`odoo-ci.yml`) fixed: updated module path `gr_project_inventory/` → `modules/gr_project_inventory/`, fixed dependency install order to preserve cryptography pin.
- 23/23 tests passing after all fixes.
- Savepoint 4: `dumps/savepoint_4_ready_to_use_20260331.dump` + `odoo_data/filestore/greenremarket_backup` (standby).
- `BACKUP_AND_SWAP.md` updated with exact Windows PowerShell commands including `source\*` filestore copy pattern.

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

## 2026-03-29 — Resume consistency gate and stale state fix
- Added a mandatory resume consistency gate in guardrails: canonical docs must be cross-checked against live git state before any recommended next action is produced.
- Added a hard prohibition against recommending merge/cherry-pick/push steps unless same-session git verification proves they are still pending.
- Replaced stale `doc/CURRENT_STATE.md` pending-integration text with verified integration status for `backup-before-p1-8`.

## 2026-03-30 — Environment readiness hard gate enforced for resume flows
- Added a mandatory resume-time environment readiness probe requirement in `AGENTS.md` and `doc/START_HERE.md`.
- Defined `NON-OPERATIONAL` behavior: agents must report missing prerequisites first and stop at environment bootstrap/recovery guidance.
- Updated `doc/CURRENT_STATE.md` and `doc/NEXT_ACTIONS.md` so backlog/code-task recommendations are blocked until local prerequisites are confirmed present.
