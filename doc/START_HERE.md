# START HERE
Status: active
Last verified: 2026-03-30

This is the canonical entrypoint for agents resuming work on this repository.

## Resume behavior
For a vague prompt such as `resume work on this project`, do not start implementing immediately.

Instead:
1. Read the canonical chain below.
2. Run a read-only environment readiness probe and compare findings with `doc/CURRENT_STATE.md`.
3. Produce the structured resume report defined in `AGENTS.md` (six sections: Environment readiness, Operating model, Validated state, Active backlog, Recommended next action, Do not touch).
4. Note the current git branch. If it matches the recommended next task, say so. If not, note that a new feature branch from `main` will be needed.
5. Wait for explicit user instruction before modifying files, creating branches, committing, or pushing.

## Mandatory environment readiness gate
Before recommending any code-task execution, verify at minimum:
- required companion repos/paths exist (`odoo`, `enterprise`, `OCA/reporting-engine`, `account_reconcile_repo`, `bank_statement_import_repo`, `l10n_france_repo`, `account_ebics_repo`)
- `.venv_odoo/Scripts/python.exe` exists
- `odoo/odoo-bin` exists
- `odoo_data/filestore/greenremarket` and `odoo_data/filestore/greenremarket_backup` exist
- PostgreSQL tooling/connectivity is available on the machine

If any mandatory prerequisite is missing, report `NON-OPERATIONAL` first and stop at environment bootstrap/recovery guidance. Do not recommend or start feature implementation, branch creation for feature work, code edits, or rollout steps until readiness is restored.

## New feature kickoff gate
For any feature being handled for the first time:
1. Run a read-only research/probing pass to map current behavior and constraints.
2. Produce a concrete implementation plan.
3. Wait for explicit developer approval of that plan.
4. Only after approval: create a feature branch from `main` and begin implementation.

Do not skip this gate, even when the feature request seems straightforward.

## Read this chain in order
0. `AGENTS.md` — repo-level rules and safety semantics
1. `doc/CURRENT_STATE.md` — authoritative live operational state
2. `doc/NEXT_ACTIONS.md` — active backlog and immediate priorities
3. `doc/WORK_LOG.md` — recent completed work and validation trail

## Read as needed
- `doc/RUNBOOKS/BACKUP_AND_SWAP.md` — standby refresh, validation, and promotion workflow
- `doc/RUNBOOKS/WEBSITE_OVERRIDE_RECOVERY.md` — GRM website override recovery
- `doc/DECISIONS/2026-03-26-active-standby-workflow.md` — why the workflow changed from the legacy test-db model

## Conflict resolution
- If an older doc conflicts with the files above, the files above win.
- Files under `doc/archive/` are historical only.
- Session handoffs should update the canonical files above instead of creating new peer docs.
- An unreviewed branch created by an accidental autonomous test must not override the canonical docs.

## Update protocol
- Update `doc/CURRENT_STATE.md` when a durable fact changes.
- Update `doc/NEXT_ACTIONS.md` when priorities or statuses change.
- Append to `doc/WORK_LOG.md` when you complete a meaningful step or validation.
- Update `AGENTS.md` or `doc/DECISIONS/` when the working method itself changes.
- After committing canonical doc changes, push to remote immediately. Operational and guardrail state must live on the remote to survive across machines and sessions.
