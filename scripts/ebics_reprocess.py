# Reset EBICS file id=3 to draft and reprocess it
print("=== Reprocess EBICS File ===")

f = env['ebics.file'].browse(3)
print(f"File: {f.name}, state: {f.state}")

# Reset to draft
f.set_to_draft()
env.cr.commit()
f = env['ebics.file'].browse(3)
print(f"After reset: state={f.state}")

# Process
result = f.process()
env.cr.commit()
f = env['ebics.file'].browse(3)
print(f"After process: state={f.state}")
print(f"note_process:\n{f.note_process or '(empty)'}")

# Bank statements
stmts = env['account.bank.statement'].search([('date', '>=', '2025-06-01')], order='date asc')
print(f"\nBank statements since 2025-06-01: {len(stmts)}")
for s in stmts[:10]:
    nlines = len(s.line_ids)
    print(f"  {s.date} | {s.name} | lines={nlines} | end_balance={s.balance_end_real}")
if len(stmts) > 10:
    print(f"  ... and {len(stmts)-10} more")

print("=== Done ===")
