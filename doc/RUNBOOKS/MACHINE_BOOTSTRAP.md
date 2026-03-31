# MACHINE BOOTSTRAP RUNBOOK
Status: active
Last verified: 2026-03-31

## Purpose
Step-by-step guide to get this Odoo 17 Enterprise environment running from scratch
on a clean Windows machine. Follow in order. No steps are optional.

---

## Prerequisites (install manually if missing)
- Python 3.11 — https://www.python.org/downloads/
- Git — https://git-scm.com/download/win
- winget (Windows Package Manager) — included in Windows 11, available via Microsoft Store on Windows 10

---

## Step 1 — Clone this repo
```
git clone https://github.com/greenremarket/gr_project_inventory.git E:\Dev\gr_project_inventory
cd E:\Dev\gr_project_inventory
```

---

## Step 2 — Install PostgreSQL 17
```
winget install PostgreSQL.PostgreSQL.17 --accept-source-agreements --accept-package-agreements
```
Add to PATH (current session):
```
$env:PATH += ";C:\Program Files\PostgreSQL\17\bin"
```
Add permanently via System Properties > Environment Variables > PATH.

Create the Odoo role (postgres superuser password is `postgres` by default from winget install):
```
$env:PGPASSWORD = "postgres"
psql -U postgres -c "CREATE ROLE odoo WITH LOGIN CREATEDB PASSWORD 'odoo';"
Remove-Item Env:PGPASSWORD
```

---

## Step 3 — Create the Python virtualenv
```
python -m venv .venv_odoo
```

---

## Step 4 — Clone Odoo community source
```
git clone https://github.com/odoo/odoo --branch 17.0 --depth 1 odoo
```

---

## Step 5 — Clone Odoo Enterprise source
Requires GitHub access with an active Odoo Enterprise subscription.
```
git clone https://github.com/odoo/enterprise --branch 17.0 --depth 1 enterprise
```

---

## Step 6 — Clone third-party modules (flat into third_party_modules/)
```
git clone https://github.com/OCA/reporting-engine --branch 17.0 --depth 1 third_party_modules/reporting-engine
git clone https://github.com/Noviat/account_ebics --branch 17.0 --depth 1 third_party_modules/account_ebics_repo
git clone https://github.com/OCA/account-reconcile --branch 17.0 --depth 1 third_party_modules/account_reconcile_repo
git clone https://github.com/OCA/bank-statement-import --branch 17.0 --depth 1 third_party_modules/bank_statement_import_repo
git clone https://github.com/OCA/l10n-france --branch 17.0 --depth 1 third_party_modules/l10n_france_repo
```

---

## Step 7 — Install pip requirements
```
.\.venv_odoo\Scripts\pip.exe install -r odoo\requirements.txt
.\.venv_odoo\Scripts\pip.exe install -r requirements.txt
```

---

## Step 8 — EBICS keys
Copy the EBICS SSL keys into `ebics_keys/` from a secure source.
See `doc/DECISIONS/2026-03-31-ebics-keys-location.md` for the expected directory structure.
The keys are machine-local and never committed to git.

---

## Step 9 — Restore or create a database
### Option A: Fresh DB from a backup zip (Odoo backup format)
1. Extract the zip — it contains `dump.sql`, `filestore/`, and `manifest.json`.
2. Create the DB:
   ```
   $env:PGPASSWORD = "odoo"
   createdb -U odoo greenremarket
   psql --pset="pager=off" -U odoo -d greenremarket -f path\to\dump.sql
   Remove-Item Env:PGPASSWORD
   ```
3. Copy the filestore:
   ```
   Copy-Item -Recurse path\to\filestore odoo_data\filestore\greenremarket
   ```

### Option B: Fresh empty DB
```
$env:PGPASSWORD = "odoo"
createdb -U odoo greenremarket
Remove-Item Env:PGPASSWORD
```
Then initialize with `--init=base --stop-after-init` (see startup command below).

---

## Step 10 — Start Odoo
```
.\.venv_odoo\Scripts\python.exe odoo\odoo-bin `
  -d greenremarket `
  --db_host=localhost --db_port=5432 --db_user=odoo --db_password=odoo `
  --data-dir=".\odoo_data" `
  --addons-path="odoo/addons,enterprise,modules,third_party_modules/reporting-engine,third_party_modules/account_ebics_repo,third_party_modules/bank_statement_import_repo,third_party_modules/account_reconcile_repo,third_party_modules/l10n_france_repo" `
  --log-level=info
```
Open http://localhost:8069 in a browser.

---

## Step 11 — Verify readiness
Before starting feature work, confirm all of these exist:
- `odoo/odoo-bin`
- `enterprise/` (non-empty)
- `modules/gr_project_inventory/__manifest__.py`
- `modules/grm_documents_project/__manifest__.py`
- `modules/grm_website/__manifest__.py`
- `third_party_modules/reporting-engine/` (non-empty)
- `third_party_modules/account_ebics_repo/` (non-empty)
- `third_party_modules/account_reconcile_repo/` (non-empty)
- `third_party_modules/bank_statement_import_repo/` (non-empty)
- `third_party_modules/l10n_france_repo/` (non-empty)
- `.venv_odoo/Scripts/python.exe`
- `odoo_data/filestore/greenremarket/` (non-empty)
- `psql` in PATH
- Role `odoo` exists in PostgreSQL
- `ebics_keys/greenremarket/` present (for EBICS connectivity)

If any of these are missing, this machine is NON-OPERATIONAL. Fix before doing feature work.

---

## Savepoint / rollback workflow
See `doc/RUNBOOKS/BACKUP_AND_SWAP.md` for the active/standby rotation workflow.

Quick savepoint of current DB:
```
$env:PGPASSWORD = "odoo"
pg_dump -U odoo -Fc greenremarket -f dumps\savepoint_YYYYMMDD_label.dump
Remove-Item Env:PGPASSWORD
```
Restore from savepoint:
```
$env:PGPASSWORD = "odoo"
dropdb -U odoo greenremarket
createdb -U odoo greenremarket
pg_restore -U odoo -d greenremarket dumps\savepoint_YYYYMMDD_label.dump
Remove-Item Env:PGPASSWORD
```
