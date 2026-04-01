import base64
print("=== Company Logo Debug ===")
company = env.company
print(f"Company: {company.name}")
print(f"uses_default_logo: {company.uses_default_logo}")
logo = company.logo
if logo:
    raw = base64.b64decode(logo)
    print(f"company.logo size: {len(logo)} base64 chars = {len(raw)} bytes decoded")
    # Write to disk so user can inspect it
    with open('scripts/debug_logo_output.png', 'wb') as f:
        f.write(raw)
    print("Written to scripts/debug_logo_output.png")
else:
    print("company.logo is EMPTY/FALSE")

logo_web = company.logo_web
if logo_web:
    print(f"company.logo_web size: {len(logo_web)} bytes (stored directly in DB)")
else:
    print("company.logo_web is empty")
