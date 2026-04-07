# NEXT ACTIONS
Status: active
Last verified: 2026-04-07

## Operating priorities
1. Keep `greenremarket_backup` in sync with active before any risky work (standby exists and is current as of 2026-03-31).
2. Keep the matching filestore pair aligned with any DB refresh or swap.
3. Preserve access to the `enterprise` companion repository.

## Product and code backlog
### Open
- **[CRITIQUE] Fix documents task folder + test Playwright** :
  Cause : stubs `documents_document.py` / `documents_folder.py` vides + `search_panel_select_range` manquant → panneau gauche Documents ne filtre pas sur le dossier de la tâche.
  Symptome : documents visibles uniquement dans "Espace de travail > Tous", tags PJ inaccessibles dans le bon contexte.
  Statut : **FERMÉ**
  - Correctif module livré en prod (`gr_project_inventory` v17.0.4.1.0)
  - CT202 validé par test Playwright réel : pièce jointe chatter → Documents → tags UI `PJ > Livrable` + `PJ > Inventaire` → portail client → téléchargement inventaire
  - CT201 validé fonctionnellement sur tâche 599 (CICLAD) : `documents_folder_id` initialisé par l'action Documents (`General / CICLAD`)
- **[CRITIQUE] Cron backup quotidien CT201** : script `backup_to_cloud.sh` prêt et testé. Planifier `0 3 * * *` via `crontab -e` sur CT201.
- **[INFRA] Cron snapshot Proxmox quotidien** : planifier sur vms1 `pct snapshot 201 daily-$(date +%Y%m%d)` chaque nuit, conserver 7 snapshots.
- **Tag PD3E automatique sur les opérations créées via le formulaire** : les opérations créées via le Formulaire de lancement d'opération doivent automatiquement recevoir le tag PD3E si ce n'est pas déjà le cas. Fix: dans `gr_project_inventory`, surcharger `create()` ou ajouter le tag dans le contexte du formulaire.
- **Vidéo login/signup** : vidéo fond 30 MB → réencoder H264 ~1.5 Mbps cible <4 MB, remplacer dans `gr_portal/static/src/img/`. Commande : `ffmpeg -i input.mp4 -c:v libx264 -b:v 1500k -an output.mp4`.
- **Boîte test IONOS factures fournisseurs** : provisionner `factures-fournisseurs-test@greenremarket.fr` pour que Matéo teste l'intégration email-→-compta sur CT202 sans toucher la prod.
- **CT200 — standby froid** : CT200 (192.168.21.200) reste en standby. Ne pas désinstaller — rollback possible via remise du NAT Keyyo sur .200.
- **Statement gap 2025-06-21 to 2026-03-04**: confirmé non-disponible via EBICS (code 90005). Import manuel depuis CIC en ligne — à traiter par l'équipe comptable.
- **Warning pile (non-critical, clean up when time allows)**:
  - `pkg_resources` deprecated API from `fintech`
  - `active_id`/`active_ids`/`active_model` in ir_ui_view expressions deprecated in Odoo 17
  - `gr_project_inventory` models not overriding `create` in batch (ORM performance hint)
  - `@route()` decorator warnings in `grm_website`

### Deferred (planned, not started)
- Cross-machine kickstart and containerization/swarm roadmap is approved as a future initiative:
  - machine-agnostic local bootstrap on Windows/Linux via Docker Compose
  - agent directive kickstart flow for deterministic startup in Warp/Windsurf
  - swarm-target architecture with scalable Odoo, PostgreSQL persistent storage, Nginx reverse proxy, and cache service
- When promoted from deferred to active, create a dedicated feature branch from `main`, implement in phases, validate, and merge back per the branching model.

### Pending review
- Client form bug (item 5c): pending live confirmation from user on test server.
- `test_date_field.py`: all tests skipped (`@unittest.skip`) — placeholder stubs with empty field names from a cherry-pick. Either rewrite against `planned_date_begin` or delete.

### Confirmed closed
- **CT201 mise en production** (2026-04-07) : CT201 = prod, CT200 = standby froid, NAT Keyyo commuté sur .201. Playwright 123/123 OK. Snapshot post-golive pris.
- **EBICS automatisation complète** (2026-04-06) : `ebics_daily.py` + `ebics_watchdog.py` actifs sur CT201, catch-up effectué, runbook EBICS.md créé.
- **EBICS catch-up 2026-03-28→J-2** : effectué, relevés importés, solde vérifié.
- **grm_documents_project absorbé** dans gr_project_inventory v17.0.4.0.0 via migration + pre/post scripts. Module marqué uninstalled.
- odoo_sartrouville deployment probe: completed 2026-04-01. Cible de déploiement finale = CT201 (pas CT200).
- Cr�er le lot Aiken depuis le Formulaire de lancement d'op�ration: implemented and live-validated (2026-04-01). `create_aiken_lot` checkbox on creation form calls `gr.erasure.service.create_lot()` synchronously; non-blocking on Aiken failure (yellow toast + logger.error). ``Cr�er et aller � la t�che`` navigation button added. Erasure cert misleading error message fixed (UserError now passes through). 36/36 tests passing. Merged to `main` 2026-04-01.
- P1.8 logo sizing is closed and should not be reopened without a new explicit request.
- Lot name length limit is implemented and tested (6-character constraint with validation).
- EBICS bank keys obtained (HPB called 2026-03-31, `#BANK` section written, FDL download confirmed).
- Open Banking cron jobs disabled (IDs 38, 39, 40, 41 on both DBs) — were crashing every 5 minutes.
- Project Inventory menu reverted to under Project app (removed incorrect standalone app behaviour).
- CI workflow fixed for `modules/` refactor — was broken since repo structure change.
- `views_simple.xml` re-enabled with tree-only change: optional `planned_date_begin` column in task list. Form view override was reverted (placed field inside date flex div causing layout corruption). `project_enterprise` added to module depends.
- `odoo_icecat_connector` state is already `uninstalled` in DB — no action needed.
- Duplication performance indexes added to `gr_internal_inventory` (task_id, client_inventory_id, created_at) and `gr_client_inventory` (task_id). Both DBs upgraded.
- `test_date_field.py` skipped via `@unittest.skip` — tests are broken placeholders from cherry-pick.
- "Reconnecter la banque" button removed: `bank_statements_source` set to `undefined`, Online Banking link cleared on both DBs.
- Startup command updated with `--max-cron-threads=0`.
- `lot_name` generation priority fixed: `client_destination_name` → `order_giver_id` → `partner_id` → `UNK`. Tests updated, 25/25 passing.
- `lot_name` layout fixed in task form: moved to its own row outside the date flex div.
- `views_simple.xml` form override reverted: `planned_date_begin` stays invisible in form (enterprise daterange widget handles it). Tree column kept.
- Creation form date field fixed: `planned_date_begin` (start date) replaces `date_deadline` in "Formulaire de lancement d'opération".
- EBICS fully resolved via Odoo shell scripts (`scripts/`). `sanitized_acc_number` was the real missing fix (SQL update of `acc_number` does not trigger stored field recompute). 16 statements imported for 2026-03-05 to 2026-03-27. Historical gap (2025-06-21 to 2026-03-04) confirmed unavailable via EBICS (code 90005). Account `00021148806` still needs investigation.
- Shell scripts archived in `scripts/` for reuse.
- Portal fixes: home follower domain, task_documents template, access token on Delivrable tag, fetch+blob download.
- Binary zip corruption fixed: isinstance(data, (str, bytes)) � Odoo ORM returns base64 as bytes not str.
- `planned_date_begin` persistence fixed and live-validated: creation form collects `date_deadline`; `create()` syncs to `planned_date_begin`. Task form shows "Planned Date" range. 28/28 tests passing.
- Ctrl-C now stops the server cleanly on Windows via `--dev=reload` (werkzeug reloader). Live-validated.
- Duplication performance (item 5a): indexes live on both DBs. Closed — reopen only if lag reappears in production.
- Client form bug (item 5c): closed by user validation.

## Resume guidance
- For short prompts such as `resume work on this project`, do not implement immediately.
- First run a live environment readiness probe and report `OPERATIONAL` or `NON-OPERATIONAL` with missing prerequisites.
- If status is `NON-OPERATIONAL`, stop at environment bootstrap/recovery guidance; do not recommend or begin feature implementation.
- Then summarize the operating model, validated state, active backlog, recommended next action, and what must not be touched.
- If a task changes the database or requires rollout-style validation, use the standby workflow from `doc/CURRENT_STATE.md` and `doc/RUNBOOKS/BACKUP_AND_SWAP.md`.







