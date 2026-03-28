# WEBSITE OVERRIDE RECOVERY
Status: active
Last verified: 2026-03-28

## Purpose
Recover GRM website pages when Odoo Web Editor-created QWeb extensions override module-defined templates.

## Safe-state rule
- Before release signoff, the expected count of active editor-style website overrides is `0` unless a specific override is explicitly approved.

## Procedure summary
1. Connect to the relevant database with `psql --pset="pager=off"`.
2. Detect candidate editor-style overrides in `ir_ui_view`.
3. Deactivate active editor-style overrides with no `ir_model_data` record.
4. Re-check the count and confirm it is `0`.
5. Refresh Odoo views/modules if needed.
6. Restart Odoo and smoke-test `/` and `/contactus`.

## Detailed source
- Original detailed runbook: `doc/archive/RUNBOOK_GRM_WEBSITE_OVERRIDE_RECOVERY.txt`
