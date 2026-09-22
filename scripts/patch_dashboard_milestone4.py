# -*- coding: utf-8 -*-
"""
Script nâng cấp Dashboard HTML cho Chặng 4 (MS-4):
- SPEC-19: [UI-03] Interactive Relationship Map Canvas (Canvas HTML5 mạng lưới Node/Edge HQ -> Groups -> Contacts -> Deals).
- SPEC-20 & SPEC-10: [UI-04] Living Profile 360 & Explainable AI (Modal/Drawer chi tiết, Tóm tắt AI 8-12 dòng, Thang điểm minh bạch, Slider 6 Mức Tự Trị 0-6, Timeline sự kiện nguyên tử).
- SPEC-24: [UI-08] Knowledge & Search (Bộ lọc Ý định Intent & Khách im lặng Went Silent trong Chat Intelligence).
"""
import os
import re

html_path = "/home/ryan/heo-harness/heo_harness/plugins/ui_dashboard/dashboard.html"
with open(html_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Nâng cấp renderActiveHub để kích hoạt Canvas khi vào relationship_radar (subtab graph)
hook_pattern = """    case 'relationship_radar':
      titleEl.textContent = 'Radar Quan Hệ & Living Profiles 360';
      subEl.textContent = 'Giám sát nhiệt độ quan hệ (Hot/Warm/Cold), trạng thái giữ bóng (Ball Control) & Hợp nhất định danh';
      container.innerHTML = renderRelationshipRadarHub();
      break;"""

hook_replacement = """    case 'relationship_radar':
      titleEl.textContent = 'Radar Quan Hệ, Bản Đồ Mạng Lưới & Hồ Sơ Sống 360';
      subEl.textContent = 'Bản đồ mạng lưới đồ thị tương tác, phân tích nhiệt độ quan hệ, giải thích điểm Explainable AI, kiểm soát lượt bóng & thang đo 6 cấp tự trị';
      container.innerHTML = renderRelationshipRadarHub();
      if ((state.subtabs.relationship_radar || 'graph') === 'graph') {
        setTimeout(initRelationshipGraphCanvas, 60);
      }
      break;"""

if hook_pattern in content:
    content = content.replace(hook_pattern, hook_replacement)
    print("✓ Đã chèn hook khởi tạo Canvas vào renderActiveHub")
else:
    print("! Cảnh báo: Không tìm thấy hook_pattern")

# 2. Thay thế renderRelationshipRadarHub cũ bằng bộ 3 views mới
old_radar_hub_regex = r"function renderRelationshipRadarHub\(\)\s*\{[\s\S]*?^function moveOpportunityStage"

new_radar_views_code = '''function renderRelationshipRadarHub() {
  state.subtabs.relationship_radar = state.subtabs.relationship_radar || 'graph';
  const curSub = state.subtabs.relationship_radar;
  const contacts = state.df_contacts || [];
  const hotContacts = contacts.filter(c => (c.heat_score || 50) >= 80);
  const warmContacts = contacts.filter(c => (c.heat_score || 50) >= 50 && (c.heat_score || 50) < 80);
  const coldContacts = contacts.filter(c => (c.heat_score || 50) < 50 || (c.went_silent_days || 0) > 7);

  return `
    <div class="hub-header">
      <div class="hub-header-top">
        <div>
          <h1 class="hub-title">Radar Quan Hệ, Bản Đồ Mạng Lưới & Hồ Sơ Sống 360</h1>
          <p class="hub-desc">
            Bản đồ đồ thị mạng lưới tương tác (Canvas HTML5), phân tích nhiệt độ quan hệ, giải thích điểm Explainable AI, trọng tài kiểm soát lượt bóng & thang trượt 6 cấp tự trị.
          </p>
        </div>
        <div style="display:flex;gap:8px">
          <button class="btn primary" onclick="openMergeContactsModal()"><i class="ph ph-link"></i> Hợp Nhất Định Danh</button>
          <button class="btn" onclick="fetchAllData()"><i class="ph ph-arrows-clockwise"></i> Làm Mới</button>
        </div>
      </div>

      <!-- Subnav Tabs Chặng 4 -->
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
    ${curSub === 'profiles' ? renderLivingProfilesTableView(contacts) : ''}
  `;
}

// ----------------------------------------------------
// View 1: Bản Đồ Mạng Lưới Đồ Thị (SPEC-19: [UI-03] Relationship Map)
// ----------------------------------------------------
function renderRelationshipGraphView() {
  return `
    <div class="card" style="margin-bottom:20px">
      <div class="card-header" style="flex-wrap:wrap;gap:10px">
        <div style="display:flex;align-items:center;gap:12px">
          <div class="card-title"><i class="ph ph-graph" style="color:var(--color-accent)"></i> Bản Đồ Quan Hệ Mạng Lưới Tương Tác (Canvas HTML5)</div>
          <span class="badge neutral" id="graph-stat-badge">Đang kết nối đồ thị...</span>
        </div>
        
        <!-- Controls Toolbar -->
        <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap">
          <div style="display:flex;background:var(--color-bg);border:1px solid var(--color-divider);border-radius:6px;padding:2px">
            <button class="btn sm subtle" id="btn-filter-all" onclick="filterGraphNodes('all')" style="font-size:11px;padding:4px 8px">Tất Cả</button>
            <button class="btn sm subtle" id="btn-filter-hot" onclick="filterGraphNodes('hot')" style="font-size:11px;padding:4px 8px;color:#ef4444">🔥 Khách Nóng</button>
            <button class="btn sm subtle" id="btn-filter-deal" onclick="filterGraphNodes('deal')" style="font-size:11px;padding:4px 8px;color:#a855f7">💼 Kèm Deals</button>
          </div>

          <input type="text" class="form-input" id="graph-search-input" placeholder="Tìm kiếm node..." style="width:140px;height:28px;font-size:11.5px;padding:2px 8px" oninput="searchGraphNode(this.value)">

          <div style="display:flex;gap:4px">
            <button class="btn sm subtle" onclick="zoomGraphCanvas(1.2)" title="Phóng to"><i class="ph ph-magnifying-glass-plus"></i></button>
            <button class="btn sm subtle" onclick="zoomGraphCanvas(0.8)" title="Thu nhỏ"><i class="ph ph-magnifying-glass-minus"></i></button>
            <button class="btn sm subtle" onclick="resetGraphCanvasView()" title="Căn giữa"><i class="ph ph-arrows-out-cardinal"></i></button>
            <button class="btn sm primary" onclick="initRelationshipGraphCanvas()" title="Tải lại đồ thị"><i class="ph ph-arrows-clockwise"></i></button>
          </div>
        </div>
      </div>

      <!-- Canvas Container -->
      <div style="position:relative;width:100%;height:620px;background:#060a12;overflow:hidden;border-radius:0 0 8px 8px">
        <canvas id="relationship-graph-canvas" style="display:block;cursor:grab;width:100%;height:100%"></canvas>
        
        <!-- Floating Legend Overlay -->
        <div style="position:absolute;bottom:16px;left:16px;background:rgba(15,23,42,0.85);backdrop-filter:blur(8px);border:1px solid rgba(255,255,255,0.1);padding:10px 14px;border-radius:8px;font-size:11px;display:flex;flex-direction:column;gap:6px;pointer-events:none;z-index:5">
          <div style="font-weight:700;color:var(--color-text);margin-bottom:2px;display:flex;align-items:center;gap:6px">
            <i class="ph ph-info"></i> CHÚ THÍCH MẠNG LƯỚI
          </div>
          <div style="display:flex;align-items:center;gap:8px">
            <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#6366f1;box-shadow:0 0 6px #6366f1"></span>
            <span style="color:#cbd5e1">👑 HQ Tổng Chỉ Huy Sếp Ryan</span>
          </div>
          <div style="display:flex;align-items:center;gap:8px">
            <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#0284c7"></span>
            <span style="color:#cbd5e1">💬 Nhóm Zalo / 📱 Nhóm WhatsApp</span>
          </div>
          <div style="display:flex;align-items:center;gap:8px">
            <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#ef4444;box-shadow:0 0 6px #ef4444"></span>
            <span style="color:#cbd5e1">🔴 Khách Hàng Nóng (Heat >= 80°)</span>
          </div>
          <div style="display:flex;align-items:center;gap:8px">
            <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#f59e0b"></span>
            <span style="color:#cbd5e1">🟡 Đối Tác Ấm Áp (Heat 50-79°)</span>
          </div>
          <div style="display:flex;align-items:center;gap:8px">
            <span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#64748b"></span>
            <span style="color:#cbd5e1">⚪ Đang Lạnh / Went Silent (<50°)</span>
          </div>
          <div style="display:flex;align-items:center;gap:8px">
            <span style="display:inline-block;width:12px;height:12px;border-radius:4px;background:#a855f7"></span>
            <span style="color:#cbd5e1">💼 Deals Cơ Hội Thương Mại (VND)</span>
          </div>
        </div>

        <!-- Floating Action Tip -->
        <div style="position:absolute;top:16px;right:16px;background:rgba(15,23,42,0.85);backdrop-filter:blur(8px);border:1px solid rgba(255,255,255,0.1);padding:8px 12px;border-radius:8px;font-size:11px;color:#94a3b8;pointer-events:none;z-index:5">
          <i class="ph ph-cursor-click"></i> <b>Kéo thả</b> node · <b>Cuộn chuột</b> phóng to · <b>Nhấp đúp vào Contact</b> để mở Hồ Sơ Sống 360
        </div>
      </div>
    </div>
  `;
}

// ----------------------------------------------------
// View 2: Phân Bổ Nhiệt Độ & Trọng Tài Bóng (SPEC-19)
// ----------------------------------------------------
function renderRelationshipRadarView(hotContacts, warmContacts, coldContacts) {
  return `
    <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(280px, 1fr));gap:14px;margin-bottom:18px">
      <!-- HOT -->
      <div class="card card-pad" style="border-top:3px solid #ef4444">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">
          <div style="font-weight:700;color:#ef4444;display:flex;align-items:center;gap:6px">
            <i class="ph ph-fire"></i> Khách Hàng Nóng (${hotContacts.length})
          </div>
          <span class="badge danger">Heat >= 80°</span>
        </div>
        <div style="font-size:11.5px;color:var(--color-neutral-400);margin-bottom:10px">Tương tác dồn dập, có giao dịch lớn hoặc khiếu nại khẩn. Cần phản hồi ngay.</div>
        <div style="display:flex;flex-direction:column;gap:8px">
          ${hotContacts.map(c => `
            <div style="background:var(--color-bg);padding:10px;border-radius:6px;border:1px solid var(--color-divider);display:flex;justify-content:space-between;align-items:center;cursor:pointer;transition:border-color 0.2s" onclick="openLivingProfile360Modal('${c.id}')">
              <div>
                <div style="font-weight:600;font-size:12.5px;display:flex;align-items:center;gap:6px">
                  ${escapeHtml(c.full_name)}
                  <span class="badge primary" style="font-size:9.5px;padding:1px 5px">Cấp ${c.autonomy_level || 1}</span>
                </div>
                <div style="font-size:11px;color:var(--color-neutral-400)">${escapeHtml(c.company || 'Doanh nghiệp')} · ${c.ball_owner === 'US' ? '🎾 Cần ta trả lời' : '⚽ Chờ khách'}</div>
              </div>
              <div style="text-align:right">
                <span class="badge danger" style="font-weight:700">${c.heat_score}°</span>
                <div style="font-size:10px;color:var(--color-neutral-400);margin-top:2px">Xem 360 →</div>
              </div>
            </div>
          `).join('')}
        </div>
      </div>

      <!-- WARM -->
      <div class="card card-pad" style="border-top:3px solid #f59e0b">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">
          <div style="font-weight:700;color:#f59e0b;display:flex;align-items:center;gap:6px">
            <i class="ph ph-sun"></i> Đối Tác Ấm Áp (${warmContacts.length})
          </div>
          <span class="badge p1">Heat 50 - 79°</span>
        </div>
        <div style="font-size:11.5px;color:var(--color-neutral-400);margin-bottom:10px">Đang trao đổi đều đặn, cơ hội đang nuôi dưỡng hoặc hợp tác định kỳ.</div>
        <div style="display:flex;flex-direction:column;gap:8px">
          ${warmContacts.map(c => `
            <div style="background:var(--color-bg);padding:10px;border-radius:6px;border:1px solid var(--color-divider);display:flex;justify-content:space-between;align-items:center;cursor:pointer;transition:border-color 0.2s" onclick="openLivingProfile360Modal('${c.id}')">
              <div>
                <div style="font-weight:600;font-size:12.5px;display:flex;align-items:center;gap:6px">
                  ${escapeHtml(c.full_name)}
                  <span class="badge neutral" style="font-size:9.5px;padding:1px 5px">Cấp ${c.autonomy_level || 1}</span>
                </div>
                <div style="font-size:11px;color:var(--color-neutral-400)">${escapeHtml(c.company || 'Doanh nghiệp')} · ${c.ball_owner === 'US' ? '🎾 Cần ta' : '⚽ Chờ khách'}</div>
              </div>
              <div style="text-align:right">
                <span class="badge p1" style="font-weight:700">${c.heat_score}°</span>
                <div style="font-size:10px;color:var(--color-neutral-400);margin-top:2px">Xem 360 →</div>
              </div>
            </div>
          `).join('')}
        </div>
      </div>

      <!-- COLD / WENT SILENT -->
      <div class="card card-pad" style="border-top:3px solid #64748b">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">
          <div style="font-weight:700;color:#94a3b8;display:flex;align-items:center;gap:6px">
            <i class="ph ph-snowflake"></i> Đang Lạnh / Went Silent (${coldContacts.length})
          </div>
          <span class="badge neutral">Im lặng > 7 ngày</span>
        </div>
        <div style="font-size:11.5px;color:var(--color-neutral-400);margin-bottom:10px">Đối tác có dấu hiệu nguội, không phản hồi sau báo giá hoặc demo.</div>
        <div style="display:flex;flex-direction:column;gap:8px">
          ${coldContacts.map(c => `
            <div style="background:var(--color-bg);padding:10px;border-radius:6px;border:1px solid var(--color-divider);display:flex;justify-content:space-between;align-items:center;cursor:pointer;transition:border-color 0.2s" onclick="openLivingProfile360Modal('${c.id}')">
              <div>
                <div style="font-weight:600;font-size:12.5px;display:flex;align-items:center;gap:6px">
                  ${escapeHtml(c.full_name)}
                  <span class="badge neutral" style="font-size:9.5px;padding:1px 5px">Cấp ${c.autonomy_level || 1}</span>
                </div>
                <div style="font-size:11px;color:#ef4444">⚠️ Im lặng ${c.went_silent_days || 8} ngày</div>
              </div>
              <div style="text-align:right">
                <span class="badge neutral">${c.heat_score}°</span>
                <div style="font-size:10px;color:var(--color-neutral-400);margin-top:2px">Xem 360 →</div>
              </div>
            </div>
          `).join('')}
        </div>
      </div>
    </div>
  `;
}

// ----------------------------------------------------
// View 3: Danh Sách Hồ Sơ Sống 360 (SPEC-20, SPEC-10)
// ----------------------------------------------------
function renderLivingProfilesTableView(contacts) {
  return `
    <div class="card">
      <div class="card-header">
        <div class="card-title"><i class="ph ph-user-list"></i> Hồ Sơ Sống 360 & Tóm Tắt Trí Tuệ (Living Profiles Directory)</div>
      </div>
      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Họ & Tên</th>
              <th>Doanh Nghiệp / Chức Vụ</th>
              <th>Kênh Kết Nối</th>
              <th>Mức Tự Trị</th>
              <th>Nhiệt Độ</th>
              <th>Ai Giữ Bóng</th>
              <th>Tóm Tắt AI (Living Profile)</th>
              <th>Thao Tác</th>
            </tr>
          </thead>
          <tbody>
            ${contacts.length === 0 ? `
              <tr><td colspan="9" style="text-align:center;padding:24px;color:var(--color-neutral-400)">Chưa có hồ sơ liên hệ</td></tr>
            ` : contacts.map(c => `
              <tr>
                <td style="font-family:var(--mono);color:var(--color-accent);font-size:11px">${c.id}</td>
                <td style="font-weight:600;cursor:pointer" onclick="openLivingProfile360Modal('${c.id}')">
                  <div style="display:flex;align-items:center;gap:6px">
                    <span style="display:inline-block;width:24px;height:24px;border-radius:50%;background:rgba(99,102,241,0.2);color:var(--color-accent);text-align:center;line-height:24px;font-size:10px;font-weight:700">${(c.full_name||'U').slice(0,2).toUpperCase()}</span>
                    <span>${escapeHtml(c.full_name)}</span>
                  </div>
                </td>
                <td style="color:var(--color-neutral-300)">${escapeHtml(c.company || '—')} <br><span style="font-size:11px;color:var(--color-neutral-400)">${escapeHtml(c.role || '')}</span></td>
                <td>
                  <div style="display:flex;flex-direction:column;gap:2px;font-size:11px">
                    ${c.phone ? `<span>📞 ${escapeHtml(c.phone)}</span>` : ''}
                    ${c.zalo_id ? `<span style="color:#0284c7">💬 Zalo: ${escapeHtml(c.zalo_id)}</span>` : ''}
                    ${c.whatsapp_id ? `<span style="color:#10b981">📱 WA: ${escapeHtml(c.whatsapp_id)}</span>` : ''}
                  </div>
                </td>
                <td>
                  <span class="badge ${c.autonomy_level >= 3 ? 'good' : (c.autonomy_level >= 1 ? 'p1' : 'neutral')}" style="font-size:10.5px">
                    Cấp ${c.autonomy_level || 1}/6
                  </span>
                </td>
                <td>
                  <span class="badge ${(c.heat_score || 50) >= 80 ? 'danger' : ((c.heat_score || 50) >= 50 ? 'p1' : 'neutral')}" style="font-weight:700">
                    ${c.heat_score || 50}°
                  </span>
                </td>
                <td>
                  <span class="badge ${c.ball_owner === 'US' ? 'danger' : 'neutral'}" style="font-size:10.5px">
                    ${c.ball_owner === 'US' ? '🎾 Phía Ta (US)' : '⚽ Đối Tác (THEM)'}
                  </span>
                </td>
                <td style="max-width:280px;font-size:11.5px;color:var(--color-neutral-300);line-height:1.4">
                  ${escapeHtml((c.ai_summary || 'Chưa có ghi chú tóm tắt AI').slice(0, 110))}...
                </td>
                <td>
                  <div style="display:flex;gap:4px">
                    <button class="btn sm primary" onclick="openLivingProfile360Modal('${c.id}')"><i class="ph ph-user"></i> Hồ Sơ 360</button>
                    <button class="btn sm" onclick="openChatWithContact('${escapeHtml(c.full_name)}')"><i class="ph ph-chat-circle-dots"></i></button>
                  </div>
                </td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    </div>
  `;
}

function moveOpportunityStage'''

content = re.sub(old_radar_hub_regex, new_radar_views_code, content, flags=re.MULTILINE)
print("✓ Đã thay thế renderRelationshipRadarHub với 3 Views chuẩn hóa")

# Ghi lại file tạm để kiểm tra
with open(html_path, "w", encoding="utf-8") as f:
    f.write(content)
print("✓ Đã lưu bước 1 vào dashboard.html")
