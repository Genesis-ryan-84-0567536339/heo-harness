"""
Patch SPEC-43: Phase 3 — Quản được (Relationship Map, 8-Stage Opportunity Kanban, Care Quality Intelligence)
into heo_harness/plugins/ui_dashboard/dashboard.html
"""

import re
import os

DASHBOARD_PATH = "heo_harness/plugins/ui_dashboard/dashboard.html"

with open(DASHBOARD_PATH, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update stages in renderOpportunitiesHub to include the 8th canonical stage
old_stages = """  const stages = [
    { key: 'RAW_SIGNAL', label: '📡 Tín Hiệu Thô', color: '#94a3b8', alias: ['RAW_SIGNAL', 'SIGNAL'] },
    { key: 'QUALIFIED', label: '🔍 Đã Xác Thực', color: '#38bdf8', alias: ['QUALIFIED', 'VERIFIED'] },
    { key: 'MATCHED', label: '🤝 Ráp Khớp Cung-Cầu', color: '#a855f7', alias: ['MATCHED'] },
    { key: 'OUTREACH', label: '📞 Tiếp Cận', color: '#f59e0b', alias: ['OUTREACH', 'APPROACHING'] },
    { key: 'NEGOTIATING', label: '💼 Đàm Phán', color: '#ec4899', alias: ['NEGOTIATING'] },
    { key: 'INTERNAL_REVIEW', label: '⚖️ Thẩm Định Nội Bộ', color: '#6366f1', alias: ['INTERNAL_REVIEW'] },
    { key: 'CLOSED_WON', label: '🏆 Chốt Đơn (Won)', color: '#10b981', alias: ['WON', 'CLOSED_WON'] }
  ];"""

new_stages = """  // 8 Cột Pipeline chuẩn hóa theo Spec LOCKED v2.2 (Mục L Phase 3 & F2.5)
  const stages = [
    { key: 'RAW_SIGNAL', label: '📡 Tín Hiệu Thô', color: '#94a3b8', alias: ['RAW_SIGNAL', 'SIGNAL'] },
    { key: 'QUALIFIED', label: '🔍 Đã Xác Thực', color: '#38bdf8', alias: ['QUALIFIED', 'VERIFIED'] },
    { key: 'MATCHED', label: '🤝 Ráp Khớp', color: '#a855f7', alias: ['MATCHED'] },
    { key: 'OUTREACH', label: '📞 Tiếp Cận', color: '#f59e0b', alias: ['OUTREACH', 'APPROACHING'] },
    { key: 'NEGOTIATING', label: '💼 Đàm Phán', color: '#ec4899', alias: ['NEGOTIATING'] },
    { key: 'INTERNAL_REVIEW', label: '⚖️ Chuyển Nội Bộ', color: '#6366f1', alias: ['INTERNAL_REVIEW', 'INTERNAL_TRANSFERRED'] },
    { key: 'CLOSED_WON', label: '🏆 Thắng (Won)', color: '#10b981', alias: ['WON', 'CLOSED_WON'] },
    { key: 'CLOSED_LOST', label: '❄️ Trượt / Ngủ Đông', color: '#64748b', alias: ['LOST', 'CLOSED_LOST', 'DORMANT'] }
  ];"""

if old_stages in content:
    content = content.replace(old_stages, new_stages)
    print("Updated 8 Kanban stages successfully.")
else:
    print("Kanban stages already updated or different.")

# 2. Update Opportunities Hub subnav button to show 8 Cột
old_btn = '<i class="ph ph-kanban"></i> Bảng Cơ Hội 7 Cột'
new_btn = '<i class="ph ph-kanban"></i> Bảng Cơ Hội 8 Cột (Kanban SSOT)'
content = content.replace(old_btn, new_btn)

# 3. Update renderRelationshipRadarHub subnav to add analytics and care_quality tabs
old_subnav = """      <!-- Subnav Tabs Chặng 4 -->
      <div style="display:flex;gap:8px;margin-top:16px;border-bottom:1px solid var(--color-divider);padding-bottom:12px">
        <button class="btn ${curSub === 'graph' ? 'primary' : 'subtle'} sm" onclick="switchSubtab('relationship_radar', 'graph')">
          <i class="ph ph-graph"></i> 🕸️ Bản Đồ Mạng Lưới Đồ Thị (Graph Canvas)
        </button>
        <button class="btn ${curSub === 'radar' ? 'primary' : 'subtle'} sm" onclick="switchSubtab('relationship_radar', 'radar')">
          <i class="ph ph-fire"></i> 📊 Radar Nhiệt Độ & Trọng Tài Bóng
        </button>
        <button class="btn ${curSub === 'profiles' ? 'primary' : 'subtle'} sm" onclick="switchSubtab('relationship_radar', 'profiles')">
          <i class="ph ph-user-list"></i> 👤 Danh Sách Hồ Sơ Sống 360 (${contacts.length})
        </button>
      </div>
    </div>

    ${curSub === 'graph' ? renderRelationshipGraphView() : ''}
    ${curSub === 'radar' ? renderRelationshipRadarView(hotContacts, warmContacts, coldContacts) : ''}
    ${curSub === 'profiles' ? renderLivingProfilesTableView(contacts) : ''}"""

new_subnav = """      <!-- Subnav Tabs Chặng 3 & 4 (SPEC-43 Phase 3) -->
      <div style="display:flex;gap:8px;margin-top:16px;border-bottom:1px solid var(--color-divider);padding-bottom:12px;flex-wrap:wrap">
        <button class="btn ${curSub === 'graph' ? 'primary' : 'subtle'} sm" onclick="switchSubtab('relationship_radar', 'graph')">
          <i class="ph ph-graph"></i> 🕸️ Bản Đồ Đồ Thị (Canvas)
        </button>
        <button class="btn ${curSub === 'analytics' ? 'primary' : 'subtle'} sm" onclick="switchSubtab('relationship_radar', 'analytics')">
          <i class="ph ph-tree-structure"></i> 🧠 Phân Tích Mạng Lưới & Cầu Nối
        </button>
        <button class="btn ${curSub === 'care_quality' ? 'primary' : 'subtle'} sm" onclick="switchSubtab('relationship_radar', 'care_quality')">
          <i class="ph ph-heartbeat"></i> 🩺 Chất Lượng Chăm Sóc (Care Quality)
        </button>
        <button class="btn ${curSub === 'radar' ? 'primary' : 'subtle'} sm" onclick="switchSubtab('relationship_radar', 'radar')">
          <i class="ph ph-fire"></i> 📊 Radar Nhiệt Độ
        </button>
        <button class="btn ${curSub === 'profiles' ? 'primary' : 'subtle'} sm" onclick="switchSubtab('relationship_radar', 'profiles')">
          <i class="ph ph-user-list"></i> 👤 Hồ Sơ Sống 360 (${contacts.length})
        </button>
      </div>
    </div>

    ${curSub === 'graph' ? renderRelationshipGraphView() : ''}
    ${curSub === 'analytics' ? renderRelationshipAnalyticsView() : ''}
    ${curSub === 'care_quality' ? renderCareQualityView() : ''}
    ${curSub === 'radar' ? renderRelationshipRadarView(hotContacts, warmContacts, coldContacts) : ''}
    ${curSub === 'profiles' ? renderLivingProfilesTableView(contacts) : ''}"""

if old_subnav in content:
    content = content.replace(old_subnav, new_subnav)
    print("Updated Relationship subnav with analytics and care_quality.")
else:
    print("Relationship subnav already updated or different.")

# 4. Append JavaScript functions for renderRelationshipAnalyticsView, renderCareQualityView, openAddRelationshipEdgeModal
spec43_js = """
// ==========================================
// SPEC-43: RELATIONSHIP ANALYTICS & CARE QUALITY VIEWS
// ==========================================

function renderRelationshipAnalyticsView() {
  const analytics = state._rel_analytics || {
    top_connectors: [
      { id: '1', full_name: 'Anh Minh (Kafi)', company: 'Kafi Securities', role: 'Giám Đốc Phân Tích', degree_connections: 5, deal_count: 2, is_bridge: true },
      { id: '3', full_name: 'Hoàng Bách', company: 'LogiTech Global', role: 'Managing Director', degree_connections: 4, deal_count: 3, is_bridge: true },
      { id: '2', full_name: 'Chị Mai Phương', company: 'VinaSupply Co', role: 'Trưởng Phòng Mua Hàng', degree_connections: 4, deal_count: 1, is_bridge: true }
    ],
    cold_leads: [
      { id: '5', full_name: 'Thảo Viettel', company: 'Viettel Telecom', went_silent_days: 8, heat_score: 40, risk_level: 'CAO', action_recommended: 'Gửi báo cáo công nghệ mới để hâm nóng' },
      { id: '4', full_name: 'Thu Hà', company: 'Thời Trang Hà My', went_silent_days: 4, heat_score: 65, risk_level: 'TRUNG BÌNH', action_recommended: 'Follow-up kết quả trải nghiệm bản demo' }
    ],
    overloaded_agents: [
      { agent_name: 'Anh Cơ La (Ryan)', holding_balls: 2, is_overloaded: false, status: 'ỔN ĐỊNH' },
      { agent_name: 'Hoàng Bách', holding_balls: 1, is_overloaded: false, status: 'ỔN ĐỊNH' }
    ],
    ball_in_court: { us_count: 4, them_count: 8, us_pct: 33.3, them_pct: 66.7 },
    network_health_score: 92
  };

  // Tự động kéo dữ liệu live từ backend nếu chưa có
  if (!state._rel_analytics_fetched) {
    state._rel_analytics_fetched = true;
    fetch('/api/relationship_graph/analytics')
      .then(r => r.json())
      .then(d => {
        if (d && d.ok) {
          state._rel_analytics = d;
          renderContent();
        }
      })
      .catch(e => console.warn('Could not fetch relationship analytics:', e));
  }

  return `
    <div style="display:flex;flex-direction:column;gap:16px">
      
      <!-- Banner Tổng Quan Sức Khỏe Mạng Lưới -->
      <div class="card card-pad" style="background:linear-gradient(135deg, rgba(99,102,241,0.08) 0%, rgba(14,165,233,0.05) 100%);border-color:rgba(99,102,241,0.25)">
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px">
          <div>
            <div style="font-size:16px;font-weight:700;color:var(--color-text);display:flex;align-items:center;gap:8px">
              <i class="ph ph-tree-structure" style="color:#818cf8;font-size:22px"></i>
              Bản Đồ Mạng Lưới Quan Hệ & Phân Bổ Trọng Tài Bóng (SSOT Phase 3)
            </div>
            <div style="font-size:12px;color:var(--color-neutral-300);margin-top:3px">
              Nhìn rõ ai là cầu nối chiến lược, khách hàng nào đang lạnh, và nhân sự nào đang ôm quá nhiều bóng cần giải phóng.
            </div>
          </div>
          <div style="display:flex;gap:8px">
            <button class="btn primary sm" onclick="openAddRelationshipEdgeModal()">
              <i class="ph ph-link-simple-horizontal"></i> Thêm Liên Kết Mới
            </button>
            <button class="btn sm" onclick="delete state._rel_analytics_fetched;renderContent()">
              <i class="ph ph-arrows-clockwise"></i> Làm Mới
            </button>
          </div>
        </div>

        <!-- 4 Chỉ Số Nhanh -->
        <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(180px, 1fr));gap:12px;margin-top:14px">
          <div style="background:rgba(255,255,255,0.03);padding:10px 14px;border-radius:8px;border:1px solid rgba(255,255,255,0.06)">
            <div style="font-size:11px;color:var(--color-neutral-400)">Điểm Sức Khỏe Mạng Lưới</div>
            <div style="font-size:22px;font-weight:700;color:#34d399">${analytics.network_health_score || 90}/100</div>
          </div>
          <div style="background:rgba(255,255,255,0.03);padding:10px 14px;border-radius:8px;border:1px solid rgba(255,255,255,0.06)">
            <div style="font-size:11px;color:var(--color-neutral-400)">Trọng Tài: Bóng Phía Ta (US)</div>
            <div style="font-size:22px;font-weight:700;color:#f43f5e">${analytics.ball_in_court?.us_count || 0} (${analytics.ball_in_court?.us_pct || 0}%)</div>
          </div>
          <div style="background:rgba(255,255,255,0.03);padding:10px 14px;border-radius:8px;border:1px solid rgba(255,255,255,0.06)">
            <div style="font-size:11px;color:var(--color-neutral-400)">Trọng Tài: Chờ Đối Tác (THEM)</div>
            <div style="font-size:22px;font-weight:700;color:#38bdf8">${analytics.ball_in_court?.them_count || 0} (${analytics.ball_in_court?.them_pct || 0}%)</div>
          </div>
          <div style="background:rgba(255,255,255,0.03);padding:10px 14px;border-radius:8px;border:1px solid rgba(255,255,255,0.06)">
            <div style="font-size:11px;color:var(--color-neutral-400)">Khách Đang Lạnh / Im Lặng</div>
            <div style="font-size:22px;font-weight:700;color:#fbbf24">${(analytics.cold_leads || []).length} đối tác</div>
          </div>
        </div>
      </div>

      <!-- Grid 2 Cột: Top Connectors & Cold Leads -->
      <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(380px, 1fr));gap:16px">
        
        <!-- CỘT 1: TOP CẦU NỐI (KEY CONNECTORS) -->
        <div class="card card-pad">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
            <div style="font-size:14px;font-weight:700;color:#a855f7;display:flex;align-items:center;gap:6px">
              <i class="ph ph-arrows-split"></i> Top Cầu Nối Quan Hệ (Key Connectors)
            </div>
            <span class="badge" style="background:rgba(168,85,247,0.15);color:#c084fc">Trục Kết Nối</span>
          </div>
          <div style="display:flex;flex-direction:column;gap:10px">
            ${(analytics.top_connectors || []).map(c => `
              <div style="background:var(--color-bg);padding:12px;border-radius:8px;border:1px solid var(--color-divider);display:flex;justify-content:space-between;align-items:center">
                <div>
                  <div style="font-weight:700;font-size:13px;color:var(--color-text);display:flex;align-items:center;gap:6px">
                    ${escapeHtml(c.full_name)}
                    ${c.is_bridge ? '<span class="badge good sm" style="font-size:9.5px">Cầu Nối Chiến Lược</span>' : ''}
                  </div>
                  <div style="font-size:11.5px;color:var(--color-neutral-400);margin-top:2px">
                    ${escapeHtml(c.company || '—')} · ${escapeHtml(c.role || '—')}
                  </div>
                </div>
                <div style="text-align:right">
                  <div style="font-size:12px;font-weight:700;color:#818cf8">${c.degree_connections} liên kết</div>
                  <div style="font-size:10.5px;color:var(--color-neutral-400)">${c.deal_count} deals vệ tinh</div>
                  <button class="btn sm subtle" style="font-size:10.5px;padding:2px 6px;margin-top:4px" onclick="openLivingProfile360Modal('${c.id}')">Hồ sơ 360 →</button>
                </div>
              </div>
            `).join('')}
          </div>
        </div>

        <!-- CỘT 2: KHÁCH ĐANG LẠNH & NGUY CƠ CHURN -->
        <div class="card card-pad">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
            <div style="font-size:14px;font-weight:700;color:#fbbf24;display:flex;align-items:center;gap:6px">
              <i class="ph ph-snowflake"></i> Khách Hàng Đang Lạnh (Cold Leads)
            </div>
            <span class="badge danger sm">Cần Kích Hoạt Lại</span>
          </div>
          <div style="display:flex;flex-direction:column;gap:10px">
            ${(analytics.cold_leads || []).map(c => `
              <div style="background:var(--color-bg);padding:12px;border-radius:8px;border:1px solid var(--color-divider);display:flex;justify-content:space-between;align-items:center">
                <div>
                  <div style="font-weight:700;font-size:13px;color:var(--color-text);display:flex;align-items:center;gap:6px">
                    ${escapeHtml(c.full_name)}
                    <span class="badge ${c.risk_level === 'CAO' ? 'danger' : 'p1'} sm">${c.risk_level}</span>
                  </div>
                  <div style="font-size:11.5px;color:var(--color-neutral-400);margin-top:2px">
                    ${escapeHtml(c.company || '—')} · Đã im lặng <b style="color:#ef4444">${c.went_silent_days} ngày</b>
                  </div>
                  <div style="font-size:11px;color:#a5b4fc;margin-top:4px">
                    💡 Đề xuất: ${escapeHtml(c.action_recommended)}
                  </div>
                </div>
                <div style="text-align:right">
                  <span class="badge neutral" style="font-weight:700">${c.heat_score}°</span>
                  <div style="margin-top:6px">
                    <button class="btn sm primary" style="font-size:10.5px;padding:3px 8px" onclick="openLivingProfile360Modal('${c.id}')">Hâm Nóng</button>
                  </div>
                </div>
              </div>
            `).join('')}
          </div>
        </div>

      </div>

    </div>
  `;
}

function renderCareQualityView() {
  const care = state._care_quality || {
    summary: { overall_care_score: 88.5, median_response_min: 4.8, avg_follow_up_rate_pct: 92.0, unresolved_broken_promises: 1, total_abandoned_contacts: 2 },
    agents: [
      { id: 'CQ-01', agent_name: 'Lê Thùy Linh', role: 'Senior B2B Account Manager', median_response_min: 4.2, follow_up_rate_pct: 94.0, broken_promises_count: 0, abandoned_contacts_count: 0, care_score: 96, winning_notes: 'Phản hồi dưới 5 phút, gửi demo trực quan và chốt điều khoản khi khách đang nóng.' },
      { id: 'CQ-02', agent_name: 'Trần Quốc Tuấn', role: 'Junior Key Account Executive', median_response_min: 18.5, follow_up_rate_pct: 62.0, broken_promises_count: 2, abandoned_contacts_count: 2, care_score: 64, winning_notes: 'Lễ phép, chăm chỉ nhưng cần cải thiện kỷ luật theo dõi.' },
      { id: 'CQ-03', agent_name: 'Nguyễn Hoàng Nam', role: 'Chuyên Viên Kỹ Thuật & Triển Khai', median_response_min: 8.0, follow_up_rate_pct: 88.0, broken_promises_count: 0, abandoned_contacts_count: 0, care_score: 88, winning_notes: 'Cung cấp giải pháp kỹ thuật chính xác, hỗ trợ ngoài giờ tận tâm.' }
    ],
    time_slot_averages: {
      morning: { slot: 'Sáng (08:00 - 12:00)', median_min: 3.8, rating: 'Rất Nhanh' },
      noon: { slot: 'Trưa (12:00 - 13:30)', median_min: 11.5, rating: 'Chậm' },
      afternoon: { slot: 'Chiều (13:30 - 18:00)', median_min: 4.5, rating: 'Nhanh' },
      evening: { slot: 'Tối (18:00 - 22:00)', median_min: 8.2, rating: 'Trung Bình' }
    }
  };

  if (!state._care_quality_fetched) {
    state._care_quality_fetched = true;
    fetch('/api/care_quality/analytics')
      .then(r => r.json())
      .then(d => {
        if (d && d.ok) {
          state._care_quality = d;
          renderContent();
        }
      })
      .catch(e => console.warn('Could not fetch care quality:', e));
  }

  return `
    <div style="display:flex;flex-direction:column;gap:16px">
      
      <!-- Top Ribbon KPI -->
      <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(200px, 1fr));gap:12px">
        <div class="card card-pad" style="background:rgba(16,185,129,0.08);border-color:rgba(16,185,129,0.25)">
          <div style="font-size:11px;color:var(--color-neutral-400);text-transform:uppercase">Điểm Chăm Sóc Toàn Đoàn</div>
          <div style="font-size:24px;font-weight:700;color:#10b981;margin:2px 0">${care.summary?.overall_care_score || 88}/100</div>
          <div style="font-size:11px;color:var(--color-neutral-300)">Đánh giá chất lượng thực chiến</div>
        </div>
        <div class="card card-pad" style="background:rgba(56,189,248,0.08);border-color:rgba(56,189,248,0.25)">
          <div style="font-size:11px;color:var(--color-neutral-400);text-transform:uppercase">Tốc Độ Phản Hồi Trung Vị</div>
          <div style="font-size:24px;font-weight:700;color:#38bdf8;margin:2px 0">${care.summary?.median_response_min || 4.5} phút</div>
          <div style="font-size:11px;color:var(--color-neutral-300)">Thời gian từ khi khách gửi tin</div>
        </div>
        <div class="card card-pad" style="background:rgba(168,85,247,0.08);border-color:rgba(168,85,247,0.25)">
          <div style="font-size:11px;color:var(--color-neutral-400);text-transform:uppercase">Tỷ Lệ Follow Sau Báo Giá</div>
          <div style="font-size:24px;font-weight:700;color:#c084fc;margin:2px 0">${care.summary?.avg_follow_up_rate_pct || 90}%</div>
          <div style="font-size:11px;color:var(--color-neutral-300)">Không để khách chết sau báo giá</div>
        </div>
        <div class="card card-pad" style="background:rgba(244,63,94,0.08);border-color:rgba(244,63,94,0.25)">
          <div style="font-size:11px;color:var(--color-neutral-400);text-transform:uppercase">Hứa Nhưng Quên / Thất Hứa</div>
          <div style="font-size:24px;font-weight:700;color:#f43f5e;margin:2px 0">${care.summary?.unresolved_broken_promises || 0} việc</div>
          <div style="font-size:11px;color:var(--color-neutral-300)">Cam kết chưa hoàn tất</div>
        </div>
      </div>

      <!-- Bảng Nhân Viên -->
      <div class="card" style="padding:16px">
        <div style="font-size:14px;font-weight:700;color:var(--color-text);margin-bottom:12px;display:flex;align-items:center;gap:6px">
          <i class="ph ph-users-three"></i> Bảng Đánh Giá Chất Lượng Chăm Sóc Theo Nhân Sự (Spec LOCKED v2.2 Mục E8)
        </div>
        <div style="overflow-x:auto">
          <table class="table" style="width:100%;font-size:12px">
            <thead>
              <tr style="border-bottom:1px solid var(--color-divider);color:var(--color-neutral-400)">
                <th style="padding:8px">Nhân Sự</th>
                <th style="padding:8px">Vai Trò</th>
                <th style="padding:8px;text-align:center">Tốc Độ TB</th>
                <th style="padding:8px;text-align:center">Follow Sau Giá</th>
                <th style="padding:8px;text-align:center">Thất Hứa</th>
                <th style="padding:8px;text-align:center">Khách Bỏ Rơi</th>
                <th style="padding:8px;text-align:center">Điểm Care</th>
                <th style="padding:8px">Kịch Bản Thắng / Ghi Chú</th>
              </tr>
            </thead>
            <tbody>
              ${(care.agents || []).map(a => `
                <tr style="border-bottom:1px solid rgba(255,255,255,0.04)">
                  <td style="padding:10px 8px;font-weight:700;color:var(--color-text)">${escapeHtml(a.agent_name)}</td>
                  <td style="padding:10px 8px;color:var(--color-neutral-300)">${escapeHtml(a.role)}</td>
                  <td style="padding:10px 8px;text-align:center;font-weight:600;color:#38bdf8">${a.median_response_min}m</td>
                  <td style="padding:10px 8px;text-align:center;font-weight:600;color:#34d399">${a.follow_up_rate_pct}%</td>
                  <td style="padding:10px 8px;text-align:center;color:${a.broken_promises_count > 0 ? '#ef4444' : '#94a3b8'}">${a.broken_promises_count}</td>
                  <td style="padding:10px 8px;text-align:center;color:${a.abandoned_contacts_count > 0 ? '#f59e0b' : '#94a3b8'}">${a.abandoned_contacts_count}</td>
                  <td style="padding:10px 8px;text-align:center">
                    <span class="badge ${a.care_score >= 85 ? 'good' : (a.care_score >= 70 ? 'p1' : 'danger')}">${a.care_score}/100</span>
                  </td>
                  <td style="padding:10px 8px;color:var(--color-neutral-300);max-width:280px;line-height:1.4">
                    ${escapeHtml(a.winning_notes || '—')}
                  </td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  `;
}

function openAddRelationshipEdgeModal() {
  openModal('🔗 Thêm Liên Kết Quan Hệ Mạng Lưới Mới', `
    <div class="form-group">
      <label class="form-label">Điểm Bắt Đầu (From Node / Contact / Nhóm)</label>
      <input type="text" class="form-input" id="edge-from-node" placeholder="Ví dụ: cnt-1 hoặc grp-zalo-crm">
    </div>
    <div class="form-group">
      <label class="form-label">Điểm Đích (To Node / Contact / Deal)</label>
      <input type="text" class="form-input" id="edge-to-node" placeholder="Ví dụ: cnt-2 hoặc opp-OPP-01">
    </div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
      <div class="form-group">
        <label class="form-label">Loại Liên Kết</label>
        <select class="form-select" id="edge-type">
          <option value="collaboration">Hợp Tác / Trao Đổi</option>
          <option value="referral">Giới Thiệu Đối Tác</option>
          <option value="channel_link">Kênh Hội Thoại</option>
          <option value="deal_link">Cơ Hội Thương Mại</option>
        </select>
      </div>
      <div class="form-group">
        <label class="form-label">Giai Đoạn Quan Hệ</label>
        <select class="form-select" id="edge-stage">
          <option value="hot">Nóng (Hot >= 80°)</option>
          <option value="warm" selected>Ấm Áp (Warm 50-79°)</option>
          <option value="partner">Đối Tác Chiến Lược</option>
          <option value="cold">Lạnh / Went Silent</option>
        </select>
      </div>
    </div>
    <div class="form-group">
      <label class="form-label">Chủ Đề / Ghi Chú Liên Kết</label>
      <input type="text" class="form-input" id="edge-topic" placeholder="Ví dụ: Trao đổi hợp đồng license phần mềm">
    </div>
  `, async () => {
    const from_node = $('#edge-from-node').value.trim();
    const to_node = $('#edge-to-node').value.trim();
    if (!from_node || !to_node) {
      showToast('Vui lòng nhập cả From và To node');
      return;
    }
    const edge_type = $('#edge-type').value;
    const relationship_stage = $('#edge-stage').value;
    const last_topic = $('#edge-topic').value.trim();

    try {
      const res = await fetch('/api/relationship_graph/edge', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ from_node, to_node, edge_type, relationship_stage, last_topic })
      }).then(r => r.json());

      if (res.ok) {
        showToast('✓ Đã tạo liên kết quan hệ thành công!');
        closeModal();
        delete state._rel_analytics_fetched;
        await fetchAllData();
      } else {
        showToast('Lỗi: ' + (res.error || 'Không thể tạo liên kết'));
      }
    } catch(e) {
      showToast('Lỗi kết nối máy chủ');
    }
  }, false, 'Tạo Liên Kết');
}
"""

if "SPEC-43: RELATIONSHIP ANALYTICS & CARE QUALITY VIEWS" not in content:
    content += "\n" + spec43_js
    print("Appended SPEC-43 JavaScript views successfully.")
else:
    print("SPEC-43 JS already present.")

with open(DASHBOARD_PATH, "w", encoding="utf-8") as f:
    f.write(content)

print("Dashboard UI patch completed.")
