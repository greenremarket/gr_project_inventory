# Verbose EBICS debug - captures xfer note and checks what was returned
from datetime import date

print("=== EBICS Debug Download ===")

try:
    # Try Z53 (camt.053 CIC-specific) first
    xfer = env['ebics.xfer'].with_context(skip_check=True).create({
        'ebics_config_id': 1,
        'ebics_userid_id': 1,
        'format_id': 4,   # camt.053 Z53
        'date_from': date(2025, 6, 21),
        'date_to': date(2026, 3, 31),
    })
    result = xfer.ebics_download()
    env.cr.commit()
    print("Action type:", result.get('type') if isinstance(result, dict) else result)
    # Reload xfer to get updated note
    xfer = env['ebics.xfer'].browse(xfer.id)
    print("xfer.note (full):", xfer.note or "(empty)")
    files = env['ebics.file'].search([], order='id desc', limit=5)
    if files:
        for f in files:
            print(f"  FILE id={f.id} name={f.name} state={f.state}")
            print(f"  note_process: {(f.note_process or '')[:500]}")
    else:
        print("No ebics.file records found after download.")
        # Check if raw data came in via xfer
        print("Checking if xfer has file attachment...")
        attachments = env['ir.attachment'].search([
            ('res_model', '=', 'ebics.xfer'),
            ('res_id', '=', xfer.id)
        ])
        for att in attachments:
            print(f"  Attachment: {att.name} ({att.mimetype}, {att.file_size} bytes)")
except Exception as e:
    import traceback
    print("ERROR:", str(e))
    traceback.print_exc()
