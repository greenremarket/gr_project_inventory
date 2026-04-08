# AGENTS
Status: active
Last updated: 2026-04-08

Legacy companion rules file: `.windsurfrules`

## Mandatory resume protocol
For prompts such as `resume work`, `resume work on this project`, or equivalent:
1. Read canonical docs in this order:
   - `AGENTS.md`
   - `doc/START_HERE.md`
   - `doc/CURRENT_STATE.md`
   - `doc/NEXT_ACTIONS.md`
   - `doc/WORK_LOG.md`
2. Run a read-only environment readiness probe.
3. Compare live probe results to the required runtime baseline in `doc/CURRENT_STATE.md`.
4. Produce a structured resume report with these sections, in order:
   - Environment readiness
   - Operating model
   - Validated state
   - Active backlog
   - Recommended next action
   - Do not touch
5. Wait for explicit user instruction before making edits, creating branches, committing, or pushing.

## Environment readiness gate (hard block)
Minimum probe surface (read-only):
- Required companion repos/paths exist: `odoo`, `enterprise`, `third_party_modules/reporting-engine`, `third_party_modules/account_reconcile_repo`, `third_party_modules/bank_statement_import_repo`, `third_party_modules/l10n_france_repo`, `third_party_modules/account_ebics_repo`
- Active custom modules: `modules/gr_project_inventory/`, `modules/gr_portal/` (`grm_documents_project` and `grm_website` are absorbed — their absence is expected)
- `.venv_odoo/Scripts/python.exe` exists
- PostgreSQL tooling/connectivity is available for this machine (`psql` at `C:\Program Files\PostgreSQL\17\bin\psql.exe` — add to PATH if missing)
- MySQL 8.0 on 192.168.21.206:3306 (`awbc_db`) reachable from CT201/CT202 — critical for gr_project_inventory reports

If any mandatory prerequisite is missing, the environment is `NON-OPERATIONAL` and the agent must:
- Explicitly report the missing prerequisites first.
- Recommend only environment bootstrap/recovery actions.
- Not recommend or start feature implementation, branching, code edits, or rollout actions.

Only when readiness is `OPERATIONAL` may the agent recommend code-task execution.

## Phase 0 Discovery Audit
A full read-only environment audit was completed 2026-04-08. All findings are in:
`audit_outputs/phase0_discovery_20260408_1410/`
Start with `PHASE0_DISCOVERY_REPORT.md` for the consolidated summary.

## Source-of-truth precedence
- Canonical docs under `doc/` are authoritative.
- Files under `doc/archive/` are historical context only.
- If historical notes conflict with canonical docs, canonical docs win.
