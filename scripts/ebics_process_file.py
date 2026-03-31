# Process the downloaded EBICS cfonb120 file into bank statements
print("=== Process EBICS File ===")

files = env['ebics.file'].search([('state', '=', 'draft')], order='id desc', limit=5)
if not files:
    print("No draft EBICS files found.")
else:
    for f in files:
        print(f"Processing: {f.name} (id={f.id}, state={f.state})")
        try:
            result = f.process()
            env.cr.commit()
            f = env['ebics.file'].browse(f.id)
            print(f"  New state: {f.state}")
            print(f"  note_process: {(f.note_process or '')[:600]}")
            # Check bank statements created
            stmts = env['account.bank.statement'].search(
                [('ebics_file_id', '=', f.id)], order='date desc'
            )
            if stmts:
                print(f"  Bank statements created: {len(stmts)}")
                for s in stmts:
                    print(f"    Statement: {s.name} date={s.date} balance_end={s.balance_end_real}")
            else:
                print("  No bank statements linked (check note_process for errors)")
        except Exception as e:
            import traceback
            print(f"  ERROR: {e}")
            traceback.print_exc()

print("=== Done ===")
