# NEXT ACTIONS
Status: active
Last verified: 2026-03-28

## Operating priorities
1. Keep `greenremarket_backup` fresh before risky database/module work.
2. Keep the matching filestore pair aligned with any DB refresh or swap.
3. Preserve access to the `enterprise` companion repository.

## Product and code backlog
### Open
- (none remaining — all items below have been addressed)

### Done
- Fix the client bug in the form (duplicate `client_destination_name` in creation form removed).
- For inventory item duplication, `copy=False` added to `created_at` and `created_by_id` fields.
- Limit the maximum length of the lot name (already implemented with `@api.constrains` and `onchange`).
- Change the operation start date: `views_simple.xml` added to manifest, exposing `planned_date_begin` in task form and tree.

### Needs confirmation before implementation
- Any task that appears to reopen P1.8 logo sizing. Current state says that work is already closed and validated.

## Resume guidance
- For short prompts such as “resume work on this project”, start by confirming the current priority from the open backlog above.
- If a task changes the database or requires rollout-like validation, use the standby workflow from `doc/CURRENT_STATE.md` and `doc/RUNBOOKS/BACKUP_AND_SWAP.md`.
