# Phase 0 Discovery — Execution Log
**Audit started:** 2026-04-08T14:10:22Z  
**Auditor:** Oz (Warp AI agent)  
**Scope:** Local (edgar), CT201 (odoo-staging), CT200 (odoo-grm jump host)

---

## 14:11:01Z — LOCAL: System topology collected
**Commands:**
- `Get-PSDrive -PSProvider FileSystem` → 4 drives (C:476GB/16GB free, D:932GB, E:477GB, G:477GB)
- `Get-WmiObject Win32_OperatingSystem` → Windows 11 Home 10.0.26200
- `Get-WmiObject Win32_Processor` → Intel i7-11800H 2.30GHz, 8 cores
- `Get-TimeZone` → Romance Standard Time (UTC+1)
- `ipconfig /all` → Wi-Fi 192.168.1.91, HyperV 172.19.16.1
- `Get-Service | Where { DisplayName -match postgres|odoo|nginx }` → postgresql-x64-17 RUNNING, WSLService RUNNING
- `Get-Process | Where { Name -match postgres|python|odoo }` → postgres (8 procs), python (1 venv), python3.11 (2 procs), odoo_ls_server (Windsurf ext)

**Outcome:** Full topology collected. C: drive critically low (16.75GB free).

---

## 14:11:30Z — LOCAL: PostgreSQL config
**Commands:**
- `pg_isready -U postgres -h localhost` → `localhost:5432 - accepting connections`
- `Get-Content pg_hba.conf` → all auth scram-sha-256, no trust
- `netstat -ano | findstr LISTENING | findstr :5432` → TCP 0.0.0.0:5432 PID 8780

**Outcome:** PostgreSQL 17 running locally. Auth is scram-sha-256 (password required, not in PATH).

---

## 14:11:45Z — LOCAL: Dev directory structure
**Command:** `Get-ChildItem E:\Dev -Depth 1`
**Outcome:** Found gr_project_inventory (Odoo) and greenremarket-dashboard-v3 (React) repos. Also found dumps/, ebics_keys/, enterprise/, modules/, third_party_modules/, odoo_data/, .venv_odoo, migmir-odoo18/ (stale Docker setup).

---

## 14:12:00Z — LOCAL: Odoo filesystem structure
**Commands:**
- `Get-ChildItem E:\Dev\gr_project_inventory\odoo` → CE source v17.0.0 (odoo/, addons/, setup/)
- `Get-ChildItem E:\Dev\gr_project_inventory\enterprise` → 300+ enterprise modules, cloned 2026-03-31
- `Get-ChildItem E:\Dev\gr_project_inventory\modules` → gr_project_inventory, gr_portal, grm_documents_project, grm_website, plus docs/tests/
- `Get-ChildItem E:\Dev\gr_project_inventory\third_party_modules` → account_ebics_repo, account_reconcile_repo, bank_statement_import_repo, l10n_france_repo, reporting-engine (OCA/Noviat)

**Outcome:** Full Odoo tree documented.

---

## 14:12:15Z — LOCAL: Git provenance
**Commands:**
- `git -C E:\Dev\gr_project_inventory remote -v` → origin=https://github.com/greenremarket/gr_project_inventory.git
- `git -C E:\Dev\gr_project_inventory rev-parse HEAD` → 67d42ebef9d8db84cf41246f5bc334d3fa165eae
- `git -C E:\Dev\gr_project_inventory status --porcelain` → DIRTY: ~30 modified files in modules/gr_portal and modules/gr_project_inventory, 3 deleted files in modules/grm_documents_project
- `git -C E:\Dev\greenremarket-dashboard-v3 remote -v` → origin=https://github.com/moradigmir/greenremarket-dashboard-v3.git
- `git -C E:\Dev\greenremarket-dashboard-v3 status --porcelain` → 2 untracked files

**Outcome:** gr_project_inventory LOCAL head (67d42eb) ≠ PROD head (ff99f22) — LOCAL IS BEHIND PROD.

---

## 14:12:30Z — LOCAL: Dependency provenance
**Commands:**
- `E:\Dev\gr_project_inventory\.venv_odoo\Scripts\python.exe --version` → Python 3.11.9
- `pip freeze` → 80+ packages including fintech==7.9.2, playwright==1.58.0, psycopg2==2.9.5

**Outcome:** Full pip freeze captured. No wkhtmltopdf installed locally.

---

## 14:12:50Z — LOCAL: Dumps and data gravity
**Command:** `Get-ChildItem E:\Dev\gr_project_inventory\dumps`
**Outcome:** 35 dump files. prod.dump=19.17MB (2026-04-06), filestore_prod.tar.gz=742.75MB (2026-04-06). Multiple checkpoint dumps (~13.8MB each) from dev workflow Apr 1-7.

---

## 14:13:00Z — LOCAL: Config files
**Files read:**
- `C:\Users\migmi\migmir-odoo18\config\odoo.conf` → Old Docker config, db_host=db, dbfilter=^migmir$, NOT active
- `E:\Dev\gr_project_inventory\scripts\nginx_odoo_grm.conf` → Generic self-signed TLS nginx config
- `E:\Dev\gr_project_inventory\scripts\ct200_nginx_odoo.conf` → CT200 nginx for sartrouville.greenremarket.fr + go.greenremarket.fr

**Outcome:** No active local odoo.conf found. CT200 nginx config present as reference.

---

## 14:13:10Z — NETWORK: SSH topology
**Commands:**
- `Get-Content ~/.ssh/config` → Found SSH aliases: odoo-grm, odoo-prod (192.168.21.201 via odoo-grm), odoo-test (192.168.21.202 via odoo-grm), proxmox (192.168.21.20)
- `Get-Content ~/.ssh/known_hosts | head -20` → Confirmed wh.greenremarket.fr, greenremarket.com, 192.168.21.200, 192.168.21.201, 192.168.21.20 in known_hosts

**Outcome:** Full network topology mapped.

---

## 14:13:54Z — CT200 (odoo-grm): Reachability
**Command:** `ssh odoo-grm "echo JUMP_OK && hostname && date -u"`
**Outcome:** REACHABLE. hostname=odoo-grm, time=2026-04-08T14:13:54Z

---

## 14:14:01Z — CT201: Reachability and OS
**Command:** `ssh odoo-prod "echo CT201_OK && hostname && uname -a && uptime && cat /etc/os-release"`
**Outcome:** REACHABLE. hostname=odoo-staging, Ubuntu 22.04, kernel 6.5.11-4-pve, uptime 1d5h, 4 vCPUs

---

## 14:14:09Z — CT200 (192.168.21.200): Probe
**Command:** `ssh -J odoo-grm root@192.168.21.200 "echo CT200_OK && hostname"`
**Outcome:** hostname=odoo-grm — 192.168.21.200 IS the odoo-grm jump host, NOT a separate standby.

---

## 14:14:30Z — CT201: Services and Odoo config
**Commands:**
- `systemctl status odoo postgresql nginx` → all ACTIVE/RUNNING
- `cat /opt/odoo/odoo.conf` (redacted) → workers=4, db=greenremarket, proxy_mode=True
- Odoo version: 17.0.0 FINAL (confirmed from release.py)
- Python: 3.10.12 in /opt/odoo/venv

**Outcome:** CT201 fully operational: Odoo 17, nginx, PostgreSQL 17.

---

## 14:15:00Z — CT201: Database metrics
**Commands:**
- `sudo -u postgres psql -d greenremarket -c "SELECT pg_size_pretty(...)"` → 131 MB
- Top tables: mail_message=14MB, ir_model_data=8.5MB, ir_ui_view=6.8MB

**Outcome:** DB is 131MB, relatively small. Custom tables: gr_internal_inventory, gr_print_job.

---

## 14:15:30Z — CT201: Filesystem, TLS, cron
**Commands:**
- `ls /opt/odoo/` → addons, addons_src, backup_staging, data, ebics_keys/, enterprise, extra_addons, grm_repo, logs, oca_addons, venv
- filestore: 861MB, 2318 files
- `cat /etc/nginx/sites-enabled/odoo` → sartrouville.greenremarket.fr + go.greenremarket.fr
- TLS cert: notAfter=2026-06-30, CN=sartrouville.greenremarket.fr
- crontab -l (root): backup_to_cloud.sh 03:00, ebics_daily.py 01:00, ebics_watchdog.py 09:00

**Outcome:** Filesystem mapped, TLS valid ~83 days, 3 daily cron jobs.

---

## 14:16:00Z — CT201: Git state
**Command:** `sudo -u odoo git -C /opt/odoo/grm_repo log --oneline -1`
**Outcome:** HEAD=ff99f22 (LOCAL is 67d42eb) — prod HEAD ≠ local HEAD, diverged.

---

## 14:16:30Z — CT201: SECURITY FINDING
**Command:** `cat /etc/systemd/system/odoo.service`
**Outcome:** MYSQL credentials in plaintext in systemd Environment= directives. SEVERITY HIGH. REDACTED in all audit outputs.

---

## 14:17:00Z — LOCAL: Tests inventory
**Command:** `file_glob tests/**/*.py`
**Outcome:** 23 test files found. All Playwright E2E. conftest.py requires ODOO_BASE_URL, seeded users, live Odoo instance.

---

**Audit data collection complete (initial pass):** 2026-04-08T14:17:00Z

---

## 14:42:00Z — MySQL: awbc_db schema probe via CT201
**Method:** Script uploaded via SCP to CT201 (`/tmp/mysql_audit.sh`), credentials sourced from `/etc/systemd/system/odoo.service` Environment= directives. Password never echoed to stdout.

**Commands executed on CT201:**
```bash
eval $(grep -E '^Environment=MYSQL' /etc/systemd/system/odoo.service | sed 's/^Environment=//')
mysql -h $MYSQL_HOST -P $MYSQL_PORT -u $MYSQL_USER -p$MYSQL_PASSWORD -e "SHOW DATABASES;"
mysql ... -e "SELECT ROUND(SUM(data_length+index_length)/1024/1024,2) AS size_mb FROM information_schema.tables WHERE table_schema='awbc_db'"
mysql ... -e "SELECT table_name, table_rows, ROUND(...) AS size_mb, engine FROM information_schema.tables WHERE table_schema='awbc_db' ORDER BY size DESC"
mysql ... awbc_db -e "SHOW TABLES;"
mysql ... -e "DESCRIBE awbc_db.Units;"
mysql ... -e "DESCRIBE awbc_db.Units_Devices;"
mysql ... -e "DESCRIBE awbc_db.Lots;"
mysql ... awbc_db -e "SHOW CREATE VIEW Units_Reports\G"
mysql ... awbc_db -e "SHOW CREATE VIEW NEW_Units_Reports\G"
```

**Outcomes:**
- MySQL 8.0.42 confirmed reachable from CT201 and CT202
- awbc_db: 352.69 MB, 47 tables/views, all InnoDB
- Dominant tables: Units_Pictures (311MB), Units_Devices (133,654 rows / 37MB), Units (7,447 rows)
- 7 views including Units_Reports and NEW_Units_Reports — the primary Odoo report data sources
- Full column schemas captured for Units, Units_Devices, Lots, Lots_Owners, Clients_Formats
- View DDL captured for Units_Reports and NEW_Units_Reports
- FREFURB() stored function identified as state-dependent switch for refurbished vs original data
- latin1 charset encoding risk noted
- 192.168.21.206 confirmed NOT in SSH config, NOT in known_hosts — undocumented host

**Full output:** `55_mysql_awbc_dependency.json`

---

**Audit fully complete:** 2026-04-08T14:50:00Z
