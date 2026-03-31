# Try multiple EBICS approaches to get bank statements
# C53 (generic camt.053), and FDL with shifted date range
from datetime import date

def try_download(label, format_id, date_from, date_to):
    print(f"\n--- Trying {label} format_id={format_id} {date_from} to {date_to} ---")
    try:
        xfer = env['ebics.xfer'].create({
            'ebics_config_id': 1,
            'ebics_userid_id': 1,
            'format_id': format_id,
            'date_from': date_from,
            'date_to': date_to,
        })
        result = xfer.ebics_download()
        env.cr.commit()
        xfer = env['ebics.xfer'].browse(xfer.id)
        note = (xfer.note or '').strip()
        if note:
            print(f"  Note: {note[:300]}")
        else:
            print("  No error note - checking for files...")
        files = env['ebics.file'].search([], order='id desc', limit=3)
        if files:
            for f in files:
                print(f"  FILE: {f.name} | state={f.state}")
                print(f"  note_process: {(f.note_process or '')[:400]}")
            return True
        return False
    except Exception as e:
        import traceback
        print(f"  EXCEPTION: {e}")
        return False

print("=== EBICS Format Sweep ===")

# 1. Try C53 (generic camt.053, id=3)
if try_download("C53 camt.053", 3, date(2025, 6, 21), date(2026, 3, 31)):
    print("SUCCESS with C53")
else:
    # 2. Try FDL cfonb120 with slightly different range (end date -1 day)
    if try_download("FDL cfonb120 shifted range", 7, date(2025, 6, 21), date(2026, 3, 30)):
        print("SUCCESS with shifted FDL range")
    else:
        # 3. Try FDL with only recent data
        if try_download("FDL cfonb120 recent only", 7, date(2026, 1, 1), date(2026, 3, 31)):
            print("SUCCESS with recent FDL range")
        else:
            # 4. Try FDL with no dates (let bank decide)
            try_download("FDL cfonb120 no dates", 7, False, False)

print("\n=== Done ===")
