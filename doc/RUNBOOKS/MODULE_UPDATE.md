## MODULE UPDATE RUNBOOK

### Hotes SSH (IMPORTANT — ne pas confondre)
- `odoo-prod`  → CT201 (192.168.21.201) — PRODUCTION
- `odoo-test`  → CT202 (192.168.21.202) — TEST (Mateo, Playwright)
- `odoo-grm`   → bastion nginx / jump host — PAS une instance Odoo
- `proxmox`    → hyperviseur Proxmox (via ProxyJump odoo-grm)

Toujours deployer sur `odoo-test` d'abord, valider, puis sur `odoo-prod`.

### Push a module update to production (code changes only, no new module)
`
# 1. SCP the updated module(s) to the server
scp -r modules\<module_name> odoo-test:/opt/odoo/grm_repo/modules/

# 2. Stop Odoo, run the update, restart (odoo-test d'abord pour valider)
ssh odoo-test "systemctl stop odoo ; sudo -u odoo /opt/odoo/venv/bin/python3 /opt/odoo/addons_src/odoo-bin -c /opt/odoo/odoo.conf --update=<module_name> --stop-after-init --log-level=warn 2>&1 | tail -5 ; systemctl start odoo"

# 3. Puis prod apres validation
scp -r modules\<module_name> odoo-prod:/opt/odoo/grm_repo/modules/
ssh odoo-prod "systemctl stop odoo ; sudo -u odoo /opt/odoo/venv/bin/python3 /opt/odoo/addons_src/odoo-bin -c /opt/odoo/odoo.conf --update=<module_name> --stop-after-init --log-level=warn 2>&1 | tail -5 ; systemctl start odoo"
`

### Push multiple modules at once
`
scp -r modules\gr_project_inventory modules\grm_website modules\grm_documents_project modules\gr_portal odoo-prod:/opt/odoo/grm_repo/modules/
ssh odoo-prod "systemctl stop odoo ; sudo -u odoo /opt/odoo/venv/bin/python3 /opt/odoo/addons_src/odoo-bin -c /opt/odoo/odoo.conf --update=gr_project_inventory,grm_website,grm_documents_project,gr_portal --stop-after-init --log-level=warn 2>&1 | tail -5 ; systemctl start odoo"
`

### Install a brand new module (first time)
`
scp -r modules\<new_module> odoo-prod:/opt/odoo/grm_repo/modules/
ssh odoo-prod "systemctl stop odoo ; sudo -u odoo /opt/odoo/venv/bin/python3 /opt/odoo/addons_src/odoo-bin -c /opt/odoo/odoo.conf --init=<new_module> --stop-after-init --log-level=warn 2>&1 | tail -5 ; systemctl start odoo"
`

### Notes
- Utiliser `;` (pas `&&`) entre les commandes SSH pour que le restart se fasse meme si --update echoue.
- scp overwrites in place — no need to delete the old directory first.
- Addons path already includes /opt/odoo/grm_repo/modules — no config change needed for new modules in that directory.
- Do NOT use rsync (not available on Windows). Use scp -r.
- Ne JAMAIS utiliser odoo-grm comme cible de deploiement.
