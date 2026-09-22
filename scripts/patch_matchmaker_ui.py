import re

with open("heo_harness/plugins/ui_dashboard/dashboard.html", "r", encoding="utf-8") as f:
    html = f.read()

# 1. Cập nhật Sidebar menu title
html = html.replace('<span>Bàn Soạn Thảo Mậu Dịch</span>', '<span>Sàn Mậu Dịch (Cung - Cầu)</span>')

# 2. Cập nhật router case workbench trong renderActiveHub
old_case = """    case 'workbench':
      titleEl.textContent = 'Bàn Soạn Thảo Thương Mại & Trợ Lý Mậu Dịch Copilot (SPEC-25 & 34)';
      subEl.textContent = 'Soạn báo giá, hợp đồng mậu dịch chuẩn SSOT, tính biên lợi nhuận, dịch song ngữ Việt-Anh-Trung & gửi 1 chạm qua Zalo/WhatsApp';
      container.innerHTML = renderCommercialWorkbenchHub();
      setTimeout(initCommercialWorkbenchUI, 60);
      break;"""

new_case = """    case 'workbench':
      titleEl.textContent = 'Sàn Phát Hiện & Ghép Nối Cung — Cầu Mậu Dịch (Supply-Demand Arbitrage Desk)';
      subEl.textContent = 'Quét tín hiệu đa kênh/group, phát hiện bên Cần & bên Có, tự động chấm thang điểm cơ hội (A+/A/B) & hỗ trợ Owner ra quyết định Next Action';
      container.innerHTML = renderCommercialWorkbenchHub();
      setTimeout(initCommercialWorkbenchUI, 60);
      break;"""

if old_case in html:
    html = html.replace(old_case, new_case)
else:
    print("Warning: old_case not found, searching via regex")

# 3. Thay thế toàn bộ khối code JS cũ của Commercial Workbench bằng Matchmaker Engine UI
# Tìm từ '// CHẶNG 4 (MS-4): COMMERCIAL ACTION WORKBENCH & COMMERCIAL COPILOT' đến '</script>'
pattern = r"// =+\s*\n// CHẶNG 4 \(MS-4\): COMMERCIAL ACTION WORKBENCH[\s\S]*?(?=</script>)"

new_matchmaker_code = '''// =============================================================================
// CHẶNG 4 (MS-4): SÀN PHÁT HIỆN & GHÉP NỐI CUNG - CẦU THƯƠNG MẠI (SPEC-25 & 34)
// Vòng lặp điều hành: LISTEN -> STRUCTURE -> SCORE -> MATCH -> ACT
// =============================================================================

let matchmakerState = {
  summary: {
    total_demands: 0,
    total_demand_budget: 0,
    total_supplies: 0,
    total_matches: 0,
    total_arbitrage_val: 0,
    avg_rating: 0,
    tier_distribution: {}
  },
  matches: [],
  demands: [],
  supplies: [],
  activeTab: 'matches', // 'matches', 'demands', 'supplies'
  filterTier: 'ALL',
  filterCategory: 'ALL',
  isLoading: false
};

function renderCommercialWorkbenchHub() {
  return `
    <div style="display:flex;flex-direction:column;gap:20px;margin-bottom:30px">
      
      <!-- 1. COMMAND KPI METRICS BAR (4 KHỐI CHỈ SỐ MẬU DỊCH) -->
      <div style="display:grid;grid-template-columns:repeat(4, 1fr);gap:16px" id="mm-kpi-bar">
        
        <div class="card" style="padding:16px;background:rgba(15,23,42,0.92);border:1px solid rgba(56,189,248,0.25);border-left:4px solid #38bdf8;border-radius:10px;box-shadow:0 4px 20px rgba(0,0,0,0.3)">
          <div style="display:flex;justify-content:space-between;align-items:flex-start">
            <span style="font-size:11px;font-weight:700;color:#94a3b8;text-transform:uppercase">🔵 Nguồn CẦU Đang Mở (Demands)</span>
            <span class="badge" style="background:rgba(56,189,248,0.15);color:#38bdf8;font-size:10px" id="mm-kpi-demands-badge">Đang Quét</span>
          </div>
          <div style="font-size:24px;font-weight:800;color:#f8fafc;margin:6px 0 2px 0" id="mm-kpi-total-demands">--</div>
          <div style="font-size:11.5px;color:#94a3b8" id="mm-kpi-demands-budget">Tổng ngân sách: -- ₫</div>
        </div>

        <div class="card" style="padding:16px;background:rgba(15,23,42,0.92);border:1px solid rgba(52,211,153,0.25);border-left:4px solid #34d399;border-radius:10px;box-shadow:0 4px 20px rgba(0,0,0,0.3)">
          <div style="display:flex;justify-content:space-between;align-items:flex-start">
            <span style="font-size:11px;font-weight:700;color:#94a3b8;text-transform:uppercase">🟢 Nguồn CUNG Sẵn Có (Supplies)</span>
            <span class="badge" style="background:rgba(52,211,153,0.15);color:#34d399;font-size:10px" id="mm-kpi-supplies-badge">Kho & Năng Lực</span>
          </div>
          <div style="font-size:24px;font-weight:800;color:#f8fafc;margin:6px 0 2px 0" id="mm-kpi-total-supplies">--</div>
          <div style="font-size:11.5px;color:#94a3b8">Đối tác & Nội bộ sẵn sàng</div>
        </div>

        <div class="card" style="padding:16px;background:rgba(15,23,42,0.92);border:1px solid rgba(192,132,252,0.25);border-left:4px solid #c084fc;border-radius:10px;box-shadow:0 4px 20px rgba(0,0,0,0.3)">
          <div style="display:flex;justify-content:space-between;align-items:flex-start">
            <span style="font-size:11px;font-weight:700;color:#94a3b8;text-transform:uppercase">🎯 Cơ Hội Đã Ráp Nối (Matches)</span>
            <span class="badge" style="background:rgba(192,132,252,0.15);color:#c084fc;font-size:10px" id="mm-kpi-matches-badge">Đã Chấm Điểm</span>
          </div>
          <div style="font-size:24px;font-weight:800;color:#f8fafc;margin:6px 0 2px 0" id="mm-kpi-total-matches">--</div>
          <div style="font-size:11.5px;color:#94a3b8" id="mm-kpi-avg-rating">Điểm trung bình: -- / 100đ</div>
        </div>

        <div class="card" style="padding:16px;background:rgba(15,23,42,0.92);border:1px solid rgba(251,191,36,0.25);border-left:4px solid #fbbf24;border-radius:10px;box-shadow:0 4px 20px rgba(0,0,0,0.3)">
          <div style="display:flex;justify-content:space-between;align-items:flex-start">
            <span style="font-size:11px;font-weight:700;color:#94a3b8;text-transform:uppercase">💎 Chênh Lệch / Lợi Nhuận Gộp</span>
            <span class="badge" style="background:rgba(251,191,36,0.15);color:#fbbf24;font-size:10px">Arbitrage Spread</span>
          </div>
          <div style="font-size:24px;font-weight:800;color:#fbbf24;margin:6px 0 2px 0" id="mm-kpi-arbitrage-val">-- ₫</div>
          <div style="font-size:11.5px;color:#34d399">Tiềm năng hoa hồng & thương mại</div>
        </div>

      </div>

      <!-- 2. TOOLBAR & VIEW CONTROLLER -->
      <div class="card" style="padding:12px 18px;background:rgba(15,23,42,0.85);border:1px solid rgba(255,255,255,0.1);border-radius:10px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px">
        
        <!-- Tab Navigation Switcher -->
        <div style="display:flex;gap:6px;background:rgba(0,0,0,0.4);padding:4px;border-radius:8px;border:1px solid rgba(255,255,255,0.08)">
          <button class="btn sm" id="tab-btn-matches" onclick="switchMatchmakerTab('matches')" style="font-size:12px;font-weight:700;padding:6px 14px">
            <i class="ph ph-handshake"></i> Cầu Nối Ráp Khớp & Thang Điểm (<span id="count-tab-matches">0</span>)
          </button>
          <button class="btn sm" id="tab-btn-demands" onclick="switchMatchmakerTab('demands')" style="font-size:12px;font-weight:700;padding:6px 14px">
            <i class="ph ph-trend-up"></i> Kho Nguồn CẦU (<span id="count-tab-demands">0</span>)
          </button>
          <button class="btn sm" id="tab-btn-supplies" onclick="switchMatchmakerTab('supplies')" style="font-size:12px;font-weight:700;padding:6px 14px">
            <i class="ph ph-package"></i> Kho Nguồn CUNG (<span id="count-tab-supplies">0</span>)
          </button>
        </div>

        <!-- Bộ Lọc Nhanh Hạng & Ngành Hàng -->
        <div style="display:flex;align-items:center;gap:10px">
          <!-- Filter Tier -->
          <div style="display:flex;align-items:center;gap:6px">
            <span style="font-size:11px;color:#94a3b8">Hạng:</span>
            <select class="form-select" id="mm-filter-tier" onchange="onMatchmakerFilterChange()" style="font-size:11.5px;padding:4px 8px;background:rgba(0,0,0,0.4);border:1px solid rgba(255,255,255,0.2);color:#fff;border-radius:6px">
              <option value="ALL">Tất cả hạng</option>
              <option value="TIER_A_PLUS">💎 Hạng A+ Kim Cương (>= 88đ)</option>
              <option value="TIER_A">🥇 Hạng A Vàng (80-87đ)</option>
              <option value="TIER_B">🥈 Hạng B Tiềm Năng (70-79đ)</option>
            </select>
          </div>

          <!-- Filter Category -->
          <div style="display:flex;align-items:center;gap:6px">
            <span style="font-size:11px;color:#94a3b8">Ngành:</span>
            <select class="form-select" id="mm-filter-cat" onchange="onMatchmakerFilterChange()" style="font-size:11.5px;padding:4px 8px;background:rgba(0,0,0,0.4);border:1px solid rgba(255,255,255,0.2);color:#fff;border-radius:6px">
              <option value="ALL">Tất cả ngành hàng</option>
              <option value="Nông Sản & Thực Phẩm">Nông Sản & Thực Phẩm</option>
              <option value="Logistics & Vận Tải">Logistics & Vận Tải</option>
              <option value="Giải Pháp Công Nghệ / AI">Giải Pháp Công Nghệ / AI</option>
              <option value="Vật Liệu & Công Nghiệp">Vật Liệu & Công Nghiệp</option>
            </select>
          </div>

          <button class="btn sm" onclick="fetchMatchmakerData()" title="Làm mới dữ liệu"><i class="ph ph-arrows-clockwise"></i> Quét Lại</button>
        </div>

      </div>

      <!-- 3. NỘI DUNG CHÍNH (CONTAINER DYNAMIC CONTENT) -->
      <div id="mm-dynamic-content" style="min-height:400px">
        <div style="padding:40px;text-align:center;color:#94a3b8">Đang nạp dữ liệu Sàn Ghép Nối Cung - Cầu...</div>
      </div>

    </div>
  `;
}

async function initCommercialWorkbenchUI() {
  await fetchMatchmakerData();
}

async function fetchMatchmakerData() {
  try {
    const [resSum, resMat, resDem, resSup] = await Promise.all([
      fetch('/api/commercial/matchmaker/summary').then(r => r.json()),
      fetch(`/api/commercial/matchmaker/matches?tier=${matchmakerState.filterTier}&category=${matchmakerState.filterCategory}`).then(r => r.json()),
      fetch(`/api/commercial/matchmaker/demands?category=${matchmakerState.filterCategory}`).then(r => r.json()),
      fetch(`/api/commercial/matchmaker/supplies?category=${matchmakerState.filterCategory}`).then(r => r.json())
    ]);

    if (resSum.ok) {
      matchmakerState.summary = resSum;
      updateMatchmakerKPIs(resSum);
    }
    if (resMat.ok) {
      matchmakerState.matches = resMat.matches || [];
      const el = document.getElementById('count-tab-matches');
      if (el) el.textContent = matchmakerState.matches.length;
    }
    if (resDem.ok) {
      matchmakerState.demands = resDem.demands || [];
      const el = document.getElementById('count-tab-demands');
      if (el) el.textContent = matchmakerState.demands.length;
    }
    if (resSup.ok) {
      matchmakerState.supplies = resSup.supplies || [];
      const el = document.getElementById('count-tab-supplies');
      if (el) el.textContent = matchmakerState.supplies.length;
    }

    renderMatchmakerActiveTab();
  } catch (err) {
    showToast('Lỗi nạp sàn mậu dịch: ' + err.message);
  }
}

function updateMatchmakerKPIs(s) {
  const dCount = document.getElementById('mm-kpi-total-demands');
  const dBudget = document.getElementById('mm-kpi-demands-budget');
  const sCount = document.getElementById('mm-kpi-total-supplies');
  const mCount = document.getElementById('mm-kpi-total-matches');
  const mRating = document.getElementById('mm-kpi-avg-rating');
  const mArb = document.getElementById('mm-kpi-arbitrage-val');

  if (dCount) dCount.textContent = s.total_demands || 0;
  if (dBudget) dBudget.textContent = `Tổng ngân sách: ${((s.total_demand_budget || 0) / 1000000000).toFixed(2)} tỷ ₫`;
  if (sCount) sCount.textContent = s.total_supplies || 0;
  if (mCount) mCount.textContent = s.total_matches || 0;
  if (mRating) mRating.textContent = `Điểm trung bình: ${s.avg_rating || 0} / 100đ`;
  if (mArb) mArb.textContent = `+${((s.total_arbitrage_val || 0) / 1000000).toLocaleString('vi-VN')} Tr ₫`;
}

function switchMatchmakerTab(tab) {
  matchmakerState.activeTab = tab;
  
  const btnM = document.getElementById('tab-btn-matches');
  const btnD = document.getElementById('tab-btn-demands');
  const btnS = document.getElementById('tab-btn-supplies');

  if (btnM) btnM.className = tab === 'matches' ? 'btn sm primary' : 'btn sm';
  if (btnD) btnD.className = tab === 'demands' ? 'btn sm primary' : 'btn sm';
  if (btnS) btnS.className = tab === 'supplies' ? 'btn sm primary' : 'btn sm';

  renderMatchmakerActiveTab();
}

function onMatchmakerFilterChange() {
  const tierSelect = document.getElementById('mm-filter-tier');
  const catSelect = document.getElementById('mm-filter-cat');
  if (tierSelect) matchmakerState.filterTier = tierSelect.value;
  if (catSelect) matchmakerState.filterCategory = catSelect.value;
  fetchMatchmakerData();
}

function renderMatchmakerActiveTab() {
  const container = document.getElementById('mm-dynamic-content');
  if (!container) return;

  if (matchmakerState.activeTab === 'matches') {
    renderMatchmakerMatchesList(container);
  } else if (matchmakerState.activeTab === 'demands') {
    renderMatchmakerDemandsList(container);
  } else if (matchmakerState.activeTab === 'supplies') {
    renderMatchmakerSuppliesList(container);
  }
}

// -----------------------------------------------------------------------------
// TAB 1: CẦU NỐI GHÉP CẶP & THANG ĐIỂM (MATCHMAKER BRIDGE VIEW)
// -----------------------------------------------------------------------------
function renderMatchmakerMatchesList(container) {
  const matches = matchmakerState.matches;
  if (!matches || matches.length === 0) {
    container.innerHTML = `
      <div class="card" style="padding:40px;text-align:center;color:#94a3b8">
        <i class="ph ph-magnifying-glass" style="font-size:36px;color:#64748b;margin-bottom:12px;display:block"></i>
        Không tìm thấy cơ hội ráp nối nào thỏa mãn bộ lọc hiện tại.
      </div>
    `;
    return;
  }

  container.innerHTML = `
    <div style="display:flex;flex-direction:column;gap:18px">
      ${matches.map(m => {
        const isDiamond = m.rating_tier === 'TIER_A_PLUS';
        const isGold = m.rating_tier === 'TIER_A';
        const tierBadgeColor = isDiamond ? 'linear-gradient(135deg, #0284c7, #6366f1)' : (isGold ? 'linear-gradient(135deg, #d97706, #f59e0b)' : 'rgba(255,255,255,0.1)');
        const tierBadgeText = isDiamond ? '💎 HẠNG A+ KIM CƯƠNG' : (isGold ? '🥇 HẠNG A VÀNG' : '🥈 HẠNG B TIỀM NĂNG');
        
        return `
          <div class="card" style="padding:0;overflow:hidden;background:rgba(15,23,42,0.95);border:1px solid ${isDiamond ? 'rgba(99,102,241,0.4)' : 'rgba(255,255,255,0.12)'};border-radius:12px;box-shadow:0 8px 24px rgba(0,0,0,0.4)">
            
            <!-- Top Strip: ID & Thang Điểm & Ngành Hàng -->
            <div style="background:rgba(0,0,0,0.3);padding:10px 18px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid rgba(255,255,255,0.08)">
              <div style="display:flex;align-items:center;gap:10px">
                <span style="font-family:var(--mono);font-size:12px;font-weight:700;color:#38bdf8">${m.id}</span>
                <span class="badge" style="background:${tierBadgeColor};color:#fff;font-weight:800;font-size:10px;padding:3px 8px;letter-spacing:0.5px">${tierBadgeText}</span>
                <span style="font-size:11.5px;color:#cbd5e1;font-weight:600"><i class="ph ph-tag"></i> ${escapeHtml(m.demand_category || '')}</span>
              </div>
              <div style="display:flex;align-items:center;gap:12px">
                <span style="font-size:11px;color:#94a3b8">Trạng thái:</span>
                <span class="badge" style="background:${m.action_status === 'PENDING' ? 'rgba(234,179,8,0.2)' : 'rgba(52,211,153,0.2)'};color:${m.action_status === 'PENDING' ? '#fbbf24' : '#34d399'};font-size:10.5px">
                  ${m.action_status === 'PENDING' ? '⏳ Chờ Sếp Duyệt' : (m.action_status === 'ARBITRAGED' ? '💼 Đang Ôm Deal' : '🤝 Đã Kết Nối')}
                </span>
              </div>
            </div>

            <!-- CẦU NỐI 3 KHỐI: NGUỒN CẦU <---> ĐỐI SOÁT & THANG ĐIỂM <---> NGUỒN CUNG -->
            <div style="display:grid;grid-template-columns:1.2fr 1fr 1.2fr;align-items:stretch;background:rgba(255,255,255,0.01)">
              
              <!-- CỘT 1: NGUỒN CẦU (DEMAND) -->
              <div style="padding:16px 20px;border-right:1px dashed rgba(255,255,255,0.1);display:flex;flex-direction:column;justify-content:space-between">
                <div>
                  <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px">
                    <span class="badge" style="background:rgba(56,189,248,0.15);color:#38bdf8;font-size:10.5px;border:1px solid rgba(56,189,248,0.3)">
                      <i class="ph ph-arrow-down-left"></i> BÊN CẦU: ${escapeHtml(m.demand_contact || 'Khách Hàng')}
                    </span>
                    <span class="badge danger" style="font-size:9.5px;padding:2px 6px">🔥 Heat ${m.demand_heat || 80}°</span>
                  </div>
                  
                  <div style="font-size:11px;color:#64748b;margin-bottom:6px">
                    <i class="ph ph-chat-circle-dots"></i> Nguồn: <b style="color:#94a3b8">${escapeHtml(m.demand_group || '')}</b>
                  </div>

                  <div style="font-size:14px;font-weight:700;color:#f8fafc;line-height:1.4;margin-bottom:8px">
                    ${escapeHtml(m.demand_title || '')}
                  </div>

                  <div style="background:rgba(0,0,0,0.35);border:1px solid rgba(255,255,255,0.06);border-radius:6px;padding:8px 10px;font-size:11.5px;color:#94a3b8;font-style:italic;margin-bottom:10px">
                    "${escapeHtml(m.demand_raw || m.demand_desc || '')}"
                  </div>
                </div>

                <div style="display:flex;justify-content:space-between;align-items:center;background:rgba(56,189,248,0.08);padding:8px 12px;border-radius:6px">
                  <span style="font-size:11px;color:#94a3b8">Ngân Sách Mua:</span>
                  <span style="font-size:14px;font-weight:800;color:#38bdf8">${(m.demand_budget || 0).toLocaleString('vi-VN')} ₫</span>
                </div>
              </div>

              <!-- CỘT 2: TRÍ TUỆ ĐỐI SOÁT & THANG ĐIỂM (MATCH SCORING) -->
              <div style="padding:16px 18px;background:rgba(0,0,0,0.25);display:flex;flex-direction:column;justify-content:space-between;align-items:center;text-align:center;position:relative">
                
                <div style="width:100%">
                  <div style="font-size:10.5px;font-weight:700;color:#a855f7;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px">
                    <i class="ph ph-cpu"></i> ĐỐI SOÁT CUNG - CẦU
                  </div>

                  <!-- Thang Điểm Tổng Hợp -->
                  <div style="display:flex;align-items:baseline;justify-content:center;gap:4px">
                    <span style="font-size:36px;font-weight:900;color:${m.total_rating >= 85 ? '#34d399' : '#fbbf24'};line-height:1">${m.total_rating}</span>
                    <span style="font-size:14px;font-weight:700;color:#64748b">/ 100đ</span>
                  </div>
                  <div style="font-size:11px;color:#94a3b8;margin-top:2px">Độ khớp tiêu chuẩn: <b style="color:#f8fafc">${m.match_score}%</b></div>

                  <!-- Chênh Lệch Lợi Nhuận Gộp (Spread Arbitrage) -->
                  <div style="margin:12px 0;background:rgba(52,211,153,0.1);border:1px solid rgba(52,211,153,0.3);border-radius:8px;padding:8px 12px">
                    <div style="font-size:10px;font-weight:700;color:#34d399;text-transform:uppercase">CHÊNH LỆCH LỢI NHUẬN GỘP:</div>
                    <div style="font-size:16px;font-weight:900;color:#34d399;margin-top:2px">
                      +${(m.arbitrage_spread_val || 0).toLocaleString('vi-VN')} ₫
                      <span style="font-size:11px;font-weight:600;color:#6ee7b7">(+${m.arbitrage_spread_pct}%)</span>
                    </div>
                  </div>

                  <!-- AI Lời Giải Trình -->
                  <div style="font-size:11px;color:#cbd5e1;line-height:1.4;text-align:left;background:rgba(255,255,255,0.03);padding:8px;border-radius:6px;border-left:2px solid #a855f7">
                    ${escapeHtml(m.explainable_reason || '')}
                  </div>
                </div>

                <div style="font-size:10.5px;color:#fbbf24;font-weight:600;margin-top:10px">
                  <i class="ph ph-sparkle"></i> Đề xuất: ${m.next_action_suggested === 'TRADE_ARBITRAGE' ? 'Đứng giữa ôm deal ăn trọn biên độ' : (m.next_action_suggested === 'INTRODUCE_COMMISSION' ? 'Giới thiệu ăn hoa hồng kết nối' : 'Gửi đề xuất giải pháp trực tiếp')}
                </div>
              </div>

              <!-- CỘT 3: NGUỒN CUNG (SUPPLY) -->
              <div style="padding:16px 20px;border-left:1px dashed rgba(255,255,255,0.1);display:flex;flex-direction:column;justify-content:space-between">
                <div>
                  <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px">
                    <span class="badge" style="background:rgba(52,211,153,0.15);color:#34d399;font-size:10.5px;border:1px solid rgba(52,211,153,0.3)">
                      <i class="ph ph-arrow-up-right"></i> BÊN CUNG: ${escapeHtml(m.supply_provider || 'Nhà Cung Ứng')}
                    </span>
                    <span class="badge good" style="font-size:9.5px;padding:2px 6px">Độ Tin ${m.supply_confidence || 90}%</span>
                  </div>

                  <div style="font-size:11px;color:#64748b;margin-bottom:6px">
                    <i class="ph ph-warehouse"></i> Kho/Nguồn: <b style="color:#94a3b8">${escapeHtml(m.supply_group || '')}</b>
                  </div>

                  <div style="font-size:14px;font-weight:700;color:#f8fafc;line-height:1.4;margin-bottom:8px">
                    ${escapeHtml(m.supply_title || '')}
                  </div>

                  <div style="background:rgba(0,0,0,0.35);border:1px solid rgba(255,255,255,0.06);border-radius:6px;padding:8px 10px;font-size:11.5px;color:#94a3b8;font-style:italic;margin-bottom:10px">
                    "${escapeHtml(m.supply_raw || m.supply_desc || '')}"
                  </div>
                </div>

                <div style="display:flex;justify-content:space-between;align-items:center;background:rgba(52,211,153,0.08);padding:8px 12px;border-radius:6px">
                  <span style="font-size:11px;color:#94a3b8">Giá Chào Bán:</span>
                  <span style="font-size:14px;font-weight:800;color:#34d399">${(m.supply_price || 0).toLocaleString('vi-VN')} ₫</span>
                </div>
              </div>

            </div>

            <!-- THANH NEXT ACTION BAR (QUYẾT ĐỊNH CỦA SẾP RYAN) -->
            <div style="background:rgba(0,0,0,0.5);padding:10px 18px;display:flex;justify-content:space-between;align-items:center;border-top:1px solid rgba(255,255,255,0.08)">
              <div style="font-size:11.5px;color:#94a3b8;display:flex;align-items:center;gap:6px">
                <i class="ph ph-hand-pointing" style="color:#fbbf24"></i>
                <span>Quyết định của Sếp: <b>${escapeHtml(m.action_notes || 'Chưa thực thi')}</b></span>
              </div>

              <div style="display:flex;align-items:center;gap:8px">
                <!-- 1. Kết Nối 2 Bên -->
                <button class="btn sm" onclick="promptExecuteMatchAction('${m.id}', 'INTRODUCE_COMMISSION')" style="font-size:11.5px;background:rgba(56,189,248,0.15);border:1px solid rgba(56,189,248,0.3);color:#38bdf8">
                  <i class="ph ph-users-three"></i> 🤝 Kết Nối 2 Bên (Hoa Hồng)
                </button>

                <!-- 2. Đứng Giữa Ôm Deal -->
                <button class="btn sm" onclick="promptExecuteMatchAction('${m.id}', 'TRADE_ARBITRAGE')" style="font-size:11.5px;background:rgba(52,211,153,0.15);border:1px solid rgba(52,211,153,0.3);color:#34d399">
                  <i class="ph ph-briefcase"></i> 💼 Đứng Giữa Ôm Deal (Thương Mại)
                </button>

                <!-- 3. Chat Xác Thực Thêm -->
                <button class="btn sm" onclick="promptExecuteMatchAction('${m.id}', 'VERIFY_MORE')" style="font-size:11.5px;background:rgba(234,179,8,0.15);border:1px solid rgba(234,179,8,0.3);color:#fbbf24">
                  <i class="ph ph-magnifying-glass"></i> 🔍 Chat Xác Thực Thêm
                </button>

                <!-- 4. Soạn Thảo Đề Xuất (Chuyển sang Office khi cần) -->
                <button class="btn sm" onclick="promptExecuteMatchAction('${m.id}', 'CREATE_PROPOSAL')" style="font-size:11.5px;background:rgba(192,132,252,0.15);border:1px solid rgba(192,132,252,0.3);color:#c084fc">
                  <i class="ph ph-file-text"></i> 📝 Soạn Báo Giá
                </button>

                <!-- Nút Bỏ Qua -->
                <button class="btn sm danger" onclick="executeMatchActionDirect('${m.id}', 'DISMISS', 'Sếp bỏ qua cơ hội này')" title="Bỏ qua cơ hội">
                  <i class="ph ph-x"></i>
                </button>
              </div>
            </div>

          </div>
        `;
      }).join('')}
    </div>
  `;
}

// -----------------------------------------------------------------------------
// TAB 2: KHO NGUỒN CẦU (DEMANDS STREAM)
// -----------------------------------------------------------------------------
function renderMatchmakerDemandsList(container) {
  const demands = matchmakerState.demands;
  container.innerHTML = `
    <div style="display:flex;flex-direction:column;gap:12px">
      <div style="font-size:12px;color:#94a3b8;margin-bottom:4px">
        Hiển thị <b>${demands.length}</b> nhu cầu thị trường được AI trích xuất tự động từ các Group Zalo, WhatsApp và tin nhắn trực tiếp:
      </div>
      <div style="display:grid;grid-template-columns:repeat(auto-fill, minmax(360px, 1fr));gap:14px">
        ${demands.map(d => `
          <div class="card card-pad" style="background:rgba(15,23,42,0.9);border:1px solid rgba(56,189,248,0.25);border-radius:10px">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:6px">
              <span class="badge" style="background:rgba(56,189,248,0.15);color:#38bdf8;font-size:10px">${escapeHtml(d.category || '')}</span>
              <span class="badge danger" style="font-size:9.5px">Heat ${d.heat_score || 80}°</span>
            </div>
            <div style="font-weight:700;font-size:13.5px;color:#f8fafc;margin-bottom:6px">${escapeHtml(d.title)}</div>
            <div style="font-size:11.5px;color:#94a3b8;margin-bottom:10px;line-height:1.4">${escapeHtml(d.description || '')}</div>
            
            <div style="background:rgba(0,0,0,0.3);padding:8px 10px;border-radius:6px;font-size:11px;color:#cbd5e1;margin-bottom:10px">
              <div>Khối lượng: <b style="color:#fff">${escapeHtml(d.quantity || 'Chưa rõ')}</b></div>
              <div>Ngân sách: <b style="color:#38bdf8">${(d.target_price || 0).toLocaleString('vi-VN')} ₫</b></div>
              <div>Bên cần: <b>${escapeHtml(d.contact_name || '')}</b> (${escapeHtml(d.source_group || '')})</div>
            </div>

            <div style="text-align:right">
              <button class="btn sm primary" onclick="switchMatchmakerTab('matches')" style="font-size:11px">
                <i class="ph ph-handshake"></i> Xem Cặp Ghép Khớp
              </button>
            </div>
          </div>
        `).join('')}
      </div>
    </div>
  `;
}

// -----------------------------------------------------------------------------
// TAB 3: KHO NGUỒN CUNG (SUPPLIES STREAM)
// -----------------------------------------------------------------------------
function renderMatchmakerSuppliesList(container) {
  const supplies = matchmakerState.supplies;
  container.innerHTML = `
    <div style="display:flex;flex-direction:column;gap:12px">
      <div style="font-size:12px;color:#94a3b8;margin-bottom:4px">
        Hiển thị <b>${supplies.length}</b> nguồn hàng / năng lực cung ứng sẵn có trong mạng lưới:
      </div>
      <div style="display:grid;grid-template-columns:repeat(auto-fill, minmax(360px, 1fr));gap:14px">
        ${supplies.map(s => `
          <div class="card card-pad" style="background:rgba(15,23,42,0.9);border:1px solid rgba(52,211,153,0.25);border-radius:10px">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:6px">
              <span class="badge" style="background:rgba(52,211,153,0.15);color:#34d399;font-size:10px">${escapeHtml(s.category || '')}</span>
              <span class="badge good" style="font-size:9.5px">Độ Tin ${s.confidence_score || 90}%</span>
            </div>
            <div style="font-weight:700;font-size:13.5px;color:#f8fafc;margin-bottom:6px">${escapeHtml(s.title)}</div>
            <div style="font-size:11.5px;color:#94a3b8;margin-bottom:10px;line-height:1.4">${escapeHtml(s.description || '')}</div>
            
            <div style="background:rgba(0,0,0,0.3);padding:8px 10px;border-radius:6px;font-size:11px;color:#cbd5e1;margin-bottom:10px">
              <div>Sẵn có / Công suất: <b style="color:#fff">${escapeHtml(s.capacity || 'Sẵn kho')}</b></div>
              <div>Giá chào: <b style="color:#34d399">${(s.offered_price || 0).toLocaleString('vi-VN')} ₫</b></div>
              <div>Bên cung: <b>${escapeHtml(s.provider_name || '')}</b> (${escapeHtml(s.source_group || '')})</div>
            </div>

            <div style="text-align:right">
              <button class="btn sm primary" onclick="switchMatchmakerTab('matches')" style="font-size:11px">
                <i class="ph ph-handshake"></i> Xem Cặp Ghép Khớp
              </button>
            </div>
          </div>
        `).join('')}
      </div>
    </div>
  `;
}

// -----------------------------------------------------------------------------
// QUYẾT ĐỊNH NEXT ACTION CỦA SẾP RYAN
// -----------------------------------------------------------------------------
function promptExecuteMatchAction(matchId, actionType) {
  const match = matchmakerState.matches.find(m => m.id === matchId);
  if (!match) return;

  const titles = {
    'INTRODUCE_COMMISSION': '🤝 KẾT NỐI HAI BÊN & THU HOA HỒNG MÔI GIỚI',
    'TRADE_ARBITRAGE': '💼 ĐỨNG GIỮA LÀM THƯƠNG MẠI (ÔM CHÊNH LỆCH ARBITRAGE)',
    'VERIFY_MORE': '🔍 GIAO AGENT CHAT XÁC MINH THÊM THÔNG TIN',
    'CREATE_PROPOSAL': '📝 CHUYỂN SANG SOẠN THẢO BÁO GIÁ ĐỀ XUẤT'
  };

  const descriptions = {
    'INTRODUCE_COMMISSION': `Sếp sẽ tạo nhóm kết nối giữa <b>${escapeHtml(match.demand_contact)}</b> và <b>${escapeHtml(match.supply_provider)}</b>. Hệ thống thu phí môi giới 3% (ước tính: <b>${((match.demand_budget || 0) * 0.03).toLocaleString('vi-VN')} ₫</b>).`,
    'TRADE_ARBITRAGE': `Sếp đứng giữa ký hợp đồng mua của <b>${escapeHtml(match.supply_provider)}</b> giá <b>${(match.supply_price||0).toLocaleString()} ₫</b> và bán cho <b>${escapeHtml(match.demand_contact)}</b> giá <b>${(match.demand_budget||0).toLocaleString()} ₫</b>. Thu trọn biên độ lợi nhuận gộp <b>+${(match.arbitrage_spread_val||0).toLocaleString()} ₫</b>.`,
    'VERIFY_MORE': `Agent sẽ tự động soạn câu hỏi gửi vào <b>${escapeHtml(match.supply_group)}</b> để kiểm tra tiêu chuẩn mã vùng trồng, chứng chỉ xuất khẩu và tiến độ giao hàng trước khi Sếp quyết định.`,
    'CREATE_PROPOSAL': `Hệ thống sẽ chuyển sang Bàn Soạn Thảo Văn Phòng để xuất file Báo Giá / Đề Xuất Hợp Tác chính thức gửi cho bên Cầu.`
  };

  openModal(titles[actionType] || 'Xác Nhận Hành Động Mậu Dịch', `
    <div style="display:flex;flex-direction:column;gap:14px">
      <div style="background:rgba(99,102,241,0.1);border:1px solid rgba(99,102,241,0.25);border-radius:8px;padding:12px;font-size:12px;color:#cbd5e1;line-height:1.5">
        ${descriptions[actionType] || ''}
      </div>

      <div>
        <label style="font-size:11px;font-weight:700;color:#94a3b8;margin-bottom:4px;display:block">GHI CHÚ / CHỈ THỊ CỦA SẾP RYAN:</label>
        <input type="text" id="action-owner-notes" class="form-input" style="width:100%;font-size:12px;background:rgba(0,0,0,0.4);color:#fff;border:1px solid rgba(255,255,255,0.2);padding:8px" value="Sếp Ryan phê duyệt thực thi ${actionType}" placeholder="Nhập chỉ thị thêm nếu có...">
      </div>

      <div style="display:flex;justify-content:flex-end;gap:10px;margin-top:10px">
        <button class="btn" onclick="closeModal()">Hủy Bỏ</button>
        <button class="btn primary" onclick="confirmExecuteMatchAction('${matchId}', '${actionType}')">
          <i class="ph ph-check"></i> Xác Nhận Thực Thi
        </button>
      </div>
    </div>
  `);
}

async function confirmExecuteMatchAction(matchId, actionType) {
  const notesInput = document.getElementById('action-owner-notes');
  const notes = notesInput ? notesInput.value : '';
  closeModal();
  await executeMatchActionDirect(matchId, actionType, notes);
}

async function executeMatchActionDirect(matchId, actionType, notes) {
  showToast('Đang ghi nhận chỉ thị của Sếp...');
  try {
    const res = await fetch('/api/commercial/matchmaker/action', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        match_id: matchId,
        action_type: actionType,
        notes: notes
      })
    }).then(r => r.json());

    if (res.ok) {
      showToast(`🎯 Đã ghi nhận quyết định của Sếp cho thương vụ ${matchId}!`);
      await fetchMatchmakerData();
    } else {
      showToast('Lỗi: ' + res.error);
    }
  } catch (err) {
    showToast('Lỗi: ' + err.message);
  }
}

// Chuyển nhanh từ Radar sang Sàn Mậu Dịch
function openWorkbenchForDeal(dealId) {
  switchHub('workbench');
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
          <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:16px">
            <div>
              <div style="font-size:16px;font-weight:800;letter-spacing:0.5px">DATA CONFIDENCE INDEX (DCI)</div>
              <div style="font-size:11px;color:#94a3b8">Tiêu chuẩn kiểm định chất lượng dữ liệu (SPEC-17)</div>
            </div>
            <button class="btn sm" onclick="document.getElementById('dci-modal-overlay').remove()"><i class="ph ph-x"></i></button>
          </div>

          <div style="display:flex;align-items:center;gap:18px;background:rgba(0,0,0,0.4);border:1px solid rgba(255,255,255,0.1);padding:16px 20px;border-radius:10px;margin-bottom:16px">
            <div style="font-size:38px;font-weight:900;color:#34d399">${res.dci_score}%</div>
            <div>
              <div style="font-weight:700;font-size:14px;color:#f8fafc">${res.grade_label}</div>
              <div style="font-size:11px;color:#94a3b8;margin-top:2px">Đánh giá lúc ${res.evaluated_at}</div>
            </div>
          </div>

          <div style="display:flex;flex-direction:column;gap:10px;margin-bottom:16px">
            <div>
              <div style="display:flex;justify-content:space-between;font-size:11.5px;margin-bottom:4px">
                <span>1. Độ đầy đủ danh tính hồ sơ:</span>
                <b style="color:#38bdf8">${m.identity_completeness_pct}% (${m.total_contacts} Đối tượng)</b>
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
'''

if re.search(pattern, html):
    html = re.sub(pattern, new_matchmaker_code, html)
    with open("heo_harness/plugins/ui_dashboard/dashboard.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Matchmaker UI successfully patched into dashboard.html!")
else:
    print("Error: Could not find regex pattern in dashboard.html")
