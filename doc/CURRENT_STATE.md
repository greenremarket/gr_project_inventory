# CURRENT STATE
Status: active
Last verified: 2026-03-28

## Repository and branch
- Repository: `greenremarket/gr_project_inventory`
- Working branch: `backup-before-p1-8`
- Canonical operational docs are Git-tracked in `doc/`.
- There is an unreviewed autonomous branch named `fix/backlog-fixes` created by an accidental takeover test. It is not canonical state.

## Current operating model
- Primary workflow is active/standby rotation for both database and filestore.
- Active DB: `greenremarket`
- Standby DB: `greenremarket_backup`
- Archived prior standby DB: `greenremarket_20260326204605`
- Active filestore: `odoo_data/filestore/greenremarket`
- Standby filestore: `odoo_data/filestore/greenremarket_backup`
- Archived prior standby filestore: `odoo_data/filestore/greenremarket_20260326204605`
- The old `greenremarket_test`-first workflow is historical, not current.

## What must not be touched without explicit approval
- Do not treat vague resume prompts as permission to implement.
- Do not modify production directly for feature work.
- Do not modify `extra_addons`.
- Do not treat the unreviewed `fix/backlog-fixes` branch as accepted project state.

## Validation and promotion workflow
- Refresh the standby side from active before risky work.
- Validate code and tests on standby.
- Promote by swapping DB aliases and matching filestore folders.
- Never swap only the database or only the filestore.
- Reference runbook: `doc/RUNBOOKS/BACKUP_AND_SWAP.md`

## Runtime essentials
- Odoo version: 17 Enterprise
- Python virtualenv: `.venv_odoo`
- Required companion repos at branch `17.0`: `odoo`, `enterprise`, `OCA/reporting-engine`, `account_reconcile_repo`, `bank_statement_import_repo`, `l10n_france_repo`, `account_ebics_repo`
- Enterprise repo access must remain valid or Odoo startup will fail.

## Current validated changes
- P1.8 report/logo work is closed.
  - `gr_project_inventory/reports/internal_inventory_report.py` uses logo scale `1.0`
  - `gr_project_inventory/reports/discrepancy_report.py` uses logo scale `1.0`
  - `gr_project_inventory/reports/audit_report_xlsx.py` contains logo insertion with scale `1.0`
- Portal loader hardening is applied in:
  - `grm_website/static/src/js/loader.js`
  - `grm_website/templates/layout.xml`
- Dashboard/menu access change is retained in:
  - `gr_project_inventory/views/views.xml`
- The canonical documentation reorganization under `doc/` is the intended takeover path.

## Pending review from accidental autonomous test
- Branch: `fix/backlog-fixes`
- Status: unreviewed and not approved
- Meaning: useful only as review material, not as current accepted backlog completion

## Current safety memory
- Do not modify `extra_addons`.
- For release stability, website editor-style overrides are high risk and should be checked before signoff.
- Expected safe state for website override recovery is zero active editor-style overrides.
- Reference runbook: `doc/RUNBOOKS/WEBSITE_OVERRIDE_RECOVERY.md`

## Startup and test commands
- Start Odoo on active:
  - `.\.venv_odoo\Scripts\python.exe odoo\odoo-bin -d greenremarket --db_host=localhost --db_port=5432 --db_user=odoo --db_password=odoo --data-dir=".\odoo_data" --addons-path="odoo/addons,enterprise,.,OCA/reporting-engine,account_ebics_repo,bank_statement_import_repo,account_reconcile_repo,l10n_france_repo,portal_gr" --log-level=info`
- Preferred validation target:
  - `greenremarket_backup`
- Targeted logo tests:
  - `--test-enable --test-tags="logo" --stop-after-init`
- Full module suite:
  - `--test-tags="/gr_project_inventory"`
