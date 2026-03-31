# NEXT ACTIONS
Status: active
Last verified: 2026-03-30

## Operating priorities
1. Create `greenremarket_backup` from active before any risky work (standby does not exist yet on this machine).
2. Keep the matching filestore pair aligned with any DB refresh or swap.
3. Preserve access to the `enterprise` companion repository.

## Product and code backlog
### Open
- Fix the client bug in the form.
- For inventory item duplication, replace copied original dates with `fields.Datetime.now()`.
- Change the operation start date behavior or configuration.
- Fix `views/views_simple.xml` xpath: inherit `project.task.view.form.inherit.project.enterprise` instead of targeting `date_deadline` directly. Re-enable in `__manifest__.py`.
- **EBICS resolved**: HPB called successfully, `#BANK` section written to key file, file download via FDL confirmed working.
- **Open Banking crons disabled** (IDs 38, 39, 40, 41) on both `greenremarket` and `greenremarket_backup`. These were crashing every 5 minutes. "Reconnecter la banque" is the OB connector, unrelated to EBICS, leave it alone.
- **EBICS safe import start date: 2026-06-21** (day after last Open Banking transaction 2025-06-20). Always start EBICS FDL from this date to avoid duplicates with historical OB data.
- **EBICS auto-download scheduled action**: No built-in cron in this Noviat module version. Must create a custom Odoo Scheduled Action calling `ebics.xfer` FDL download + auto-import. This is the task that replaces Open Banking for executives — they should never have to manually trigger imports.
- **Icecat/MySQL**: `odoo_icecat_connector` connection errors on startup (external MySQL not reachable on this machine). Disable the module.
- **Warning pile (non-critical, clean up when time allows)**:
  - `pkg_resources` deprecated API warning from `fintech` package
  - `active_id`/`active_ids`/`active_model` in ir_ui_view expressions deprecated in Odoo 17
  - `gr_project_inventory` models not overriding `create` method in batch (ORM performance hint)
  - `@route()` decorator warnings in `grm_website`

### Deferred (planned, not started)
- Cross-machine kickstart and containerization/swarm roadmap is approved as a future initiative:
  - machine-agnostic local bootstrap on Windows/Linux via Docker Compose
  - agent directive kickstart flow for deterministic startup in Warp/Windsurf
  - swarm-target architecture with scalable Odoo, PostgreSQL persistent storage, Nginx reverse proxy, and cache service
- When promoted from deferred to active, create a dedicated feature branch from `main`, implement in phases, validate, and merge back per the branching model.

### Pending review
- Code for the three items above exists in artifact branch `fix/backlog-client-form-duplication-start-date` and is being cherry-picked; needs test validation before closure.
- Do not mark any of these confirmed closed without passing tests and a WORK_LOG entry.

### Confirmed closed
- P1.8 logo sizing is closed and should not be reopened without a new explicit request.
- Lot name length limit is implemented and tested (6-character constraint with validation).

## Resume guidance
- For short prompts such as `resume work on this project`, do not implement immediately.
- First run a live environment readiness probe and report `OPERATIONAL` or `NON-OPERATIONAL` with missing prerequisites.
- If status is `NON-OPERATIONAL`, stop at environment bootstrap/recovery guidance; do not recommend or begin feature implementation.
- Then summarize the operating model, validated state, active backlog, recommended next action, and what must not be touched.
- If a task changes the database or requires rollout-style validation, use the standby workflow from `doc/CURRENT_STATE.md` and `doc/RUNBOOKS/BACKUP_AND_SWAP.md`.
