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

## Windows commands

### Refresh standby from active
```powershell
$env:PATH += ";C:\Program Files\PostgreSQL\17\bin"
$env:PGPASSWORD = "odoo"
# Drop and recreate standby DB
dropdb -U odoo greenremarket_backup
createdb -U odoo greenremarket_backup
pg_restore -U odoo -d greenremarket_backup -Fc dumps\savepoint_YYYYMMDD_label.dump
Remove-Item Env:PGPASSWORD
# Refresh standby filestore (note: use \* to copy CONTENTS, not the directory itself)
Move-Item odoo_data\filestore\greenremarket_backup odoo_data\filestore\greenremarket_backup_prev
New-Item -ItemType Directory odoo_data\filestore\greenremarket_backup | Out-Null
Copy-Item -Recurse odoo_data\filestore\greenremarket\* odoo_data\filestore\greenremarket_backup\
```
Critical: always use `source\*` (with backslash-star) when copying filestore contents. Without the `*`, PowerShell nests the source directory inside the destination.

### Create a savepoint dump of active
```powershell
$env:PATH += ";C:\Program Files\PostgreSQL\17\bin"
$env:PGPASSWORD = "odoo"
pg_dump -U odoo -Fc greenremarket -f dumps\savepoint_YYYYMMDD_label.dump
Remove-Item Env:PGPASSWORD
```

### Start Odoo on standby for validation
```powershell
$env:PATH += ";C:\Program Files\PostgreSQL\17\bin"
.\venv_odoo\Scripts\Activate.ps1
python odoo\odoo-bin -d greenremarket_backup --db_host=localhost --db_port=5432 --db_user=odoo --db_password=odoo --data-dir=".\odoo_data" --addons-path="odoo/addons,enterprise,modules,third_party_modules/reporting-engine,third_party_modules/account_ebics_repo,third_party_modules/bank_statement_import_repo,third_party_modules/account_reconcile_repo,third_party_modules/l10n_france_repo" --log-level=warn
```

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
