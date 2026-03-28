# BACKUP AND SWAP RUNBOOK
Status: active
Last verified: 2026-03-28

## Purpose
Use this runbook for risky database or filestore changes. The current workflow validates on standby and promotes by swapping aliases.

## Standard flow
1. Confirm the active side is `greenremarket` and the standby side is `greenremarket_backup`.
2. Refresh the standby DB from active.
3. Refresh the standby filestore from active.
4. Run validation on standby.
5. Promote by swapping DB aliases and the matching filestore folders together.
6. Verify Odoo startup and smoke-test the promoted side.

## Guardrails
- Never change the active DB directly for feature work when standby validation is possible.
- Never swap only the DB or only the filestore.
- Keep archived rollback pairs intact when creating a new standby or promoting a change.
- Use `--pset="pager=off"` with `psql` on Windows.

## Current aliases
- Active DB: `greenremarket`
- Standby DB: `greenremarket_backup`
- Active filestore: `odoo_data/filestore/greenremarket`
- Standby filestore: `odoo_data/filestore/greenremarket_backup`

## Historical reference
- Detailed evidence and earlier promotion notes: `doc/archive/HANDOFF_PROD_SNAPSHOT_SWITCH_20260323.txt`
