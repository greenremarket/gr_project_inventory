# DECISION: EBICS Keys Location
Date: 2026-03-31
Status: active

## Context
The EBICS module (`account_ebics_repo`) requires SSL keys and certificates that were used to generate
the bank INI/contract file submitted to the bank. These files are machine-specific, sensitive, and
must never be committed to git.

## Decision
EBICS keys are stored in `ebics_keys/` at the repo root. The directory is git-tracked via
`ebics_keys/.gitkeep` but its contents are gitignored. On every new machine, the keys must be
copied manually from a secure source before EBICS connectivity will work.

## Current machine (migmi / E:\Dev\gr_project_inventory)
- `ebics_keys/greenremarket/` — active EBICS keys for the greenremarket bank connection
- `ebics_keys/keys.bak/` — backup of those keys

## On a new machine
1. Obtain the EBICS keys from a secure location (existing machine, encrypted backup, or bank re-registration).
2. Copy into `ebics_keys/` matching the structure above.
3. Update the path in the database — it is stored in the `ebics_config` table, `ebics_keys` column:
   ```
   UPDATE ebics_config SET ebics_keys = '<absolute path to ebics_keys/greenremarket on this machine>' WHERE id = 1;
   ```
   On the migmi Windows machine: `E:\Dev\gr_project_inventory\ebics_keys\greenremarket`
   On the production Linux server: `/etc/odoo/ebics_keys/greenremarket`
   On a new machine, the path will differ — always update the DB record before starting Odoo.

## Key file naming
- Key files are named `<ebics_user_id>_keys` (e.g. `120558690001_keys`)
- They contain JSON with A (authentication), E (encryption), and X (signature) key pairs
- Never share or log this file content

## Security note
Never commit key files to git. Never store them in cloud drives without encryption.
The `ebics_keys/*` gitignore pattern enforces this at the git level.
