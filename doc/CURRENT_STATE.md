# CURRENT STATE
Status: active
Last verified: 2026-04-01 (session 8)

## Repository and branch
- Repository: `greenremarket/gr_project_inventory`
- Canonical integration branch: `main` — pushed, stable, all work consolidated here
- New feature work: branch from `main`, name after the task, merge back when done
- Canonical operational docs are Git-tracked in `doc/`.

## Current operating model
- Primary workflow is active/standby rotation for both database and filestore.
- Active DB: `greenremarket` (production snapshot 2026-03-31, gr modules installed)
- Standby DB: `greenremarket_backup` (mirror of active as of 2026-04-01, savepoint 6, ready to use)
- Archived previous standby DB: `greenremarket_backup_20260401`
- Active filestore: `odoo_data/filestore/greenremarket`
- Standby filestore: `odoo_data/filestore/greenremarket_backup`
- Archived standby filestores: `odoo_data/filestore/greenremarket_backup_20260401` (savepoint 6), `odoo_data/filestore/greenremarket_backup_pre_sp5`
- Prior partial setup filestore archived at: `odoo_data/filestore/greenremarket_prior_march30`
- The old `greenremarket_test`-first workflow is historical, not current.
- Feature intake workflow now enforces a mandatory gate: research/probing, written plan, explicit developer approval, then implementation.

## What must not be touched without explicit approval
- Do not treat vague resume prompts as permission to implement.
- Do not modify production directly for feature work.
- Do not modify `extra_addons`.
- Do not do feature work directly on `main`.

## Validation and promotion workflow
- Refresh the standby side from active before risky work.
- Validate code and tests on standby.
- Promote by swapping DB aliases and matching filestore folders.
- Never swap only the database or only the filestore.
- Reference runbook: `doc/RUNBOOKS/BACKUP_AND_SWAP.md`

## Runtime essentials
- Odoo version: 17 Enterprise
- Python virtualenv: `.venv_odoo` (Python 3.11)
- PostgreSQL 17 at `C:\Program Files\PostgreSQL\17\bin` — must be in PATH
  - postgres superuser password: `postgres`
  - Odoo role: user `odoo`, password `odoo`, CREATEDB privilege

## Repository layout (all paths relative to repo root)
- `odoo/` — Odoo 17.0 community source: `git clone https://github.com/odoo/odoo --branch 17.0 --depth 1 odoo`
- `enterprise/` — Odoo 17.0 enterprise source: `git clone https://github.com/odoo/enterprise --branch 17.0 --depth 1 enterprise`
- `modules/gr_project_inventory/` — GRM custom inventory module (git-tracked)
- `modules/grm_documents_project/` — GRM documents module (git-tracked)
- `modules/grm_website/` — GRM website module (git-tracked)
- `third_party_modules/reporting-engine/` — OCA: `git clone https://github.com/OCA/reporting-engine --branch 17.0 --depth 1 third_party_modules/reporting-engine`
- `third_party_modules/account_ebics_repo/` — Noviat: `git clone https://github.com/Noviat/account_ebics --branch 17.0 --depth 1 third_party_modules/account_ebics_repo`
- `third_party_modules/account_reconcile_repo/` — OCA: `git clone https://github.com/OCA/account-reconcile --branch 17.0 --depth 1 third_party_modules/account_reconcile_repo`
- `third_party_modules/bank_statement_import_repo/` — OCA: `git clone https://github.com/OCA/bank-statement-import --branch 17.0 --depth 1 third_party_modules/bank_statement_import_repo`
- `third_party_modules/l10n_france_repo/` — OCA: `git clone https://github.com/OCA/l10n-france --branch 17.0 --depth 1 third_party_modules/l10n_france_repo`
- `ebics_keys/` — EBICS SSL keys (gitignored, machine-local — see `doc/DECISIONS/2026-03-31-ebics-keys-location.md`)

## pip requirements (into .venv_odoo)
1. `pip install -r odoo/requirements.txt`
2. `pip install -r requirements.txt`

## Resume-time environment readiness gate
- Any resume flow must probe live machine readiness before recommending code changes.
- Minimum required checks:
  - companion repos: `odoo/odoo-bin`, `enterprise/`, `third_party_modules/reporting-engine`, `third_party_modules/account_ebics_repo`, `third_party_modules/account_reconcile_repo`, `third_party_modules/bank_statement_import_repo`, `third_party_modules/l10n_france_repo`
  - runtime entrypoint: `.venv_odoo/Scripts/python.exe`
  - data paths: `odoo_data/filestore/greenremarket`, `odoo_data/filestore/greenremarket_backup`
  - PostgreSQL: `psql` in PATH, role `odoo` exists with CREATEDB
  - PostgreSQL tooling/connectivity on the local machine
- If any mandatory prerequisite is missing, status must be reported as `NON-OPERATIONAL` before any backlog recommendation.
- In `NON-OPERATIONAL` state, only environment bootstrap/recovery actions may be recommended until readiness is restored.

## Current validated changes
- P1.8 report/logo work is closed.
- Portal loader hardening is applied in `grm_website`.
- `views_simple.xml` re-enabled: tree view exposes `planned_date_begin` as an optional column. Form view keeps `planned_date_begin` invisible — the enterprise daterange widget on `date_deadline` already exposes it as the range start.
- `lot_name` row fixed in task form: now appears on its own row below `date_deadline` (was landing inside the date flex div).
- `lot_name` generation priority: `client_destination_name` → `order_giver_id.name` → `partner_id.name` → `UNK`. 25/25 tests passing.
- Bank journal (BNK1): `acc_number` set to `00021148802` (raw BBAN from EBICS CFONB file). `bank_statements_source` = `undefined`, Open Banking link cleared. “Reconnecter la banque” button gone.
- Pending: confirm correct full IBAN for account `00021148802` from CIC online banking and update both `acc_number` and `sanitized_acc_number` on `res_partner_bank` id=1 (both DBs). Account `00021148806` may need a second journal.
- "Formulaire de lancement d'opération" date fix: form collects `date_deadline` (labeled "Date de début"); `create()` syncs to `planned_date_begin`. Task form shows "Planned Date" range. Live-validated.
- Ctrl-C: `--dev=reload` in startup command cleanly stops the server on Windows. Live-validated.
- Bank statements imported via EBICS: 2026-03-05 to 2026-03-27 (16 statements). Gap 2025-06-21 to 2026-03-04 is not available via EBICS (CIC retention limit). Must be imported manually.
- Shell scripts for EBICS operations available in `scripts/`. Key script for future FDL runs: `scripts/ebics_try_formats.py`.

## Integration status
- `backup-before-p1-8` is already merged into `main`.
- Branch-first workflow remains in force: new feature work starts from `main` on a dedicated feature branch and merges back after validation.

## Current safety memory
- Do not modify `extra_addons`.
- For release stability, website editor-style overrides are high risk and should be checked before signoff.
- Expected safe state for website override recovery is zero active editor-style overrides.
- Reference runbook: `doc/RUNBOOKS/WEBSITE_OVERRIDE_RECOVERY.md`

## Startup and test commands
- Start Odoo on active:
  - `.\.venv_odoo\Scripts\python.exe odoo\odoo-bin -d greenremarket --db_host=localhost --db_port=5432 --db_user=odoo --db_password=odoo --data-dir=".\odoo_data" --addons-path="odoo/addons,enterprise,modules,third_party_modules/reporting-engine,third_party_modules/account_ebics_repo,third_party_modules/bank_statement_import_repo,third_party_modules/account_reconcile_repo,third_party_modules/l10n_france_repo" --log-level=warn --logfile=odoo_data/odoo.log --max-cron-threads=0 --dev=reload`
  - `--max-cron-threads=0`: avoids Windows-specific `pg_conn.poll()` crash in background cron threads.
  - `--dev=reload`: enables werkzeug dev reloader so Ctrl-C cleanly stops the server on Windows.
- PostgreSQL credentials: superuser `postgres`/`postgres`, Odoo role `odoo`/`odoo`. Use `$env:PGPASSWORD = "odoo"` before psql commands.
- Preferred validation target:
  - `greenremarket_backup`
- Targeted logo tests:
  - `--test-enable --test-tags="logo" --stop-after-init`
- Full module suite:
  - `--test-tags="/gr_project_inventory"`



