# AGENTS
Status: active
Last updated: 2026-03-30

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
- Required companion repos/paths exist: `odoo`, `enterprise`, `OCA/reporting-engine`, `account_reconcile_repo`, `bank_statement_import_repo`, `l10n_france_repo`, `account_ebics_repo`,grm_documents_project,grm_website   
- PostgreSQL tooling/connectivity is available for this machine

If any mandatory prerequisite is missing, the environment is `NON-OPERATIONAL` and the agent must:
- Explicitly report the missing prerequisites first.
- Recommend only environment bootstrap/recovery actions.
- Not recommend or start feature implementation, branching, code edits, or rollout actions.

Only when readiness is `OPERATIONAL` may the agent recommend code-task execution.

## Source-of-truth precedence
- Canonical docs under `doc/` are authoritative.
- Files under `doc/archive/` are historical context only.
- If historical notes conflict with canonical docs, canonical docs win.
