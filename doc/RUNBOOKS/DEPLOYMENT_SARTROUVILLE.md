# DEPLOYMENT PROBE — odoo_sartrouville
Date: 2026-04-01 (session 8)
Status: active — read-only probe completed

## Server
- Ubuntu 24.04.1 LTS, hostname: odoo
- Odoo 17.0 — matches local dev. Good.
- Python venv: /opt/odoo/venv/bin/python3
- PostgreSQL 16 (local socket, peer auth for odoo user)
- nginx in front: domains go.greenremarket.fr, wh.greenremarket.fr, sartrouville.greenremarket.fr

## Two running Odoo instances
### odoo.service — PRODUCTION
- Config: /opt/odoo/odoo.conf (= /etc/odoo.conf, same file)
- Addons: /opt/odoo/addons, /opt/odoo/enterprise, /opt/odoo/extra_addons
- data_dir: NOT SET ? defaults to /opt/odoo/.local/share/Odoo
- Port: 8069 (default)
- Running since: 2026-03-29 (PID 681504)

### odoo-test.service — TEST INSTANCE
- Config: /etc/odoo-test.conf
- db_name: greenremarket_working, dbfilter: ^greenremarket_dupe2$
- Port: 8089, longpolling: 8092
- Addons: addons + enterprise + oca_addons + test_addons/greenremarket + test_addons/portal_gr
- data_dir: /opt/odoo/.local/share/Odoo/test

## Databases on server
- greenremarket ? PRODUCTION (active since 2026-03-29)
- greenremarket_working ? test instance active DB (since 2026-03-13)
- greenremarket_dupe, greenremarket_dupe2, greenremarket_test, gr20251221 ? copies/archives

## Production (greenremarket) module state
- gr_project_inventory: installed, version 1.2 ? OLD. Our latest is much newer (session 8).
- grm_website: NOT installed, NOT in extra_addons
- grm_documents_project: NOT installed, NOT in extra_addons
- portal_gr: uninstalled (present in extra_addons, uninstalled in DB)
- account_ebics + account_ebics_oe: installed (EBICS configured)
- report_xlsx + report_xlsx_helper: installed 17.0.1.0.1 (OCA — present in both oca_addons and extra_addons)
- studio_customization: installed ? Odoo Studio is in use; view overrides may exist in DB

## gr_project_inventory on server
- Path: /opt/odoo/extra_addons/gr_project_inventory/
- Version in manifest: 1.2
- NOT a git repo (plain file copy, last modified 2025-11-17)
- Must be replaced with our latest code (git pull from greenremarket/gr_project_inventory)

## grm_website and grm_documents_project
- Neither exists anywhere in the addon paths
- test_addons/greenremarket/ contains gr_project_inventory + many scripts/docs — NOT a proper module dir
- Both modules must be added to extra_addons (or a new dedicated path) before installation

## Filestore
- Path: /opt/odoo/.local/share/Odoo/filestore/greenremarket/
- File count: 257 (local dev has ~2261 — production has much less data)

## Bank accounts (production DB)
- id=1: acc_number=FR76 1027 8061 6400 0202 5770 259 (full IBAN), sanitized=FR7610278061640002025770259
- id=2: E98 5004 0000 0589 3375 02
- CRITICAL: production still has full IBAN on account id=1. Local dev was changed to raw BBAN
  (00021148802) to fix EBICS "no financial journal found" errors. This fix must be applied to
  production at deployment time.

## EBICS config
- 1 record: id=1, name="CM-CIC"
- ebics_userid column does not exist on this version ? minor schema diff vs our local
  (may be version difference in account_ebics module)

## MySQL workbench credentials
- ir_config_parameter: ALL EMPTY (gr.workbench_* params not set in DB)
- systemd unit (/etc/systemd/system/odoo.service) has WRONG credentials (confirmed by operator)
- Correct credentials to use: from local greenremarket DB (manager / gren2803awb / 192.168.21.206)
- At deployment: update systemd Environment lines with correct values

## Production config hardening needed
The current /opt/odoo/odoo.conf is missing critical production settings:
- proxy_mode = True (nginx is in front — MISSING, XFF headers not trusted)
- db_name = greenremarket (MISSING — DB manager exposed to public)
- dbfilter = ^greenremarket$ (MISSING — any DB accessible)
- list_db = False (currently True — DB selector visible publicly)
- workers = N (MISSING — single-process mode, not multi-user grade)
- log_level = warn (currently debug — very verbose, performance impact)

## Deployment action items (in order)
1. Harden /opt/odoo/odoo.conf (proxy_mode, db_name, dbfilter, list_db, workers, log_level)
2. Replace /opt/odoo/extra_addons/gr_project_inventory/ with latest from GitHub
3. Add grm_website and grm_documents_project to /opt/odoo/extra_addons/
4. Run --update=gr_project_inventory on production greenremarket DB
5. Run --init=grm_website,grm_documents_project on production
6. Fix bank account id=1: acc_number + sanitized_acc_number ? BBAN 00021148802
7. Update systemd odoo.service Environment lines with correct MySQL credentials
8. systemctl daemon-reload + systemctl restart odoo
9. Smoke-test: login, Formulaire de lancement, EBICS import, erasure cert
