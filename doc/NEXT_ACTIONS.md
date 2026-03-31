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
- Fix `views/views_simple.xml` xpath: `<field name="date_deadline" position="before">` fails on this enterprise task form version. Investigate the correct xpath to expose `planned_date_begin` and re-enable the file in `__manifest__.py`.

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
