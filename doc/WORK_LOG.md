# WORK LOG
Status: active
Last updated: 2026-04-01 (session 10, CT 200 deploy)

## 2026-03-23 â€” Database recovery
- Restored the project after dump-format confusion by using the correct PostgreSQL restore method for plain SQL dumps.
- Recovered the active database as `greenremarket`.
- Re-established the working Odoo environment and preserved data integrity.
- Historical evidence: `doc/archive/COMPLETE_HANDOFF_FULL_PROJECT.md`

## 2026-03-23 â€” Snapshot restore and promotion
- Loaded a production snapshot into an isolated working database and filestore.
- Installed/upgraded `gr_project_inventory`, `grm_website`, and `grm_documents_project`.
- Validated startup and module tests, deactivated unsafe website editor-style overrides, and promoted the snapshot to active.
- Historical evidence: `doc/archive/HANDOFF_PROD_SNAPSHOT_SWITCH_20260323.txt`

## 2026-03-23 â€” Dashboard and initial P1.8 rollout
- Promoted the GR menu root to a top-level app entry.
- Added report logo tests and applied the initial P1.8 report changes.
- Validated targeted logo tests and the full `/gr_project_inventory` suite before rollout.
- Historical evidence: `doc/archive/HANDOFF_PROD_SNAPSHOT_SWITCH_20260323.txt`

## 2026-03-26 â€” Rotation workflow adopted and stabilized
- Normalized active/standby DB aliases to `greenremarket` and `greenremarket_backup`.
- Normalized matching filestore aliases and completed a bidirectional swap drill.
- Hardened the portal loader and aligned the remaining logo scale mismatch to `1.0`.
- Revalidated targeted logo tests and the full `/gr_project_inventory` suite.
- Historical evidence: `doc/archive/HANDOFF_PROD_SNAPSHOT_SWITCH_20260323.txt`

## 2026-03-28 â€” Canonical takeover docs introduced
- Added the canonical takeover chain under `doc/`.
- Archived stale operational docs under `doc/archive/`.
- Established `doc/START_HERE.md` as the entrypoint for future agents.

## 2026-03-28 â€” Failed live takeover test
- A live `oz agent run` test was mistakenly used with the vague prompt `resume work on this project`.
- The agent treated that prompt as authorization to implement work, created branch `fix/backlog-fixes`, committed changes, and pushed them.
- That outcome is now treated as a guardrail failure case, not as accepted project progress.

## 2026-03-28 â€” Backlog test review completed
- Reviewed active backlog items against existing test coverage in `gr_project_inventory/tests/`.
- **Lot name length**: Confirmed implemented and tested via `test_lot_name_generation.py`:
  - 6-character maximum constraint enforced (`test_lot_name_length_constraint_6_chars`)
  - Unique constraint with proper ValidationError (`test_lot_name_unique_constraint`)
  - Auto-generation format XXXYZZ validated (`test_format_compatibility`)
- **Inventory item duplication**: No tests found covering date reset on copy; implementation status unknown.
- **Operation start date**: Tests exist in `test_date_field.py` but field names appear incomplete (placeholder `''` values); needs verification.
- **Client bug in form**: No tests found; needs clarification on specific issue.
- Moved "Lot name length" from Open to Confirmed closed in `doc/NEXT_ACTIONS.md`.

## 2026-03-31 â€” migmi machine bootstrap (session 4)
- Repo refactored: `gr_project_inventory`, `grm_documents_project`, `grm_website` moved to `modules/`.
- `third_party_modules/` and `ebics_keys/` directories created with `.gitkeep`; contents gitignored.
- `portal_gr` removed from all references (no longer exists; replaced by `grm_*` in `modules/`).
- Git remote fixed from stale OneDrive path to `https://github.com/greenremarket/gr_project_inventory.git`.
- `doc/DECISIONS/2026-03-31-ebics-keys-location.md` created documenting EBICS key location.
- PostgreSQL 17.9 installed via winget. Role `odoo/odoo` with CREATEDB created.
- Cloned at `17.0 --depth 1`: `odoo`, `enterprise`, `third_party_modules/reporting-engine` (OCA), `third_party_modules/account_ebics_repo` (Noviat), `third_party_modules/account_reconcile_repo` (OCA), `third_party_modules/bank_statement_import_repo` (OCA), `third_party_modules/l10n_france_repo` (OCA).
- pip requirements installed from `odoo/requirements.txt` and `requirements.txt` into `.venv_odoo`.
- Production backup `greenremarket_2026-03-31_17-20-12.zip` received (PG 16.13 source, 69 MB SQL + 2252 filestore files).
- Savepoint 0: extracted to `dumps/savepoint_0_production_20260331/` (immutable baseline).
- DB `greenremarket_incoming` created and restored from `dump.sql`. Filestore copied to `odoo_data/filestore/greenremarket_incoming/`. 2252 files confirmed.
- Savepoint 1: `dumps/savepoint_1_restored_raw.dump` (pg_dump -Fc of raw restored DB).
- Next: website cleanup â†’ savepoint 2 â†’ module upgrade â†’ savepoint 3 â†’ promote to `greenremarket`.
- Website cleanup done: 4 editor-style overrides deactivated (template_header_default, header_text_element, footer_custom, footer_copyright_company_name). Count confirmed 0.
- Savepoint 2: `dumps/savepoint_2_cleaned.dump`.
- Missing pip dependencies discovered and installed: `pymysql>=1.1`, `fintech`, `pdfminer.six`. Added to `requirements.txt`.
- `views_simple.xml` commented out in manifest â€” `date_deadline` xpath fails on this enterprise version. Added as open backlog item.
- gr modules upgraded/installed: `gr_project_inventory` 17.0.1.2, `grm_website` 17.0.1.1.3, `grm_documents_project` 17.0.1.1.2. `account_ebics` and `account_ebics_oe` synced.
- Savepoint 3: `dumps/savepoint_3_upgraded.dump`.
- DB renamed `greenremarket_incoming` â†’ `greenremarket`. Filestore promoted. Old March 30 filestore archived as `greenremarket_prior_march30`.
- Machine is now operational.
- Standby pair created: `greenremarket_backup` DB (240 installed modules confirmed) and `odoo_data/filestore/greenremarket_backup`. Active/standby rotation model is now fully operational on this machine.

## 2026-04-01 â€” Savepoint 5, standby sync, portal fixes (session 7 start)
- Portal home (`portal_home.py`) fixed: was searching by `user_ids` (internal assignment), portal clients are followers not assignees. Changed to commercial partner follower domain with PD3E tag filter.
- Document portal downloads fixed: `documents_document.write()` now generates `attachment.access_token` when the Delivrable tag is added. 704/713 existing document attachments had no token (downloads silently failed).
- `scripts/generate_delivrable_access_tokens.py` added for backfill (found 0 Delivrable documents in local DB â€” no existing delivrable docs yet).
- Savepoint 5 created: `dumps/savepoint_5_ebics_portal_fixes_20260401.dump` (14.3 MB, includes 16 EBICS bank statements).
- `greenremarket_backup` fully refreshed from savepoint 5: DB restored + filestore synced (2261 files each). Both DBs now identical and contain the EBICS statements.
- Old backup filestore archived as `odoo_data/filestore/greenremarket_backup_pre_sp5`.

## 2026-03-31 â€” planned_date_begin fix, Ctrl-C, test coverage (session 6, end)
- Root cause confirmed via test: `Form()` fires `_onchange_planned_dates` after each field change, not after the whole form is filled. Setting `planned_date_begin` first always wipes it even if `date_deadline` is set next.
- Fix: creation form now collects `date_deadline` (labeled "Date de dÃ©but de l'opÃ©ration"). `date_deadline` has no enterprise onchange that wipes it. `create()` override mirrors `date_deadline` â†’ `planned_date_begin` at midnight server-side.
- `default_get` override: when `gr_creation_form` context flag is present, pre-fills `date_deadline` to today+1 so the form always opens with a valid date (prevents onchange wipe on first keypress).
- `--dev=reload` added to startup command: werkzeug dev reloader handles Ctrl-C on Windows.
- 28/28 tests passing. New tests: `test_planned_date_begin_wiped_without_deadline` (documents bug), `test_create_syncs_planned_date_from_deadline` (validates fix), `test_explicit_planned_date_begin_is_not_overwritten`.

## 2026-03-31 â€” EBICS full resolution + statement import (session 6, late)
- Root cause of "No financial journal found" identified: `sanitized_acc_number` is a stored computed field. SQL update to `acc_number` does NOT trigger a recompute. Both `acc_number` and `sanitized_acc_number` on `res_partner_bank` id=1 now set to `00021148802` on both DBs.
- EBICS 91116 on FDL with end date 2026-03-31: bank considers that delivery "consumed" (receipt acknowledged). Shifting end date to 2026-03-30 bypassed the block.
- Z53 (camt.053 CIC-specific) rejected with 91005 INVALID_ORDER_TYPE. C53 rejected with functional error. FDL/cfonb120 is the only working format at CIC for this EBICS contract.
- 16 bank statements imported: 2026-03-05 through 2026-03-27.
- Historical gap 2025-06-21 to 2026-03-04: confirmed unavailable via EBICS (code 90005 EBICS_NO_DOWNLOAD_DATA_AVAILABLE). CIC only retains ~30 days of CFONB in EBICS FDL. This gap must be imported manually from CIC online banking export.
- Shell scripts created in `scripts/` for reuse: `ebics_download_camt053.py`, `ebics_debug.py`, `ebics_try_formats.py`, `ebics_process_file.py`, `ebics_reprocess.py`, `ebics_missing_range.py`.
- Creation form date field: `planned_date_begin` replaces `date_deadline` in "Formulaire de lancement d'opÃ©ration".

## 2026-03-31 â€” lot_name generation, view layout, EBICS, bank config (session 6 final)
- `lot_name` generation priority fixed: `_generate_client_hint` now tries `client_destination_name` first (the free-text destinataire field), then `order_giver_id.name`, then `partner_id.name`, then falls back to `UNK`. Logic, uniqueness, and 6-char constraints unchanged.
- `test_lot_name_generation.py` updated: `test_client_hint_from_client_destination_name` and `test_client_destination_overrides_order_giver` added. 25/25 tests passing.
- `lot_name` form layout fixed: xpath was targeting `//field[@name='date_deadline']` position=after which placed the field inside `div#date_deadline_and_recurring_task` (d-inline-flex), causing MOR601 to appear on the date row. Changed to target `//div[@id='date_deadline_and_recurring_task']` position=after â€” now a proper labeled row.
- `views_simple.xml` form view override removed: making `planned_date_begin` visible inside the flex div corrupted the entire date row. The enterprise daterange widget already exposes it. Tree column kept.
- Bank journal (BNK1): `acc_number` updated from IBAN `FR76 1027 8061 6400 0202 5770 259` to raw BBAN `00021148802` (what EBICS CFONB file sends). IBAN-to-BBAN mismatch was the root cause of "No financial journal found" errors on all 17 transactions. IBAN confirmation from CIC still pending.
- `bank_statements_source` set to `undefined`, `account_online_account_id`/`account_online_link_id` cleared â€” removes "Reconnecter la banque" button on both DBs.
- Startup command fixed with `--max-cron-threads=0` â€” prevents Windows cron thread crash (`pg_conn.poll()` incompatibility). HTTP server is unaffected.

## 2026-03-31 â€” Duplication performance fix, test skip, db indexes (session 6 continued)
- Root cause of ~15s duplication delay: `gr_internal_inventory` and `gr_client_inventory` had only primary-key indexes; lookups by `task_id` were full table scans.
- Added `index=True` on `gr.internal.inventory.task_id`, `client_inventory_id`, `created_at` and `gr.client.inventory.task_id`.
- `test_date_field.py` marked with `@unittest.skip` â€” the tests were broken placeholders (empty field names from cherry-pick) and were causing test run failures.
- Both DBs upgraded; 4 new indexes confirmed in `pg_indexes`.

## 2026-03-31 â€” views_simple.xml fix and icecat audit (session 6)
- `views_simple.xml` was disabled because both its views tried to add `planned_date_begin` to views where enterprise already added it (invisible), causing a duplicate-field conflict.
- Form view fixed: now inherits `project_enterprise.project_task_view_form`, uses xpath `//div[@id='date_deadline_and_recurring_task']/field[@name='planned_date_begin']` to flip `invisible=0` and set `string="Date de dÃ©but"`.
- Tree view fixed: inherits `project.view_task_tree2`, uses xpath `//field[@name='planned_date_begin']` to set `column_invisible=0` and `optional=show` (field was added `column_invisible="True"` by enterprise to `project_task_view_tree_base`, which is the parent).
- `project_enterprise` added to `gr_project_inventory` depends in `__manifest__.py`.
- `views_simple.xml` re-enabled in manifest.
- Both `greenremarket_backup` and `greenremarket` upgraded cleanly (no errors, only known warnings).
- `odoo_icecat_connector` confirmed already `uninstalled` in both DBs â€” no action needed.

## 2026-03-31 â€” First functional validation session (session 5)
- First browser validation on `greenremarket_backup`. Core module features confirmed working.
- Menu fix: Project Inventory reverted to under Project app (`views.xml` `parent="project.menu_main_pm"` restored; incorrect standalone app change reverted and applied to both DBs).
- EBICS: HPB called, `#BANK` section written to `ebics_keys/greenremarket/120558690001_keys`. FDL file download confirmed working.
- Open Banking cron jobs (IDs 38, 39, 40, 41) disabled on both `greenremarket` and `greenremarket_backup` â€” were crashing every 5 minutes due to invalid PSD2 tokens from production.
- EBICS safe import start date established: 2025-06-21 (day after last Open Banking transaction).
- `pdfminer.six` removed from `requirements.txt` (cryptography conflict with Odoo's `==3.4.8` pin).
- CI workflow (`odoo-ci.yml`) fixed: updated module path `gr_project_inventory/` â†’ `modules/gr_project_inventory/`, fixed dependency install order to preserve cryptography pin.
- 23/23 tests passing after all fixes.
- Savepoint 4: `dumps/savepoint_4_ready_to_use_20260331.dump` + `odoo_data/filestore/greenremarket_backup` (standby).
- `BACKUP_AND_SWAP.md` updated with exact Windows PowerShell commands including `source\*` filestore copy pattern.

## 2026-03-28 â€” Guardrail docs patched and branching model established (session 3)
- External research pass confirmed design alignment with AGENTS.md community standard, guardrails.md Signs architecture, OpenAI Codex AGENTS.md discovery model, and GitHub Agentic Workflows 3-layer guardrail pattern.
- Four gaps identified and addressed: structured 5-section resume report format, privilege boundaries (safe vs. requires approval), push-and-sync requirement, backlog closure criteria requiring test evidence.
- Added Git and branching model: `main` as stable integration branch, feature branches per task, agents check current branch on resume.
- Cleaned up stale `fix/backlog-fixes` references from all canonical docs.
- Updated `doc/CURRENT_STATE.md` to reflect `main`-first model and pending consolidation of `backup-before-p1-8`.
- Code fixes from artifact branch `fix/backlog-client-form-duplication-start-date` cherry-picked onto `backup-before-p1-8` (copy=False on created_at/created_by_id, remove duplicate client field, add views_simple.xml to manifest).

## 2026-03-28 â€” Deferred platform roadmap captured for later execution
- Added a deferred backlog item in `doc/NEXT_ACTIONS.md` to preserve the cross-machine kickstart and containerization/swarm initiative.
- Explicitly documented future execution mode: create a dedicated feature branch from `main`, implement in phases, validate, and merge when ready.

## 2026-03-28 â€” Mandatory feature intake gate added
- Updated guardrail workflow to require a strict pre-implementation sequence for first-pass feature work: research/probing, written plan, then explicit developer approval.
- Added the same gate to the canonical startup guidance so future sessions enforce it consistently before branching or coding.
- Updated current-state documentation to reflect this as active operating policy.

## 2026-03-29 â€” Resume consistency gate and stale state fix
- Added a mandatory resume consistency gate in guardrails: canonical docs must be cross-checked against live git state before any recommended next action is produced.
- Added a hard prohibition against recommending merge/cherry-pick/push steps unless same-session git verification proves they are still pending.
- Replaced stale `doc/CURRENT_STATE.md` pending-integration text with verified integration status for `backup-before-p1-8`.

## 2026-03-30 â€” Environment readiness hard gate enforced for resume flows
- Added a mandatory resume-time environment readiness probe requirement in `AGENTS.md` and `doc/START_HERE.md`.
- Defined `NON-OPERATIONAL` behavior: agents must report missing prerequisites first and stop at environment bootstrap/recovery guidance.
- Updated `doc/CURRENT_STATE.md` and `doc/NEXT_ACTIONS.md` so backlog/code-task recommendations are blocked until local prerequisites are confirmed present.

## 2026-04-01 — Report logo fix (session 7 continued)
- company.logo = related to partner_id.image_1920 (filestore). EMPTY in this DB — image_1920 not restored from production dump.
- company.logo_web = 17,704 bytes stored directly in res_company table. Always present.
- Fixed both internal_inventory_report.py and discrepancy_report.py to use logo_web first, logo as fallback.
- Fixed scale regression: was 0.125 (P1.8 broke this), restored to 1.0. logo_web is 180px so 1.0 is correct.
- Validated by user (2026-04-01). Closed.

## 2026-04-01 -- Aiken Workbench credentials investigation (session 8)
- All five \gr.workbench_*\ params exist in local \ir.config_parameter\ but have empty values.
- Credentials \manager / gren2803awb\ are NOT stored in the local DB.
- Code in \erasure_service._dsn()\ falls back to hardcoded defaults: host=192.168.21.206, user=awbadmin, password=(blank), db=awbc_db.
- On production, credentials must be set either in \ir.config_parameter\ (gr.workbench_user / gr.workbench_pwd) or as env vars (MYSQL_HOST / MYSQL_PORT / MYSQL_USER / MYSQL_PASSWORD / MYSQL_DATABASE) in the systemd unit.
- Production server comment in code references \/opt/odoo/MYSQL_WORKBENCH_README.md\ for setup details.
- To enable Aiken locally: populate the \gr.workbench_*\ params via Settings -> Technical -> System Parameters, or set MYSQL_* env vars before starting Odoo.


## 2026-04-01 — Savepoint 6 and Créer le lot Aiken planning (session 8)
- Savepoint 6 created: `dumps/savepoint_6_pre_aiken_lot_20260401.dump` (full dump of active `greenremarket`).
- Old standby pair archived: DB renamed to `greenremarket_backup_20260401`; filestore moved to `odoo_data/filestore/greenremarket_backup_20260401`.
- New `greenremarket_backup` (DB + filestore) is now a fresh mirror of `greenremarket` as of 2026-04-01.
- Aiken Workbench MySQL probing completed (read-only): `Lots` table has no AUTO_INCREMENT on `LotID`; `Params` is 352 bytes of ASCII '0'; current max `LotID` is 1177; `Lots_Owners` confirms `AIKEN` (ID=1) as the owner for GRM operations.
- Warp plan created: "Créer le lot Aiken depuis le Formulaire de lancement d'opération".
- Next: branch from `main` and implement the `create_aiken_lot` checkbox feature.

## 2026-04-01 — Créer le lot Aiken + erasure fix (session 8, feature complete)
- `create_aiken_lot` Boolean field on `project.task`; checkbox in Formulaire de lancement d'opération.
- `gr.erasure.service.create_lot()`: transactional INSERT (duplicate check + MAX(LotID)+1 + Params=352×'0').
- Non-blocking hook in `project.task.create()`: MySQL failure → `_logger.error` + `bus.bus` yellow sticky warning toast; task always created.
- `action_create_and_open()`: "Créer et aller à la tâche" navigates to full task form after save.
- Custom footer: Créer et aller à la tâche (primary) / Créer (save) / Annuler (cancel).
- Erasure cert error message fixed: `UserError` from `fetch_for_lot` now passes through; only unexpected errors show generic "Could not connect" message.
- Live-validated: lot MOR601 created in Aiken, navigation works, correct error on cert with no erasures.
- 36/36 tests passing. Branch feat/aiken-lot-creation merged to main.

## 2026-04-01 — CT 200 deployment on Proxmox (session 8, deployment)
- Proxmox host vms1 (192.168.21.20) probed: 32 cores, 62 GB RAM, 5.3 TB LVM thin pool, Ubuntu 24.04 on host.
- SSH key (ed25519) generated on Windows and deployed to Proxmox host and CT 200. `odoo-grm` added to ~/.ssh/config.
- CT 200 created: Ubuntu 22.04, 4 cores, 4 GB RAM, 60 GB disk, IP 192.168.21.200, hostname odoo-grm.
- Full Odoo 17 Enterprise stack installed: PostgreSQL 16, Python 3.10 venv, wkhtmltopdf 0.12.6, nginx, gevent, psycopg2, all Odoo/GRM requirements.
- Community source cloned to /opt/odoo/addons_src. Enterprise (462 MB) transferred via scp. OCA/EBICS modules cloned.
- GRM modules cloned from GitHub: gr_project_inventory, grm_website, grm_documents_project at /opt/odoo/grm_repo/modules.
- Database restored: plain SQL dump streamed from local PG17 to CT 200 PG16. Encoding bug fixed (SQL_ASCII → UTF-8): locale-gen fr_FR.UTF-8, recreated DB, re-imported.
- Filestore copied from local odoo_data/filestore/greenremarket to CT 200 /opt/odoo/data/filestore/.
- Module upgrade (gr_project_inventory) applied on CT 200 to pick up create_aiken_lot and all recent changes.
- Systemd service: /etc/systemd/system/odoo.service, enabled, auto-restarts. Correct Aiken MySQL credentials in Environment.
- nginx HTTPS: self-signed cert (real Let's Encrypt pending router port-forward). HTTP redirects to HTTPS. Longpolling + WebSocket config.
- odoo.conf: proxy_mode=True, workers=4, db_name=greenremarket, dbfilter=^greenremarket$, list_db=False.
- Odoo responds HTTP/HTTPS 200. Accents rendering correctly after UTF-8 fix.
- Pending before go-live: router NAT, certbot real cert, --init grm_website+grm_documents_project, EBICS bank account BBAN fix, DNS cutover, Proxmox snapshot.

## 2026-04-01 — CT 200 deployment fixes (session 9)
- Charset bug root cause: previous deployment used SSH pipe (pg_dump | ssh psql) which mangled UTF-8 bytes in transit. Local data was always clean.
- Fix: pg_dump -Fc on local PG17 → scp dump to server → pg_restore natively on server. No pipe, no encoding loss.
- PostgreSQL 16 removed from CT 200; PostgreSQL 17 installed and configured on port 5432. pg_restore version now matches dump format (1.16).
- DB re-restored cleanly: octet_length != char_length confirmed for accented chars (e.g. données: octet=30, char=29).
- All 4 GRM modules redeployed via scp: gr_project_inventory, grm_website, grm_documents_project, gr_portal (new module added from feature/portal-login-revamp).
- Let's Encrypt cert obtained via DNS challenge for sartrouville.greenremarket.fr + go.greenremarket.fr (valid 2026-06-30). nginx updated to use real cert.
- Filestore synced from local odoo_data/filestore/greenremarket to /opt/odoo/data/filestore/greenremarket.
- Odoo restarted and confirmed active.
- Remaining go-live blockers: router NAT (80/443 → 192.168.21.200), EBICS bank account BBAN fix, DNS cutover, Proxmox snapshot.

## 2026-04-01 — CT 200 gr_portal deploy + pre-existing gevent issue (session 10, late)
- `scp -r modules/gr_portal/ odoo-grm:/opt/odoo/grm_repo/modules/` — all files transferred OK (new logo, portal.js, portal_templates.xml, controllers).
- `--update gr_portal` ran on CT 200 with no template or code errors.
- Odoo will not restart: `pkg_resources.DistributionNotFound: The 'zope.interface' distribution was not found`.
- This is a **pre-existing venv issue**, not caused by gr_portal. Odoo was running continuously since session 9 without restart — issue was masked.
- Debugging steps taken:
  - Confirmed `import zope.interface` and `import gevent` both work fine
  - `zope_interface-8.2.dist-info` exists with valid METADATA
  - Error originates from `gevent 21.12.0` entry_point loading: `plugin.load()` calls `pkg_resources.require(['zope.interface'])` and the working_set can't resolve it
  - setuptools upgraded 59.6.0 → 82.0.1 (broke pkg_resources entirely) → downgraded to 70.3.0
  - `pip install zope` run during debug — added full Zope 6.0 ecosystem (side effect, should be cleaned up)
  - gevent 21.12.0 has no version pin on zope packages (just `Requires-Dist: zope.interface`)
  - `import gevent` → clean exit 0
- CT 200 current venv: setuptools=70.3.0, gevent=21.12.0, greenlet=1.1.2, zope.interface=8.2
- Odoo service is stopped on CT 200. gr_portal code IS deployed. Need to fix venv to restart.
- Next: try `pip install 'zope.interface==5.5.2' 'zope.event==4.5.0'` or reinstall venv from requirements.txt

## 2026-04-01 — gr_portal visual refresh from Lovable (session 10)
- Reviewed Lovable prototype repo `moradigmir/remix-of-green-remarket-portal-refresh` (private).
- Identified and applied visual changes: GR logo in loader + hero, collage right column removed,
  layout centered (col-lg-6 col-xl-5), `fa-chevron-right` CTA icon (avoids `grm_website` SVG override).
- Full `portal.css` rewrite: glassmorphism form card, fixed video to `position:fixed`,
  defensive CSS-grid bleed suppression, `!important` overrides for grm_website link bleed-in
  (font-weight, text-decoration), submit button `min-width:0` reset, `bg-greenrm` utility class.
- `login.js` replaced: jQuery fadeIn/fadeOut transitions, `readyState >= 4` loader check, proper `destroy()`.
- New `portal.js` (Odoo 17 `@odoo-module`): staggered fade-in on portal tile cards.
- New `portal_templates.xml`: welcome banner injected before `grm_website.portal_my_home_custom`
  (NOT `portal.portal_my_home` — grm_website overrides the /my route directly).
- `__manifest__.py`: version 17.0.1.1.0, added `portal` dep, `portal_templates.xml`, `portal.js`.
- `GR-Logo-2026-RVB.png` (55 KB) downloaded via `gh api` + PowerShell base64 decode (repo is private).
- Lovable errors caught and fixed: wrong `inherit_id`, `dashboard_metrics` undefined variable,
  `portal_my_home_community` broken XPath, `portal_my_orders` missing `sale` dep,
  Tailwind classes → Bootstrap 5, FA5/FA6 icons → FA4, `assets.xml` old-style loading dropped,
  `portal.js` `odoo.define` → `@odoo-module`.
- Branch: `feat/gr-portal-login-cleanup` (6 commits). Smoke-tested visually on local DB. Merged to `main`.

### Bug fixes found during smoke-test (same session):
- **Loader never hid** (`login.js`): `this.$('.o_login_loader')` scoped to `.o_login_page` but loader div is a
  sibling of the section (outside it). Fixed to `$('#gr_login_loader')` and `$('video.o_login_video_bg')`
  using document-level jQuery so elements outside the widget root are found.
- **Hero blocks reset_password/signup** (`login_templates.xml`): Hero and back link now wrapped in
  `<t t-if="is_login">` where `is_login = 'reset_password' not in path and 'signup' not in path`.
  Form container gets `display:none` only on `/web/login`; visible immediately on other auth pages.
- **`/` showed grm_website landing** (`controllers/main.py` — new file):
  Added `GRPortalHome` controller overriding `GET /` with `website=True`:
    - Unauthenticated → `/web/login`
    - Portal user → `/my`
    - Internal user → `/web` (NOT `/odoo` — that URL falls through to website 404 catch-all)
  Added `GRPortalLogin(WebHome)` overriding `_login_redirect`:
    - Portal users land on `/my` after login (not `/` which would loop)
    - Internal users get standard backend redirect
    - Explicit `?redirect=` always honoured
  `is_user_internal` imported with `try/except` fallback for older 17.0 builds.

## 2026-04-01 -- Savepoint 6, portal login revamp, report + Aiken fixes (session 8)
- New module `gr_portal` added on branch `feature/portal-login-revamp`:
  video-background login page with hero section, image collage, pill-form inputs,
  page loader. Inherits `grm_website.template_login_inherit` (priority 100).
  Installed on `greenremarket`.
- Report logo fixes committed: logo added to audit_report_xlsx, x/y_scale corrected
  from 1.0 to 0.091 in discrepancy and internal inventory reports.
- `ir_config_parameter.xml`: Aiken Workbench defaults (host/port/user) now set on
  module install instead of being left blank.
- `fetch_audit_for_lot` bug fixed: `Created.strftime()` crash when MySQL returns
  non-datetime type silently skipped all rows, producing empty result. Fixed with
  `hasattr(val, 'strftime')` guard. `u.Manufacturer` added to GROUP BY (was
  missing, would fail MySQL strict mode).
- `fetch_for_lot` and `fetch_audit_for_lot`: improved empty-lot error messages.
  Both now distinguish `lot not found` from `lot exists but has no units`, with
  French user-facing messages.
- Savepoint 6 created: `dumps/savepoint_6_portal_login_aiken_fixes_20260401.dump`
  (13.7 MB). `greenremarket_backup` restored from savepoint 6. Filestore synced
  (2299 files each). Old backup filestore archived as
  `odoo_data/filestore/greenremarket_backup_pre_sp6`.
- DB safety rule clarified in `doc/CURRENT_STATE.md`: never run --init/--update
  on `greenremarket_backup`; it is the clean fallback only.