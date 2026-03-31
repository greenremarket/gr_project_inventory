# EBICS FDL download using camt.053 Z53 (CIC-specific)
# Run via: Get-Content scripts\ebics_download_camt053.py | python odoo\odoo-bin shell ...
# Purpose: bypass the 91116 error on FDL/cfonb120 by using a different order type
from datetime import date

print("=== EBICS camt.053 Z53 Download ===")

config = env['ebics.config'].browse(1)
userid = env['ebics.userid'].browse(1)
fmt = env['ebics.file.format'].browse(4)  # camt.053 Z53 - CIC specific

print(f"Config: {config.name}")
print(f"User: {userid.name}, state: {userid.state}")
print(f"Format: {fmt.name} / order_type: {fmt.order_type}")
print(f"Passphrase stored: {userid.ebics_passphrase_store}")

try:
    xfer = env['ebics.xfer'].with_context(skip_check=True).create({
        'ebics_config_id': 1,
        'ebics_userid_id': 1,
        'format_id': 4,
        'date_from': date(2025, 6, 21),
        'date_to': date(2026, 3, 31),
    })
    print(f"xfer record created: id={xfer.id}")
    result = xfer.ebics_download()
    env.cr.commit()
    print("Download complete. Result action:", result.get('type') if isinstance(result, dict) else result)
    # Check created files
    files = env['ebics.file'].search([], order='id desc', limit=5)
    for f in files:
        print(f"  File: {f.name} | state: {f.state} | note: {(f.note_process or '')[:200]}")
except Exception as e:
    import traceback
    print("ERROR:", str(e))
    traceback.print_exc()
