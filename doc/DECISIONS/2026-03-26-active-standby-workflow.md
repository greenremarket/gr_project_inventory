# Decision: adopt active/standby rotation for database and filestore
Date: 2026-03-26
Status: active

## Decision
The project now uses active/standby rotation for both database and filestore:
- active: `greenremarket`
- standby: `greenremarket_backup`

## Why
- The earlier `greenremarket_test`-first workflow no longer reflects how risky changes are validated and promoted.
- Active/standby rotation gives a clearer promotion path, cleaner rollback semantics, and better alignment between database and filestore state.

## Consequences
- Agents should validate risky changes on standby first.
- Promotion means swapping both DB and filestore aliases together.
- Older docs that describe `greenremarket_test` as the primary validation path are historical and must not override current operational guidance.

## References
- `doc/CURRENT_STATE.md`
- `doc/RUNBOOKS/BACKUP_AND_SWAP.md`
- `doc/archive/HANDOFF_PROD_SNAPSHOT_SWITCH_20260323.txt`
