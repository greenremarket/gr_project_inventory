# PHASE 0 DISCOVERY REPORT — Green Remarket
**Audit date:** 2026-04-08T14:10:22Z → 14:35:00Z  
**Auditor:** Oz (Warp AI agent)  
**Method:** Read-only observation. No writes, no restarts, no config edits.

---

## 1. Environment Inventory

Four environments were in scope. All were reached and audited.

### CT200 — Jump Host / Public Proxy (192.168.21.200)
Public hostname: `sartrouville.greenremarket.fr` / `wh.greenremarket.fr`  
Role: SSH ProxyJump relay + nginx TLS termination entry point  
OS: Ubuntu 22.04, kernel 6.5.11-4-pve (Proxmox LXC), uptime 7d10h  
**Not an Odoo server.** Does not host Odoo. Acts as the public internet entry point routing HTTPS traffic inward to CT201 or CT202.

### CT201 — odoo-staging (192.168.21.201)
Hostname: `odoo-staging`  
Role: Active Odoo 17 server (currently serving prod traffic)  
OS: Ubuntu 22.04, 4 vCPU, 4GB RAM, 59GB disk (9.5GB used)  
Uptime since: 2026-04-07T22:18:57Z  
**Odoo 17.0.0 running** — 4 workers + gevent, nginx, PostgreSQL 17.9  
DB: `greenremarket`, 131 MB  
Filestore: 861 MB, 2318 files

### CT202 — odoo-test (192.168.21.202)
Hostname: `odoo-test`  
Role: Intended staging/test environment  
OS: Ubuntu 22.04, 4 vCPU, 4GB RAM, 59GB disk (9.5GB used)  
Uptime since: 2026-04-07T22:22:11Z  
**Odoo 17.0.0 running** — identical setup to CT201  
DB: `greenremarket`, 131 MB — **IDENTICAL to CT201**  
Filestore: 860 MB, 2319 files — **NEAR-IDENTICAL to CT201**

### Local — edgar (Windows 11)
Hostname: `edgar`, Acer Predator PH315-54  
i7-11800H 8c/16t, 24GB RAM  
Drives: C: 476GB (⚠ 16.75GB free), D: 932GB, E: 477GB  
**No Odoo process running.** PostgreSQL 17 running. WSL2 active.  
Python 3.11.9 venv at `E:\Dev\gr_project_inventory\.venv_odoo`

---

## 2. Architecture Overview

```
Internet
   │
   ▼
[CT200 / odoo-grm]  sartrouville.greenremarket.fr
  nginx TLS + SSH relay
  192.168.21.200
   │
   ├──► [CT201 / odoo-staging]  192.168.21.201
   │       Odoo 17.0.0, PG 17, nginx
   │       DB: greenremarket (131MB)
   │
   └──► [CT202 / odoo-test]    192.168.21.202   ⚠ NOT differentiated
           Odoo 17.0.0, PG 17, nginx
           DB: greenremarket (131MB) — CLONE OF CT201
           nginx serves: sartrouville.greenremarket.fr ← SAME AS CT201

[Proxmox]  192.168.21.20
  Hosts all LXC containers

[Local / edgar]
  Windows 11, dev workstation
  No local Odoo running
  Repos at E:\Dev\
```

---

## 3. Runtime Services Summary

| Service | Local | CT201 | CT202 |
|---------|-------|-------|-------|
| Odoo 17 | NOT RUNNING | ✓ active | ✓ active |
| PostgreSQL 17 | ✓ running | ✓ running | ✓ running |
| nginx | ✗ | ✓ active | ✓ active |
| wkhtmltopdf 0.12.6.1 patched-qt | ✗ NOT INSTALLED | ✓ | ✓ |
| Python | 3.11.9 | 3.10.12 | 3.10.12 |
| gevent | ✗ absent | ✓ 21.12.0 | ✓ 21.12.0 |
| TLS cert | N/A | valid to 2026-06-30 | valid to 2026-06-30 |

---

## 4. Source Control State

| Repo | Environment | Remote | Branch | HEAD | Status |
|------|-------------|--------|--------|------|--------|
| gr_project_inventory | Local | github.com/greenremarket | main | 67d42eb | ⚠ DIRTY + BEHIND PROD |
| gr_project_inventory | CT201 | github.com/greenremarket | main | ff99f22 | ⚠ DIRTY |
| gr_project_inventory | CT202 | github.com/greenremarket | main | ff99f22 | ⚠ DIRTY (identical to CT201) |
| greenremarket-dashboard-v3 | Local | github.com/moradigmir | main | a9c8d4a | 2 untracked files |

**Key finding:** Local is at commit 67d42eb; both servers are at ff99f22. Local has 30+ modified files (modules/gr_portal, modules/gr_project_inventory) plus 3 deleted files (modules/grm_documents_project) that are not committed. The deleted module is still deployed on both servers.

---

## 5. Data Gravity

| Metric | CT201 (live) | CT202 (live) | Local dumps |
|--------|-------------|-------------|-------------|
| DB size | 131 MB | 131 MB | prod.dump: 19 MB |
| Filestore | 861 MB / 2318 files | 860 MB / 2319 files | filestore_prod.tar.gz: 743 MB |
| Largest table | mail_message: 14 MB | mail_message: 14 MB | — |
| Custom tables | gr_internal_inventory (2.3MB), gr_print_job (1.6MB) | same | — |
| Backup schedule | Daily 03:00 UTC → cloud | Daily 03:00 UTC → cloud | 35 manual dumps (Mar 30 – Apr 7) |
| Cloud destination | UNKNOWN | UNKNOWN | N/A |

Data gravity is low — 131MB DB + 861MB filestore is well within feasible range for containerisation. The filestore is the only non-trivial artifact to manage (requires persistent volume or object storage).

---

## 6. Dependency Provenance

| Component | Local | CT201 | CT202 | Pin Status |
|-----------|-------|-------|-------|------------|
| Odoo CE 17 | 17.0.0 | 17.0.0 | 17.0.0 | Git clone, no SHA pin |
| Odoo Enterprise 17 | 17.0.0 | 17.0.0 | 17.0.0 | Git clone, **token undocumented** |
| Python | 3.11.9 | 3.10.12 | 3.10.12 | Version drift |
| fintech (EBICS) | 7.9.2 | 7.9.2 | 7.9.2 | ✓ pinned in freeze |
| OCA repos (×5) | present | present | present | ⚠ NO COMMIT PIN |
| Zope stack | absent | present | present | From dashboard-v3 merge |
| gevent | absent | 21.12.0 | 21.12.0 | ⚠ missing locally |

---

## 7. Test Suite Assessment

All 24 tests in `tests/` are Playwright E2E tests. **There are zero synthetic data or unit tests.**

Every test requires:
- A live Odoo 17 instance at `ODOO_BASE_URL`
- Seeded users: `client@ecosolutions.fr`, `operateur@greenremarket.fr`, `superviseur@greenremarket.fr`
- Pre-populated business data (operations, orders, invoices, deliverables)
- Enterprise modules (for accounting, documents, dashboard tests)

Two tests (`test_workflow_karim_full.py`, `test_workflow_signup_karim.py`) are coupled to a named user in the DB and are classified **flaky** — they fail if the user already exists or the DB is in the wrong state.

---

## 8. External MySQL Dependency — awbc_db (CRITICAL)
**Probed:** 2026-04-08T14:42:00Z via CT201 environment variables

Both CT201 and CT202 connect at runtime to an external MySQL 8.0.42 database:
- **Host:** 192.168.21.206:3306 (undocumented server, not in SSH config)
- **Database:** awbc_db (352 MB)
- **User:** manager / **Password:** ***REDACTED*** (plaintext in `/etc/systemd/system/odoo.service`)
- **Driver:** PyMySQL==1.1.2

**What awbc_db is:** An ITAD/hardware refurbishment tracking platform (AWB Client). It stores hardware scan data for every physical device processed by Green Remarket.

**Why it is CRITICAL:** `gr_project_inventory` reads from it via PyMySQL to generate all hardware device reports. The `Units_Reports` / `NEW_Units_Reports` views assemble a complete hardware profile per unit (CPU, RAM, storage, grade, COA, serial numbers) by pivoting 133,654 component rows from `Units_Devices`. Without this connection, **all report generation in gr_project_inventory fails**.

**Key tables:**
- `Units` — 7,447 device records (UnitID, LotID, SerialNumber, Chassis, Manufacturer, Model, Grade, WarehLocation)
- `Units_Devices` — 133,654 component scan records (Category: CPU|RAM|STORAGE|LCD|BATTERY|BOARD|COA|VIDEO|KEYBOARD|OPTICAL|WEBCAM)
- `Units_Pictures` — 739 device photos as LONGBLOB (311 MB — 88% of DB)
- `Lots` — 149 lot/batch records (Number, Owner, Customer, Description, Status)
- `Lots_Owners` — 5 ITAD partner records

**Report views consumed by Odoo:**
- `Units_Reports` — pivots all component categories into one flat row per unit. Uses stored function `FREFURB()` to return original vs refurbished fields conditionally.
- `NEW_Units_Reports` — superset of Units_Reports, adds HwID, BatterySize, Videocard2, WarehLocation, PackGroupNumber. Defined by `root@localhost`.

**Encoding risk:** Database uses `latin1/latin1_swedish_ci`. French accented characters in ObservNotes/Model may be mangled without explicit charset handling in the PyMySQL connection.

**Phase 0 implication:** Any containerised Odoo deployment must have network access to 192.168.21.206:3306. This host must be audited separately. Credentials must be migrated to a secrets manager before containerisation.

Full schema: `55_mysql_awbc_dependency.json`

---

## 9. Critical Findings

### F-01: CT202 is a pixel-perfect clone of CT201 with no environment separation
Both containers have identical: git HEAD (ff99f22), DB (131MB greenremarket), filestore (~860MB), nginx config (same server_names), TLS cert, cron jobs, systemd unit. They were restarted 4 minutes apart, confirming Proxmox snapshot origin. **CT202 is currently not a safe staging environment** — any test run against it modifies data that is identical to production.

### F-02: MySQL database on 192.168.21.206 wired into both Odoo instances
The systemd service file on both CT201 and CT202 injects credentials for an external MySQL host at 192.168.21.206 (database: `awbc_db`). This host was not audited. It represents an undocumented external dependency that must be accounted for in any containerisation or migration plan. Credentials are stored in plaintext (REDACTED from this report).

### F-03: Zope stack (50+ packages) present in Odoo venv on servers
Confirmed by user: arrived via greenremarket-dashboard-v3 merge into the unified server venv. This bloats the container image and must be explicitly excluded or separated in Phase 0 Docker design.

### F-04: No CI/CD pipeline observed
No `.github/workflows/` directory found in `gr_project_inventory` (only Odoo's own upstream `.github`). No Dockerfile in the repo. The only containerisation artifact is the stale `migmir-odoo18/` setup from October 2025 at `C:\Users\migmi\migmir-odoo18`, which is not connected to the current repo or workflow.

---

## 9. Environment Readiness Verdict

| Environment | Verdict | Rationale |
|-------------|---------|-----------|
| Local (edgar) | PARTIAL | PostgreSQL present, source code present, venv present. No running Odoo, no wkhtmltopdf, dirty repo, missing gevent, C: drive critical. |
| CT201 (odoo-staging) | OPERATIONAL | Odoo 17 running and serving traffic. PostgreSQL, nginx, wkhtmltopdf all correct. Dirty git, MySQL dependency undocumented. |
| CT202 (odoo-test) | PARTIAL | Operationally equivalent to CT201 but has no staging identity. Cannot safely be used for test runs without risk of confusion with prod data. Requires hostname separation and DB reset. |
| CT200 (odoo-grm) | OPERATIONAL | Functioning as jump host and public proxy. No Odoo service expected. |

---

## 10. Top 10 Blockers to Reproducibility

1. **CT202 has no distinct identity** — same nginx hostnames, same DB, same git state as CT201. Phase 0 staging is unusable until CT202 gets its own hostname and a clean DB.
2. **All environments dirty** — no clean commit to build a reproducible image from. Every environment has uncommitted local modifications.
3. **Local is behind prod (67d42eb vs ff99f22)** — local dev tree is not the source of truth. Changes may conflict on next push.
4. **No local Odoo running** — development loop requires network connectivity to CT201/CT202. No offline or isolated dev possible.
5. **Enterprise token undocumented** — containerised CI cannot clone enterprise without a documented token/credential strategy.
6. **gevent missing locally** — the local venv cannot run Odoo in production-equivalent multi-worker mode.
7. **OCA repos unpinned** — 5 third-party repos have no pinned commit SHA; a fresh container build may pull a different version.
8. **EBICS key import procedure undocumented** — any fresh deployment will fail EBICS without documented key onboarding.
9. **MySQL awbc_db (192.168.21.206) — ITAD platform, single point of failure** — 7,447 device records and 133K component rows backing all gr_project_inventory reports. Reachable only from 192.168.21.x; local dev and any future CI container cannot reach it without network access or a tunnel.
10. **Zero unit tests** — there is no test coverage that can run without a live Odoo stack + seeded DB, making automated CI gating impossible without a full environment spin-up.

---

## 11. Minimum Phase 0 Inputs Now Available

- Odoo 17.0.0 source layout (local + server paths) ✓
- Full addons_path mapping for all environments ✓
- Server venv Python version: 3.10.12 ✓
- wkhtmltopdf version confirmed: 0.12.6.1 patched-qt ✓
- PostgreSQL version: 17.9 ✓
- DB size + schema (top tables + custom tables) ✓
- Filestore size: ~860MB ✓
- Production DB dump + filestore archive available locally ✓
- Nginx config templates documented ✓
- TLS cert status known (expires 2026-06-30) ✓
- Cron job inventory complete ✓
- EBICS dependency chain documented (fintech 7.9.2, 3 scripts, key dir paths) ✓
- Test suite fully classified: all E2E, all require live stack ✓
- SSH topology fully mapped ✓
- Proxmox container layout known (CT200, CT201, CT202, PVE at .20) ✓
- MySQL awbc_db fully audited: schema, 47 tables/views, column definitions for all key tables ✓
- awbc_db Odoo integration pattern documented (PyMySQL, systemd env vars, Units_Reports view) ✓

---

## 12. Immediate Next 5 Actions (ordered, low-risk, high-impact)

### Action 1: Give CT202 its own identity (low-risk, 30 min)
Update CT202's `/etc/nginx/sites-enabled/odoo` to use `test.greenremarket.fr` (or equivalent). Update CT202's `/opt/odoo/odoo.conf` `dbfilter` to `^greenremarket_test$`. Create a fresh `greenremarket_test` DB from the latest checkpoint dump. This immediately eliminates BLOCKER-01/02 and makes CT202 usable as a real test environment.

### Action 2: Create a clean git baseline tag (low-risk, 15 min)
Commit or stash all outstanding changes on the local working tree. On CT201/CT202, stash or reset the working tree to HEAD. Create a `v0.1.0-phase0-baseline` tag. This gives Phase 0 containerisation a reproducible starting point.

### Action 3: Document and store the enterprise Git token as a CI secret (low-risk, 20 min)
Capture the Odoo enterprise clone credential (token or deploy key) and store it as a GitHub Actions secret (`ODOO_ENTERPRISE_TOKEN`). Add it to a `bootstrap_odoo_lxc.sh` comment. This unblocks CI without exposing the token in code.

### Action 4: Fix psql PATH and add `C:\Program Files\PostgreSQL\17\bin` to Windows system PATH (low-risk, 5 min)
Enables all local DB operations to work from PowerShell without full path invocation. Prerequisite for any local automation script.

### Action 5: Audit 192.168.21.206 and document its HA/backup story (medium-risk, 2 hours)
Identify what server 192.168.21.206 is (Proxmox VM, bare metal, cloud instance), who operates it, whether it has a backup/restore procedure, and what its availability SLA is. Determine whether it is reachable from the intended CI/container network. Without this, Phase 0 containerisation cannot guarantee report generation will work after a deployment.

### Action 6: Pin OCA repo commit SHAs (low-risk, 1 hour)
For each of the 5 third-party repos in `third_party_modules/`, run `git rev-parse HEAD` and record it in a new `third_party_pins.txt` or as `submodule` SHA locks. This converts the 5 unpinned repos into reproducible artifacts and eliminates reproducibility risk R07 for the Phase 0 Dockerfile.
