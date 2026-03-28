# Project Rules
## Odoo/GRM website override safety memory
- Treat Web Editor-created website QWeb extensions as high-risk during restores and updates: they can override GRM module templates and mask expected UI behavior.
- Before QA signoff and before production cutover, check for active editor-style overrides in `ir_ui_view` with all of:
  - `type = 'qweb'`
  - `mode = 'extension'`
  - `inherit_id IS NOT NULL`
  - `website_id IS NOT NULL`
  - no matching `ir_model_data` row for the view
- Default action for release stability: deactivate these editor-style overrides unless they are explicitly approved for the release.
- Always run a post-change verification query to confirm the active override count is `0`.
