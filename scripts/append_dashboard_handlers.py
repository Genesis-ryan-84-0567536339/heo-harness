# -*- coding: utf-8 -*-
dashboard_path = "/home/ryan/heo-harness/heo_harness/plugins/ui_dashboard/dashboard.html"
with open(dashboard_path, "r", encoding="utf-8") as f:
    text = f.read()

handlers_code = """
// ==========================================
// DRAG & DROP AND ADVANCED ACTIONS (MILESTONE 3)
// ==========================================
let draggedOppId = null;

function handleOppDragStart(e, oppId) {
  draggedOppId = oppId;
  e.dataTransfer.setData('text/plain', oppId);
  e.dataTransfer.effectAllowed = 'move';
  const card = document.getElementById('opp-card-' + oppId);
  if (card) card.style.opacity = '0.5';
}

function handleOppDragOver(e) {
  e.preventDefault();
  e.dataTransfer.dropEffect = 'move';
  const col = e.currentTarget;
  col.style.background = 'rgba(99, 102, 241, 0.08)';
  col.style.borderColor = 'rgba(99, 102, 241, 0.6)';
}

function handleOppDragLeave(e) {
  const col = e.currentTarget;
  col.style.background = 'var(--color-surface)';
  col.style.borderColor = 'var(--color-divider)';
}

async function handleOppDrop(e, stageKey) {
  e.preventDefault();
  const col = e.currentTarget;
  col.style.background = 'var(--color-surface)';
  col.style.borderColor = 'var(--color-divider)';
  const oppId = e.dataTransfer.getData('text/plain') || draggedOppId;
  if (!oppId) return;

  const card = document.getElementById('opp-card-' + oppId);
  if (card) card.style.opacity = '1';

  await moveOpportunityStage(oppId, stageKey);
}

function openOpportunityDetailModal(oppId) {
  const opps = state.df_opps || [];
  const o = opps.find(x => x.id === oppId);
  if (!o) return;

  const stages = [
    { key: 'RAW_SIGNAL', label: '📡 Tín Hiệu Thô' },
    { key: 'QUALIFIED', label: '🔍 Đã Xác Thực' },
    { key: 'MATCHED', label: '🤝 Ráp Khớp Cung-Cầu' },
    { key: 'OUTREACH', label: '📞 Tiếp Cận' },
    { key: 'NEGOTIATING', label: '💼 Đàm Phán' },
    { key: 'INTERNAL_REVIEW', label: '⚖️ Thẩm Định Nội Bộ' },
    { key: 'CLOSED_WON', label: '🏆 Chốt Đơn (Won)' },
    { key: 'CLOSED_LOST', label: '❌ Tạm Dừng / Trượt' }
  ];

  openModal(`🎯 Chi Tiết Cơ Hội: ${escapeHtml(o.title)}`, `
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;background:rgba(255,255,255,0.03);padding:10px 14px;border-radius:6px">
      <div>
        <span class="badge" style="font-family:var(--mono);color:#c7d2fe">${o.id}</span>
        <span class="badge" style="text-transform:uppercase;margin-left:6px">${o.channel || 'zalo'}</span>
      </div>
      <div>
        <span class="badge live"><i class="ph ph-fire"></i> Độ nóng: ${o.heat_score || 60}°</span>
        <span class="badge good" style="margin-left:6px">Độ tin cậy: ${o.confidence_score || 75}%</span>
      </div>
    </div>

    <div class="form-group">
      <label class="form-label">Tên Tiêu Đề Cơ Hội</label>
      <input type="text" class="form-input" id="edit-opp-title" value="${escapeHtml(o.title || '')}">
    </div>

    <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
      <div class="form-group">
        <label class="form-label">Đối Tác / Khách Hàng</label>
        <input type="text" class="form-input" id="edit-opp-contact" value="${escapeHtml(o.contact_name || '')}">
      </div>
      <div class="form-group">
        <label class="form-label">Giá Trị Ước Tính (VND)</label>
        <input type="number" class="form-input" id="edit-opp-value" value="${o.estimated_value || 0}">
      </div>
    </div>

    <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
      <div class="form-group">
        <label class="form-label">Giai Đoạn Hiện Tại (Kanban Stage)</label>
        <select class="form-select" id="edit-opp-stage">
          ${stages.map(s => `<option value="${s.key}" ${(s.key === o.stage || (s.key === 'CLOSED_WON' && o.stage === 'WON')) ? 'selected' : ''}>${s.label}</option>`).join('')}
        </select>
      </div>
      <div class="form-group">
        <label class="form-label">Người Phụ Trách (Owner)</label>
        <input type="text" class="form-input" id="edit-opp-owner" value="${escapeHtml(o.owner || 'Anh Cơ La (Ryan)')}">
      </div>
    </div>

    <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
      <div class="form-group">
        <label class="form-label">Xác Suất Thắng (% Win Rate: <span id="win-prob-label">${o.win_probability || 50}</span>%)</label>
        <input type="range" min="5" max="100" step="5" class="pct-slider" id="edit-opp-win-prob" value="${o.win_probability || 50}" oninput="document.getElementById('win-prob-label').innerText=this.value" style="width:100%;margin-top:8px">
      </div>
      <div class="form-group">
        <label class="form-label">Độ Nóng Cơ Hội</label>
        <input type="number" class="form-input" id="edit-opp-heat" value="${o.heat_score || 60}">
      </div>
    </div>

    <div class="form-group">
      <label class="form-label">Tóm Tắt Nhu Cầu Cụ Thể (Ý Định Khách Hàng)</label>
      <textarea class="form-textarea" id="edit-opp-summary" style="height:75px">${escapeHtml(o.need_summary || '')}</textarea>
    </div>

    <div class="form-group">
      <label class="form-label">Ghi Chú Rủi Ro / Kế Hoạch Tiếp Cận</label>
      <input type="text" class="form-input" id="edit-opp-risk" value="${escapeHtml(o.risk_notes || '')}">
    </div>

    <div style="display:flex;justify-content:space-between;align-items:center;margin-top:14px;padding-top:12px;border-top:1px solid var(--color-divider)">
      <div style="display:flex;gap:6px">
        <button class="btn sm" style="background:rgba(16, 185, 129, 0.15);color:#34d399;border:1px solid rgba(16, 185, 129, 0.3)" onclick="quickCreateQuotationFromEvent('${o.source_event_id || ''}', '${escapeHtml(o.contact_name || '')}', '${escapeHtml(o.need_summary || '')}')">
          <i class="ph ph-file-text"></i> Soạn Báo Giá Word
        </button>
        <button class="btn sm" style="background:rgba(168,85,247,0.15);color:#c084fc;border:1px solid rgba(168,85,247,0.3)" onclick="quickMatchOpportunity('${o.id}')">
          <i class="ph ph-arrows-merge"></i> Ráp Khớp Cung-Cầu
        </button>
      </div>
      <button class="btn sm danger" onclick="deleteOpportunity('${o.id}')">
        <i class="ph ph-trash"></i> Xóa Deal
      </button>
    </div>
  `, async () => {
    const title = $('#edit-opp-title').value.trim();
    const contact_name = $('#edit-opp-contact').value.trim();
    const estimated_value = parseFloat($('#edit-opp-value').value) || 0;
    const stage = $('#edit-opp-stage').value;
    const owner = $('#edit-opp-owner').value.trim();
    const win_probability = parseFloat($('#edit-opp-win-prob').value) || 50;
    const heat_score = parseFloat($('#edit-opp-heat').value) || 60;
    const need_summary = $('#edit-opp-summary').value.trim();
    const risk_notes = $('#edit-opp-risk').value.trim();

    showToast('Đang cập nhật cơ hội...');
    const res = await fetch('/api/data_factory/opportunity/update', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        id: oppId,
        title, contact_name, estimated_value, stage, owner,
        win_probability, heat_score, need_summary, risk_notes
      })
    });
    const d = await res.json();
    if (d.ok) {
      closeModal();
      showToast('Đã cập nhật cơ hội thành công!');
      await fetchAllData();
    } else {
      showToast('Lỗi cập nhật: ' + d.error);
    }
  }, false, 'Lưu Thay Đổi');
}

async function quickMatchOpportunity(oppId) {
  showToast('Đang quét và ráp khớp cung-cầu...');
  try {
    const res = await fetch('/api/data_factory/opportunity/match', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ opp_id: oppId })
    });
    const d = await res.json();
    if (d.ok && d.match?.matched) {
      showToast(`🎯 Ráp khớp thành công: ${d.match.service_name} (${(d.match.recommended_price/1000000).toFixed(0)}tr ₫)!`);
      await fetchAllData();
    } else {
      showToast(d.match?.reason || 'Chưa tìm được dịch vụ phù hợp trong Catalog.');
    }
  } catch(e) {
    showToast('Lỗi: ' + e.message);
  }
}

async function deleteOpportunity(oppId) {
  if (!confirm('Sếp có chắc chắn muốn xóa cơ hội này khỏi Pipeline?')) return;
  showToast('Đang xóa cơ hội...');
  try {
    const res = await fetch('/api/data_factory/opportunity/delete', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ opp_id: oppId })
    });
    const d = await res.json();
    if (d.ok) {
      closeModal();
      showToast('Đã xóa cơ hội thành công!');
      await fetchAllData();
    }
  } catch(e) {
    showToast('Lỗi: ' + e.message);
  }
}

async function archiveMeaningEvent(evtId) {
  try {
    const res = await fetch('/api/data_factory/event/archive', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ event_id: evtId })
    });
    const d = await res.json();
    if (d.ok) {
      showToast('Đã xử lý xong (Inbox Zero)!');
      await fetchAllData();
    }
  } catch(e) {
    showToast('Lỗi: ' + e.message);
  }
}

function quickCreateQuotationFromEvent(evtId, contactName, content) {
  switchHub('tools', 'office');
  setTimeout(() => {
    const tInput = $('#doc-title') || $('input[name="title"]');
    if (tInput) tInput.value = `Báo Giá Dịch Vụ — Khách Hàng ${contactName}`;
    const pInput = $('#doc-customer') || $('input[name="customer"]');
    if (pInput) pInput.value = contactName;
    showToast(`Đã chuyển sang Bàn Soạn Thảo Văn Phòng cho ${contactName}!`);
  }, 150);
}
"""

if 'function handleOppDragStart' not in text:
    text = text.replace('</script>', handlers_code + '\n</script>')
    with open(dashboard_path, 'w', encoding='utf-8') as f:
        f.write(text)
    print('Appended handlers to dashboard.html!')
else:
    print('Handlers already present!')
