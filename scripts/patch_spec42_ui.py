"""
Patch SPEC-42 (Living Profiles, Early Warning, Identity Resolution & Brain Search) UI into dashboard.html
"""

import re
import os

DASHBOARD_PATH = "heo_harness/plugins/ui_dashboard/dashboard.html"

with open(DASHBOARD_PATH, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Insert Early Warning Banner into renderCommandCenterHub
target_anchor = '<div class="kpi-grid">'
banner_html = """    <!-- SPEC-42: EARLY WARNING RADAR TICKER BANNER (MỤC L PHASE 2 & E9) -->
    <div id="early-warning-radar-banner" style="margin-bottom:16px;background:linear-gradient(135deg, rgba(239,68,68,0.08) 0%, rgba(245,158,11,0.05) 100%);border:1px solid rgba(239,68,68,0.25);border-radius:10px;padding:14px 18px">
      <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px">
        <div style="display:flex;align-items:center;gap:12px">
          <div style="width:40px;height:40px;border-radius:8px;background:rgba(239,68,68,0.15);display:flex;align-items:center;justify-content:center;color:#ef4444;font-size:20px">
            <i class="ph ph-radar"></i>
          </div>
          <div>
            <div style="display:flex;align-items:center;gap:8px">
              <span style="font-weight:800;font-size:14px;color:var(--color-text)">Radar Cảnh Báo Sớm & Hồ Sơ Động (SPEC-42 Phase 2)</span>
              <span class="badge danger sm">Giám Sát Thời Gian Thực</span>
            </div>
            <div style="font-size:12px;color:var(--color-neutral-300);margin-top:2px">
              Tự động cảnh báo khách lạnh, phản hồi trễ, than phiền lặp lại, cam kết quá hạn và hợp nhất định danh Zalo ↔ WhatsApp.
            </div>
          </div>
        </div>
        <div style="display:flex;align-items:center;gap:8px">
          <button class="btn sm danger" onclick="openEarlyWarningModal()"><i class="ph ph-warning"></i> Radar Cảnh Báo</button>
          <button class="btn sm primary" onclick="openIdentityResolutionModal()"><i class="ph ph-link"></i> Hợp Nhất Danh Tính</button>
          <button class="btn sm" onclick="openBrainSearchModal()"><i class="ph ph-brain"></i> Search Có Não</button>
        </div>
      </div>
    </div>

    <div class="kpi-grid">"""

if "early-warning-radar-banner" not in content:
    content = content.replace(target_anchor, banner_html, 1)
    print("✓ Added Early Warning Radar Banner to CommandCenterHub")

# 2. Add JavaScript Functions for SPEC-42 at the bottom
js_block = """
// =============================================================================
// SPEC-42: EARLY WARNING, IDENTITY RESOLUTION, LIVING PROFILES & BRAIN SEARCH
// =============================================================================

// 1. MODAL RADAR CẢNH BÁO SỚM (EARLY WARNING SYSTEM - E9)
async function openEarlyWarningModal() {
  showToast('Đang tải dữ liệu Radar Cảnh Báo Sớm...');
  try {
    const [alrRes, sumRes] = await Promise.all([
      fetch('/api/early_warning/alerts?status=ACTIVE'),
      fetch('/api/early_warning/summary')
    ]);
    const alrData = await alrRes.json();
    const sumData = await sumRes.json();

    const alerts = alrData.alerts || [];
    const summary = sumData || {};

    const modalHtml = `
      <div style="display:flex;flex-direction:column;gap:16px">
        <!-- Summary KPI Row -->
        <div style="display:grid;grid-template-columns:repeat(4, 1fr);gap:10px">
          <div class="card card-pad" style="border-left:3px solid #ef4444;background:rgba(239,68,68,0.05)">
            <div style="font-size:11px;color:var(--color-neutral-400)">CẢNH BÁO KHẨN</div>
            <div style="font-size:22px;font-weight:800;color:#ef4444;margin:2px 0">${summary.critical || 0}</div>
            <div style="font-size:10px;color:var(--color-neutral-400)">Cần can thiệp ngay</div>
          </div>
          <div class="card card-pad" style="border-left:3px solid #f59e0b;background:rgba(245,158,11,0.05)">
            <div style="font-size:11px;color:var(--color-neutral-400)">KHÁCH NGUỘI LẠNH</div>
            <div style="font-size:22px;font-weight:800;color:#f59e0b;margin:2px 0">${summary.cold_leads_count || 0}</div>
            <div style="font-size:10px;color:var(--color-neutral-400)">Im lặng trên 3 ngày</div>
          </div>
          <div class="card card-pad" style="border-left:3px solid #a855f7;background:rgba(168,85,247,0.05)">
            <div style="font-size:11px;color:var(--color-neutral-400)">CAM KẾT QUÁ HẠN</div>
            <div style="font-size:22px;font-weight:800;color:#a855f7;margin:2px 0">${summary.overdue_promises_count || 0}</div>
            <div style="font-size:10px;color:var(--color-neutral-400)">Chưa hoàn thành</div>
          </div>
          <div class="card card-pad" style="border-left:3px solid #38bdf8;background:rgba(56,189,248,0.05)">
            <div style="font-size:11px;color:var(--color-neutral-400)">TỔNG ĐANG MỞ</div>
            <div style="font-size:22px;font-weight:800;color:#38bdf8;margin:2px 0">${summary.total_active || 0}</div>
            <div style="font-size:10px;color:var(--color-neutral-400)">Đang theo dõi</div>
          </div>
        </div>

        <!-- Action Header -->
        <div style="display:flex;justify-content:space-between;align-items:center;margin-top:4px">
          <div style="font-size:13px;font-weight:700;color:var(--color-text)">Danh Sách Cảnh Báo Cần Xử Lý (${alerts.length})</div>
          <button class="btn sm" onclick="triggerAlertScan()"><i class="ph ph-arrows-clockwise"></i> Quét Radar Lại</button>
        </div>

        <!-- Alert Cards List -->
        <div style="max-height:450px;overflow-y:auto;display:flex;flex-direction:column;gap:10px;padding-right:4px">
          ${alerts.length === 0 ? `
            <div style="text-align:center;padding:30px;color:var(--color-neutral-400)">
              <i class="ph ph-check-circle" style="font-size:32px;color:#10b981"></i>
              <div style="margin-top:8px;font-weight:600">Tuyệt vời! Không có cảnh báo nguy cơ nào đang hoạt động.</div>
            </div>
          ` : alerts.map(a => `
            <div style="background:var(--color-bg);border:1px solid ${a.severity==='CRITICAL'?'rgba(239,68,68,0.35)':(a.severity==='WARNING'?'rgba(245,158,11,0.35)':'var(--color-divider)')};border-radius:8px;padding:14px;display:flex;flex-direction:column;gap:8px">
              <div style="display:flex;justify-content:space-between;align-items:flex-start">
                <div style="display:flex;align-items:center;gap:8px">
                  <span class="badge ${a.severity==='CRITICAL'?'danger':(a.severity==='WARNING'?'warn':'neutral')}" style="font-size:10.5px">
                    ${a.severity==='CRITICAL'?'🚨 KHẨN CẤP':(a.severity==='WARNING'?'⚠️ CHÚ Ý':'ℹ️ THÔNG TIN')}
                  </span>
                  <span style="font-weight:700;font-size:13px;color:var(--color-text)">${escapeHtml(a.type)} · ${escapeHtml(a.target_name)}</span>
                </div>
                <span style="font-size:10.5px;color:var(--color-neutral-400)">Phụ trách: <b>${escapeHtml(a.assignee || 'Sếp')}</b></span>
              </div>

              <!-- Reason & Evidence -->
              <div style="font-size:12px;color:var(--color-text);line-height:1.5">
                ${escapeHtml(a.reason)}
              </div>
              ${a.evidence ? `
                <div style="font-size:11px;background:rgba(255,255,255,0.03);padding:6px 10px;border-radius:4px;border-left:2px solid var(--color-accent);color:var(--color-neutral-300)">
                  <b>Chứng cứ:</b> ${escapeHtml(a.evidence)}
                </div>
              ` : ''}

              <!-- Suggested Action & Buttons -->
              <div style="display:flex;justify-content:space-between;align-items:center;margin-top:4px;padding-top:8px;border-top:1px dashed var(--color-divider);flex-wrap:wrap;gap:8px">
                <div style="font-size:11.5px;color:#38bdf8">
                  <i class="ph ph-lightning"></i> <b>Đề xuất:</b> ${escapeHtml(a.suggested_action)}
                </div>
                <div style="display:flex;gap:6px">
                  <button class="btn sm" onclick="handleAlertAction('${a.id}', 'acknowledge')"><i class="ph ph-check"></i> Đã Xem</button>
                  <button class="btn sm primary" onclick="handleAlertAction('${a.id}', 'resolve')"><i class="ph ph-seal-check"></i> Xử Lý Xong</button>
                  <button class="btn sm" style="color:var(--color-neutral-400)" onclick="handleAlertAction('${a.id}', 'dismiss')"><i class="ph ph-x"></i> Bỏ Qua</button>
                </div>
              </div>
            </div>
          `).join('')}
        </div>
      </div>
    `;

    openModal('🚨 Radar Cảnh Báo Sớm (Early Warning Intelligence)', modalHtml, null, true);
  } catch (err) {
    showToast('Lỗi tải radar: ' + err.message);
  }
}

async function triggerAlertScan() {
  showToast('Đang kích hoạt quét radar...');
  try {
    const res = await fetch('/api/early_warning/action', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ action: 'scan' })
    });
    const data = await res.json();
    if (data.ok) {
      showToast(data.message || 'Quét radar thành công');
      openEarlyWarningModal();
    } else {
      showToast('Lỗi: ' + data.error);
    }
  } catch (e) {
    showToast('Lỗi kết nối: ' + e.message);
  }
}

async function handleAlertAction(alertId, actionType) {
  try {
    const res = await fetch('/api/early_warning/action', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ id: alertId, action: actionType })
    });
    const data = await res.json();
    if (data.ok) {
      showToast('Đã cập nhật trạng thái cảnh báo');
      openEarlyWarningModal();
    } else {
      showToast('Lỗi: ' + (data.error || 'Thao tác bị từ chối'));
    }
  } catch (e) {
    showToast('Lỗi kết nối: ' + e.message);
  }
}

// 2. MODAL HỢP NHẤT DANH TÍNH ĐA KÊNH (IDENTITY RESOLUTION - G2)
async function openIdentityResolutionModal() {
  showToast('Đang nạp gợi ý hợp nhất danh tính...');
  try {
    const [sugRes, histRes] = await Promise.all([
      fetch('/api/identity/suggestions'),
      fetch('/api/identity/history')
    ]);
    const sugData = await sugRes.json();
    const histData = await histRes.json();

    const suggestions = sugData.suggestions || [];
    const history = histData.history || [];

    const modalHtml = `
      <div style="display:flex;flex-direction:column;gap:16px">
        <div style="background:rgba(99,102,241,0.08);border:1px solid rgba(99,102,241,0.25);border-radius:8px;padding:12px 16px;font-size:12px;color:var(--color-text)">
          <div style="font-weight:700;color:var(--color-accent);margin-bottom:4px;display:flex;align-items:center;gap:6px">
            <i class="ph ph-link"></i> NGUYÊN TẮC HỢP NHẤT DANH TÍNH (MỤC G2 SPEC LOCKED)
          </div>
          Cùng một khách hàng hoặc đối tác xuất hiện trên Zalo, WhatsApp, Facebook và Telegram sẽ được bóc tách và gợi ý hợp nhất để tạo thành một <b>Hồ Sơ Sống Duy Nhất (Single Source of Truth)</b>.
        </div>

        <div style="font-weight:700;font-size:13px;color:var(--color-text);margin-top:4px">
          Gợi Ý Trùng Khớp Từ AI (${suggestions.length})
        </div>

        <div style="max-height:350px;overflow-y:auto;display:flex;flex-direction:column;gap:10px">
          ${suggestions.length === 0 ? `
            <div style="text-align:center;padding:25px;color:var(--color-neutral-400)">
              <i class="ph ph-check-circle" style="font-size:28px;color:#10b981"></i>
              <div style="margin-top:6px">Dữ liệu định danh đã được chuẩn hóa tối ưu. Không có liên hệ trùng lặp.</div>
            </div>
          ` : suggestions.map(s => `
            <div style="background:var(--color-bg);border:1px solid var(--color-divider);border-radius:8px;padding:14px;display:flex;flex-direction:column;gap:10px">
              <div style="display:flex;justify-content:space-between;align-items:center">
                <span class="badge warn" style="font-size:11px">Độ tin cậy khớp: ${s.confidence_pct}%</span>
                <span style="font-size:11.5px;color:var(--color-neutral-300)">${escapeHtml(s.match_reason)}</span>
              </div>
              <div style="display:grid;grid-template-columns:1fr auto 1fr;gap:12px;align-items:center">
                <div style="background:rgba(255,255,255,0.02);padding:10px;border-radius:6px;border:1px solid var(--color-divider)">
                  <div style="font-weight:700;font-size:13px">${escapeHtml(s.primary.full_name)}</div>
                  <div style="font-size:11px;color:var(--color-neutral-400)">${escapeHtml(s.primary.company || 'Doanh nghiệp')} · ${escapeHtml(s.primary.phone || 'N/A')}</div>
                  <div style="font-size:10.5px;color:#0284c7;margin-top:2px">ID: ${s.primary.id} (Gốc chính)</div>
                </div>
                <div style="font-size:20px;color:var(--color-accent)">
                  <i class="ph ph-arrow-left"></i>
                </div>
                <div style="background:rgba(255,255,255,0.02);padding:10px;border-radius:6px;border:1px solid var(--color-divider)">
                  <div style="font-weight:700;font-size:13px">${escapeHtml(s.secondary.full_name)}</div>
                  <div style="font-size:11px;color:var(--color-neutral-400)">${escapeHtml(s.secondary.company || 'Doanh nghiệp')} · ${escapeHtml(s.secondary.phone || 'N/A')}</div>
                  <div style="font-size:10.5px;color:#f59e0b;margin-top:2px">ID: ${s.secondary.id} (Sẽ gộp vào)</div>
                </div>
              </div>
              <div style="display:flex;justify-content:flex-end">
                <button class="btn sm primary" onclick="handleIdentityMerge('${s.primary.id}', '${s.secondary.id}')">
                  <i class="ph ph-git-merge"></i> Tiến Hành Hợp Nhất (Merge)
                </button>
              </div>
            </div>
          `).join('')}
        </div>

        ${history.length > 0 ? `
          <div style="font-weight:700;font-size:13px;color:var(--color-text);margin-top:8px">Lịch Sử Gộp / Tách Định Danh</div>
          <div style="max-height:180px;overflow-y:auto;display:flex;flex-direction:column;gap:6px">
            ${history.map(h => `
              <div style="font-size:11.5px;padding:8px 12px;background:var(--color-bg);border-radius:6px;border:1px solid var(--color-divider);display:flex;justify-content:space-between;align-items:center">
                <div>
                  <b>${escapeHtml(h.secondary_name)}</b> → <b>${escapeHtml(h.primary_name)}</b>
                  <span style="color:var(--color-neutral-400);margin-left:6px">(${h.status === 'MERGED' ? 'Đã gộp' : 'Đã tách rollback'})</span>
                </div>
                ${h.status === 'MERGED' ? `
                  <button class="btn sm" onclick="handleIdentitySplit('${h.id}')"><i class="ph ph-arrow-u-up-left"></i> Tách Lại</button>
                ` : '<span class="badge neutral sm">Đã hoàn tác</span>'}
              </div>
            `).join('')}
          </div>
        ` : ''}
      </div>
    `;

    openModal('🔗 Identity Resolution — Hợp Nhất Danh Tính Đa Kênh', modalHtml, null, true);
  } catch (err) {
    showToast('Lỗi tải gợi ý: ' + err.message);
  }
}

async function handleIdentityMerge(primaryId, secondaryId) {
  if (!confirm('Sếp có chắc chắn muốn gộp 2 định danh này không? Tất cả tin nhắn, sự kiện và deal sẽ được hợp nhất vào hồ sơ chính.')) return;
  try {
    const res = await fetch('/api/identity/merge', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ primary_id: primaryId, secondary_id: secondaryId })
    });
    const data = await res.json();
    if (data.ok) {
      showToast(data.message || 'Đã hợp nhất danh tính thành công!');
      openIdentityResolutionModal();
    } else {
      showToast('Lỗi: ' + data.error);
    }
  } catch (e) {
    showToast('Lỗi kết nối: ' + e.message);
  }
}

async function handleIdentitySplit(historyId) {
  if (!confirm('Sếp có muốn hoàn tác và phục hồi lại định danh ban đầu từ bản sao lưu không?')) return;
  try {
    const res = await fetch('/api/identity/split', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ history_id: historyId })
    });
    const data = await res.json();
    if (data.ok) {
      showToast(data.message || 'Đã tách định danh thành công!');
      openIdentityResolutionModal();
    } else {
      showToast('Lỗi: ' + data.error);
    }
  } catch (e) {
    showToast('Lỗi kết nối: ' + e.message);
  }
}

// 3. TÌM KIẾM CÓ NÃO (BRAIN SEARCH - F2 8)
function openBrainSearchModal() {
  const modalHtml = `
    <div style="display:flex;flex-direction:column;gap:14px">
      <div style="position:relative">
        <input id="brain-search-input" type="text" class="input" placeholder="Nhập từ khóa tìm kiếm có não (VD: báo giá, khiếu nại, đối thủ, VinaSupply, Tuấn Minh...)" 
               style="width:100%;padding:12px 14px;font-size:13.5px;background:var(--color-bg);border:1px solid var(--color-accent);border-radius:8px"
               oninput="handleBrainSearchDebounce(this.value)" autofocus>
      </div>
      <div style="font-size:11px;color:var(--color-neutral-400)">
        ⚡ <b>Search Có Não:</b> Tự động nhận diện ý định (Intent), bóc tách thực thể và giải thích lý do vì sao dữ liệu khớp với bối cảnh của Sếp.
      </div>
      <div id="brain-search-results-container" style="max-height:420px;overflow-y:auto;display:flex;flex-direction:column;gap:8px;padding-right:4px">
        <div style="text-align:center;padding:30px;color:var(--color-neutral-400)">
          Gõ từ khóa để bắt đầu truy vấn tri thức hội thoại...
        </div>
      </div>
    </div>
  `;
  openModal('🔍 Search Có Não — Tri Thức Hội Thoại Cấp Cao', modalHtml, null, true);
}

let brainSearchTimer = null;
function handleBrainSearchDebounce(query) {
  clearTimeout(brainSearchTimer);
  brainSearchTimer = setTimeout(() => executeBrainSearch(query), 250);
}

async function executeBrainSearch(query) {
  const container = document.getElementById('brain-search-results-container');
  if (!container) return;
  if (!query || !query.trim()) {
    container.innerHTML = '<div style="text-align:center;padding:30px;color:var(--color-neutral-400)">Gõ từ khóa để bắt đầu truy vấn tri thức...</div>';
    return;
  }
  container.innerHTML = '<div style="text-align:center;padding:20px;color:var(--color-neutral-400)"><i class="ph ph-spinner ph-spin"></i> Đang suy luận tìm kiếm...</div>';

  try {
    const res = await fetch(`/api/brain_search?q=${encodeURIComponent(query.trim())}`);
    const data = await res.json();
    const results = data.results || [];

    if (results.length === 0) {
      container.innerHTML = `<div style="text-align:center;padding:30px;color:var(--color-neutral-400)">Không tìm thấy kết quả nào khớp với '<b>${escapeHtml(query)}</b>'</div>`;
      return;
    }

    container.innerHTML = results.map(r => `
      <div style="background:var(--color-bg);border:1px solid var(--color-divider);border-radius:8px;padding:12px;display:flex;flex-direction:column;gap:4px;cursor:pointer;transition:border-color 0.2s"
           onmouseover="this.style.borderColor='var(--color-accent)'" onmouseout="this.style.borderColor='var(--color-divider)'"
           onclick="${r.category==='CONTACT'?`openLivingProfile360Modal('${r.target_id}')`:'showToast(\"Đã chọn \" + escapeHtml(r.title))'}">
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span style="font-weight:700;font-size:13px;color:var(--color-text)">${escapeHtml(r.title)}</span>
          <span class="badge ${r.category==='CONTACT'?'info':(r.category==='OPPORTUNITY'?'warn':(r.category==='ALERT'?'danger':'neutral'))}" style="font-size:10px">
            ${r.category}
          </span>
        </div>
        <div style="font-size:12px;color:var(--color-neutral-300);line-height:1.4">${escapeHtml(r.snippet)}</div>
        <div style="font-size:11px;color:#38bdf8;margin-top:2px">
          <i class="ph ph-sparkle"></i> <b>Lý do khớp:</b> ${escapeHtml(r.match_reason)}
        </div>
      </div>
    `).join('');
  } catch (e) {
    container.innerHTML = `<div style="color:var(--status-bad);padding:10px">Lỗi: ${e.message}</div>`;
  }
}

// 4. LƯU GHI CHÚ TAY CHO LIVING PROFILE (SPEC-42)
async function saveLivingProfileNotes(contactId) {
  const notes = document.getElementById('living-profile-notes-input')?.value || '';
  try {
    const res = await fetch('/api/living_profile/save_notes', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ id: contactId, notes: notes })
    });
    const data = await res.json();
    if (data.ok) {
      showToast('Đã lưu ghi chú tay của Sếp thành công!');
    } else {
      showToast('Lỗi lưu ghi chú: ' + data.error);
    }
  } catch (e) {
    showToast('Lỗi: ' + e.message);
  }
}

async function updateLivingProfileAutonomy(contactId) {
  const select = document.getElementById('living-profile-autonomy-select');
  if (!select) return;
  const lvl = parseInt(select.value, 10);
  try {
    const res = await fetch('/api/living_profile/update_autonomy', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ id: contactId, autonomy_level: lvl })
    });
    const data = await res.json();
    if (data.ok) {
      showToast(data.message || 'Đã cập nhật mức tự trị');
    } else {
      showToast('Lỗi: ' + data.error);
    }
  } catch (e) {
    showToast('Lỗi: ' + e.message);
  }
}
"""

if "function openEarlyWarningModal" not in content:
    # Append before the last </script> tag
    idx = content.rfind("</script>")
    if idx != -1:
        content = content[:idx] + "\n" + js_block + "\n" + content[idx:]
        print("✓ Appended SPEC-42 JavaScript handlers to dashboard.html")

with open(DASHBOARD_PATH, "w", encoding="utf-8") as f:
    f.write(content)

print("✓ Successfully patched dashboard.html with SPEC-42 UI!")
