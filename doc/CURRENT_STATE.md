# CURRENT STATE
Status: active
Last verified: 2026-04-01 (session 9, deployment fixes)

## Repository and branch
- Repository: `greenremarket/gr_project_inventory`
- Canonical integration branch: `main` ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â pushed, stable, all work consolidated here
- New feature work: branch from `main`, name after the task, merge back when done
- Canonical operational docs are Git-tracked in `doc/`.

## Deployment Ã¢â‚¬â€ Proxmox CT 200 (odoo-grm)
- New Odoo 17 Enterprise container created 2026-04-01 on Proxmox host vms1 (192.168.21.20).
- Container ID: 200, hostname: odoo-grm, IP: 192.168.21.200/24, gw: 192.168.21.254
- Proxmox SSH: `ssh root@192.168.21.20` (passwordless via migmi key)
- Container SSH: `ssh odoo-grm` (passwordless via migmi key, see `~/.ssh/config`)
- OS: Ubuntu 22.04 LTS, PostgreSQL 17, Python 3.10, Odoo venv at `/opt/odoo/venv`
- Odoo source: `/opt/odoo/addons_src` (community), `/opt/odoo/enterprise`, `/opt/odoo/grm_repo` (GRM modules)
- OCA/EBICS addons: `/opt/odoo/extra_addons`
- Config: `/opt/odoo/odoo.conf` Ã¢â‚¬â€ db_name=greenremarket, proxy_mode=True, workers=4
- Service: `systemctl status odoo` Ã¢â‚¬â€ enabled, starts on boot
- MySQL env: correct Aiken credentials (`manager`/`gren2803awb`/`192.168.21.206`) in systemd unit
- nginx: HTTPS with Let's Encrypt cert (sartrouville.greenremarket.fr + go.greenremarket.fr, valid 2026-06-30, DNS challenge — no auto-renewal without DNS plugin)
- Database: `greenremarket` restored from local savepoint, UTF-8 encoding (fr_FR.UTF-8 locale)
- Filestore: `/opt/odoo/data/filestore/greenremarket` (copied from local)
- Pending before go-live:
  - Router port forward 80/443 ? 192.168.21.200
  - `certbot --nginx -d sartrouville.greenremarket.fr` (or the target domain) for real SSL
  - Install grm_website + grm_documents_project (`--init`)
  - Fix EBICS bank account id=1: BBAN 00021148802 (currently IBAN)
  - DNS cutover from odoo_sartrouville to odoo-grm
  - Take Proxmox snapshot after smoke-test passes
- Rollback: Proxmox snapshot or just point DNS back to odoo_sartrouville
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
- SAFETY RULE: `greenremarket_backup` is the clean fallback. Never run --init or --update on it.
  Apply changes to `greenremarket` (active) first, validate there, THEN sync backup.
- Automated test passes (--test-enable) may target `greenremarket_backup` (no schema changes).
- To promote: swap DB aliases + filestore folders together. Never swap one without the other.
- Reference runbook: `doc/RUNBOOKS/BACKUP_AND_SWAP.md`

## Runtime essentials
- Odoo version: 17 Enterprise
- Python virtualenv: `.venv_odoo` (Python 3.11)
- PostgreSQL 17 at `C:\Program Files\PostgreSQL\17\bin` ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â must be in PATH
  - postgres superuser password: `postgres`
  - Odoo role: user `odoo`, password `odoo`, CREATEDB privilege

## Repository layout (all paths relative to repo root)
- `odoo/` ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â Odoo 17.0 community source: `git clone https://github.com/odoo/odoo --branch 17.0 --depth 1 odoo`
- `enterprise/` ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â Odoo 17.0 enterprise source: `git clone https://github.com/odoo/enterprise --branch 17.0 --depth 1 enterprise`
- `modules/gr_project_inventory/` ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â GRM custom inventory module (git-tracked)
- `modules/grm_documents_project/` ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â GRM documents module (git-tracked)
- `modules/grm_website/` ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â GRM website module (git-tracked)
- `third_party_modules/reporting-engine/` ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â OCA: `git clone https://github.com/OCA/reporting-engine --branch 17.0 --depth 1 third_party_modules/reporting-engine`
- `third_party_modules/account_ebics_repo/` ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â Noviat: `git clone https://github.com/Noviat/account_ebics --branch 17.0 --depth 1 third_party_modules/account_ebics_repo`
- `third_party_modules/account_reconcile_repo/` ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â OCA: `git clone https://github.com/OCA/account-reconcile --branch 17.0 --depth 1 third_party_modules/account_reconcile_repo`
- `third_party_modules/bank_statement_import_repo/` ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â OCA: `git clone https://github.com/OCA/bank-statement-import --branch 17.0 --depth 1 third_party_modules/bank_statement_import_repo`
- `third_party_modules/l10n_france_repo/` ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â OCA: `git clone https://github.com/OCA/l10n-france --branch 17.0 --depth 1 third_party_modules/l10n_france_repo`
- `ebics_keys/` ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â EBICS SSL keys (gitignored, machine-local ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â see `doc/DECISIONS/2026-03-31-ebics-keys-location.md`)

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
- `CrÃƒÂ©er le lot Aiken`: checkbox on Formulaire de lancement d'opÃƒÂ©ration triggers synchronous lot INSERT in `awbc_db.Lots`; non-blocking (bus.bus warning toast on failure). `CrÃƒÂ©er et aller ÃƒÂ  la tÃƒÂ¢che` navigation button. Live-validated 2026-04-01.
- Erasure cert error fix: `UserError` from `fetch_for_lot` now passes through instead of being swallowed by generic 'Could not connect' message. Live-validated 2026-04-01.
- P1.8 report/logo work is closed.
- Portal loader hardening is applied in `grm_website`.
- `views_simple.xml` re-enabled: tree view exposes `planned_date_begin` as an optional column. Form view keeps `planned_date_begin` invisible ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â the enterprise daterange widget on `date_deadline` already exposes it as the range start.
- `lot_name` row fixed in task form: now appears on its own row below `date_deadline` (was landing inside the date flex div).
- `lot_name` generation priority: `client_destination_name` ÃƒÂ¢Ã¢â‚¬Â Ã¢â‚¬â„¢ `order_giver_id.name` ÃƒÂ¢Ã¢â‚¬Â Ã¢â‚¬â„¢ `partner_id.name` ÃƒÂ¢Ã¢â‚¬Â Ã¢â‚¬â„¢ `UNK`. 25/25 tests passing.
- Bank journal (BNK1): `acc_number` set to `00021148802` (raw BBAN from EBICS CFONB file). `bank_statements_source` = `undefined`, Open Banking link cleared. ÃƒÂ¢Ã¢â€šÂ¬Ã…â€œReconnecter la banqueÃƒÂ¢Ã¢â€šÂ¬Ã‚Â button gone.
- Pending: confirm correct full IBAN for account `00021148802` from CIC online banking and update both `acc_number` and `sanitized_acc_number` on `res_partner_bank` id=1 (both DBs). Account `00021148806` may need a second journal.
- "Formulaire de lancement d'opÃƒÆ’Ã‚Â©ration" date fix: form collects `date_deadline` (labeled "Date de dÃƒÆ’Ã‚Â©but"); `create()` syncs to `planned_date_begin`. Task form shows "Planned Date" range. Live-validated.
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
- Test runs (--test-enable, read-only) use `greenremarket_backup` as target.
  - `greenremarket_backup`
- Targeted logo tests:
  - `--test-enable --test-tags="logo" --stop-after-init`
- Full module suite:
  - `--test-tags="/gr_project_inventory"`






