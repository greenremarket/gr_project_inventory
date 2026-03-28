# HANDOFF FOR WINDSURF — CURRENT STATE (Odoo 17)
Date: 26 Mar 2026  
Purpose: Continue locally in Windsurf with the latest DB/filestore rotation, feature changes, and rollback plan. Warp credits exhausted.

---
## 1) Active topology (DB + filestore rotation)
- **Active DB:** `greenremarket`
- **Standby DB (hot clone):** `greenremarket_backup`
- **Archived prior standby:** `greenremarket_20260326204605`
- **Active filestore:** `odoo_data/filestore/greenremarket`
- **Standby filestore:** `odoo_data/filestore/greenremarket_backup`
- **Archived filestore:** `odoo_data/filestore/greenremarket_20260326204605`
- **Swap drill:** Completed bidirectional swap; Odoo booted on both sides (evidence in `doc/HANDOFF_PROD_SNAPSHOT_SWITCH_20260323.txt`, rotation section).

Rollback recipe:
1) Stop Odoo.  
2) Swap DB names (`greenremarket` ↔ `greenremarket_backup`) using Postgres superuser.  
3) Swap filestore folders (`greenremarket` ↔ `greenremarket_backup`).  
4) Start Odoo and verify.

---
## 2) Repositories (required beside main repo, branch 17.0)
- `odoo/` (public) — https://github.com/odoo/odoo.git
- `enterprise/` (private) — https://github.com/odoo/enterprise.git (needs valid access)
- `OCA/reporting-engine/` — https://github.com/OCA/reporting-engine.git
- `account_reconcile_repo/` — https://github.com/OCA/account-reconcile.git
- `bank_statement_import_repo/` — https://github.com/OCA/bank-statement-import.git
- `l10n_france_repo/` — https://github.com/OCA/l10n-france.git
- `account_ebics_repo/` — https://github.com/Noviat/account_ebics.git

Shallow clone example:
```
git clone --depth=1 --branch=17.0 https://github.com/odoo/odoo.git odoo
git clone --depth=1 --branch=17.0 https://github.com/odoo/enterprise.git enterprise   # requires access
git clone --depth=1 --branch=17.0 https://github.com/OCA/reporting-engine.git OCA/reporting-engine
git clone --depth=1 --branch=17.0 https://github.com/OCA/account-reconcile.git account_reconcile_repo
git clone --depth=1 --branch=17.0 https://github.com/OCA/bank-statement-import.git bank_statement_import_repo
git clone --depth=1 --branch=17.0 https://github.com/OCA/l10n-france.git l10n_france_repo
git clone --depth=1 --branch=17.0 https://github.com/Noviat/account_ebics.git account_ebics_repo
```

Main tracked repo: `greenremarket/gr_project_inventory` (branch `backup-before-p1-8`, commit `3fd8b12`).

---
## 3) Runtime & commands
- Python 3.10 virtualenv: `.venv_odoo`
- Install deps:
```
pip install -r odoo/requirements.txt
pip install -r requirements.txt   # xlsxwriter 3.1.9, openpyxl>=3.1.0, pandas>=2.0.0, numpy>=1.24.0
```
- wkhtmltopdf 0.12.6 installed and on PATH.
- Start Odoo (active DB):
```
$env:PGPASSWORD="odoo"
.\.venv_odoo\Scripts\python.exe odoo\odoo-bin `
  -d greenremarket `
  --db_host=localhost --db_port=5432 --db_user=odoo --db_password=odoo `
  --data-dir=".\odoo_data" `
  --addons-path="odoo/addons,enterprise,.,OCA/reporting-engine,account_ebics_repo,bank_statement_import_repo,account_reconcile_repo,l10n_france_repo,portal_gr" `
  --log-level=info
```
- Testing/staging: prefer using `greenremarket_backup` (clone from active) for validation before swaps.

---
## 4) Recent changes (features/fixes)
### a) P1.8 logo sizing closed
- `gr_project_inventory/reports/internal_inventory_report.py` → logo `x_scale/y_scale = 1.0` (aligned with discrepancy/audit).
- `gr_project_inventory/reports/discrepancy_report.py` → logo scale already at 1.0.
- `gr_project_inventory/reports/audit_report_xlsx.py` → logo insertion present, scale 1.0.
- Tests: `gr_project_inventory/tests/test_report_logo.py` (tag `logo`) passing on validation DB; full `/gr_project_inventory` suite also passing.

### b) Portal loader hardening
- `grm_website/static/src/js/loader.js`: removed jQuery dependency for loader path; deterministic hide timing; fallback timeout retained.
- `grm_website/templates/layout.xml`: added critical inline CSS fallback for loader overlay.
- Applied with module upgrade on active DB.

### c) Dashboard/menu access (prior work, retained)
- `gr_project_inventory/views/views.xml`: GR menu root promoted to top-level app (no parent), sequence 45, action `action_gr_client_inventory`.

---
## 5) Backup/failover discipline (current workflow)
- Work directly on **active + standby rotation** (not on the old `greenremarket_test` flow).
- Before risky changes: clone active to standby (`greenremarket` → `greenremarket_backup`) and sync filestore.
- Validate changes on standby DB/filestore; swap to promote if clean.
- Keep archived rollback pairs (DB + filestore) with timestamps:
  - `greenremarket_20260326204605` (DB) + matching filestore folder.
  - Earlier rollback pairs listed in `doc/HANDOFF_PROD_SNAPSHOT_SWITCH_20260323.txt`.

---
## 6) Testing guidance
- Prefer running targeted tests on standby DB before swap:
```
$env:PGPASSWORD="odoo"
.\.venv_odoo\Scripts\python.exe odoo\odoo-bin `
  -d greenremarket_backup `
  --test-enable --test-tags="logo" --stop-after-init `
  --addons-path="odoo/addons,enterprise,.,OCA/reporting-engine,account_ebics_repo,bank_statement_import_repo,account_reconcile_repo,l10n_france_repo,portal_gr"
```
- Full suite:
```
--test-tags="/gr_project_inventory"
```

---
## 7) Open items / next steps
- Maintain enterprise repo access; without it Odoo fails to start.
- Keep standby fresh before any module upgrades.
- If a swap is performed, always move the matching filestore pair with the DB rename.

---
## 8) Key references
- Rotation, P1.8, and loader change evidence: `doc/HANDOFF_PROD_SNAPSHOT_SWITCH_20260323.txt` (end sections).
- Dashboard missing analysis: `doc/HANDOFF_FOR_WARP_DASHBOARD.md`.
- Website override recovery runbook: `doc/RUNBOOK_GRM_WEBSITE_OVERRIDE_RECOVERY.txt`.

---
Prepared for: Windsurf local development  
Prepared by: Oz (Warp Agent)  
Co-Authored-By: Oz <oz-agent@warp.dev>
