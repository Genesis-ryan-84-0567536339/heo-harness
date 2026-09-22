# -*- coding: utf-8 -*-
import os

dashboard_path = "/home/ryan/heo-harness/heo_harness/plugins/ui_dashboard/dashboard.html"
with open(dashboard_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. NEW renderOpportunitiesHub FUNCTION
new_render_hub = """// ==========================================
// MILESTONE 3: OPPORTUNITY KANBAN 7 CỘT & INBOX OF MEANING (SPEC F2.5, F2.2)
// ==========================================
let currentMeaningFilter = 'ALL';
let currentOppChannelFilter = 'ALL';
let currentOppHeatFilter = 'ALL';

function renderOpportunitiesHub() {
  const opps = state.df_opps || [];
  const events = (state.df_events || []).filter(e => !e.archived && e.status !== 'ARCHIVED');
  const currentSub = state.subtab?.opportunities || 'kanban_opps';

  // 7 Cột Pipeline chuẩn hóa theo Spec LOCKED v2.2 (Mục F2.5)
  const stages = [
    { key: 'RAW_SIGNAL', label: '📡 Tín Hiệu Thô', color: '#94a3b8', alias: ['RAW_SIGNAL', 'SIGNAL'] },
    { key: 'QUALIFIED', label: '🔍 Đã Xác Thực', color: '#38bdf8', alias: ['QUALIFIED', 'VERIFIED'] },
    { key: 'MATCHED', label: '🤝 Ráp Khớp Cung-Cầu', color: '#a855f7', alias: ['MATCHED'] },
    { key: 'OUTREACH', label: '📞 Tiếp Cận', color: '#f59e0b', alias: ['OUTREACH', 'APPROACHING'] },
    { key: 'NEGOTIATING', label: '💼 Đàm Phán', color: '#ec4899', alias: ['NEGOTIATING'] },
    { key: 'INTERNAL_REVIEW', label: '⚖️ Thẩm Định Nội Bộ', color: '#6366f1', alias: ['INTERNAL_REVIEW'] },
    { key: 'CLOSED_WON', label: '🏆 Chốt Đơn (Won)', color: '#10b981', alias: ['WON', 'CLOSED_WON'] }
  ];

  // Pipeline Metrics Calculation
  let filteredOpps = opps;
  if (currentOppChannelFilter !== 'ALL') {
    filteredOpps = filteredOpps.filter(o => (o.channel || '').toLowerCase() === currentOppChannelFilter.toLowerCase());
  }
  if (currentOppHeatFilter === 'HOT') {
    filteredOpps = filteredOpps.filter(o => (o.heat_score || 0) >= 80);
  } else if (currentOppHeatFilter === 'WARM') {
    filteredOpps = filteredOpps.filter(o => (o.heat_score || 0) >= 50 && (o.heat_score || 0) < 80);
  } else if (currentOppHeatFilter === 'COLD') {
    filteredOpps = filteredOpps.filter(o => (o.heat_score || 0) < 50);
  }

  const totalPipelineValue = filteredOpps.reduce((sum, o) => sum + (o.estimated_value || 0), 0);
  const wonOpps = filteredOpps.filter(o => ['WON', 'CLOSED_WON'].includes(o.stage));
  const wonValue = wonOpps.reduce((sum, o) => sum + (o.estimated_value || 0), 0);
  const avgDealSize = filteredOpps.length > 0 ? (totalPipelineValue / filteredOpps.length) : 0;

  // Format currency helper
  const formatMoney = val => {
    if (!val || val === 0) return '0 ₫';
    if (val >= 1000000000) return (val / 1000000000).toFixed(2) + ' tỷ ₫';
    if (val >= 1000000) return (val / 1000000).toFixed(1) + ' tr ₫';
    return val.toLocaleString('vi-VN') + ' ₫';
  };

  return `
    <div class="hub-header">
      <div class="hub-header-top">
        <div>
          <h1 class="hub-title">Hộp Thư Ý Nghĩa & Bảng Cơ Hội (Inbox of Meaning & Opportunities)</h1>
          <p class="hub-desc">Bóc tách ý định kinh doanh thực tế, đề xuất hành động và quy trình Kanban 7 cột chuẩn hóa từ hội thoại đa kênh Zalo & WhatsApp.</p>
        </div>
        <div style="display:flex;gap:8px">
          <button class="btn primary" onclick="openCreateOpportunityModal()"><i class="ph ph-plus"></i> Tạo Cơ Hội Mới</button>
          <button class="btn" onclick="fetchAllData()"><i class="ph ph-arrows-clockwise"></i> Làm Mới</button>
        </div>
      </div>

      <!-- Pipeline KPIs Ribbon -->
      <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(210px, 1fr));gap:12px;margin-top:14px">
        <div class="card card-pad" style="background:rgba(99, 102, 241, 0.08);border-color:rgba(99, 102, 241, 0.3)">
          <div style="font-size:11px;color:var(--color-neutral-400);text-transform:uppercase;font-weight:600">Tổng Giá Trị Pipeline</div>
          <div style="font-size:22px;font-weight:700;color:#818cf8;margin:2px 0">${formatMoney(totalPipelineValue)}</div>
          <div style="font-size:11px;color:var(--color-neutral-300)">${filteredOpps.length} cơ hội đang vận hành</div>
        </div>
        <div class="card card-pad" style="background:rgba(16, 185, 129, 0.08);border-color:rgba(16, 185, 129, 0.3)">
          <div style="font-size:11px;color:var(--color-neutral-400);text-transform:uppercase;font-weight:600">Doanh Số Đã Chốt (Won)</div>
          <div style="font-size:22px;font-weight:700;color:#34d399;margin:2px 0">${formatMoney(wonValue)}</div>
          <div style="font-size:11px;color:var(--color-neutral-300)">${wonOpps.length} hợp đồng thành công</div>
        </div>
        <div class="card card-pad" style="background:rgba(245, 158, 11, 0.08);border-color:rgba(245, 158, 11, 0.3)">
          <div style="font-size:11px;color:var(--color-neutral-400);text-transform:uppercase;font-weight:600">Giá Trị Deal Trung Bình</div>
          <div style="font-size:22px;font-weight:700;color:#fbbf24;margin:2px 0">${formatMoney(avgDealSize)}</div>
          <div style="font-size:11px;color:var(--color-neutral-300)">Quy mô đơn hàng trung bình</div>
        </div>
        <div class="card card-pad" style="background:rgba(56, 189, 248, 0.08);border-color:rgba(56, 189, 248, 0.3)">
          <div style="font-size:11px;color:var(--color-neutral-400);text-transform:uppercase;font-weight:600">Hộp Thư Ý Nghĩa Cần Xử Lý</div>
          <div style="font-size:22px;font-weight:700;color:#38bdf8;margin:2px 0">${events.length} thẻ</div>
          <div style="font-size:11px;color:var(--color-neutral-300)">Tín hiệu mới từ Zalo/WhatsApp</div>
        </div>
      </div>

      <!-- Subnav Pills & Filters -->
      <div class="hub-subnav" style="margin-top:14px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px">
        <div style="display:flex;gap:8px">
          <button class="hub-subnav-btn ${currentSub === 'kanban_opps' ? 'active' : ''}" onclick="switchSubtab('opportunities', 'kanban_opps')">
            <i class="ph ph-kanban"></i> Bảng Cơ Hội 7 Cột (${filteredOpps.length})
          </button>
          <button class="hub-subnav-btn ${currentSub === 'meaning_inbox' ? 'active' : ''}" onclick="switchSubtab('opportunities', 'meaning_inbox')">
            <i class="ph ph-cards"></i> Hộp Thư Ý Nghĩa (Meaning Cards) (${events.length})
          </button>
        </div>

        ${currentSub === 'kanban_opps' ? `
          <div style="display:flex;gap:8px;align-items:center">
            <span style="font-size:11.5px;color:var(--color-neutral-400)">Kênh:</span>
            <select style="background:var(--color-surface);color:var(--color-text);font-size:11.5px;border:1px solid var(--color-divider);padding:4px 8px;border-radius:4px" onchange="currentOppChannelFilter=this.value;renderContent()">
              <option value="ALL" ${currentOppChannelFilter === 'ALL' ? 'selected' : ''}>Tất Cả Kênh</option>
              <option value="zalo" ${currentOppChannelFilter === 'zalo' ? 'selected' : ''}>Zalo</option>
              <option value="whatsapp" ${currentOppChannelFilter === 'whatsapp' ? 'selected' : ''}>WhatsApp</option>
              <option value="manual" ${currentOppChannelFilter === 'manual' ? 'selected' : ''}>Thủ công</option>
            </select>
            <span style="font-size:11.5px;color:var(--color-neutral-400)">Độ Nóng:</span>
            <select style="background:var(--color-surface);color:var(--color-text);font-size:11.5px;border:1px solid var(--color-divider);padding:4px 8px;border-radius:4px" onchange="currentOppHeatFilter=this.value;renderContent()">
              <option value="ALL" ${currentOppHeatFilter === 'ALL' ? 'selected' : ''}>Tất Cả</option>
              <option value="HOT" ${currentOppHeatFilter === 'HOT' ? 'selected' : ''}>🔥 Nóng (>80°)</option>
              <option value="WARM" ${currentOppHeatFilter === 'WARM' ? 'selected' : ''}>☀️ Ấm (50-80°)</option>
              <option value="COLD" ${currentOppHeatFilter === 'COLD' ? 'selected' : ''}>❄️ Lạnh (<50°)</option>
            </select>
          </div>
        ` : `
          <div style="display:flex;gap:6px;align-items:center;flex-wrap:wrap">
            <span style="font-size:11.5px;color:var(--color-neutral-400)">Lọc Ý Định:</span>
            <button class="btn sm ${currentMeaningFilter === 'ALL' ? 'primary' : ''}" onclick="currentMeaningFilter='ALL';renderContent()">Tất Cả</button>
            <button class="btn sm ${currentMeaningFilter === 'AskedPrice' ? 'primary' : ''}" onclick="currentMeaningFilter='AskedPrice';renderContent()">💰 Hỏi Giá</button>
            <button class="btn sm ${currentMeaningFilter === 'Complained' ? 'primary' : ''}" onclick="currentMeaningFilter='Complained';renderContent()">⚠️ Khiếu Nại</button>
            <button class="btn sm ${currentMeaningFilter === 'ScheduledMeeting' ? 'primary' : ''}" onclick="currentMeaningFilter='ScheduledMeeting';renderContent()">📅 Lịch Hẹn</button>
            <button class="btn sm ${currentMeaningFilter === 'RequestedPartnership' ? 'primary' : ''}" onclick="currentMeaningFilter='RequestedPartnership';renderContent()">🤝 Hợp Tác</button>
          </div>
        `}
      </div>
    </div>

    ${currentSub === 'kanban_opps' ? `
      <!-- KANBAN BOARD 7 CỘT CHUẨN HOÁ KÈM DRAG & DROP -->
      <div style="display:flex;gap:14px;overflow-x:auto;padding-bottom:16px;min-height:580px;align-items:flex-start">
        ${stages.map(st => {
          const colOpps = filteredOpps.filter(o => st.alias.includes(o.stage) || o.stage === st.key);
          const totalVal = colOpps.reduce((sum, o) => sum + (o.estimated_value || 0), 0);
          return `
            <div
              class="kanban-column"
              data-stage="${st.key}"
              ondragover="handleOppDragOver(event)"
              ondragleave="handleOppDragLeave(event)"
              ondrop="handleOppDrop(event, '${st.key}')"
              style="min-width:300px;max-width:330px;flex:1;background:var(--color-surface);border:1px solid var(--color-divider);border-radius:var(--radius-lg);display:flex;flex-direction:column;transition:border-color 0.2s ease, background 0.2s ease"
            >
              <div style="padding:12px 14px;border-bottom:1px solid var(--color-divider);display:flex;align-items:center;justify-content:space-between;background:rgba(255,255,255,0.02);border-top:3px solid ${st.color};border-top-left-radius:var(--radius-lg);border-top-right-radius:var(--radius-lg)">
                <div>
                  <div style="font-size:13px;font-weight:700;color:${st.color};display:flex;align-items:center;gap:6px">
                    ${st.label}
                  </div>
                  <div style="font-size:10.5px;color:var(--color-neutral-400);margin-top:2px">
                    ${colOpps.length} deal · ${formatMoney(totalVal)}
                  </div>
                </div>
                <span class="badge" style="background:rgba(255,255,255,0.08);color:var(--color-text);font-weight:700">${colOpps.length}</span>
              </div>

              <div style="padding:10px;flex:1;overflow-y:auto;display:flex;flex-direction:column;gap:10px;min-height:480px">
                ${colOpps.length === 0 ? `
                  <div style="text-align:center;padding:36px 12px;color:var(--color-neutral-500);font-size:12px;border:1px dashed rgba(255,255,255,0.06);border-radius:var(--radius-md)">
                    <i class="ph ph-tray" style="font-size:24px;display:block;margin-bottom:6px;opacity:0.4"></i>
                    Thả cơ hội vào đây
                  </div>
                ` : colOpps.map(o => `
                  <div
                    class="kanban-card"
                    id="opp-card-${o.id}"
                    draggable="true"
                    ondragstart="handleOppDragStart(event, '${o.id}')"
                    style="background:var(--color-bg);border:1px solid var(--color-divider);border-radius:var(--radius-md);padding:12px;display:flex;flex-direction:column;gap:8px;box-shadow:0 2px 6px rgba(0,0,0,0.2);cursor:grab;transition:transform 0.15s ease, border-color 0.15s ease"
                    onmouseover="this.style.borderColor='rgba(99,102,241,0.5)'"
                    onmouseout="this.style.borderColor='var(--color-divider)'"
                  >
                    <div style="display:flex;justify-content:space-between;align-items:center">
                      <div style="display:flex;align-items:center;gap:6px">
                        <span class="badge" style="font-size:9.5px;font-family:var(--mono);background:rgba(255,255,255,0.06);color:#c7d2fe">${o.id}</span>
                        <span class="badge" style="font-size:9px;text-transform:uppercase;background:rgba(99,102,241,0.15);color:#818cf8">${o.channel || 'zalo'}</span>
                      </div>
                      <span class="badge live" style="font-size:9.5px;background:rgba(245,158,11,0.15);color:#fbbf24;border:1px solid rgba(245,158,11,0.3)">
                        <i class="ph ph-fire"></i> ${o.heat_score || 60}°
                      </span>
                    </div>

                    <div style="font-weight:600;font-size:13px;color:var(--color-text);line-height:1.35;cursor:pointer" onclick="openOpportunityDetailModal('${o.id}')">
                      ${escapeHtml(o.title)}
                    </div>

                    <div style="font-size:11.5px;color:var(--color-neutral-300);display:flex;align-items:center;gap:6px">
                      <i class="ph ph-user"></i> <b>${escapeHtml(o.contact_name || 'Khách')}</b>
                      <span style="color:var(--color-neutral-500)">·</span>
                      <span style="font-size:11px;color:var(--color-neutral-400)">${escapeHtml(o.group_name || '1-1')}</span>
                    </div>

                    ${o.estimated_value > 0 ? `
                      <div style="display:flex;justify-content:space-between;align-items:center;background:rgba(16, 185, 129, 0.08);padding:6px 8px;border-radius:4px;border:1px solid rgba(16, 185, 129, 0.2)">
                        <span style="font-size:11px;color:var(--color-neutral-300)">Giá trị deal:</span>
                        <span style="font-size:12.5px;font-weight:700;color:#10b981;font-family:var(--mono)">${formatMoney(o.estimated_value)}</span>
                      </div>
                    ` : ''}

                    <div style="font-size:11px;color:var(--color-neutral-400);line-height:1.4;background:rgba(255,255,255,0.02);padding:6px 8px;border-radius:4px;max-height:45px;overflow:hidden;text-overflow:ellipsis">
                      ${escapeHtml(o.need_summary || 'Chưa có tóm tắt nhu cầu')}
                    </div>

                    <div style="display:flex;justify-content:space-between;align-items:center;font-size:10.5px;color:var(--color-neutral-400);margin-top:2px">
                      <span><i class="ph ph-user-circle"></i> ${escapeHtml(o.owner || 'Sếp Ryan')}</span>
                      <span>Xác suất: <b style="color:#a5b4fc">${o.win_probability || 50}%</b></span>
                    </div>

                    <div style="display:flex;justify-content:space-between;align-items:center;margin-top:6px;padding-top:6px;border-top:1px solid rgba(255,255,255,0.06);gap:6px">
                      <button class="btn sm" style="padding:3px 7px;font-size:10.5px" onclick="openOpportunityDetailModal('${o.id}')">
                        <i class="ph ph-magnifying-glass"></i> Chi Tiết
                      </button>
                      <button class="btn sm" style="padding:3px 7px;font-size:10.5px;background:rgba(168,85,247,0.15);color:#c084fc;border:1px solid rgba(168,85,247,0.3)" onclick="quickMatchOpportunity('${o.id}')" title="Tự động ráp khớp với catalog dịch vụ công ty">
                        <i class="ph ph-arrows-merge"></i> Ráp Khớp
                      </button>
                      <select style="background:var(--color-surface);color:var(--color-text);font-size:10.5px;border:1px solid var(--color-divider);padding:2px 4px;border-radius:4px;max-width:90px" onchange="moveOpportunityStage('${o.id}', this.value)">
                        ${stages.map(s => `<option value="${s.key}" ${(s.alias.includes(o.stage) || s.key === o.stage) ? 'selected' : ''}>➔ ${s.label.split(' ')[1]}</option>`).join('')}
                      </select>
                    </div>
                  </div>
                `).join('')}
              </div>
            </div>
          `;
        }).join('')}
      </div>
    ` : `
      <!-- MEANING INBOX (ACTIONABLE MEANING CARDS) -->
      <div style="display:flex;flex-direction:column;gap:14px">
        <div style="display:grid;grid-template-columns:repeat(auto-fill, minmax(360px, 1fr));gap:14px">
          ${(() => {
            let filteredEvents = events;
            if (currentMeaningFilter !== 'ALL') {
              filteredEvents = filteredEvents.filter(e => e.event_type === currentMeaningFilter || e.intent === currentMeaningFilter);
            }
            if (filteredEvents.length === 0) {
              return `
                <div class="card card-pad" style="grid-column:1/-1;text-align:center;padding:48px 16px;color:var(--color-neutral-400)">
                  <i class="ph ph-check-circle" style="font-size:36px;color:#10b981;margin-bottom:10px;display:block"></i>
                  <div style="font-size:15px;font-weight:600;color:var(--color-text);margin-bottom:4px">Đã Đạt Trạng Thái Inbox Zero!</div>
                  <div>Không còn thẻ ý nghĩa nào đang chờ xử lý trong danh mục này.</div>
                </div>
              `;
            }

            return filteredEvents.map(e => {
              const intentColors = {
                AskedPrice: '#f59e0b',
                Complained: '#ef4444',
                ScheduledMeeting: '#38bdf8',
                RequestedPartnership: '#a855f7',
                SentQuotation: '#10b981',
                MentionsCompetitor: '#ec4899',
                GeneralConversation: '#94a3b8'
              };
              const col = intentColors[e.event_type] || '#38bdf8';
              let parsedEnt = {};
              try { parsedEnt = typeof e.extracted_entities === 'string' ? JSON.parse(e.extracted_entities) : (e.extracted_entities || {}); } catch(err){}

              return `
                <div class="card" style="border-left:4px solid ${col};display:flex;flex-direction:column;justify-content:space-between;box-shadow:0 3px 8px rgba(0,0,0,0.2)">
                  <div style="padding:14px">
                    <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px">
                      <div style="display:flex;align-items:center;gap:8px">
                        <span class="badge" style="background:${col}22;color:${col};border:1px solid ${col}44;font-weight:700;font-size:10.5px">
                          ${escapeHtml(e.intent || e.event_type)}
                        </span>
                        <span class="badge" style="font-size:10px;text-transform:uppercase;background:rgba(255,255,255,0.06)">${e.channel || 'zalo'}</span>
                      </div>
                      <div style="display:flex;align-items:center;gap:6px">
                        <span class="badge ${e.priority === 'P0' ? 'danger' : e.priority === 'P1' ? 'p1' : 'neutral'}" style="font-size:10px">
                          ${e.priority || 'P2'} · <i class="ph ph-fire"></i> ${e.heat_score || 50}°
                        </span>
                        <button class="icon-btn" style="font-size:11px;color:var(--color-neutral-400)" onclick="archiveMeaningEvent('${e.id}')" title="Đánh dấu đã xử lý (Lưu trữ)">✕</button>
                      </div>
                    </div>

                    <div style="font-weight:600;font-size:13.5px;color:var(--color-text);margin-bottom:6px">
                      👤 ${escapeHtml(e.sender_name || 'Đối tác')}
                      <span style="font-weight:400;color:var(--color-neutral-400);font-size:11px">(${escapeHtml(e.group_name || '1-1')})</span>
                    </div>

                    <div style="background:rgba(255,255,255,0.03);padding:8px 10px;border-radius:var(--radius-sm);font-size:12px;color:var(--color-neutral-300);margin-bottom:10px;font-style:italic;border-left:2px solid rgba(255,255,255,0.1)">
                      "${escapeHtml(e.content)}"
                    </div>

                    <div style="font-size:12.5px;color:var(--color-text);margin-bottom:6px">
                      <b style="color:#a5b4fc">💡 Ý nghĩa:</b> ${escapeHtml(e.meaning_summary || 'Chưa có phân tích')}
                    </div>

                    <div style="font-size:12.5px;color:#38bdf8;margin-bottom:8px">
                      <b>⚡ Hành động đề xuất:</b> ${escapeHtml(e.action_suggested || 'Theo dõi tiếp')}
                    </div>

                    ${(parsedEnt.prices?.length || parsedEnt.products?.length || parsedEnt.dates?.length) ? `
                      <div style="display:flex;flex-wrap:wrap;gap:5px;margin-top:6px;padding:6px;background:rgba(0,0,0,0.2);border-radius:4px">
                        ${(parsedEnt.prices || []).map(p => `<span class="badge good" style="font-size:10px">💰 ${escapeHtml(p)}</span>`).join('')}
                        ${(parsedEnt.products || []).map(p => `<span class="badge neutral" style="font-size:10px">📦 ${escapeHtml(p)}</span>`).join('')}
                        ${(parsedEnt.dates || []).map(d => `<span class="badge p1" style="font-size:10px">📅 ${escapeHtml(d)}</span>`).join('')}
                      </div>
                    ` : ''}
                  </div>

                  <!-- 1-Click Action Hub -->
                  <div style="padding:10px 14px;border-top:1px solid var(--color-divider);background:rgba(255,255,255,0.015);display:flex;gap:6px;justify-content:flex-end;flex-wrap:wrap">
                    <button class="btn sm primary" onclick="acceptSuggestedAction('${e.id}', '${escapeHtml(e.action_suggested || '')}')">
                      <i class="ph ph-check"></i> Duyệt Trả Lời
                    </button>
                    <button class="btn sm" style="background:rgba(16, 185, 129, 0.15);color:#34d399;border:1px solid rgba(16, 185, 129, 0.3)" onclick="quickCreateQuotationFromEvent('${e.id}', '${escapeHtml(e.sender_name || 'Khách')}', '${escapeHtml(e.content)}')">
                      <i class="ph ph-file-text"></i> Soạn Báo Giá
                    </button>
                    <button class="btn sm" onclick="convertEventToTask('${e.id}', '${escapeHtml(e.meaning_summary || e.content)}')">
                      <i class="ph ph-check-square"></i> Tạo Việc
                    </button>
                    <button class="btn sm" onclick="convertEventToOpportunity('${e.id}', '${escapeHtml(e.sender_name || 'Khách')}', '${escapeHtml(e.content)}')">
                      <i class="ph ph-target"></i> Sang Deal
                    </button>
                    <button class="btn sm" style="color:var(--color-neutral-400)" onclick="archiveMeaningEvent('${e.id}')" title="Ẩn thẻ này">
                      <i class="ph ph-archive"></i> Xong
                    </button>
                  </div>
                </div>
              `;
            }).join('');
          })()}
        </div>
      </div>
    `}
  `;
}
"""

# Replace renderOpportunitiesHub block
import re
pattern = r'// ==========================================\s*// MILESTONE 3: OPPORTUNITY KANBAN.*?\nfunction renderOpportunitiesHub\(\) \{.*?\n\}\n\n// ==========================================\s*// MILESTONE 2: CONVERSATION DATA FACTORY'
match = re.search(pattern, content, flags=re.DOTALL)
if match:
    content = content[:match.start()] + new_render_hub + "\n\n// ==========================================\n// MILESTONE 2: CONVERSATION DATA FACTORY" + content[match.end():]
    print("Replaced renderOpportunitiesHub successfully!")
else:
    # Alternative replace
    s_idx = content.find("function renderOpportunitiesHub()")
    e_idx = content.find("function renderDataFactoryHub()")
    if s_idx != -1 and e_idx != -1:
        # Find preceding comment
        c_start = content.rfind("// ==========================================", 0, s_idx)
        if c_start == -1: c_start = s_idx
        content = content[:c_start] + new_render_hub + "\n\n" + content[e_idx:]
        print("Replaced renderOpportunitiesHub via index slice!")
    else:
        print("Could not find renderOpportunitiesHub block!")

with open(dashboard_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Saved updated dashboard.html!")
