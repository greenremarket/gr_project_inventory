# NEXT ACTIONS
Status: active
Last verified: 2026-04-08 (Phase 0 discovery audit)

## Operating priorities
1. Keep `greenremarket_backup` in sync with active before any risky work (standby exists and is current as of 2026-03-31).
2. Keep the matching filestore pair aligned with any DB refresh or swap.
3. Preserve access to the `enterprise` companion repository.

## Phase 0 — Reproducible environment (containerisation)
**Discovery audit COMPLETED 2026-04-08** — see `audit_outputs/phase0_discovery_20260408_1410/PHASE0_DISCOVERY_REPORT.md`

### Phase 0 blockers (must resolve before implementation can start)
- **[P0-CRITICAL] CT202 has no staging identity** — identical DB/filestore/nginx hostnames as CT201. Must assign distinct hostname (test.greenremarket.fr), separate dbfilter, and reset DB before CT202 is safe for test use.
- **[P0-CRITICAL] All 3 environments have dirty git trees** — no clean baseline commit to build a reproducible image from.
- **[P0-HIGH] Enterprise Git token undocumented** — CI/automated builds cannot clone enterprise without a stored secret.
- **[P0-HIGH] awbc_db (192.168.21.206) host unaudited** — need HA/backup story, availability SLA, and confirmation it is reachable from the target container network.
- **[P0-HIGH] EBICS key import procedure undocumented** — any fresh deployment will fail EBICS without a documented key onboarding runbook.
- **[P0-MEDIUM] OCA repos unpinned** — add commit SHA pins for all 5 third_party repos.
- **[P0-MEDIUM] gevent missing from local venv** — cannot run Odoo in multi-worker mode locally.
- **[P0-MEDIUM] psql not in Windows PATH** — `C:\Program Files\PostgreSQL\17\bin` must be added.
- **[P0-MEDIUM] MySQL latin1 encoding** — PyMySQL connection config must set `charset=latin1` / decode with care for French text in awbc_db.

---

## Product and code backlog
### Open
- **[URGENT] Renouvellement licence Odoo Enterprise avant le 19 juin 2026** : code M240531148400622, expiration 2026-06-19, reason=renewal. Bannière de renouvellement visible dans l'UI. Renouveler sur odoo.com avant cette date pour éviter le blocage backend.
- **[CRITIQUE] Fix documents task folder + test Playwright** :
  Cause : stubs `documents_document.py` / `documents_folder.py` vides + `search_panel_select_range` manquant â†’ panneau gauche Documents ne filtre pas sur le dossier de la tÃ¢che.
  Symptome : documents visibles uniquement dans "Espace de travail > Tous", tags PJ inaccessibles dans le bon contexte.
  Statut : **FERMÃ‰**
  - Correctif module livrÃ© en prod (`gr_project_inventory` v17.0.4.1.0)
  - CT202 validÃ© par test Playwright rÃ©el : piÃ¨ce jointe chatter â†’ Documents â†’ tags UI `PJ > Livrable` + `PJ > Inventaire` â†’ portail client â†’ tÃ©lÃ©chargement inventaire
  - CT201 validÃ© fonctionnellement sur tÃ¢che 599 (CICLAD) : `documents_folder_id` initialisÃ© par l'action Documents (`General / CICLAD`)
- **[CRITIQUE] Cron backup quotidien CT201** : script `backup_to_cloud.sh` prÃªt et testÃ©. Planifier `0 3 * * *` via `crontab -e` sur CT201.
- **[INFRA] Cron snapshot Proxmox quotidien** : planifier sur vms1 `pct snapshot 201 daily-$(date +%Y%m%d)` chaque nuit, conserver 7 snapshots.
- **Tag PD3E automatique sur les opÃ©rations crÃ©Ã©es via le formulaire** : les opÃ©rations crÃ©Ã©es via le Formulaire de lancement d'opÃ©ration doivent automatiquement recevoir le tag PD3E si ce n'est pas dÃ©jÃ  le cas. Fix: dans `gr_project_inventory`, surcharger `create()` ou ajouter le tag dans le contexte du formulaire.
- **VidÃ©o login/signup** : vidÃ©o fond 30 MB â†’ rÃ©encoder H264 ~1.5 Mbps cible <4 MB, remplacer dans `gr_portal/static/src/img/`. Commande : `ffmpeg -i input.mp4 -c:v libx264 -b:v 1500k -an output.mp4`.
- **BoÃ®te test IONOS factures fournisseurs** : provisionner `factures-fournisseurs-test@greenremarket.fr` pour que MatÃ©o teste l'intÃ©gration email-â†’-compta sur CT202 sans toucher la prod.
- **CT200 â€” standby froid** : CT200 (192.168.21.200) reste en standby. Ne pas dÃ©sinstaller â€” rollback possible via remise du NAT Keyyo sur .200.
- **Statement gap 2025-06-21 to 2026-03-04**: confirmÃ© non-disponible via EBICS (code 90005). Import manuel depuis CIC en ligne â€” Ã  traiter par l'Ã©quipe comptable.
- **Warning pile (non-critical, clean up when time allows)**:
  - `pkg_resources` deprecated API from `fintech`
  - `active_id`/`active_ids`/`active_model` in ir_ui_view expressions deprecated in Odoo 17
  - `gr_project_inventory` models not overriding `create` in batch (ORM performance hint)
  - `@route()` decorator warnings in `grm_website`

### Deferred (planned, not started)
- Phase 0 implementation (Docker Compose + CI/CD) — promoted from deferred to **active planning**. Discovery audit done. Resolve Phase 0 blockers above before implementation begins.
  - machine-agnostic local bootstrap on Windows/Linux via Docker Compose
  - agent directive kickstart flow for deterministic startup in Warp/Windsurf
  - swarm-target architecture with scalable Odoo, PostgreSQL persistent storage, Nginx reverse proxy, and cache service
- When ready to implement, create a dedicated feature branch from `main`.

### Pending review
- Client form bug (item 5c): pending live confirmation from user on test server.
- `test_date_field.py`: all tests skipped (`@unittest.skip`) â€” placeholder stubs with empty field names from a cherry-pick. Either rewrite against `planned_date_begin` or delete.

### Confirmed closed
- **CT201 mise en production** (2026-04-07) : CT201 = prod, CT200 = standby froid, NAT Keyyo commutÃ© sur .201. Playwright 123/123 OK. Snapshot post-golive pris.
- **EBICS automatisation complÃ¨te** (2026-04-06) : `ebics_daily.py` + `ebics_watchdog.py` actifs sur CT201, catch-up effectuÃ©, runbook EBICS.md crÃ©Ã©.
- **EBICS catch-up 2026-03-28â†’J-2** : effectuÃ©, relevÃ©s importÃ©s, solde vÃ©rifiÃ©.
- **grm_documents_project absorbÃ©** dans gr_project_inventory v17.0.4.0.0 via migration + pre/post scripts. Module marquÃ© uninstalled.
- odoo_sartrouville deployment probe: completed 2026-04-01. Cible de dÃ©ploiement finale = CT201 (pas CT200).
- Crï¿½er le lot Aiken depuis le Formulaire de lancement d'opï¿½ration: implemented and live-validated (2026-04-01). `create_aiken_lot` checkbox on creation form calls `gr.erasure.service.create_lot()` synchronously; non-blocking on Aiken failure (yellow toast + logger.error). ``Crï¿½er et aller ï¿½ la tï¿½che`` navigation button added. Erasure cert misleading error message fixed (UserError now passes through). 36/36 tests passing. Merged to `main` 2026-04-01.
- P1.8 logo sizing is closed and should not be reopened without a new explicit request.
- Lot name length limit is implemented and tested (6-character constraint with validation).
- EBICS bank keys obtained (HPB called 2026-03-31, `#BANK` section written, FDL download confirmed).
- Open Banking cron jobs disabled (IDs 38, 39, 40, 41 on both DBs) â€” were crashing every 5 minutes.
- Project Inventory menu reverted to under Project app (removed incorrect standalone app behaviour).
- CI workflow fixed for `modules/` refactor â€” was broken since repo structure change.
- `views_simple.xml` re-enabled with tree-only change: optional `planned_date_begin` column in task list. Form view override was reverted (placed field inside date flex div causing layout corruption). `project_enterprise` added to module depends.
- `odoo_icecat_connector` state is already `uninstalled` in DB â€” no action needed.
- Duplication performance indexes added to `gr_internal_inventory` (task_id, client_inventory_id, created_at) and `gr_client_inventory` (task_id). Both DBs upgraded.
- `test_date_field.py` skipped via `@unittest.skip` â€” tests are broken placeholders from cherry-pick.
- "Reconnecter la banque" button removed: `bank_statements_source` set to `undefined`, Online Banking link cleared on both DBs.
- Startup command updated with `--max-cron-threads=0`.
- `lot_name` generation priority fixed: `client_destination_name` â†’ `order_giver_id` â†’ `partner_id` â†’ `UNK`. Tests updated, 25/25 passing.
- `lot_name` layout fixed in task form: moved to its own row outside the date flex div.
- `views_simple.xml` form override reverted: `planned_date_begin` stays invisible in form (enterprise daterange widget handles it). Tree column kept.
- Creation form date field fixed: `planned_date_begin` (start date) replaces `date_deadline` in "Formulaire de lancement d'opÃ©ration".
- EBICS fully resolved via Odoo shell scripts (`scripts/`). `sanitized_acc_number` was the real missing fix (SQL update of `acc_number` does not trigger stored field recompute). 16 statements imported for 2026-03-05 to 2026-03-27. Historical gap (2025-06-21 to 2026-03-04) confirmed unavailable via EBICS (code 90005). Account `00021148806` still needs investigation.
- Shell scripts archived in `scripts/` for reuse.
- Portal fixes: home follower domain, task_documents template, access token on Delivrable tag, fetch+blob download.
- Binary zip corruption fixed: isinstance(data, (str, bytes)) ï¿½ Odoo ORM returns base64 as bytes not str.
- `planned_date_begin` persistence fixed and live-validated: creation form collects `date_deadline`; `create()` syncs to `planned_date_begin`. Task form shows "Planned Date" range. 28/28 tests passing.
- Ctrl-C now stops the server cleanly on Windows via `--dev=reload` (werkzeug reloader). Live-validated.
- Duplication performance (item 5a): indexes live on both DBs. Closed â€” reopen only if lag reappears in production.
- Client form bug (item 5c): closed by user validation.

## Resume guidance
- For short prompts such as `resume work on this project`, do not implement immediately.
- First run a live environment readiness probe and report `OPERATIONAL` or `NON-OPERATIONAL` with missing prerequisites.
- If status is `NON-OPERATIONAL`, stop at environment bootstrap/recovery guidance; do not recommend or begin feature implementation.
- Then summarize the operating model, validated state, active backlog, recommended next action, and what must not be touched.
- If a task changes the database or requires rollout-style validation, use the standby workflow from `doc/CURRENT_STATE.md` and `doc/RUNBOOKS/BACKUP_AND_SWAP.md`.








