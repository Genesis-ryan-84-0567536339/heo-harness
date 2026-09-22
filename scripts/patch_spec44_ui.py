"""
Patch SPEC-44: Phase 4 — Làm được (Commercial Copilot, AI Quotation Studio, Autonomy Level 4-5)
into heo_harness/plugins/ui_dashboard/dashboard.html
"""

import os
import re

DASHBOARD_PATH = "heo_harness/plugins/ui_dashboard/dashboard.html"

with open(DASHBOARD_PATH, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add "Báo Giá" button to Opportunity Kanban cards
old_actions = """                      <button class="btn sm" style="padding:3px 7px;font-size:10.5px;background:rgba(168,85,247,0.15);color:#c084fc;border:1px solid rgba(168,85,247,0.3)" onclick="quickMatchOpportunity('${o.id}')" title="Tự động ráp khớp với catalog dịch vụ công ty">
                        <i class="ph ph-arrows-merge"></i> Ráp Khớp
                      </button>"""

new_actions = """                      <button class="btn sm" style="padding:3px 7px;font-size:10.5px;background:rgba(168,85,247,0.15);color:#c084fc;border:1px solid rgba(168,85,247,0.3)" onclick="quickMatchOpportunity('${o.id}')" title="Tự động ráp khớp với catalog dịch vụ công ty">
                        <i class="ph ph-arrows-merge"></i> Ráp Khớp
                      </button>
                      <button class="btn sm" style="padding:3px 7px;font-size:10.5px;background:rgba(16,185,129,0.15);color:#34d399;border:1px solid rgba(16,185,129,0.3)" onclick="openAIQuotationModal('${o.id}')" title="Tự động sinh Báo Giá Thông Minh AI (SPEC-44 Autonomy 4-5)">
                        <i class="ph ph-file-text"></i> Báo Giá
                      </button>"""

if old_actions in content:
    content = content.replace(old_actions, new_actions)
    print("Added Báo Giá button to Opportunity Kanban cards.")
else:
    print("Báo Giá button already added or anchor not found.")

# 2. Add Quotation Tab in Commercial Workbench
old_tabs = """          <button class="btn sm" id="tab-btn-supplies" onclick="switchMatchmakerTab('supplies')" style="font-size:12px;font-weight:700;padding:6px 14px">
            <i class="ph ph-package"></i> Kho Nguồn CUNG (<span id="count-tab-supplies">0</span>)
          </button>
        </div>"""

new_tabs = """          <button class="btn sm" id="tab-btn-supplies" onclick="switchMatchmakerTab('supplies')" style="font-size:12px;font-weight:700;padding:6px 14px">
            <i class="ph ph-package"></i> Kho Nguồn CUNG (<span id="count-tab-supplies">0</span>)
          </button>
          <button class="btn sm" id="tab-btn-quotations" onclick="switchMatchmakerTab('quotations')" style="font-size:12px;font-weight:700;padding:6px 14px">
            <i class="ph ph-file-text"></i> Bàn Soạn Thảo Báo Giá AI (Copilot)
          </button>
        </div>"""

if old_tabs in content:
    content = content.replace(old_tabs, new_tabs)
    print("Added Quotation Tab in Commercial Workbench.")
else:
    print("Quotation Tab already added or anchor not found.")

# 3. Add SPEC-44 JavaScript functions before </script>
spec44_js = """
// =============================================================================
// SPEC-44: COMMERCIAL COPILOT & AI QUOTATION STUDIO (AUTONOMY LEVEL 4-5)
// =============================================================================

let activeGeneratedQuotation = null;

async function openAIQuotationModal(dealId) {
  openModal('✨ Commercial Copilot — Soạn Báo Giá AI Thông Minh', `
    <div style="padding:16px;text-align:center;color:var(--color-neutral-400)">
      <i class="ph ph-spinner ph-spin" style="font-size:28px;color:#38bdf8;margin-bottom:8px;display:block"></i>
      Đang liên kết hồ sơ sống, catalog dịch vụ và tính toán chiết khấu tự động...
    </div>
  `);

  try {
    const res = await fetch('/api/commercial/generate_copilot', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ deal_id: dealId, language: 'vi' })
    }).then(r => r.json());

    if (!res.ok || !res.document) {
      showToast('Lỗi sinh báo giá: ' + (res.error || 'Không rõ lỗi'));
      closeModal();
      return;
    }

    const doc = res.document;
    activeGeneratedQuotation = doc;

    const modalBody = `
      <div style="display:flex;flex-direction:column;gap:14px">
        
        <!-- Header Phiếu Báo Giá -->
        <div style="background:rgba(255,255,255,0.03);padding:14px;border-radius:8px;border:1px solid rgba(255,255,255,0.08);display:flex;justify-content:space-between;align-items:flex-start">
          <div>
            <div style="font-size:15px;font-weight:700;color:#f8fafc">${escapeHtml(doc.title || 'Báo Giá Thương Mại')}</div>
            <div style="font-size:12px;color:var(--color-neutral-300);margin-top:3px">
              Khách hàng: <b>${escapeHtml(doc.contact_name)}</b> (${escapeHtml(doc.company || 'Doanh Nghiệp')}) · Kênh: <span style="text-transform:uppercase">${escapeHtml(doc.channel || 'Zalo')}</span>
            </div>
          </div>
          <div style="text-align:right">
            <span class="badge primary sm" style="font-family:var(--mono)">${doc.id}</span>
            <div style="font-size:11px;color:#34d399;margin-top:4px">
              Mức Tự Trị: <b>Cấp 4-5</b> (Có Thẩm Định)
            </div>
          </div>
        </div>

        <!-- Bảng Hạng Mục Dịch Vụ & Sản Phẩm -->
        <div style="border:1px solid var(--color-divider);border-radius:8px;overflow:hidden">
          <table style="width:100%;font-size:12px;border-collapse:collapse">
            <thead>
              <tr style="background:rgba(255,255,255,0.05);color:var(--color-neutral-400);border-bottom:1px solid var(--color-divider)">
                <th style="padding:8px 10px;text-align:left">Mã</th>
                <th style="padding:8px 10px;text-align:left">Hạng Mục / Dịch Vụ</th>
                <th style="padding:8px 10px;text-align:center">ĐVT</th>
                <th style="padding:8px 10px;text-align:right">Đơn Giá</th>
                <th style="padding:8px 10px;text-align:center">SL</th>
                <th style="padding:8px 10px;text-align:right">Thành Tiền</th>
              </tr>
            </thead>
            <tbody>
              ${(doc.items || []).map(it => `
                <tr style="border-bottom:1px solid rgba(255,255,255,0.04)">
                  <td style="padding:8px 10px;font-family:var(--mono);color:#94a3b8">${it.code}</td>
                  <td style="padding:8px 10px;color:var(--color-text);font-weight:600">${escapeHtml(it.name)}</td>
                  <td style="padding:8px 10px;text-align:center;color:#94a3b8">${it.unit}</td>
                  <td style="padding:8px 10px;text-align:right;color:#cbd5e1">${(it.unit_price || 0).toLocaleString('vi-VN')} ₫</td>
                  <td style="padding:8px 10px;text-align:center">${it.quantity || 1}</td>
                  <td style="padding:8px 10px;text-align:right;font-weight:700;color:#10b981">${(it.total || 0).toLocaleString('vi-VN')} ₫</td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>

        <!-- Tổng Kết Tài Chính & Điều Khoản -->
        <div style="display:grid;grid-template-columns:1.2fr 1fr;gap:14px">
          <div style="background:rgba(255,255,255,0.02);padding:12px;border-radius:8px;border:1px solid rgba(255,255,255,0.06);font-size:11.5px;color:var(--color-neutral-300);line-height:1.5">
            <div style="font-weight:700;color:#cbd5e1;margin-bottom:4px">Điều Khoản Thanh Toán & Giao Hàng:</div>
            <div>• Đợt 1: Tạm ứng 50% ngay khi ký hợp đồng</div>
            <div>• Đợt 2: Thanh toán 50% sau khi bàn giao nghiệm thu</div>
            <div>• Thời gian triển khai: 10 - 15 ngày làm việc</div>
            <div style="margin-top:6px;color:#a5b4fc">💡 Lý do chiết khấu: Khách hàng thân thiết có Heat Score cao</div>
          </div>

          <div style="background:rgba(255,255,255,0.02);padding:12px;border-radius:8px;border:1px solid rgba(255,255,255,0.06);display:flex;flex-direction:column;gap:6px;font-size:12px">
            <div style="display:flex;justify-content:space-between">
              <span style="color:#94a3b8">Tạm tính:</span>
              <span style="font-weight:600">${(doc.subtotal || 0).toLocaleString('vi-VN')} ₫</span>
            </div>
            <div style="display:flex;justify-content:space-between;color:#f59e0b">
              <span>Chiết khấu (${doc.discount_percent || 0}%):</span>
              <span>- ${(doc.discount_amount || 0).toLocaleString('vi-VN')} ₫</span>
            </div>
            <div style="display:flex;justify-content:space-between">
              <span style="color:#94a3b8">Thuế VAT (8%):</span>
              <span>+ ${(doc.tax_amount || 0).toLocaleString('vi-VN')} ₫</span>
            </div>
            <div style="border-top:1px solid rgba(255,255,255,0.1);padding-top:6px;display:flex;justify-content:space-between;font-size:14px;font-weight:800;color:#10b981">
              <span>TỔNG CỘNG:</span>
              <span>${(doc.total_amount || 0).toLocaleString('vi-VN')} ₫</span>
            </div>
            <div style="font-size:10.5px;color:#38bdf8;text-align:right">
              Biên lợi nhuận gộp ước tính: <b>${doc.gross_profit_margin || 65}%</b>
            </div>
          </div>
        </div>

        <!-- Hộp Hành Động Phân Cấp Tự Trị (SPEC-44) -->
        <div style="display:flex;justify-content:space-between;align-items:center;margin-top:8px;padding-top:10px;border-top:1px solid var(--color-divider);flex-wrap:wrap;gap:8px">
          <div style="font-size:11px;color:var(--color-neutral-400)">
            Chọn hành động phù hợp theo mức tự trị tổ chức
          </div>
          <div style="display:flex;gap:8px">
            <button class="btn sm" onclick="saveActiveQuotationDraft(false)" style="background:rgba(255,255,255,0.06)">
              <i class="ph ph-floppy-disk"></i> Lưu Nháp (Cấp 4)
            </button>
            <button class="btn sm primary" onclick="saveActiveQuotationDraft(true)" style="background:#10b981;border-color:#10b981">
              <i class="ph ph-paper-plane-tilt"></i> Phê Duyệt & Gửi Khách (Cấp 5)
            </button>
          </div>
        </div>

      </div>
    `;

    openModal('✨ Commercial Copilot — Soạn Báo Giá AI Thông Minh', modalBody);
  } catch (e) {
    showToast('Lỗi kết nối máy chủ: ' + e.message);
    closeModal();
  }
}

async function saveActiveQuotationDraft(autoApprove) {
  if (!activeGeneratedQuotation) {
    showToast('Không có dữ liệu báo giá');
    return;
  }
  showToast(autoApprove ? 'Đang duyệt và gửi báo giá...' : 'Đang lưu bản nháp vào Kho Tài Liệu...');
  try {
    const res = await fetch('/api/commercial/save_document', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ document: activeGeneratedQuotation })
    }).then(r => r.json());

    if (res.ok) {
      if (autoApprove) {
        await fetch('/api/commercial/send_or_approve', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ id: activeGeneratedQuotation.id, action: 'approve_and_send' })
        });
        showToast('✓ Đã phê duyệt và chuyển trạng thái báo giá sang ĐÃ GỬI (Cấp 5)!');
      } else {
        showToast('✓ Đã lưu bản nháp báo giá chờ Sếp duyệt (Cấp 4)!');
      }
      closeModal();
      await fetchAllData();
    } else {
      showToast('Lỗi: ' + (res.error || 'Không thể lưu tài liệu'));
    }
  } catch(e) {
    showToast('Lỗi kết nối: ' + e.message);
  }
}
"""

if "SPEC-44: COMMERCIAL COPILOT & AI QUOTATION STUDIO" not in content:
    # Insert right before </script>
    script_idx = content.rfind("</script>")
    if script_idx != -1:
        content = content[:script_idx] + spec44_js + "\n" + content[script_idx:]
        print("Appended SPEC-44 JavaScript functions inside <script>.")
    else:
        content += "\n" + spec44_js
        print("Appended SPEC-44 JavaScript at end.")
else:
    print("SPEC-44 JS already present.")

with open(DASHBOARD_PATH, "w", encoding="utf-8") as f:
    f.write(content)

print("SPEC-44 UI patch completed.")
