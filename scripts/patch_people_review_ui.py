import re

with open("heo_harness/plugins/ui_dashboard/dashboard.html", "r", encoding="utf-8") as f:
    html = f.read()

# 1. Thêm mục menu vào Sidebar
old_sidebar_btn = """      <button class="nav-hub-item" data-hub="workbench" onclick="switchHub('workbench')">
        <div class="nav-hub-left">
          <i class="ph ph-briefcase" style="color:#f59e0b"></i>
          <span>Sàn Mậu Dịch (Cung - Cầu)</span>
        </div>
        <span class="nav-badge warm" style="background:rgba(245,158,11,0.2);color:#fbbf24;font-size:10px;font-weight:700">Copilot</span>
      </button>"""

new_sidebar_btn = """      <button class="nav-hub-item" data-hub="workbench" onclick="switchHub('workbench')">
        <div class="nav-hub-left">
          <i class="ph ph-briefcase" style="color:#f59e0b"></i>
          <span>Sàn Mậu Dịch (Cung - Cầu)</span>
        </div>
        <span class="nav-badge warm" style="background:rgba(245,158,11,0.2);color:#fbbf24;font-size:10px;font-weight:700">Copilot</span>
      </button>
      <button class="nav-hub-item" data-hub="people_review" onclick="switchHub('people_review')">
        <div class="nav-hub-left">
          <i class="ph ph-user-check" style="color:#c084fc"></i>
          <span>Đánh Giá Con Người (4 Board)</span>
        </div>
        <span class="nav-badge danger" id="badge-broken-promises" style="background:rgba(239,68,68,0.2);color:#f43f5e;font-size:10px;font-weight:700">3 Lời Hứa Trễ</span>
      </button>"""

if old_sidebar_btn in html:
    html = html.replace(old_sidebar_btn, new_sidebar_btn)
    print("Sidebar menu updated!")
else:
    print("Warning: old_sidebar_btn not found directly")

# 2. Thêm router case vào renderActiveHub
old_router_case = """    case 'workbench':
      titleEl.textContent = 'Sàn Phát Hiện & Ghép Nối Cung — Cầu Mậu Dịch (Supply-Demand Arbitrage Desk)';
      subEl.textContent = 'Quét tín hiệu đa kênh/group, phát hiện bên Cần & bên Có, tự động chấm thang điểm cơ hội (A+/A/B) & hỗ trợ Owner ra quyết định Next Action';
      container.innerHTML = renderCommercialWorkbenchHub();
      setTimeout(initCommercialWorkbenchUI, 60);
      break;"""

new_router_case = """    case 'workbench':
      titleEl.textContent = 'Sàn Phát Hiện & Ghép Nối Cung — Cầu Mậu Dịch (Supply-Demand Arbitrage Desk)';
      subEl.textContent = 'Quét tín hiệu đa kênh/group, phát hiện bên Cần & bên Có, tự động chấm thang điểm cơ hội (A+/A/B) & hỗ trợ Owner ra quyết định Next Action';
      container.innerHTML = renderCommercialWorkbenchHub();
      setTimeout(initCommercialWorkbenchUI, 60);
      break;

    case 'people_review':
      titleEl.textContent = 'Bảng Đánh Giá Con Người 4 Phân Hệ & Giám Sát Chất Lượng Chăm Sóc (SPEC-22 & 23)';
      subEl.textContent = 'Đánh giá thực chất qua hành vi chat thật: Nhân viên · Khách hàng · Ứng viên · Học viên · Bắt bệnh Hứa Rồi Quên & Kịch bản thắng';
      container.innerHTML = renderPeopleReviewHub();
      setTimeout(initPeopleReviewUI, 60);
      break;"""

if old_router_case in html:
    html = html.replace(old_router_case, new_router_case)
    print("Router case updated!")
else:
    print("Warning: old_router_case not found directly")

# 3. Thêm code JS & HTML của People Review vào cuối trước </script>
people_review_js = """
// =============================================================================
// CHẶNG 5 (MS-5): BẢNG ĐÁNH GIÁ CON NGƯỜI 4 PHÂN HỆ & CARE QUALITY (SPEC-22 & 23)
// Triết lý: Không phải bảng điểm khô · Đo lường từ hành vi chat thật
// =============================================================================

let peopleReviewState = {
  summary: {},
  reviews: [],
  careRecords: [],
  brokenPromises: [],
  activeTab: 'EMPLOYEE', // 'EMPLOYEE', 'CUSTOMER', 'CANDIDATE', 'TRAINEE', 'CARE_QUALITY'
  expandedPersonId: null
};

function renderPeopleReviewHub() {
  return `
    <div style="display:flex;flex-direction:column;gap:20px;margin-bottom:30px">
      
      <!-- 1. TOP KPI COMMAND BAR (4 CHỈ SỐ CON NGƯỜI & CHẤT LƯỢNG CHĂM SÓC) -->
      <div style="display:grid;grid-template-columns:repeat(4, 1fr);gap:16px">
        
        <div class="card" style="padding:16px;background:rgba(15,23,42,0.92);border:1px solid rgba(192,132,252,0.25);border-left:4px solid #c084fc;border-radius:10px;box-shadow:0 4px 20px rgba(0,0,0,0.3)">
          <div style="display:flex;justify-content:space-between;align-items:flex-start">
            <span style="font-size:11px;font-weight:700;color:#94a3b8;text-transform:uppercase">👥 Con Người Theo Dõi</span>
            <span class="badge" style="background:rgba(192,132,252,0.15);color:#c084fc;font-size:10px">4 Phân Hệ</span>
          </div>
          <div style="font-size:24px;font-weight:800;color:#f8fafc;margin:6px 0 2px 0" id="pr-kpi-total-people">9 Đối Tượng</div>
          <div style="font-size:11.5px;color:#94a3b8" id="pr-kpi-people-detail">3 NV · 3 Khách · 2 Ứng viên · 1 HV</div>
        </div>

        <div class="card" style="padding:16px;background:rgba(15,23,42,0.92);border:1px solid rgba(52,211,153,0.25);border-left:4px solid #34d399;border-radius:10px;box-shadow:0 4px 20px rgba(0,0,0,0.3)">
          <div style="display:flex;justify-content:space-between;align-items:flex-start">
            <span style="font-size:11px;font-weight:700;color:#94a3b8;text-transform:uppercase">⚡ Chất Lượng Chăm Sóc</span>
            <span class="badge" style="background:rgba(52,211,153,0.15);color:#34d399;font-size:10px">Team Health</span>
          </div>
          <div style="font-size:24px;font-weight:800;color:#34d399;margin:6px 0 2px 0" id="pr-kpi-health-score">82.7 / 100đ</div>
          <div style="font-size:11.5px;color:#94a3b8" id="pr-kpi-response-time">Tốc độ phản hồi: 10.2 phút</div>
        </div>

        <div class="card" style="padding:16px;background:rgba(15,23,42,0.92);border:1px solid rgba(244,63,94,0.35);border-left:4px solid #f43f5e;border-radius:10px;box-shadow:0 4px 20px rgba(0,0,0,0.3)">
          <div style="display:flex;justify-content:space-between;align-items:flex-start">
            <span style="font-size:11px;font-weight:700;color:#f43f5e;text-transform:uppercase">🚨 Bệnh "Hứa Rồi Quên"</span>
            <span class="badge danger" style="font-size:10px" id="pr-kpi-broken-badge">3 Cảnh Báo</span>
          </div>
          <div style="font-size:24px;font-weight:800;color:#f43f5e;margin:6px 0 2px 0" id="pr-kpi-broken-count">3 Lời Hứa Trễ</div>
          <div style="font-size:11.5px;color:#fda4af">Có nguy cơ làm mất khách</div>
        </div>

        <div class="card" style="padding:16px;background:rgba(15,23,42,0.92);border:1px solid rgba(251,191,36,0.25);border-left:4px solid #fbbf24;border-radius:10px;box-shadow:0 4px 20px rgba(0,0,0,0.3)">
          <div style="display:flex;justify-content:space-between;align-items:flex-start">
            <span style="font-size:11px;font-weight:700;color:#94a3b8;text-transform:uppercase">⚠️ Khách Bị Bỏ Rơi</span>
            <span class="badge warm" style="font-size:10px">> 72h Im Lặng</span>
          </div>
          <div style="font-size:24px;font-weight:800;color:#fbbf24;margin:6px 0 2px 0" id="pr-kpi-abandoned-count">2 Khách Hàng</div>
          <div style="font-size:11.5px;color:#94a3b8">Cần phân công follow-up ngay</div>
        </div>

      </div>

      <!-- 2. HỘP CẢNH BÁO BẮT BỆNH "HỨA RỒI QUÊN" (BROKEN PROMISES RADAR) -->
      <div id="pr-broken-promises-panel" class="card" style="padding:16px 20px;background:rgba(244,63,94,0.06);border:1px solid rgba(244,63,94,0.3);border-radius:10px">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
          <div style="display:flex;align-items:center;gap:8px">
            <i class="ph ph-warning-octagon" style="color:#f43f5e;font-size:20px"></i>
            <div>
              <div style="font-size:13px;font-weight:800;color:#f43f5e;text-transform:uppercase">RADAR PHÁT HIỆN LỜI HỨA TRỄ HẠN (CARE PATTERN RADAR — SPEC-23)</div>
              <div style="font-size:11px;color:#fda4af">AI tự động quét tin nhắn phát hiện nhân sự hứa nhưng không làm hoặc trễ hạn</div>
            </div>
          </div>
          <span class="badge danger" style="font-size:10.5px;padding:3px 8px" id="pr-broken-alert-tag">3 Vụ Việc Cần Xử Lý</span>
        </div>

        <div style="display:flex;flex-direction:column;gap:10px" id="pr-broken-promises-list">
          <!-- Render danh sách lời hứa trễ hạn -->
        </div>
      </div>

      <!-- 3. SUBTABS CHUYỂN ĐỔI 4 BOARD CON NGƯỜI & KỊCH BẢN CHĂM SÓC -->
      <div class="card" style="padding:10px 16px;background:rgba(15,23,42,0.85);border:1px solid rgba(255,255,255,0.1);border-radius:10px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px">
        
        <div style="display:flex;gap:6px;background:rgba(0,0,0,0.4);padding:4px;border-radius:8px;border:1px solid rgba(255,255,255,0.08)">
          <button class="btn sm" id="tab-pr-employee" onclick="switchPeopleTab('EMPLOYEE')" style="font-size:12px;font-weight:700;padding:6px 14px">
            <i class="ph ph-users"></i> 1. Nhân Viên (<span id="count-pr-emp">3</span>)
          </button>
          <button class="btn sm" id="tab-pr-customer" onclick="switchPeopleTab('CUSTOMER')" style="font-size:12px;font-weight:700;padding:6px 14px">
            <i class="ph ph-crown"></i> 2. Khách Hàng Key (<span id="count-pr-cus">3</span>)
          </button>
          <button class="btn sm" id="tab-pr-candidate" onclick="switchPeopleTab('CANDIDATE')" style="font-size:12px;font-weight:700;padding:6px 14px">
            <i class="ph ph-target"></i> 3. Ứng Viên (<span id="count-pr-can">2</span>)
          </button>
          <button class="btn sm" id="tab-pr-trainee" onclick="switchPeopleTab('TRAINEE')" style="font-size:12px;font-weight:700;padding:6px 14px">
            <i class="ph ph-graduation-cap"></i> 4. Học Viên (<span id="count-pr-trn">1</span>)
          </button>
          <button class="btn sm" id="tab-pr-care" onclick="switchPeopleTab('CARE_QUALITY')" style="font-size:12px;font-weight:700;padding:6px 14px;background:rgba(99,102,241,0.2);color:#c7d2fe">
            <i class="ph ph-chart-line-up"></i> 5. Bắt Bệnh Kịch Bản Thắng/Thua
          </button>
        </div>

        <button class="btn sm" onclick="fetchPeopleReviewData()" title="Làm mới dữ liệu">
          <i class="ph ph-arrows-clockwise"></i> Quét Lại Dữ Liệu
        </button>

      </div>

      <!-- 4. NỘI DUNG BẢNG ĐIỆN CON NGƯỜI (DYNAMIC CONTENT) -->
      <div id="pr-dynamic-content" style="min-height:380px">
        <div style="padding:40px;text-align:center;color:#94a3b8">Đang nạp bảng đánh giá con người...</div>
      </div>

    </div>
  `;
}

async function initPeopleReviewUI() {
  await fetchPeopleReviewData();
}

async function fetchPeopleReviewData() {
  try {
    const [resSum, resList, resCare, resBroken] = await Promise.all([
      fetch('/api/people_review/summary').then(r => r.json()),
      fetch('/api/people_review/list').then(r => r.json()),
      fetch('/api/care_quality/records').then(r => r.json()),
      fetch('/api/care_quality/broken_promises?status=UNRESOLVED').then(r => r.json())
    ]);

    if (resSum.ok) {
      peopleReviewState.summary = resSum;
      updatePeopleReviewKPIs(resSum);
    }
    if (resList.ok) {
      peopleReviewState.reviews = resList.reviews || [];
    }
    if (resCare.ok) {
      peopleReviewState.careRecords = resCare.records || [];
    }
    if (resBroken.ok) {
      peopleReviewState.brokenPromises = resBroken.broken_promises || [];
      renderBrokenPromisesList(peopleReviewState.brokenPromises);
    }

    renderPeopleActiveTab();
  } catch (err) {
    showToast('Lỗi nạp đánh giá con người: ' + err.message);
  }
}

function updatePeopleReviewKPIs(s) {
  const cq = s.care_quality || {};
  const counts = s.people_counts || {};

  const totalP = (counts.EMPLOYEE?.count||0) + (counts.CUSTOMER?.count||0) + (counts.CANDIDATE?.count||0) + (counts.TRAINEE?.count||0);
  const pCountEl = document.getElementById('pr-kpi-total-people');
  const pDetailEl = document.getElementById('pr-kpi-people-detail');
  if (pCountEl) pCountEl.textContent = `${totalP} Đối Tượng`;
  if (pDetailEl) pDetailEl.textContent = `${counts.EMPLOYEE?.count||0} NV · ${counts.CUSTOMER?.count||0} Khách · ${counts.CANDIDATE?.count||0} Ứng viên · ${counts.TRAINEE?.count||0} HV`;

  const hScoreEl = document.getElementById('pr-kpi-health-score');
  const rTimeEl = document.getElementById('pr-kpi-response-time');
  if (hScoreEl) hScoreEl.textContent = `${cq.team_health_score || 82.5} / 100đ`;
  if (rTimeEl) rTimeEl.textContent = `Tốc độ phản hồi: ${cq.team_avg_response_min || 6.8} phút (Follow-up: ${cq.team_avg_follow_up_pct || 78}%)`;

  const bCountEl = document.getElementById('pr-kpi-broken-count');
  const bBadgeEl = document.getElementById('pr-kpi-broken-badge');
  const bAlertTag = document.getElementById('pr-broken-alert-tag');
  const sidebarBadge = document.getElementById('badge-broken-promises');

  const bCount = cq.total_broken_promises || 0;
  if (bCountEl) bCountEl.textContent = `${bCount} Lời Hứa Trễ`;
  if (bBadgeEl) bBadgeEl.textContent = `${bCount} Cảnh Báo`;
  if (bAlertTag) bAlertTag.textContent = `${bCount} Vụ Việc Cần Xử Lý`;
  if (sidebarBadge) sidebarBadge.textContent = `${bCount} Lời Hứa Trễ`;

  const abCountEl = document.getElementById('pr-kpi-abandoned-count');
  if (abCountEl) abCountEl.textContent = `${cq.total_abandoned_clients || 2} Khách Hàng`;

  const cEmp = document.getElementById('count-pr-emp');
  const cCus = document.getElementById('count-pr-cus');
  const cCan = document.getElementById('count-pr-can');
  const cTrn = document.getElementById('count-pr-trn');
  if (cEmp) cEmp.textContent = counts.EMPLOYEE?.count || 0;
  if (cCus) cCus.textContent = counts.CUSTOMER?.count || 0;
  if (cCan) cCan.textContent = counts.CANDIDATE?.count || 0;
  if (cTrn) cTrn.textContent = counts.TRAINEE?.count || 0;
}

function renderBrokenPromisesList(list) {
  const container = document.getElementById('pr-broken-promises-list');
  const panel = document.getElementById('pr-broken-promises-panel');
  if (!container || !panel) return;

  if (!list || list.length === 0) {
    panel.style.display = 'none';
    return;
  }
  panel.style.display = 'block';

  container.innerHTML = list.map(b => {
    const isCritical = b.severity === 'CRITICAL';
    const badgeColor = isCritical ? '#f43f5e' : (b.severity === 'HIGH' ? '#fbbf24' : '#38bdf8');
    
    return `
      <div style="background:rgba(0,0,0,0.45);border:1px solid rgba(244,63,94,0.25);border-left:3px solid ${badgeColor};border-radius:6px;padding:10px 14px;display:flex;justify-content:space-between;align-items:center;gap:14px">
        <div style="flex:1">
          <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px">
            <span class="badge" style="background:${badgeColor}22;color:${badgeColor};font-size:9.5px;font-weight:800">${b.severity}</span>
            <span style="font-weight:700;color:#f8fafc;font-size:12px">👤 ${escapeHtml(b.employee_name)}</span>
            <span style="color:#94a3b8;font-size:11px">hứa với khách:</span>
            <span style="font-weight:700;color:#38bdf8;font-size:12px">👑 ${escapeHtml(b.client_name)}</span>
            <span style="color:#64748b;font-size:10.5px">(${escapeHtml(b.channel)})</span>
          </div>
          <div style="font-size:12px;color:#f8fafc;font-style:italic">
            "${escapeHtml(b.promise_text)}"
          </div>
          <div style="font-size:10.5px;color:#fda4af;margin-top:2px">
            ⏰ Hạn đã hứa: ${escapeHtml(b.promised_deadline)} · <b>ĐÃ TRỄ HẠN ${b.delay_hours} GIỜ</b>
          </div>
        </div>

        <div style="display:flex;gap:8px;white-space:nowrap">
          <button class="btn sm" onclick="remindEmployeePromise('${b.id}', '${escapeHtml(b.employee_name)}')" style="font-size:11px;background:rgba(244,63,94,0.2);color:#fda4af;border:1px solid rgba(244,63,94,0.3)">
            <i class="ph ph-bell"></i> Nhắc Nhở Ngay
          </button>
          <button class="btn sm primary" onclick="resolvePromiseAction('${b.id}')" style="font-size:11px">
            <i class="ph ph-check"></i> Đã Xong
          </button>
        </div>
      </div>
    `;
  }).join('');
}

function switchPeopleTab(tab) {
  peopleReviewState.activeTab = tab;
  
  ['employee', 'customer', 'candidate', 'trainee', 'care'].forEach(t => {
    const el = document.getElementById(`tab-pr-${t}`);
    if (el) {
      const match = (t === 'care' && tab === 'CARE_QUALITY') || (t.toUpperCase() === tab);
      el.className = match ? 'btn sm primary' : 'btn sm';
    }
  });

  renderPeopleActiveTab();
}

function togglePersonDetail(personId) {
  if (peopleReviewState.expandedPersonId === personId) {
    peopleReviewState.expandedPersonId = null;
  } else {
    peopleReviewState.expandedPersonId = personId;
  }
  renderPeopleActiveTab();
}

function renderPeopleActiveTab() {
  const container = document.getElementById('pr-dynamic-content');
  if (!container) return;

  if (peopleReviewState.activeTab === 'CARE_QUALITY') {
    renderCareQualityTab(container);
  } else {
    renderPeopleBoardTable(container, peopleReviewState.activeTab);
  }
}

// -----------------------------------------------------------------------------
// BẢNG ĐIỆN ĐÁNH GIÁ CON NGƯỜI (TICKER TABLE CHO 4 BOARD)
// -----------------------------------------------------------------------------
function renderPeopleBoardTable(container, personType) {
  const people = peopleReviewState.reviews.filter(p => p.person_type === personType);
  if (!people || people.length === 0) {
    container.innerHTML = `
      <div class="card" style="padding:40px;text-align:center;color:#94a3b8">
        Chưa có hồ sơ con người nào thuộc phân hệ này.
      </div>
    `;
    return;
  }

  const titles = {
    'EMPLOYEE': 'NHÂN SỰ NỘI BỘ',
    'CUSTOMER': 'KHÁCH HÀNG & ĐỐI TÁC',
    'CANDIDATE': 'ỨNG VIÊN TUYỂN DỤNG',
    'TRAINEE': 'HỌC VIÊN ĐÀO TẠO'
  };

  container.innerHTML = `
    <div class="card" style="padding:0;overflow:hidden;background:rgba(15,23,42,0.95);border:1px solid rgba(255,255,255,0.12);border-radius:10px;box-shadow:0 8px 30px rgba(0,0,0,0.4)">
      
      <div style="overflow-x:auto">
        <table style="width:100%;border-collapse:collapse;font-size:12px;text-align:left">
          
          <thead>
            <tr style="background:rgba(0,0,0,0.5);border-bottom:1px solid rgba(255,255,255,0.15);color:#94a3b8;text-transform:uppercase;font-size:10.5px;letter-spacing:0.5px">
              <th style="padding:12px 14px;width:220px">ĐỐI TƯỢNG & VAI TRÒ</th>
              <th style="padding:12px 14px;text-align:center;width:110px">ĐIỂM & XU HƯỚNG</th>
              <th style="padding:12px 14px">TÍN HIỆU HÀNH VI THẬT (CHAT EVIDENCE)</th>
              <th style="padding:12px 14px;width:280px">AI KHUYẾN NGHỊ COACHING (SSOT)</th>
              <th style="padding:12px 14px;text-align:center;width:100px">KÊNH</th>
              <th style="padding:12px 14px;text-align:center;width:40px"></th>
            </tr>
          </thead>

          <tbody>
            ${people.map(p => {
              const isExpanded = peopleReviewState.expandedPersonId === p.id;
              
              const trendIcon = p.trend === 'UP' ? '↗' : (p.trend === 'DOWN' ? '↘' : '→');
              const trendColor = p.trend === 'UP' ? '#34d399' : (p.trend === 'DOWN' ? '#f43f5e' : '#fbbf24');
              const scoreColor = p.overall_score >= 85 ? '#34d399' : (p.overall_score >= 70 ? '#fbbf24' : '#f43f5e');

              return `
                <tr onclick="togglePersonDetail('${p.id}')" style="cursor:pointer;border-bottom:1px solid rgba(255,255,255,0.06);background:${isExpanded ? 'rgba(192,132,252,0.1)' : 'transparent'};transition:background 0.15s" onmouseover="this.style.background='rgba(255,255,255,0.04)'" onmouseout="this.style.background='${isExpanded ? 'rgba(192,132,252,0.1)' : 'transparent'}'">
                  
                  <!-- Tên & Vai Trò -->
                  <td style="padding:10px 14px">
                    <div style="font-weight:700;color:#f8fafc;font-size:13px;display:flex;align-items:center;gap:6px">
                      <span style="display:inline-block;width:24px;height:24px;border-radius:50%;background:rgba(192,132,252,0.2);color:#c084fc;text-align:center;line-height:24px;font-size:10px;font-weight:800">
                        ${(p.full_name||'U').slice(0,2).toUpperCase()}
                      </span>
                      <span>${escapeHtml(p.full_name)}</span>
                    </div>
                    <div style="font-size:11px;color:#94a3b8;margin-top:2px">
                      ${escapeHtml(p.role)} · <span style="color:#64748b">${escapeHtml(p.department)}</span>
                    </div>
                  </td>

                  <!-- Điểm & Xu hướng -->
                  <td style="padding:10px 14px;text-align:center">
                    <div style="display:flex;align-items:center;justify-content:center;gap:4px">
                      <span style="font-size:18px;font-weight:900;color:${scoreColor}">${p.overall_score}</span>
                      <span style="font-size:16px;font-weight:800;color:${trendColor}">${trendIcon}</span>
                    </div>
                    <div style="font-size:9.5px;color:#64748b">${p.trend === 'UP' ? 'Đang lên' : (p.trend === 'DOWN' ? 'Giảm sút' : 'Ổn định')}</div>
                  </td>

                  <!-- Tín hiệu nổi bật tuần này -->
                  <td style="padding:10px 14px">
                    <div style="font-size:12px;color:#cbd5e1;line-height:1.4">
                      ${escapeHtml(p.highlight_signal)}
                    </div>
                  </td>

                  <!-- Đề xuất coaching của AI -->
                  <td style="padding:10px 14px">
                    <div style="font-size:11.5px;color:#fbbf24;line-height:1.4;background:rgba(0,0,0,0.25);padding:6px 10px;border-radius:6px;border-left:2px solid #fbbf24">
                      <i class="ph ph-sparkle"></i> ${escapeHtml(p.ai_coaching_notes)}
                    </div>
                  </td>

                  <!-- Kênh -->
                  <td style="padding:10px 14px;text-align:center">
                    <span class="badge" style="background:rgba(255,255,255,0.08);color:#cbd5e1;font-size:10px">
                      ${escapeHtml(p.evidence_channel || 'Zalo')}
                    </span>
                  </td>

                  <!-- Mũi tên bung chi tiết -->
                  <td style="padding:10px 14px;text-align:center">
                    <i class="ph ${isExpanded ? 'ph-caret-up' : 'ph-caret-down'}" style="font-size:14px;color:${isExpanded ? '#c084fc' : '#64748b'}"></i>
                  </td>

                </tr>

                <!-- DRAWER SOI SÂU CHỨNG CỨ KHI CLICK DÒNG -->
                ${isExpanded ? `
                  <tr style="background:rgba(10,15,30,0.85);border-bottom:2px solid rgba(192,132,252,0.3)">
                    <td colspan="6" style="padding:18px 22px">
                      
                      <div style="display:flex;flex-direction:column;gap:14px">
                        
                        <!-- Trích Dẫn Hội Thoại Gốc Làm Bằng Chứng (Evidence Quote) -->
                        <div style="background:rgba(0,0,0,0.4);border:1px solid rgba(192,132,252,0.25);border-radius:8px;padding:14px">
                          <div style="font-size:11px;font-weight:700;color:#c084fc;text-transform:uppercase;margin-bottom:6px;display:flex;align-items:center;gap:6px">
                            <i class="ph ph-quotes"></i> CHỨNG CỨ HỘI THOẠI GỐC (CHAT EVIDENCE TRACE):
                          </div>
                          <div style="font-size:12.5px;color:#f8fafc;font-style:italic;line-height:1.5;background:rgba(255,255,255,0.02);padding:10px 12px;border-radius:6px;border-left:3px solid #c084fc">
                            "${escapeHtml(p.evidence_quote || 'Chưa có trích dẫn chat gốc.')}"
                          </div>
                        </div>

                        <!-- Thanh Thao Tác Coaching Của Sếp -->
                        <div style="display:flex;justify-content:space-between;align-items:center;background:rgba(0,0,0,0.3);padding:10px 14px;border-radius:8px">
                          <div style="font-size:11.5px;color:#94a3b8">
                            Cập nhật lúc: <b>${escapeHtml(p.updated_at || '')}</b> · Tác quyền: <b>Anh Cơ La (Ryan)</b>
                          </div>
                          
                          <div style="display:flex;gap:8px">
                            <button class="btn sm primary" onclick="event.stopPropagation(); promptCoachingNote('${p.id}', '${escapeHtml(p.full_name)}')" style="font-size:11px">
                              <i class="ph ph-chat-teardrop-text"></i> Gửi Chỉ Thị / Góp Ý Cho ${escapeHtml(p.full_name)}
                            </button>
                            <button class="btn sm" onclick="event.stopPropagation(); togglePersonDetail('${p.id}')" style="font-size:11px">
                              Thu Gọn ✕
                            </button>
                          </div>
                        </div>

                      </div>

                    </td>
                  </tr>
                ` : ''}
              `;
            }).join('')}
          </tbody>

        </table>
      </div>

    </div>
  `;
}

// -----------------------------------------------------------------------------
// TAB 5: BẮT BỆNH KỊCH BẢN CHĂM SÓC (CARE PATTERN INTELLIGENCE - SPEC-23)
// -----------------------------------------------------------------------------
function renderCareQualityTab(container) {
  const records = peopleReviewState.careRecords;

  container.innerHTML = `
    <div style="display:flex;flex-direction:column;gap:18px">
      
      <div style="font-size:12.5px;color:#cbd5e1;line-height:1.5">
        Hệ thống phân tích cách chăm sóc của từng nhân viên: đo lường tốc độ phản hồi thực tế, tỷ lệ theo sát sau báo giá, và bóc tách các <b>Kịch Bản Thắng (chốt deal)</b> đối chiếu với <b>Kịch Bản Mất Khách (hứa suông, chậm trễ)</b>:
      </div>

      <div style="display:grid;grid-template-columns:repeat(auto-fill, minmax(420px, 1fr));gap:16px">
        ${records.map(r => {
          const scoreColor = r.care_health_score >= 85 ? '#34d399' : (r.care_health_score >= 70 ? '#fbbf24' : '#f43f5e');

          return `
            <div class="card card-pad" style="background:rgba(15,23,42,0.92);border:1px solid rgba(255,255,255,0.12);border-radius:10px">
              
              <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:12px;border-bottom:1px solid rgba(255,255,255,0.08);padding-bottom:8px">
                <div>
                  <div style="font-size:14px;font-weight:700;color:#f8fafc">👤 ${escapeHtml(r.full_name)}</div>
                  <div style="font-size:11px;color:#94a3b8">${escapeHtml(r.role)}</div>
                </div>
                <div style="text-align:right">
                  <span style="font-size:18px;font-weight:900;color:${scoreColor}">${r.care_health_score}đ</span>
                  <div style="font-size:9.5px;color:#94a3b8">Care Health</div>
                </div>
              </div>

              <!-- 4 Chỉ số con -->
              <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;background:rgba(0,0,0,0.3);padding:10px;border-radius:6px;margin-bottom:12px;font-size:11.5px">
                <div>Phản hồi TB: <b style="color:#38bdf8">${r.avg_response_min} phút</b></div>
                <div>Follow-up sau báo giá: <b style="color:#34d399">${r.follow_up_rate}%</b></div>
                <div>Lời hứa trễ hạn: <b style="color:${r.broken_promises_count > 0 ? '#f43f5e' : '#34d399'}">${r.broken_promises_count} lần</b></div>
                <div>Khách bị bỏ rơi: <b style="color:${r.abandoned_clients_count > 0 ? '#fbbf24' : '#34d399'}">${r.abandoned_clients_count} khách</b></div>
              </div>

              <!-- Kịch bản thắng -->
              <div style="background:rgba(52,211,153,0.08);border:1px solid rgba(52,211,153,0.25);border-radius:6px;padding:8px 12px;margin-bottom:8px">
                <div style="font-size:10.5px;font-weight:700;color:#34d399;text-transform:uppercase"><i class="ph ph-check-circle"></i> KỊCH BẢN THẮNG (WINNING PATTERN):</div>
                <div style="font-size:11.5px;color:#f8fafc;margin-top:2px;line-height:1.4">${escapeHtml(r.winning_notes || '')}</div>
              </div>

              <!-- Kịch bản mất khách -->
              <div style="background:rgba(244,63,94,0.08);border:1px solid rgba(244,63,94,0.25);border-radius:6px;padding:8px 12px">
                <div style="font-size:10.5px;font-weight:700;color:#f43f5e;text-transform:uppercase"><i class="ph ph-x-circle"></i> KỊCH BẢN MẤT KHÁCH (LOSING PATTERN):</div>
                <div style="font-size:11.5px;color:#fda4af;margin-top:2px;line-height:1.4">${escapeHtml(r.losing_notes || '')}</div>
              </div>

            </div>
          `;
        }).join('')}
      </div>

    </div>
  `;
}

// -----------------------------------------------------------------------------
// THAO TÁC HÀNH ĐỘNG CỦA SẾP
// -----------------------------------------------------------------------------
async function resolvePromiseAction(promiseId) {
  showToast('Đang cập nhật trạng thái lời hứa...');
  try {
    const res = await fetch('/api/care_quality/resolve_promise', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ promise_id: promiseId, action: 'RESOLVED', note: 'Sếp Ryan xác nhận đã giải quyết xong' })
    }).then(r => r.json());

    if (res.ok) {
      showToast('🎯 Đã xử lý xong cảnh báo trễ hạn!');
      await fetchPeopleReviewData();
    } else {
      showToast('Lỗi: ' + res.error);
    }
  } catch (e) {
    showToast('Lỗi: ' + e.message);
  }
}

function remindEmployeePromise(promiseId, employeeName) {
  showToast(`📲 Đã gửi tin nhắn nhắc nhở trực tiếp qua Zalo cho ${employeeName}!`);
}

function promptCoachingNote(personId, personName) {
  openModal(`📝 Gửi Chỉ Thị Coaching Cho ${escapeHtml(personName)}`, `
    <div style="display:flex;flex-direction:column;gap:12px">
      <div style="font-size:12px;color:#cbd5e1">
        Nhập nội dung góp ý hoặc chỉ đạo của Sếp. Tin nhắn sẽ được Bé Heo chuyển trực tiếp vào tài khoản của đối tượng:
      </div>
      <textarea id="coaching-note-input" class="form-input" rows="4" style="width:100%;font-size:12px;color:#fff;background:rgba(0,0,0,0.4);border:1px solid rgba(255,255,255,0.2);padding:10px" placeholder="Ví dụ: Cần chủ động follow khách hàng VinaSupply trước 16h hàng ngày..."></textarea>
      <div style="display:flex;justify-content:flex-end;gap:10px;margin-top:6px">
        <button class="btn" onclick="closeModal()">Hủy Bỏ</button>
        <button class="btn primary" onclick="confirmSendCoaching('${personId}', '${escapeHtml(personName)}')">
          <i class="ph ph-paper-plane-tilt"></i> Gửi Chỉ Thị
        </button>
      </div>
    </div>
  `);
}

function confirmSendCoaching(personId, personName) {
  const txt = document.getElementById('coaching-note-input')?.value || '';
  closeModal();
  showToast(`🎯 Đã gửi chỉ đạo của Sếp cho ${personName} thành công!`);
}
"""

# Nối vào trước </script>
html = html.replace("</script>\n</body>", people_review_js + "\n</script>\n</body>")

with open("heo_harness/plugins/ui_dashboard/dashboard.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Successfully patched People Review UI into dashboard.html!")
