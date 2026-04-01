# EBICS catch-up: download and process statements from 2026-03-28 onwards.
# Last successful FDL run ended 2026-03-27. This picks up the gap to 2026-03-31.
from datetime import date

DATE_FROM = date(2026, 3, 28)
DATE_TO   = date(2026, 3, 31)
FORMAT_ID = 7   # FDL cfonb120 — the only working format at CIC for this EBICS contract

print(f"=== EBICS catch-up: {DATE_FROM} to {DATE_TO} ===")

try:
    xfer = env['ebics.xfer'].create({
        'ebics_config_id': 1,
        'ebics_userid_id': 1,
        'format_id': FORMAT_ID,
        'date_from': DATE_FROM,
        'date_to': DATE_TO,
    })
    result = xfer.ebics_download()
    env.cr.commit()
    xfer = env['ebics.xfer'].browse(xfer.id)
    note = (xfer.note or '').strip()
    print(f"xfer.note: {note[:400]}")

    files = env['ebics.file'].search([('state', '=', 'draft')], order='id desc', limit=5)
    if not files:
        print("No new draft file — may be 90005 (no data available) or already consumed.")
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

stmts = env['account.bank.statement'].search(
    [('date', '>=', '2026-03-01')], order='date asc'
)
print(f"\n=== Bank statements since 2026-03-01: {len(stmts)} ===")
for s in stmts:
    print(f"  {s.date} | lines={len(s.line_ids)}")

print("\n=== Done ===")
