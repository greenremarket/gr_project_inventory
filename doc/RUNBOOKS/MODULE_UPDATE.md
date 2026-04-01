## MODULE UPDATE RUNBOOK (CT 200 / odoo-grm)

### Push a module update to production (code changes only, no new module)
`
# 1. SCP the updated module(s) to the server
scp -r modules\<module_name> odoo-grm:/opt/odoo/grm_repo/modules/

# 2. Stop Odoo, run the update, restart
ssh odoo-grm "systemctl stop odoo && sudo -u odoo /opt/odoo/venv/bin/python3 /opt/odoo/addons_src/odoo-bin -c /opt/odoo/odoo.conf --update=<module_name> --stop-after-init --log-level=warn && systemctl start odoo"
`

### Push multiple modules at once
`
scp -r modules\gr_project_inventory modules\grm_website modules\grm_documents_project modules\gr_portal odoo-grm:/opt/odoo/grm_repo/modules/
ssh odoo-grm "systemctl stop odoo && sudo -u odoo /opt/odoo/venv/bin/python3 /opt/odoo/addons_src/odoo-bin -c /opt/odoo/odoo.conf --update=gr_project_inventory,grm_website,grm_documents_project,gr_portal --stop-after-init --log-level=warn && systemctl start odoo"
`

### Install a brand new module (first time)
`
scp -r modules\<new_module> odoo-grm:/opt/odoo/grm_repo/modules/
ssh odoo-grm "systemctl stop odoo && sudo -u odoo /opt/odoo/venv/bin/python3 /opt/odoo/addons_src/odoo-bin -c /opt/odoo/odoo.conf --init=<new_module> --stop-after-init --log-level=warn && systemctl start odoo"
`

### Notes
- Always stop odoo BEFORE running --update/--init (port 8069 conflict otherwise).
- scp overwrites in place — no need to delete the old directory first.
- Addons path already includes /opt/odoo/grm_repo/modules — no config change needed for new modules in that directory.
- Do NOT use rsync (not available on Windows). Use scp -r.
