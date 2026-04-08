# Phase 0 Blockers — Evidence Capture
**Captured:** 2026-04-08T14:10:22Z

---

## BLOCKER-01: CT202 serves identical hostnames to CT201 — no staging isolation
**Severity:** CRITICAL  
**Environments:** CT201, CT202  
**Reproducibility:** 100% — observed in config  

**Evidence:**
```
# CT201 /etc/nginx/sites-enabled/odoo
server_name sartrouville.greenremarket.fr go.greenremarket.fr;

# CT202 /etc/nginx/sites-enabled/odoo  (IDENTICAL)
server_name sartrouville.greenremarket.fr go.greenremarket.fr;
```
Both containers share the same public hostnames. Neither has a distinct `test.greenremarket.fr` or `staging.greenremarket.fr` DNS entry. Routing between them is ambiguous — only one receives external traffic at any time, but there is no config-level distinction.

**Likely root cause:** CT202 was cloned from CT201 via Proxmox snapshot. The nginx config was never updated to give CT202 a separate identity. CONFIDENCE: HIGH

---

## BLOCKER-02: CT201 and CT202 are identical snapshots — no true environment isolation
**Severity:** CRITICAL  
**Environments:** CT201, CT202  
**Reproducibility:** 100%  

**Evidence:**
```
CT201 git HEAD:  ff99f22
CT202 git HEAD:  ff99f22   ← IDENTICAL

CT201 DB size:   131 MB
CT202 DB size:   131 MB    ← IDENTICAL

CT201 filestore: 861 MB, 2318 files
CT202 filestore: 860 MB, 2319 files  ← NEAR-IDENTICAL

CT201 uptime since: 2026-04-07T22:18:57Z
CT202 uptime since: 2026-04-07T22:22:11Z  ← same restart window
```
Both environments were restarted ~4 minutes apart on the same day, with identical data. They appear to have been provisioned from the same Proxmox snapshot.

**Likely root cause:** No post-clone differentiation procedure was run. CONFIDENCE: HIGH

---

## BLOCKER-03: External MySQL credentials in plaintext systemd env vars — both CT201 and CT202
**Severity:** HIGH (security)  
**Environments:** CT201, CT202  
**Reproducibility:** 100%  

**Evidence:**
```
# /etc/systemd/system/odoo.service (both CT201 and CT202 — IDENTICAL)
Environment=MYSQL_HOST=192.168.21.206
Environment=MYSQL_PORT=3306
Environment=MYSQL_USER=manager
Environment=MYSQL_PASSWORD=***REDACTED***
Environment=MYSQL_DATABASE=awbc_db
```
Credentials to an external MySQL host (192.168.21.206) are stored as plaintext in the systemd unit file, readable by any root-level process. The database `awbc_db` on host `.206` has not been audited.

**Likely root cause:** Quick deployment without secrets management (no vault, no env file permissions). CONFIDENCE: HIGH

---

## BLOCKER-04: gr_project_inventory repo DIRTY on all three environments
**Severity:** HIGH  
**Environments:** Local, CT201, CT202  
**Reproducibility:** 100%  

**Evidence:**
```
# LOCAL (edgar)
git status --porcelain | head -5:
 M modules/gr_portal/__init__.py
 M modules/gr_portal/__manifest__.py
 M modules/gr_project_inventory/__init__.py
 M modules/gr_project_inventory/data/barcode_data.xml
 D modules/grm_documents_project/__init__.py   ← DELETED module

# CT201 (odoo-prod)  
 M modules/gr_project_inventory/TODO
 M modules/gr_project_inventory/__init__.py
 M modules/gr_project_inventory/data/barcode_data.xml
 (10+ more)

# CT202 (odoo-test) — SAME as CT201
 M modules/gr_project_inventory/TODO
 M modules/gr_project_inventory/__init__.py
 (same files)
```
No environment is at a clean commit. CI/CD cannot be reliably built from a dirty tree.

**Likely root cause:** Active development directly on deployed containers; no git-based deploy workflow enforced. CONFIDENCE: HIGH

---

## BLOCKER-05: Local HEAD behind production — uncommitted divergence
**Severity:** HIGH  
**Environments:** Local vs CT201/CT202  
**Reproducibility:** 100%  

**Evidence:**
```
Local HEAD:  67d42ebef9d8db84cf41246f5bc334d3fa165eae
CT201 HEAD:  ff99f22  (docs: add deployment probe report for odoo_sartrouville)
CT202 HEAD:  ff99f22  ← same as CT201
```
Local is behind by at least 1 commit. The local working tree also has uncommitted changes (30+ modified files, 3 deleted) not present on either server.

**Likely root cause:** Development being done in divergent branches or directly on the server without syncing back. CONFIDENCE: HIGH

---

## BLOCKER-06: No Odoo running locally — dev workflow requires SSH access to CT201/CT202
**Severity:** HIGH  
**Environment:** Local  
**Reproducibility:** 100%  

**Evidence:**
```
# Local process list:
odoo_ls_server.exe  (Windsurf IDE extension — NOT a running Odoo server)
python.exe (venv) — 4.8MB working set (not Odoo, likely a test script)
# No port 8069 listening locally
# No Odoo in ODOO_BASE_URL default: http://localhost:8069
```
All E2E tests default to `ODOO_BASE_URL=http://localhost:8069`. With no local Odoo running, tests cannot run without manually overriding this env var to point at a remote server.

**Likely root cause:** No local Odoo startup script / Makefile / docker-compose.yml for dev. CONFIDENCE: HIGH

---

## BLOCKER-07: wkhtmltopdf not installed locally
**Severity:** MEDIUM  
**Environment:** Local  
**Reproducibility:** 100%  

**Evidence:**
```
PS> Get-ChildItem "C:\Program Files\wkhtmltopdf" → NOT FOUND
PS> Get-ChildItem "C:\Program Files (x86)\wkhtmltopdf" → NOT FOUND
```
PDF generation (delivery notes, invoices) cannot be tested locally. CT201 and CT202 both have wkhtmltopdf 0.12.6.1 (patched qt).

---

## BLOCKER-08: Enterprise clone auth method undocumented — CI/CD would fail
**Severity:** HIGH  
**Environments:** All  
**Reproducibility:** Likely HIGH in CI  

**Evidence:**  
The enterprise modules at `/opt/odoo/enterprise` (CT201/CT202) and `E:\Dev\gr_project_inventory\enterprise` (local) are Git clones of the private Odoo enterprise repository. No `~/.netrc`, deploy key, or token was found documented in the repo or scripts. The `bootstrap_odoo_lxc.sh` script exists locally but was not inspected for enterprise clone credentials.

**Likely root cause:** Credentials exist in developer's shell environment or SSH agent but are not captured in any reproducible CI secret. CONFIDENCE: MEDIUM

---

## BLOCKER-09: OCA/Noviat dependency pins missing — reproducibility risk
**Severity:** MEDIUM  
**Environments:** All  
**Reproducibility:** Latent (will manifest at fresh build)  

**Evidence:**
```
# Local third_party_modules/ — no requirements.txt with hashes
# account_ebics_repo: OCA/Noviat — no pinned commit SHA
# reporting-engine: OCA — checked out, no pin
```
All five OCA/Noviat repos (`account_ebics_repo`, `account_reconcile_repo`, `bank_statement_import_repo`, `l10n_france_repo`, `reporting-engine`) have no pinned commit SHA or hash. A fresh clone would pick up HEAD, which may be a different version.

---

## BLOCKER-10: C: drive critically low (16.75 GB free)
**Severity:** MEDIUM  
**Environment:** Local  
**Reproducibility:** 100%  

**Evidence:**
```
Name UsedGB FreeGB TotalGB
C    459.14  16.75  475.89   ← 3.5% free
```
Installing Docker Desktop, WSL distros, or additional tooling required for Phase 0 containerisation would be at risk on the C: drive. Dev work should target E: or D:.

---

## BLOCKER-11: psql not in Windows PATH
**Severity:** LOW  
**Environment:** Local  
**Reproducibility:** 100%  

**Evidence:**
```
PS> psql -U postgres -c "SELECT version();"
psql : Le terme «psql» n'est pas reconnu...
# PostgreSQL 17 installed at C:\Program Files\PostgreSQL\17\bin\psql.exe
# but C:\Program Files\PostgreSQL\17\bin is NOT in system PATH
```
Manual path invocation required for any local DB operations.

---

## BLOCKER-12: All tests are Playwright E2E — zero synthetic/unit tests
**Severity:** MEDIUM  
**Environments:** All  
**Reproducibility:** 100%  

**Evidence:**
```
tests/ — 24 files, all Playwright test_*.py
conftest.py requires: ODOO_BASE_URL, live seeded users, live running Odoo
0 Odoo Python unit tests found (no tests/ inside custom modules beyond stub __init__.py)
```
There are no tests runnable without a live Odoo instance + seeded database. This means CI cannot validate changes without a full Odoo stack, and there is no unit-level regression safety net.
