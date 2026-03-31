# NEXT ACTIONS
Status: active
Last verified: 2026-03-31

## Operating priorities
1. Keep `greenremarket_backup` in sync with active before any risky work (standby exists and is current as of 2026-03-31).
2. Keep the matching filestore pair aligned with any DB refresh or swap.
3. Preserve access to the `enterprise` companion repository.

## Product and code backlog
### Open
- Fix the client bug in the form.
- For inventory item duplication, replace copied original dates with `fields.Datetime.now()`.
- Change the operation start date behavior or configuration.
- **EBICS catch-up import**: Run FDL manually from 2025-06-21 to today to import all missing bank statements. Safe start date is 2025-06-21 (day after last Open Banking transaction). Odoo deduplication handles overlap within EBICS.
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
- Client form bug, duplication date reset, and operation start date: code was cherry-picked from artifact branch. Needs explicit test validation before closure per backlog closure criteria.

### Confirmed closed
- P1.8 logo sizing is closed and should not be reopened without a new explicit request.
- Lot name length limit is implemented and tested (6-character constraint with validation).
- EBICS bank keys obtained (HPB called 2026-03-31, `#BANK` section written, FDL download confirmed).
- Open Banking cron jobs disabled (IDs 38, 39, 40, 41 on both DBs) — were crashing every 5 minutes.
- Project Inventory menu reverted to under Project app (removed incorrect standalone app behaviour).
- CI workflow fixed for `modules/` refactor — was broken since repo structure change.
- `views_simple.xml` fixed and re-enabled: form inherits `project_enterprise.project_task_view_form` to expose existing invisible `planned_date_begin`; tree view makes the enterprise-added hidden column optional/visible. `project_enterprise` added to module depends.
- `odoo_icecat_connector` state is already `uninstalled` in DB — no action needed.

## Resume guidance
- For short prompts such as `resume work on this project`, do not implement immediately.
- First run a live environment readiness probe and report `OPERATIONAL` or `NON-OPERATIONAL` with missing prerequisites.
- If status is `NON-OPERATIONAL`, stop at environment bootstrap/recovery guidance; do not recommend or begin feature implementation.
- Then summarize the operating model, validated state, active backlog, recommended next action, and what must not be touched.
- If a task changes the database or requires rollout-style validation, use the standby workflow from `doc/CURRENT_STATE.md` and `doc/RUNBOOKS/BACKUP_AND_SWAP.md`.
