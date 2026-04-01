import base64
print("=== Fix company logo_web ===")
company = env.company
print(f"Company: {company.name}, id={company.id}")
print(f"Partner id: {company.partner_id.id}")

# Check image attachments for the company partner
attachments = env['ir.attachment'].sudo().search([
    ('res_model', '=', 'res.partner'),
    ('res_id', '=', company.partner_id.id),
    ('res_field', 'in', ['image_1920', 'image_128', 'image_256']),
])
for att in attachments:
    size = len(att.datas) if att.datas else 0
    print(f"  Attachment: res_field={att.res_field}, name={att.name}, size={size} base64 chars")

logo = company.logo  # related to partner_id.image_1920
logo_web_before = company.logo_web

print(f"\nBefore recompute:")
print(f"  company.logo: {'EMPTY' if not logo else str(len(logo)) + ' chars'}")
print(f"  company.logo_web: {'EMPTY' if not logo_web_before else str(len(logo_web_before)) + ' bytes'}")

if logo:
    # Force recompute logo_web from current logo
    company._compute_logo_web()
    env.cr.commit()
    logo_web_after = env['res.company'].browse(company.id).logo_web
    print(f"\nAfter recompute:")
    print(f"  company.logo_web: {'EMPTY' if not logo_web_after else str(len(logo_web_after)) + ' bytes'}")
    if logo_web_before and logo_web_after and len(logo_web_before) != len(logo_web_after):
        print("  logo_web CHANGED - new logo will now appear in reports")
    else:
        print("  logo_web unchanged (same logo or logo still empty)")
else:
    print("\ncompany.logo is empty - no image_1920 on partner.")
    print("User should re-upload the logo in Settings > Companies > Green Remarket.")
    print("Or the attachment might need to be stored differently.")
