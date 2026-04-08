# Phase 0 Inputs Summary
**Captured:** 2026-04-08T14:10:22Z

## What Is Now Confirmed Available

### Source Code
- Odoo 17.0.0 CE source: `E:\Dev\gr_project_inventory\odoo` (local) / `/opt/odoo/addons_src` (CT201/CT202)
- Odoo 17.0.0 Enterprise: present locally and on both servers
- Custom modules: `gr_project_inventory`, `gr_portal` (active); `grm_documents_project`, `grm_website` (present on servers, deleted locally)
- React dashboard: `E:\Dev\greenremarket-dashboard-v3` (clean, Vite+TypeScript+bun)
- Third-party OCA/Noviat repos: 5 repos, all present locally and on servers

### Infrastructure
- Proxmox hypervisor at 192.168.21.20 (accessible via jump host)
- Jump host (CT200/odoo-grm): Ubuntu 22.04, SSH relay, nginx reverse proxy, public IP at sartrouville.greenremarket.fr
- CT201 (odoo-staging): Ubuntu 22.04, Odoo 17 running, 59GB disk, 4 vCPU, 4GB RAM
- CT202 (odoo-test): Ubuntu 22.04, Odoo 17 running, 59GB disk, 4 vCPU, 4GB RAM — identical clone of CT201
- SSH access from local to all three: confirmed working

### Data
- Production DB dump: `dumps/prod.dump` (19.17MB, 2026-04-06)
- Production filestore archive: `dumps/filestore_prod.tar.gz` (742.75MB, 2026-04-06)
- Live DB on CT201 and CT202: greenremarket, 131MB each
- Live filestores: ~860MB each on CT201/CT202
- 8 checkpoint dumps from Apr 1-7 (dev workflow snapshots)

### Dependencies
- Python 3.11.9 locally, 3.10.12 on servers — both pinned in their respective venvs
- Full pip freeze captured for local venv (80+ packages)
- Partial pip freeze captured for server venv; Zope stack confirmed present on both CT201 and CT202
- wkhtmltopdf 0.12.6.1 (patched qt) on CT201 and CT202 — correct version
- PostgreSQL 17.9 on both servers; PostgreSQL 17 on local Windows

### Config
- odoo.conf on CT201 and CT202: identical, fully documented (redacted)
- nginx config: documented for CT200/CT201/CT202
- TLS cert: valid until 2026-06-30 (83 days remaining)
- Systemd service: fully documented (security issue noted)
- Cron jobs: 3 daily jobs documented (backup, ebics_daily, ebics_watchdog)

### EBICS
- Key directory paths confirmed on all environments: `ebics_keys/`
- Three daily EBICS scripts on CT201/CT202: ebics_daily.py, ebics_watchdog.py, ebics_catchup.py
- fintech==7.9.2 installed on all environments

---

## What Is Still Missing Before Phase 0 Implementation Can Begin

### MUST HAVE
1. **Enterprise Git token/credentials**: Method to clone `odoo/enterprise` in a CI/automated context is undocumented. This is a hard blocker for any containerised build.
2. **CT202 distinct identity**: CT202 must be reconfigured with its own hostname (e.g. `test.greenremarket.fr`) before it can safely function as a staging environment without risk of serving prod traffic.
3. **Clean git baseline**: All three environments are dirty. A clean tagged release commit is needed before Phase 0 build can be reproducible.
4. **EBICS key import procedure**: The EBICS keys at `/opt/odoo/ebics_keys/` need a documented import process for any new container deployment. Paths and fintech config not inspected.
5. **DB seeding script validation**: `scripts/seed_test_users.py` exists but has not been run against a fresh DB. It must be validated before CI tests can run.

### SHOULD HAVE
6. **OCA/Noviat commit SHA pins**: All 5 OCA repos need pinned commit SHAs added to a manifest (e.g. `requirements-addons.txt` or `.gitmodules`) to guarantee reproducible builds.
7. **backup_to_cloud.sh contents + cloud destination**: Cloud backup destination unknown. Restore procedure not documented.
8. **Local Odoo startup script**: No `Makefile`, `docker-compose.yml`, or launch script exists for starting Odoo locally. Required for dev loop.
9. **Python version decision**: Choose between 3.10 (server) and 3.11 (local) for containerised target. Docker image base must reflect this.
10. **awbc_db / MySQL host 192.168.21.206 audit**: Unknown external MySQL database referenced in systemd env. Must be understood before containerising the service.

### NICE TO HAVE
11. Full pip freeze from CT201/CT202 venv (only partial captured)
12. Proxmox disk/LVM layout audit (not done — hypervisor not directly inspected)
13. CT202 bootstrap_odoo_lxc.sh content review (to understand provisioning procedure)
14. Log analysis for startup errors, EBICS failures, token errors (logs not tailed in this audit)
