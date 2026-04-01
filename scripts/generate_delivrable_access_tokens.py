# Backfill access_token on all existing Delivrable-tagged document attachments.
# Portal download URLs require ?access_token=... which is only set explicitly.
print("=== Backfill Delivrable document access tokens ===")

delivrable_tag = env.ref('grm_documents_project.documents_project_delivrable', raise_if_not_found=False)
if not delivrable_tag:
    print("ERROR: grm_documents_project.documents_project_delivrable tag not found.")
else:
    print(f"Delivrable tag: id={delivrable_tag.id}, name={delivrable_tag.name}")
    docs = env['documents.document'].sudo().search([('tag_ids', 'in', [delivrable_tag.id])])
    print(f"Found {len(docs)} Delivrable documents")
    fixed = 0
    already_ok = 0
    no_attachment = 0
    for doc in docs:
        if not doc.attachment_id:
            no_attachment += 1
            continue
        if doc.attachment_id.sudo().access_token:
            already_ok += 1
            continue
        doc.attachment_id.sudo().generate_access_token()
        fixed += 1
    env.cr.commit()
    print(f"  Already had token: {already_ok}")
    print(f"  No attachment: {no_attachment}")
    print(f"  Token generated: {fixed}")
    print("Done.")
