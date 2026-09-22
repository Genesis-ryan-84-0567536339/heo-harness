import re

html_path = "heo_harness/plugins/ui_dashboard/dashboard.html"

with open(html_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Thêm Nav Item vào Sidebar Navigation (sau Inbox Ý Nghĩa & Cơ Hội)
old_nav_item = """      <button class="nav-hub-item" data-hub="opportunities" onclick="switchHub('opportunities')">
        <div class="nav-hub-left">
          <i class="ph ph-kanban" style="color:#38bdf8"></i>
          <span>Inbox Ý Nghĩa & Cơ Hội</span>
        </div>
        <span class="nav-badge good" id="badge-opportunities">0</span>
      </button>"""

new_nav_item = """      <button class="nav-hub-item" data-hub="opportunities" onclick="switchHub('opportunities')">
        <div class="nav-hub-left">
          <i class="ph ph-kanban" style="color:#38bdf8"></i>
          <span>Inbox Ý Nghĩa & Cơ Hội</span>
        </div>
        <span class="nav-badge good" id="badge-opportunities">0</span>
      </button>
      <button class="nav-hub-item" data-hub="workbench" onclick="switchHub('workbench')">
        <div class="nav-hub-left">
          <i class="ph ph-briefcase" style="color:#f59e0b"></i>
          <span>Bàn Soạn Thảo Mậu Dịch</span>
        </div>
        <span class="nav-badge warm" style="background:rgba(245,158,11,0.2);color:#fbbf24;font-size:10px;font-weight:700">Copilot</span>
      </button>"""

if old_nav_item in content:
    content = content.replace(old_nav_item, new_nav_item)
    print("✓ Đã thêm Bàn Soạn Thảo Mậu Dịch vào Sidebar Navigation")
else:
    print("! Không tìm thấy old_nav_item")

# 2. Thêm Badge DCI vào Topbar Header
old_topbar = """        <div class="topbar-pill" id="topbar-core-badge" style="cursor:pointer" onclick="switchHub('assistant', 'quota')"><i class="ph ph-coins" style="color:var(--status-warn)"></i> <span>Token 0 ₫ · Antigravity</span></div>"""

new_topbar = """        <div class="topbar-pill" id="topbar-dci-badge" style="cursor:pointer;background:rgba(16,185,129,0.15);border:1px solid rgba(16,185,129,0.3);color:#34d399;font-weight:700" onclick="showDciModal()" title="Chỉ số độ tin cậy dữ liệu SSOT (SPEC-17)">
          <i class="ph ph-shield-check"></i> <span id="topbar-dci-text">DCI: 98% (Tin Cậy)</span>
        </div>
        <div class="topbar-pill" id="topbar-core-badge" style="cursor:pointer" onclick="switchHub('assistant', 'quota')"><i class="ph ph-coins" style="color:var(--status-warn)"></i> <span>Token 0 ₫ · Antigravity</span></div>"""

if old_topbar in content:
    content = content.replace(old_topbar, new_topbar)
    print("✓ Đã thêm Badge DCI vào Topbar Header")
else:
    print("! Không tìm thấy old_topbar")

# 3. Thêm Router case 'workbench' vào renderActiveHub()
old_router_case = """    case 'relationship_radar':
      titleEl.textContent = 'Radar Quan Hệ, Bản Đồ Mạng Lưới & Hồ Sơ Sống 360';
      subEl.textContent = 'Bản đồ mạng lưới đồ thị tương tác, phân tích nhiệt độ quan hệ, giải thích điểm Explainable AI, kiểm soát lượt bóng & thang đo 6 cấp tự trị';
      container.innerHTML = renderRelationshipRadarHub();
      if ((state.subtabs.relationship_radar || 'graph') === 'graph') {
        setTimeout(initRelationshipGraphCanvas, 60);
      }
      break;"""

new_router_case = """    case 'relationship_radar':
      titleEl.textContent = 'Radar Quan Hệ, Bản Đồ Mạng Lưới & Hồ Sơ Sống 360';
      subEl.textContent = 'Bản đồ mạng lưới đồ thị tương tác, phân tích nhiệt độ quan hệ, giải thích điểm Explainable AI, kiểm soát lượt bóng & thang đo 6 cấp tự trị';
      container.innerHTML = renderRelationshipRadarHub();
      if ((state.subtabs.relationship_radar || 'graph') === 'graph') {
        setTimeout(initRelationshipGraphCanvas, 60);
      }
      break;

    case 'workbench':
      titleEl.textContent = 'Bàn Soạn Thảo Thương Mại & Trợ Lý Mậu Dịch Copilot (SPEC-25 & 34)';
      subEl.textContent = 'Soạn báo giá, hợp đồng mậu dịch chuẩn SSOT, tính biên lợi nhuận, dịch song ngữ Việt-Anh-Trung & gửi 1 chạm qua Zalo/WhatsApp';
      container.innerHTML = renderCommercialWorkbenchHub();
      setTimeout(initCommercialWorkbenchUI, 60);
      break;"""

if old_router_case in content:
    content = content.replace(old_router_case, new_router_case)
    print("✓ Đã thêm router case workbench vào renderActiveHub")
else:
    print("! Không tìm thấy old_router_case")

# 4. Thêm hàm renderCommercialWorkbenchHub và code JS điều khiển
workbench_code = """
// =============================================================================
// CHẶNG 4 (MS-4): COMMERCIAL ACTION WORKBENCH & COMMERCIAL COPILOT (SPEC-25 & 34)
// =============================================================================

let workbenchState = {
  currentDealId: null,
  currentDoc: null,
  catalog: [],
  deals: [],
  activeLanguage: 'vi',
  discountPct: 0
};

function renderCommercialWorkbenchHub() {
  return `
    <div style="display:grid;grid-template-columns:380px 1fr;gap:20px;align-items:start;margin-bottom:30px">
      
      <!-- CỘT TRÁI: COMMERCIAL COPILOT PANEL (SPEC-34) -->
      <div class="card" style="padding:18px;background:rgba(15,23,42,0.92);border:1px solid rgba(255,255,255,0.12);border-radius:12px;box-shadow:0 8px 30px rgba(0,0,0,0.4);display:flex;flex-direction:column;gap:16px">
        
        <!-- Header Copilot -->
        <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid rgba(255,255,255,0.08);padding-bottom:12px">
          <div style="display:flex;align-items:center;gap:10px">
            <div style="width:34px;height:34px;border-radius:8px;background:linear-gradient(135deg, #818cf8, #c084fc);display:flex;align-items:center;justify-content:center;color:#fff;font-size:18px;box-shadow:0 0 12px rgba(129,140,248,0.4)">
              <i class="ph ph-sparkle"></i>
            </div>
            <div>
              <div style="font-size:13.5px;font-weight:700;color:#f8fafc">COMMERCIAL COPILOT</div>
              <div style="font-size:11px;color:#94a3b8">Trợ lý mậu dịch & Báo giá tự động</div>
            </div>
          </div>
          <span class="badge" style="background:rgba(16,185,129,0.2);color:#34d399;border:1px solid rgba(16,185,129,0.3);font-size:10px">SSOT v2.2</span>
        </div>

        <!-- 1. Chọn Cơ Hội Deal Cần Xử Lý -->
        <div>
          <label style="font-size:11px;font-weight:700;color:#cbd5e1;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:6px;display:flex;align-items:center;gap:6px">
            <i class="ph ph-target" style="color:#38bdf8"></i> 1. Chọn Cơ Hội Deals (Từ Radar)
          </label>
          <select class="form-select" id="wb-select-deal" style="width:100%;font-size:12px;background:rgba(0,0,0,0.4);border:1px solid rgba(255,255,255,0.18);color:#fff" onchange="onWorkbenchDealChanged(this.value)">
            <option value="">-- Đang nạp danh sách cơ hội --</option>
          </select>
        </div>

        <!-- 2. Nút Bấm Copilot Tự Động Soạn -->
        <button class="btn primary" onclick="triggerCopilotAutoDraft()" style="width:100%;padding:10px;justify-content:center;font-size:12.5px;font-weight:700;background:linear-gradient(135deg, #4f46e5, #7c3aed);box-shadow:0 4px 16px rgba(124,58,237,0.35);border:none">
          <i class="ph ph-magic-wand" style="font-size:16px"></i> ✨ Copilot Tự Động Soạn Báo Giá
        </button>

        <!-- 3. Ngôn Ngữ Văn Kiện (Việt / Anh / Trung) -->
        <div>
          <label style="font-size:11px;font-weight:700;color:#cbd5e1;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:6px;display:flex;align-items:center;gap:6px">
            <i class="ph ph-translate" style="color:#fbbf24"></i> 2. Ngôn Ngữ Văn Kiện
          </label>
          <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px">
            <button class="btn sm primary" id="btn-lang-vi" onclick="setWorkbenchLanguage('vi')" style="font-size:11px;padding:5px 0;justify-content:center">
              🇻🇳 Tiếng Việt
            </button>
            <button class="btn sm" id="btn-lang-en" onclick="setWorkbenchLanguage('en')" style="font-size:11px;padding:5px 0;justify-content:center;background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.15)">
              🇬🇧 English
            </button>
            <button class="btn sm" id="btn-lang-zh" onclick="setWorkbenchLanguage('zh')" style="font-size:11px;padding:5px 0;justify-content:center;background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.15)">
              🇨🇳 中文
            </button>
          </div>
        </div>

        <!-- 4. Thêm Module Dịch Vụ Từ Catalog (SPEC-18) -->
        <div>
          <label style="font-size:11px;font-weight:700;color:#cbd5e1;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:6px;display:flex;align-items:center;gap:6px">
            <i class="ph ph-plus-circle" style="color:#34d399"></i> 3. Bổ Sung Gói Từ Service Catalog
          </label>
          <div style="display:flex;gap:6px">
            <select class="form-select" id="wb-select-catalog-item" style="flex:1;font-size:11.5px;background:rgba(0,0,0,0.4);border:1px solid rgba(255,255,255,0.18);color:#fff">
              <option value="">-- Chọn dịch vụ niêm yết --</option>
            </select>
            <button class="btn sm primary" onclick="addSelectedCatalogModule()" style="padding:0 12px" title="Thêm vào báo giá">
              <i class="ph ph-plus"></i> Thêm
            </button>
          </div>
        </div>

        <!-- 5. Phân Tích Tài Chính & Biên Lợi Nhuận (Financial Analyzer) -->
        <div style="background:rgba(0,0,0,0.3);border:1px solid rgba(255,255,255,0.08);border-radius:10px;padding:12px">
          <div style="font-size:11px;font-weight:700;color:#cbd5e1;margin-bottom:8px;display:flex;justify-content:space-between">
            <span>PHÂN TÍCH TÀI CHÍNH MẬU DỊCH</span>
            <span id="wb-margin-badge" style="color:#34d399;font-weight:700">Margin: 75%</span>
          </div>
          
          <div style="display:flex;justify-content:space-between;font-size:11.5px;color:#94a3b8;margin-bottom:4px">
            <span>Tổng niêm yết (Subtotal):</span>
            <span id="wb-calc-subtotal" style="color:#fff;font-weight:600">0 ₫</span>
          </div>

          <div style="display:flex;justify-content:space-between;align-items:center;font-size:11.5px;color:#94a3b8;margin-bottom:4px">
            <span>Chiết khấu ưu đãi (%):</span>
            <input type="number" id="wb-input-discount" value="0" min="0" max="30" style="width:65px;height:24px;font-size:11.5px;padding:2px 6px;text-align:right;background:rgba(0,0,0,0.4);border:1px solid rgba(255,255,255,0.2);color:#fb7185;border-radius:4px" onchange="onWorkbenchDiscountChanged(this.value)">
          </div>

          <div style="display:flex;justify-content:space-between;font-size:13px;color:#38bdf8;font-weight:700;border-top:1px solid rgba(255,255,255,0.08);padding-top:6px;margin-top:6px">
            <span>Tổng thanh toán:</span>
            <span id="wb-calc-total">0 ₫</span>
          </div>
        </div>

        <!-- 6. Lời Khuyên Copilot Insights -->
        <div id="wb-copilot-insight-box" style="background:rgba(99,102,241,0.08);border:1px solid rgba(99,102,241,0.25);border-radius:8px;padding:10px 12px;font-size:11px;color:#c7d2fe;line-height:1.4">
          <div style="font-weight:700;color:#818cf8;display:flex;align-items:center;gap:4px;margin-bottom:4px">
            <i class="ph ph-info"></i> Nhận định mậu dịch của Copilot:
          </div>
          <div id="wb-copilot-insight-text">Chọn một cơ hội ở trên hoặc nhấp nút Copilot để hệ thống tự động thiết kế báo giá tối ưu nhất.</div>
        </div>

      </div>

      <!-- CỘT PHẢI: GIẤY BÁO GIÁ DOANH NGHIỆP TRỰC QUAN (LIVE QUOTATION CANVAS) -->
      <div class="card" style="padding:24px;background:#ffffff;color:#0f172a;border-radius:12px;box-shadow:0 12px 40px rgba(0,0,0,0.5);display:flex;flex-direction:column;gap:18px;min-height:750px;position:relative">
        
        <!-- Header Báo Giá Chuẩn Doanh Nghiệp -->
        <div style="display:flex;justify-content:space-between;align-items:flex-start;border-bottom:2px solid #0f172a;padding-bottom:14px">
          <div>
            <div style="display:flex;align-items:center;gap:8px">
              <div style="width:32px;height:32px;border-radius:6px;background:#0f172a;color:#fff;display:flex;align-items:center;justify-content:center;font-weight:900;font-size:16px">G</div>
              <div>
                <div style="font-size:16px;font-weight:800;color:#0f172a;letter-spacing:0.5px">GEN-HARNESS OS</div>
                <div style="font-size:10px;color:#64748b;text-transform:uppercase">Genesis Executive Intelligence</div>
              </div>
            </div>
            <div style="font-size:11px;color:#475569;margin-top:6px">
              Đơn vị phát hành: <b>Anh Cơ La (Ryan) / Tổng Chỉ Huy Tối Cao</b><br>
              Email: <b>genesis.corp.os@gmail.com</b> · Trụ sở: Cloud On-Premise
            </div>
          </div>

          <div style="text-align:right">
            <div style="font-size:18px;font-weight:900;color:#0284c7;letter-spacing:1px" id="preview-doc-type">BÁO GIÁ THƯƠNG MẠI</div>
            <div style="font-size:11px;color:#64748b;margin-top:4px">
              Số: <b id="preview-doc-id">DOC-20260921-001</b><br>
              Ngày lập: <b id="preview-doc-date">21/09/2026</b><br>
              Hiệu lực đến: <b id="preview-doc-valid">11/10/2026</b>
            </div>
          </div>
        </div>

        <!-- Khung Người Nhận & Đơn Vị Thụ Hưởng -->
        <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;padding:12px 16px;display:flex;justify-content:space-between">
          <div>
            <div style="font-size:10.5px;color:#64748b;text-transform:uppercase;font-weight:700">Đơn vị nhận đề xuất:</div>
            <div style="font-size:14px;font-weight:800;color:#0f172a;margin-top:2px" id="preview-contact-company">VinaSupply Corp</div>
            <div style="font-size:11.5px;color:#334155;margin-top:2px">
              Người đại diện: <b id="preview-contact-name">Chị Mai Phương</b> · Kênh: <span class="badge" style="background:#e0f2fe;color:#0284c7;font-size:10px" id="preview-contact-channel">Zalo</span>
            </div>
          </div>
          <div style="text-align:right">
            <div style="font-size:10.5px;color:#64748b;text-transform:uppercase;font-weight:700">Trạng thái tài liệu:</div>
            <span class="badge" id="preview-doc-status-badge" style="background:#fef3c7;color:#b45309;font-weight:700;font-size:11px;margin-top:4px;display:inline-block">DRAFT (BẢN NHÁP)</span>
          </div>
        </div>

        <!-- Thư Ngỏ (Cover Letter) Có Thể Gõ Soạn Thảo Trực Tiếp -->
        <div>
          <label style="font-size:11px;font-weight:700;color:#475569;margin-bottom:4px;display:block">LỜI NGỎ / THƯ CHÀO HÀNG:</label>
          <textarea id="preview-cover-letter" class="form-input" rows="4" style="width:100%;font-size:12px;line-height:1.5;color:#1e293b;background:#ffffff;border:1px solid #cbd5e1;padding:8px 10px;border-radius:6px" placeholder="Nhập lời ngỏ thương mại gửi đối tác..."></textarea>
        </div>

        <!-- Bảng Danh Sách Dịch Vụ & Chi Phí (Items Table) -->
        <div>
          <div style="font-size:11px;font-weight:700;color:#475569;margin-bottom:6px">CHI TIẾT HẠNG MỤC DỊCH VỤ & PHẦN MỀM:</div>
          <table style="width:100%;border-collapse:collapse;font-size:11.5px">
            <thead>
              <tr style="background:#f1f5f9;border-bottom:2px solid #cbd5e1;color:#334155;text-align:left">
                <th style="padding:8px 10px">STT</th>
                <th style="padding:8px 10px">Tên Module / Dịch Vụ</th>
                <th style="padding:8px 10px;text-align:center">ĐVT</th>
                <th style="padding:8px 10px;text-align:right">Đơn Giá (VNĐ)</th>
                <th style="padding:8px 10px;text-align:center">SL</th>
                <th style="padding:8px 10px;text-align:right">Thành Tiền (VNĐ)</th>
                <th style="padding:8px 10px;text-align:center;width:40px">Xóa</th>
              </tr>
            </thead>
            <tbody id="preview-items-tbody">
              <tr>
                <td colspan="7" style="padding:20px;text-align:center;color:#94a3b8">Chưa có hạng mục nào. Hãy chọn Deal hoặc bấm Copilot ở cột trái.</td>
              </tr>
            </tbody>
            <tfoot>
              <tr style="border-top:1px solid #e2e8f0;font-size:12px;color:#475569">
                <td colspan="5" style="padding:8px 10px;text-align:right;font-weight:600">Cộng tiền dịch vụ:</td>
                <td style="padding:8px 10px;text-align:right;font-weight:700" id="preview-subtotal-text">0 ₫</td>
                <td></td>
              </tr>
              <tr style="font-size:12px;color:#dc2626">
                <td colspan="5" style="padding:4px 10px;text-align:right;font-weight:600">Chiết khấu ưu đãi:</td>
                <td style="padding:4px 10px;text-align:right;font-weight:700" id="preview-discount-text">0 ₫</td>
                <td></td>
              </tr>
              <tr style="background:#f8fafc;border-top:2px solid #0f172a;font-size:14px;color:#0284c7">
                <td colspan="5" style="padding:10px;text-align:right;font-weight:800">TỔNG CỘNG THANH TOÁN:</td>
                <td style="padding:10px;text-align:right;font-weight:900" id="preview-total-text">0 ₫</td>
                <td></td>
              </tr>
            </tfoot>
          </table>
        </div>

        <!-- Điều Khoản Thanh Toán & Hiệu Lực -->
        <div>
          <label style="font-size:11px;font-weight:700;color:#475569;margin-bottom:4px;display:block">ĐIỀU KHOẢN THANH TOÁN & BÀN GIAO:</label>
          <input type="text" id="preview-payment-terms" class="form-input" style="width:100%;font-size:11.5px;color:#1e293b;background:#ffffff;border:1px solid #cbd5e1;padding:6px 10px;border-radius:6px" value="Tạm ứng 50% ngay sau khi ký; Thanh toán 50% còn lại sau khi bàn giao nghiệm thu UAT.">
        </div>

        <!-- 3 Nút Hành Động Mậu Dịch (Action Bar) -->
        <div style="border-top:1px solid #e2e8f0;padding-top:16px;margin-top:auto;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px">
          <div style="display:flex;gap:8px">
            <button class="btn sm" onclick="saveCurrentWorkbenchDoc()" style="color:#0f172a;border:1px solid #cbd5e1;background:#f8fafc">
              <i class="ph ph-floppy-disk"></i> Lưu Bản Nháp
            </button>
            <button class="btn sm" onclick="window.print()" style="color:#0f172a;border:1px solid #cbd5e1;background:#f8fafc">
              <i class="ph ph-printer"></i> In Báo Giá
            </button>
          </div>

          <div style="display:flex;gap:8px">
            <!-- Nút Trình Sếp Duyệt -->
            <button class="btn" onclick="requestDocApprovalAction()" style="background:#f59e0b;color:#fff;border:none;font-weight:700;padding:8px 14px;display:flex;align-items:center;gap:6px">
              <i class="ph ph-seal-check"></i> 👑 Trình Sếp Phê Duyệt
            </button>
            
            <!-- Nút Gửi Trực Tiếp 1 Chạm -->
            <button class="btn primary" onclick="sendDocDirectAction()" style="background:#0284c7;color:#fff;border:none;font-weight:800;padding:8px 16px;display:flex;align-items:center;gap:6px;box-shadow:0 4px 12px rgba(2,132,199,0.35)">
              <i class="ph ph-paper-plane-tilt"></i> 🚀 Gửi 1 Chạm Qua Kênh
            </button>
          </div>
        </div>

      </div>

    </div>
  `;
}

// ----------------------------------------------------
// HANDLERS CHO COMMERCIAL WORKBENCH
// ----------------------------------------------------

async function initCommercialWorkbenchUI() {
  try {
    // 1. Nạp Service Catalog
    const catRes = await fetch('/api/commercial/catalog').then(r => r.json()).catch(() => ({}));
    if (catRes.ok && catRes.catalog) {
      workbenchState.catalog = catRes.catalog;
      populateCatalogDropdown(catRes.catalog);
    }

    // 2. Nạp danh sách Opportunities từ Data Factory
    const oppRes = await fetch('/api/data_factory/opportunities').then(r => r.json()).catch(() => ({}));
    if (oppRes.ok && oppRes.opportunities) {
      workbenchState.deals = oppRes.opportunities;
      populateDealsDropdown(oppRes.opportunities);
    }

    // Nếu có dealId được chọn sẵn từ trước
    if (workbenchState.currentDealId) {
      const dealSelect = document.getElementById('wb-select-deal');
      if (dealSelect) dealSelect.value = workbenchState.currentDealId;
      triggerCopilotAutoDraft();
    } else if (workbenchState.deals && workbenchState.deals.length > 0) {
      // Tự động chọn deal đầu tiên
      const dealSelect = document.getElementById('wb-select-deal');
      if (dealSelect) {
        dealSelect.value = workbenchState.deals[0].id;
        workbenchState.currentDealId = workbenchState.deals[0].id;
        triggerCopilotAutoDraft();
      }
    }
  } catch (err) {
    console.error('Lỗi init Workbench UI:', err);
  }
}

function populateDealsDropdown(deals) {
  const sel = document.getElementById('wb-select-deal');
  if (!sel) return;
  sel.innerHTML = deals.map(d => {
    const valStr = d.estimated_value ? ` (${(d.estimated_value/1e6).toFixed(0)}tr ₫)` : '';
    return `<option value="${d.id}">[${d.id}] ${d.contact_name} · ${d.title}${valStr}</option>`;
  }).join('');
}

function populateCatalogDropdown(catalog) {
  const sel = document.getElementById('wb-select-catalog-item');
  if (!sel) return;
  sel.innerHTML = `<option value="">-- Chọn dịch vụ niêm yết --</option>` + catalog.map(c => {
    return `<option value="${c.code}">[${c.code}] ${c.name} (${(c.base_price/1e6).toFixed(0)}tr ₫)</option>`;
  }).join('');
}

function onWorkbenchDealChanged(dealId) {
  workbenchState.currentDealId = dealId;
  triggerCopilotAutoDraft();
}

async function triggerCopilotAutoDraft() {
  const dealId = workbenchState.currentDealId || (document.getElementById('wb-select-deal') ? document.getElementById('wb-select-deal').value : null);
  if (!dealId) {
    showToast('Vui lòng chọn một cơ hội Deal');
    return;
  }

  showToast('✨ Commercial Copilot đang bóc tách & soạn báo giá...');

  try {
    const res = await fetch('/api/commercial/generate_copilot', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        deal_id: dealId,
        language: workbenchState.activeLanguage
      })
    }).then(r => r.json());

    if (!res.ok) throw new Error(res.error || 'Lỗi sinh báo giá');

    workbenchState.currentDoc = res.document;
    renderCurrentQuotationPreview(res.document);

    // Cập nhật insight box
    if (res.copilot_insights) {
      const insText = document.getElementById('wb-copilot-insight-text');
      if (insText) {
        insText.innerHTML = `
          <div><b>Phù hợp:</b> ${res.copilot_insights.match_reason}</div>
          <div><b>Chiết khấu:</b> ${res.copilot_insights.discount_reason}</div>
          <div><b>Biên lợi nhuận:</b> <span style="color:#34d399;font-weight:700">${res.copilot_insights.estimated_margin}</span></div>
        `;
      }
    }
  } catch (err) {
    showToast('Lỗi: ' + err.message);
  }
}

function setWorkbenchLanguage(lang) {
  workbenchState.activeLanguage = lang;
  ['vi', 'en', 'zh'].forEach(l => {
    const btn = document.getElementById('btn-lang-' + l);
    if (btn) btn.className = 'btn sm ' + (l === lang ? 'primary' : 'subtle');
  });
  triggerCopilotAutoDraft();
}

function addSelectedCatalogModule() {
  const sel = document.getElementById('wb-select-catalog-item');
  if (!sel || !sel.value) {
    showToast('Vui lòng chọn một gói dịch vụ');
    return;
  }
  const code = sel.value;
  const srv = workbenchState.catalog.find(c => c.code === code);
  if (!srv) return;

  if (!workbenchState.currentDoc) {
    workbenchState.currentDoc = { items: [] };
  }
  if (!workbenchState.currentDoc.items) workbenchState.currentDoc.items = [];

  workbenchState.currentDoc.items.push({
    code: srv.code,
    name: srv.name,
    unit: srv.unit,
    unit_price: srv.base_price,
    quantity: 1,
    total: srv.base_price,
    cost: srv.cost_price
  });

  recalculateWorkbenchDoc();
  renderCurrentQuotationPreview(workbenchState.currentDoc);
  showToast(`Đã thêm ${srv.name} vào báo giá`);
}

function removeQuotationItem(idx) {
  if (!workbenchState.currentDoc || !workbenchState.currentDoc.items) return;
  workbenchState.currentDoc.items.splice(idx, 1);
  recalculateWorkbenchDoc();
  renderCurrentQuotationPreview(workbenchState.currentDoc);
}

function onWorkbenchDiscountChanged(val) {
  workbenchState.discountPct = parseFloat(val) || 0;
  recalculateWorkbenchDoc();
  renderCurrentQuotationPreview(workbenchState.currentDoc);
}

function recalculateWorkbenchDoc() {
  if (!workbenchState.currentDoc) return;
  const items = workbenchState.currentDoc.items || [];
  let subtotal = 0;
  let totalCost = 0;

  items.forEach(it => {
    it.total = (it.unit_price || 0) * (it.quantity || 1);
    subtotal += it.total;
    totalCost += (it.cost || (it.unit_price * 0.25)) * (it.quantity || 1);
  });

  const discountAmount = subtotal * (workbenchState.discountPct / 100);
  const totalAmount = subtotal - discountAmount;
  const marginPct = totalAmount > 0 ? ((totalAmount - totalCost) / totalAmount * 100) : 0;

  workbenchState.currentDoc.subtotal_amount = subtotal;
  workbenchState.currentDoc.discount_amount = discountAmount;
  workbenchState.currentDoc.total_amount = totalAmount;
  workbenchState.currentDoc.margin_pct = Math.round(marginPct * 10) / 10;
}

function renderCurrentQuotationPreview(doc) {
  if (!doc) return;

  // Cập nhật các trường xem trước
  const setText = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };
  const setVal = (id, val) => { const el = document.getElementById(id); if (el) el.value = val; };

  setText('preview-doc-id', doc.id || 'DOC-PREVIEW');
  setText('preview-doc-date', (doc.created_at || '').slice(0, 10) || new Date().toISOString().slice(0, 10));
  setText('preview-doc-valid', doc.valid_until || '20 ngày kể từ ngày lập');
  setText('preview-contact-company', doc.company || 'Doanh Nghiệp Đối Tác');
  setText('preview-contact-name', doc.contact_name || 'Đại diện đối tác');
  setText('preview-contact-channel', (doc.channel || 'Zalo').toUpperCase());

  const statusBadge = document.getElementById('preview-doc-status-badge');
  if (statusBadge) {
    statusBadge.textContent = doc.status || 'DRAFT';
    if (doc.status === 'SENT') {
      statusBadge.style.background = '#dcfce7';
      statusBadge.style.color = '#15803d';
    } else if (doc.status === 'WAITING_APPROVAL') {
      statusBadge.style.background = '#fef3c7';
      statusBadge.style.color = '#b45309';
    }
  }

  setVal('preview-cover-letter', doc.cover_letter || '');
  setVal('preview-payment-terms', doc.payment_terms || '');

  // Render bảng sản phẩm
  const tbody = document.getElementById('preview-items-tbody');
  if (tbody) {
    const items = doc.items || [];
    if (items.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" style="padding:20px;text-align:center;color:#94a3b8">Chưa có hạng mục nào.</td></tr>`;
    } else {
      tbody.innerHTML = items.map((it, idx) => `
        <tr style="border-bottom:1px solid #f1f5f9;color:#1e293b">
          <td style="padding:8px 10px">${idx + 1}</td>
          <td style="padding:8px 10px;font-weight:600">${escapeHtml(it.name)}</td>
          <td style="padding:8px 10px;text-align:center;color:#64748b">${it.unit || 'Gói'}</td>
          <td style="padding:8px 10px;text-align:right">${(it.unit_price || 0).toLocaleString('vi-VN')} ₫</td>
          <td style="padding:8px 10px;text-align:center">${it.quantity || 1}</td>
          <td style="padding:8px 10px;text-align:right;font-weight:700">${((it.unit_price || 0) * (it.quantity || 1)).toLocaleString('vi-VN')} ₫</td>
          <td style="padding:8px 10px;text-align:center">
            <button onclick="removeQuotationItem(${idx})" style="border:none;background:none;color:#ef4444;cursor:pointer;font-size:14px" title="Xóa hạng mục">✕</button>
          </td>
        </tr>
      `).join('');
    }
  }

  const subtotal = doc.subtotal_amount || 0;
  const discount = doc.discount_amount || 0;
  const total = doc.total_amount || 0;
  const margin = doc.margin_pct || 75;

  setText('preview-subtotal-text', `${subtotal.toLocaleString('vi-VN')} ₫`);
  setText('preview-discount-text', `-${discount.toLocaleString('vi-VN')} ₫`);
  setText('preview-total-text', `${total.toLocaleString('vi-VN')} ₫`);

  setText('wb-calc-subtotal', `${subtotal.toLocaleString('vi-VN')} ₫`);
  setText('wb-calc-total', `${total.toLocaleString('vi-VN')} ₫`);
  setText('wb-margin-badge', `Margin: ${margin}%`);
}

async function saveCurrentWorkbenchDoc() {
  if (!workbenchState.currentDoc) {
    showToast('Không có văn kiện để lưu');
    return;
  }
  const cl = document.getElementById('preview-cover-letter');
  if (cl) workbenchState.currentDoc.cover_letter = cl.value;
  const pt = document.getElementById('preview-payment-terms');
  if (pt) workbenchState.currentDoc.payment_terms = pt.value;

  try {
    const res = await fetch('/api/commercial/save_document', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ document: workbenchState.currentDoc })
    }).then(r => r.json());

    if (res.ok) {
      showToast('✓ Đã lưu bản nháp báo giá thành công!');
    } else {
      showToast('Lỗi lưu: ' + (res.error || 'Thất bại'));
    }
  } catch (err) {
    showToast('Lỗi kết nối: ' + err.message);
  }
}

async function requestDocApprovalAction() {
  await saveCurrentWorkbenchDoc();
  if (!workbenchState.currentDoc || !workbenchState.currentDoc.id) return;

  try {
    const res = await fetch('/api/commercial/send_or_approve', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        id: workbenchState.currentDoc.id,
        action: 'request_approval'
      })
    }).then(r => r.json());

    if (res.ok) {
      showToast('👑 Đã trình văn kiện vào Hàng Đợi Phê Duyệt Chiến Lược của Sếp!');
      workbenchState.currentDoc.status = 'WAITING_APPROVAL';
      renderCurrentQuotationPreview(workbenchState.currentDoc);
    } else {
      showToast('Lỗi: ' + res.error);
    }
  } catch (err) {
    showToast('Lỗi: ' + err.message);
  }
}

async function sendDocDirectAction() {
  await saveCurrentWorkbenchDoc();
  if (!workbenchState.currentDoc || !workbenchState.currentDoc.id) return;

  const ch = (workbenchState.currentDoc.channel || 'Zalo').toUpperCase();
  const cname = workbenchState.currentDoc.contact_name || 'Khách hàng';

  if (!confirm(`Xác nhận gửi báo giá trị giá ${workbenchState.currentDoc.total_amount.toLocaleString('vi-VN')} ₫ qua kênh ${ch} cho ${cname}?`)) {
    return;
  }

  try {
    const res = await fetch('/api/commercial/send_or_approve', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        id: workbenchState.currentDoc.id,
        action: 'approve_and_send'
      })
    }).then(r => r.json());

    if (res.ok) {
      showToast(`🚀 Đã gửi thành công qua ${ch} cho ${cname}!`);
      workbenchState.currentDoc.status = 'SENT';
      renderCurrentQuotationPreview(workbenchState.currentDoc);
    } else {
      showToast('Lỗi: ' + res.error);
    }
  } catch (err) {
    showToast('Lỗi: ' + err.message);
  }
}

// Modal Data Confidence Index (SPEC-17)
async function showDciModal() {
  try {
    const res = await fetch('/api/system/dci').then(r => r.json());
    if (!res.ok) throw new Error('Không lấy được DCI');

    const m = res.metrics || {};
    const recs = res.recommendations || [];

    const modalHtml = `
      <div id="dci-modal-overlay" style="position:fixed;inset:0;background:rgba(0,0,0,0.7);backdrop-filter:blur(6px);z-index:9999;display:flex;align-items:center;justify-content:center;padding:20px">
        <div style="width:100%;max-width:550px;background:#0f172a;border:1px solid rgba(255,255,255,0.15);border-radius:14px;padding:24px;box-shadow:0 16px 48px rgba(0,0,0,0.6);color:#f8fafc">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;border-bottom:1px solid rgba(255,255,255,0.1);padding-bottom:12px">
            <div style="display:flex;align-items:center;gap:10px">
              <div style="width:36px;height:36px;border-radius:8px;background:rgba(16,185,129,0.2);color:#34d399;display:flex;align-items:center;justify-content:center;font-size:20px">
                <i class="ph ph-shield-check"></i>
              </div>
              <div>
                <div style="font-size:15px;font-weight:800">DATA CONFIDENCE INDEX (DCI)</div>
                <div style="font-size:11px;color:#94a3b8">Tiêu chuẩn kiểm định chất lượng dữ liệu (SPEC-17)</div>
              </div>
            </div>
            <button onclick="document.getElementById('dci-modal-overlay').remove()" style="border:none;background:none;color:#94a3b8;font-size:20px;cursor:pointer">✕</button>
          </div>

          <div style="background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.3);border-radius:10px;padding:16px;text-align:center;margin-bottom:16px">
            <div style="font-size:36px;font-weight:900;color:#34d399">${res.dci_score}%</div>
            <div style="font-size:13px;font-weight:700;color:#e2e8f0;margin-top:4px">${res.grade_label}</div>
            <div style="font-size:11px;color:#94a3b8;margin-top:2px">Đánh giá lúc: ${res.evaluated_at}</div>
          </div>

          <div style="display:flex;flex-direction:column;gap:10px;margin-bottom:16px">
            <div>
              <div style="display:flex;justify-content:space-between;font-size:11.5px;margin-bottom:4px">
                <span>1. Độ đầy đủ danh tính hồ sơ:</span>
                <b style="color:#38bdf8">${m.identity_completeness_pct}% (${m.total_contacts} Đối tác)</b>
              </div>
              <div style="height:6px;background:rgba(255,255,255,0.1);border-radius:3px;overflow:hidden">
                <div style="width:${m.identity_completeness_pct}%;height:100%;background:#38bdf8"></div>
              </div>
            </div>

            <div>
              <div style="display:flex;justify-content:space-between;font-size:11.5px;margin-bottom:4px">
                <span>2. Tỷ lệ sự kiện gán đối tượng:</span>
                <b style="color:#34d399">${m.event_mapping_rate_pct}% (${m.total_events} Sự kiện)</b>
              </div>
              <div style="height:6px;background:rgba(255,255,255,0.1);border-radius:3px;overflow:hidden">
                <div style="width:${m.event_mapping_rate_pct}%;height:100%;background:#34d399"></div>
              </div>
            </div>

            <div>
              <div style="display:flex;justify-content:space-between;font-size:11.5px;margin-bottom:4px">
                <span>3. Độ phủ định giá cơ hội:</span>
                <b style="color:#c084fc">${m.valuation_coverage_pct}% (${m.total_opportunities} Deals)</b>
              </div>
              <div style="height:6px;background:rgba(255,255,255,0.1);border-radius:3px;overflow:hidden">
                <div style="width:${m.valuation_coverage_pct}%;height:100%;background:#c084fc"></div>
              </div>
            </div>
          </div>

          <div style="background:rgba(0,0,0,0.3);border:1px solid rgba(255,255,255,0.08);border-radius:8px;padding:12px">
            <div style="font-size:11px;font-weight:700;color:#fbbf24;margin-bottom:6px">KHUYẾN NGHỊ TỐI ƯU HÓA SSOT:</div>
            <ul style="margin:0;padding-left:18px;font-size:11px;color:#cbd5e1;display:flex;flex-direction:column;gap:4px">
              ${recs.map(r => `<li>${escapeHtml(r)}</li>`).join('')}
            </ul>
          </div>

          <div style="text-align:right;margin-top:16px">
            <button class="btn primary sm" onclick="document.getElementById('dci-modal-overlay').remove()" style="padding:6px 16px">
              Đã Hiểu
            </button>
          </div>
        </div>
      </div>
    `;

    const div = document.createElement('div');
    div.innerHTML = modalHtml;
    document.body.appendChild(div.firstElementChild);
  } catch (err) {
    showToast('Lỗi nạp DCI: ' + err.message);
  }
}

// Chuyển nhanh từ Radar sang Workbench
function openWorkbenchForDeal(dealId) {
  workbenchState.currentDealId = dealId;
  switchHub('workbench');
}
"""

content += workbench_code
print("✓ Đã thêm các hàm JavaScript điều khiển Workbench, Copilot và DCI Modal")

with open(html_path, "w", encoding="utf-8") as f:
    f.write(content)

print("✓ Hoàn thành nâng cấp giao diện Workbench!")
