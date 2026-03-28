# NEXT ACTIONS
Status: active
Last verified: 2026-03-28

## Operating priorities
1. Keep `greenremarket_backup` fresh before risky database/module work.
2. Keep the matching filestore pair aligned with any DB refresh or swap.
3. Preserve access to the `enterprise` companion repository.

## Product and code backlog
### Open
- Fix the client bug in the form.
- For inventory item duplication, replace copied original dates with `fields.Datetime.now()`.
- Change the operation start date behavior or configuration.

### Pending review
- Code for the three items above exists in artifact branch `fix/backlog-client-form-duplication-start-date` and is being cherry-picked; needs test validation before closure.
- Do not mark any of these confirmed closed without passing tests and a WORK_LOG entry.

### Confirmed closed
- P1.8 logo sizing is closed and should not be reopened without a new explicit request.
- Lot name length limit is implemented and tested (6-character constraint with validation).

## Resume guidance
- For short prompts such as `resume work on this project`, do not implement immediately.
- First summarize the operating model, validated state, active backlog, recommended next action, and what must not be touched.
- If a task changes the database or requires rollout-style validation, use the standby workflow from `doc/CURRENT_STATE.md` and `doc/RUNBOOKS/BACKUP_AND_SWAP.md`.
