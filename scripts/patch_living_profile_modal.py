"""
Patch openLivingProfile360Modal in dashboard.html to include:
- /api/living_profile/detail endpoint
- Documents exchanged
- Owner manual notes textarea
- Explainable AI modal trigger
"""

with open("heo_harness/plugins/ui_dashboard/dashboard.html", "r", encoding="utf-8") as f:
    html = f.read()

target = 'const res = await fetch(`/api/contacts/detail?id=${encodeURIComponent(contactId)}`);'
replacement = 'const res = await fetch(`/api/living_profile/detail?id=${encodeURIComponent(contactId)}`);'

if target in html:
    html = html.replace(target, replacement, 1)
    print("✓ Updated endpoint to /api/living_profile/detail")

# Also add documents & notes block before closing `</div>`, null, 'large');
doc_notes_anchor = """        <!-- Atomic Events Timeline & Opportunities -->"""
doc_notes_block = """        <!-- Documents & Owner Notes Row (SPEC-42) -->
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px">
          <!-- Documents Exchanged -->
          <div class="card card-pad">
            <div style="font-weight:700;font-size:12.5px;margin-bottom:8px;display:flex;align-items:center;gap:6px">
              <i class="ph ph-files" style="color:var(--color-accent)"></i> Tài Liệu Đã Trao Đổi (${(data.documents||[]).length})
            </div>
            <div style="display:flex;flex-direction:column;gap:6px;max-height:160px;overflow-y:auto">
              ${(data.documents||[]).length === 0 ? `
                <div style="font-size:11.5px;color:var(--color-neutral-400);padding:10px;text-align:center">Chưa có tài liệu trao đổi</div>
              ` : (data.documents||[]).map(d => `
                <div style="background:var(--color-bg);padding:8px 10px;border-radius:6px;border:1px solid var(--color-divider);display:flex;justify-content:space-between;align-items:center;font-size:11.5px">
                  <div>
                    <div style="font-weight:600">${escapeHtml(d.title || d.doc_type || 'Tài liệu')}</div>
                    <div style="font-size:10px;color:var(--color-neutral-400)">${d.doc_type} · ${escapeHtml(d.created_at || '')}</div>
                  </div>
                  <span class="badge ${d.status==='APPROVED'?'primary':'neutral'} sm">${d.status || 'DRAFT'}</span>
                </div>
              `).join('')}
            </div>
          </div>

          <!-- Owner Manual Notes -->
          <div class="card card-pad">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
              <div style="font-weight:700;font-size:12.5px;display:flex;align-items:center;gap:6px">
                <i class="ph ph-note-pencil" style="color:#f59e0b"></i> Ghi Chú Tay Của Sếp
              </div>
              <button class="btn sm" onclick="saveLivingProfileNotes('${c.id}')"><i class="ph ph-floppy-disk"></i> Lưu Ghi Chú</button>
            </div>
            <textarea id="living-profile-notes-input" style="width:100%;height:100px;background:var(--color-bg);border:1px solid var(--color-divider);border-radius:6px;padding:8px;font-size:11.5px;color:var(--color-text);resize:none" placeholder="Nhập ghi chú riêng của Sếp dành cho đối tác này...">${escapeHtml(data.notes || c.notes || '')}</textarea>
          </div>
        </div>

        <!-- Atomic Events Timeline & Opportunities -->"""

if "Tài Liệu Đã Trao Đổi" not in html and doc_notes_anchor in html:
    html = html.replace(doc_notes_anchor, doc_notes_block, 1)
    print("✓ Added Documents & Owner Notes block to Living Profile modal")

with open("heo_harness/plugins/ui_dashboard/dashboard.html", "w", encoding="utf-8") as f:
    f.write(html)

print("✓ Finished updating living profile modal!")
