# START HERE
Status: active
Last verified: 2026-03-28

This is the canonical entrypoint for agents resuming work on this repository.

## Resume behavior
For a vague prompt such as `resume work on this project`, do not start implementing immediately.

Instead:
1. Read the canonical chain below.
2. Produce the structured resume report defined in `AGENTS.md` (five sections: Operating model, Validated state, Active backlog, Recommended next action, Do not touch).
3. Note the current git branch. If it matches the recommended next task, say so. If not, note that a new feature branch from `main` will be needed.
4. Wait for explicit user instruction before modifying files, creating branches, committing, or pushing.

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
