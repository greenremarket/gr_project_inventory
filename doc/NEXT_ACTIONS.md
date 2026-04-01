# NEXT ACTIONS
Status: active
Last verified: 2026-03-31

## Operating priorities
1. Keep `greenremarket_backup` in sync with active before any risky work (standby exists and is current as of 2026-03-31).
2. Keep the matching filestore pair aligned with any DB refresh or swap.
3. Preserve access to the `enterprise` companion repository.

## Product and code backlog
### Open
- **NEW — Créer le lot Aiken depuis le Formulaire de lancement d'opération**: When an operator uses the launch form, a `lot_name` is generated. Add a checkbox `Créer le lot Aiken` to the form; when checked, the task's `create()` calls a new method on `gr.erasure.service` that INSERTs into `awbc_db.Lots` (synchronous, LAN). `LotID` is `MAX(LotID)+1` inside a MySQL transaction. `Params` is 352 bytes of ASCII '0'. Full plan in Warp: "Créer le lot Aiken depuis le Formulaire de lancement d'opération". Branch from `main` before starting.- **EBICS bank account â€” needs IBAN confirmation**: Bank account is currently stored as raw BBAN `00021148802`. Once the correct full IBAN is obtained from CIC/CM online banking, update `res_partner_bank` id=1 and id=1 on `greenremarket_backup` (both `acc_number` and `sanitized_acc_number`). Account `00021148806` may need a second journal if it belongs to the company.
- **Statement gap 2025-06-21 to 2026-03-04**: CIC EBICS FDL only retains ~30 days of CFONB history (90005 on earlier range). Statements for this 9-month gap must be imported manually from CIC online banking PDF/CSV export. Accounting team to handle.
- **EBICS catch-up for 2026-03-28 onwards**: Next FDL run needed to pick up the last few days (file ended 2026-03-27). Should be done from the UI now that the account matching is fixed.
- **EBICS auto-download scheduled action**: Build a custom Odoo Scheduled Action calling `ebics.xfer` FDL + auto-import daily. Replaces manual imports for accounting team.
- **Warning pile (non-critical, clean up when time allows)**:
  - `pkg_resources` deprecated API from `fintech`
  - `active_id`/`active_ids`/`active_model` in ir_ui_view expressions deprecated in Odoo 17
  - `gr_project_inventory` models not overriding `create` in batch (ORM performance hint)
  - `@route()` decorator warnings in `grm_website`

### Deferred (planned, not started)
- Cross-machine kickstart and containerization/swarm roadmap is approved as a future initiative:
  - machine-agnostic local bootstrap on Windows/Linux via Docker Compose
  - agent directive kickstart flow for deterministic startup in Warp/Windsurf
  - swarm-target architecture with scalable Odoo, PostgreSQL persistent storage, Nginx reverse proxy, and cache service
- When promoted from deferred to active, create a dedicated feature branch from `main`, implement in phases, validate, and merge back per the branching model.

### Pending review
- Client form bug (item 5c): pending live confirmation from user on test server.
- `test_date_field.py`: all tests skipped (`@unittest.skip`) â€” placeholder stubs with empty field names from a cherry-pick. Either rewrite against `planned_date_begin` or delete.

### Confirmed closed
- P1.8 logo sizing is closed and should not be reopened without a new explicit request.
- Lot name length limit is implemented and tested (6-character constraint with validation).
- EBICS bank keys obtained (HPB called 2026-03-31, `#BANK` section written, FDL download confirmed).
- Open Banking cron jobs disabled (IDs 38, 39, 40, 41 on both DBs) â€” were crashing every 5 minutes.
- Project Inventory menu reverted to under Project app (removed incorrect standalone app behaviour).
- CI workflow fixed for `modules/` refactor â€” was broken since repo structure change.
- `views_simple.xml` re-enabled with tree-only change: optional `planned_date_begin` column in task list. Form view override was reverted (placed field inside date flex div causing layout corruption). `project_enterprise` added to module depends.
- `odoo_icecat_connector` state is already `uninstalled` in DB â€” no action needed.
- Duplication performance indexes added to `gr_internal_inventory` (task_id, client_inventory_id, created_at) and `gr_client_inventory` (task_id). Both DBs upgraded.
- `test_date_field.py` skipped via `@unittest.skip` â€” tests are broken placeholders from cherry-pick.
- "Reconnecter la banque" button removed: `bank_statements_source` set to `undefined`, Online Banking link cleared on both DBs.
- Startup command updated with `--max-cron-threads=0`.
- `lot_name` generation priority fixed: `client_destination_name` â†’ `order_giver_id` â†’ `partner_id` â†’ `UNK`. Tests updated, 25/25 passing.
- `lot_name` layout fixed in task form: moved to its own row outside the date flex div.
- `views_simple.xml` form override reverted: `planned_date_begin` stays invisible in form (enterprise daterange widget handles it). Tree column kept.
- Creation form date field fixed: `planned_date_begin` (start date) replaces `date_deadline` in "Formulaire de lancement d'opÃ©ration".
- EBICS fully resolved via Odoo shell scripts (`scripts/`). `sanitized_acc_number` was the real missing fix (SQL update of `acc_number` does not trigger stored field recompute). 16 statements imported for 2026-03-05 to 2026-03-27. Historical gap (2025-06-21 to 2026-03-04) confirmed unavailable via EBICS (code 90005). Account `00021148806` still needs investigation.
- Shell scripts archived in `scripts/` for reuse.
- Portal fixes: home follower domain, task_documents template, access token on Delivrable tag, fetch+blob download.
- Binary zip corruption fixed: isinstance(data, (str, bytes)) — Odoo ORM returns base64 as bytes not str.
- `planned_date_begin` persistence fixed and live-validated: creation form collects `date_deadline`; `create()` syncs to `planned_date_begin`. Task form shows "Planned Date" range. 28/28 tests passing.
- Ctrl-C now stops the server cleanly on Windows via `--dev=reload` (werkzeug reloader). Live-validated.
- Duplication performance (item 5a): indexes live on both DBs. Closed â€” reopen only if lag reappears in production.
- Client form bug (item 5c): closed by user validation.

## Resume guidance
- For short prompts such as `resume work on this project`, do not implement immediately.
- First run a live environment readiness probe and report `OPERATIONAL` or `NON-OPERATIONAL` with missing prerequisites.
- If status is `NON-OPERATIONAL`, stop at environment bootstrap/recovery guidance; do not recommend or begin feature implementation.
- Then summarize the operating model, validated state, active backlog, recommended next action, and what must not be touched.
- If a task changes the database or requires rollout-style validation, use the standby workflow from `doc/CURRENT_STATE.md` and `doc/RUNBOOKS/BACKUP_AND_SWAP.md`.


