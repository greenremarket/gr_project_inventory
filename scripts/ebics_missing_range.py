# Download and process the missing statement period: 2025-06-21 to 2026-03-04
from datetime import date

print("=== EBICS Missing Range Download ===")
print("Date range: 2025-06-21 to 2026-03-04")

try:
    xfer = env['ebics.xfer'].create({
        'ebics_config_id': 1,
        'ebics_userid_id': 1,
        'format_id': 7,   # FDL cfonb120
        'date_from': date(2025, 6, 21),
        'date_to': date(2026, 3, 4),
    })
    result = xfer.ebics_download()
    env.cr.commit()
    xfer = env['ebics.xfer'].browse(xfer.id)
    note = (xfer.note or '').strip()
    print(f"xfer.note: {note[:400]}")

    # Find the new draft file
    files = env['ebics.file'].search([('state', '=', 'draft')], order='id desc', limit=5)
    if not files:
        print("No new draft file - download may have returned no data or an error.")
    else:
        for f in files:
            print(f"\nProcessing: {f.name} (id={f.id})")
            f.process()
            env.cr.commit()
            f = env['ebics.file'].browse(f.id)
            print(f"State: {f.state}")
            print(f"note_process:\n{f.note_process or '(empty)'}")
except Exception as e:
    import traceback
    print(f"ERROR: {e}")
    traceback.print_exc()

# Final statement count
stmts = env['account.bank.statement'].search(
    [('date', '>=', '2025-06-01')], order='date asc'
)
print(f"\n=== Total bank statements since 2025-06-01: {len(stmts)} ===")
for s in stmts:
    print(f"  {s.date} | lines={len(s.line_ids)} | end={s.balance_end_real}")

print("\n=== Done ===")
