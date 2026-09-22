# -*- coding: utf-8 -*-
import re

file_path = "/home/ryan/heo-harness/heo_harness/plugins/ui_dashboard/dashboard.html"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update brand in sidebar
content = content.replace(
    '<div class="brand-title">HEO OS · HARNESS</div>\n        <div class="brand-sub">Agent Runtime · v3.0</div>',
    '<div class="brand-title">GEN-HARNESS OS</div>\n        <div class="brand-sub">Genesis Harness (HEO OS) v2.2</div>'
)

# 2. Add Agent Identity Studio to subnav of assistant hub
old_subnav = """      <!-- Subnav Pills -->
      <div class="hub-subnav">
        <button class="hub-subnav-btn ${currentSub === 'chat' ? 'active' : ''}" onclick="switchSubtab('assistant', 'chat')">
          💬 Live Chat Cùng Bé Heo
        </button>
        <button class="hub-subnav-btn ${currentSub === 'heo_cfg' ? 'active' : ''}" onclick="switchSubtab('assistant', 'heo_cfg')">
          ⚙️ Cấu Hình Bé Heo & Sếp (Heo Settings)
        </button>"""

new_subnav = """      <!-- Subnav Pills -->
      <div class="hub-subnav">
        <button class="hub-subnav-btn ${currentSub === 'identities' ? 'active' : ''}" onclick="switchSubtab('assistant', 'identities')">
          🤖 Agent Identity Studio (Spec E13)
        </button>
        <button class="hub-subnav-btn ${currentSub === 'chat' ? 'active' : ''}" onclick="switchSubtab('assistant', 'chat')">
          💬 Live Console Chat
        </button>
        <button class="hub-subnav-btn ${currentSub === 'heo_cfg' ? 'active' : ''}" onclick="switchSubtab('assistant', 'heo_cfg')">
          ⚙️ Thái Độ & Tác Quyền Sếp
        </button>"""

if old_subnav in content:
    content = content.replace(old_subnav, new_subnav)

# 3. Update routing in renderAssistantHub
old_render_hub = "${currentSub === 'chat' ? renderAssistantChatView() : currentSub === 'heo_cfg' ? renderHeoSettingsView() : currentSub === 'quota' ? renderQuotaView() : renderRunnersHubView()}"
new_render_hub = "${currentSub === 'identities' ? renderAgentIdentityStudioView() : currentSub === 'chat' ? renderAssistantChatView() : currentSub === 'heo_cfg' ? renderHeoSettingsView() : currentSub === 'quota' ? renderQuotaView() : renderRunnersHubView()}"
if old_render_hub in content:
    content = content.replace(old_render_hub, new_render_hub)

# 4. Insert renderAgentIdentityStudioView and supporting functions before </script>
agent_studio_code = """
// =============================================================================
// AGENT IDENTITY STUDIO (Spec E13 & SPEC-02)
// =============================================================================
state.agent_identities = [];

async function loadAgentIdentities() {
  try {
    const res = await fetch('/api/agent_identities');
    if (res.ok) {
      const data = await res.json();
      if (data.ok && data.identities) {
        state.agent_identities = data.identities;
        state.active_agent_id = data.active_id;
        const badge = $('#badge-identities-count');
        if (badge) badge.textContent = `${data.identities.length} Agent`;
      }
    }
  } catch (e) {
    console.warn('loadAgentIdentities failed', e);
  }
}

function renderAgentIdentityStudioView() {
  const identities = state.agent_identities || [];
  const activeId = state.active_agent_id || (identities.find(x => x.active) || {}).id;

  const getRoleIcon = (id) => {
    if (id.includes('comm')) return '💼';
    if (id.includes('key')) return '🎯';
    if (id.includes('logistics') || id.includes('admin')) return '📦';
    if (id.includes('cskh')) return '🌸';
    if (id.includes('recruit')) return '👥';
    if (id.includes('secret')) return '🏛️';
    if (id.includes('heo')) return '🐷';
    return '🤖';
  };

  const getAutonomyBadge = (lvl) => {
    const map = {
      0: { text: 'Cấp 0: Chỉ ghi nhận', bg: 'var(--color-neutral-800)', col: '#9ca3af' },
      1: { text: 'Cấp 1: Tóm tắt', bg: 'rgba(59, 130, 246, 0.15)', col: '#60a5fa' },
      2: { text: 'Cấp 2: Chấm điểm', bg: 'rgba(147, 51, 234, 0.15)', col: '#c084fc' },
      3: { text: 'Cấp 3: Gợi ý hành động', bg: 'rgba(245, 158, 11, 0.15)', col: '#fbbf24' },
      4: { text: 'Cấp 4: Soạn sẵn chờ duyệt', bg: 'rgba(99, 102, 241, 0.2)', col: '#a5b4fc' },
      5: { text: 'Cấp 5: Tự làm việc an toàn', bg: 'rgba(16, 185, 129, 0.15)', col: '#34d399' },
      6: { text: 'Cấp 6: Tự thực thi whitelist', bg: 'rgba(6, 182, 212, 0.2)', col: '#22d3ee' }
    };
    const b = map[lvl] || map[4];
    return `<span style="font-size:11px;padding:2px 8px;border-radius:4px;background:${b.bg};color:${b.col};font-weight:600">${b.text}</span>`;
  };

  return `
    <div style="display:flex;flex-direction:column;gap:18px">
      <!-- Toolbar Header -->
      <div style="display:flex;justify-content:space-between;align-items:center;background:var(--color-surface);border:1px solid var(--color-divider);border-radius:var(--radius-md);padding:14px 18px;flex-wrap:wrap;gap:12px">
        <div>
          <div style="font-size:15px;font-weight:700;color:var(--color-text);display:flex;align-items:center;gap:8px">
            <span>🤖 Quản Trị Đa Danh Tính Agent Identity (Spec E13)</span>
            <span class="badge good" style="font-size:10px">0đ Token Antigravity</span>
          </div>
          <div style="font-size:12px;color:var(--color-neutral-400);margin-top:2px">
            Agent Bot không còn mặc định là Bé Heo. Sếp có thể tự tạo, nhân bản và kích hoạt từng vai trò chuyên biệt cho từng kênh.
          </div>
        </div>
        <div style="display:flex;gap:8px">
          <button class="btn sm primary" onclick="openNewAgentModal()"><i class="ph ph-plus"></i> Tạo Agent Mới</button>
          <button class="btn sm" onclick="loadAgentIdentities(); renderHub();"><i class="ph ph-arrows-clockwise"></i> Làm Mới</button>
        </div>
      </div>

      <!-- Identities Grid -->
      <div style="display:grid;grid-template-columns:repeat(auto-fill, minmax(350px, 1fr));gap:16px">
        ${identities.map(it => {
          const isActive = it.id === activeId || it.active;
          const icon = getRoleIcon(it.id);
          const forbiddenList = it.forbidden_actions || [];

          return `
            <div class="card card-pad" style="border-color:${isActive ? 'var(--color-accent)' : 'var(--color-divider)'};box-shadow:${isActive ? '0 0 20px -4px rgba(99, 102, 241, 0.3)' : 'none'};position:relative;display:flex;flex-direction:column;justify-content:space-between">
              <div>
                <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px">
                  <div style="display:flex;align-items:center;gap:10px">
                    <div style="width:38px;height:38px;border-radius:10px;background:var(--color-neutral-900);border:1px solid var(--color-divider);display:flex;align-items:center;justify-content:center;font-size:20px">
                      ${icon}
                    </div>
                    <div>
                      <div style="font-weight:700;font-size:14px;color:var(--color-text)">${escapeHtml(it.name)}</div>
                      <div style="font-size:11.5px;color:var(--color-neutral-400)">${escapeHtml(it.role)}</div>
                    </div>
                  </div>
                  <div>
                    ${isActive ? '<span class="badge good">🟢 ĐANG TRỰC BAN</span>' : '<span class="badge neutral">⚪ Dự Phòng</span>'}
                  </div>
                </div>

                <div style="font-size:12px;color:var(--color-text);background:var(--color-bg);border:1px solid var(--color-divider);border-radius:6px;padding:8px 12px;margin-bottom:12px;line-height:1.5">
                  ${escapeHtml(it.about || it.greeting || 'Chưa có mô tả chi tiết.')}
                </div>

                <div style="display:flex;flex-direction:column;gap:6px;font-size:11.5px;color:var(--color-neutral-400);margin-bottom:14px">
                  <div style="display:flex;justify-content:space-between;align-items:center">
                    <span>Mức tự trị (Autonomy):</span>
                    ${getAutonomyBadge(it.autonomy_level)}
                  </div>
                  <div style="display:flex;justify-content:space-between;align-items:center">
                    <span>Kênh hoạt động:</span>
                    <span style="color:var(--color-text);font-weight:500">${(it.channels || []).join(', ') || 'Tất cả'}</span>
                  </div>
                  <div style="display:flex;justify-content:space-between;align-items:center">
                    <span>Quy tắc lắng nghe:</span>
                    <span style="color:#a5b4fc;font-family:var(--mono)">${it.listen_mode === 'proactive_and_tag' ? 'Bắt tín hiệu & @Tag' : it.listen_mode === 'silent' ? 'Chỉ Quan Sát' : 'Chỉ Khi @Tag'}</span>
                  </div>
                  <div style="display:flex;justify-content:space-between;align-items:center">
                    <span>Giới hạn cấm kỵ:</span>
                    <span style="color:#f87171">${forbiddenList.length} điều cấm</span>
                  </div>
                </div>
              </div>

              <div style="display:flex;justify-content:space-between;align-items:center;border-top:1px solid var(--color-divider);padding-top:10px;margin-top:6px">
                ${isActive ? 
                  `<span style="font-size:12px;font-weight:600;color:var(--status-good)">✔ Đại diện mặc định</span>` : 
                  `<button class="btn sm primary" onclick="setActiveAgentIdentity('${it.id}')">⚡ Kích Hoạt Ngay</button>`
                }
                <div style="display:flex;gap:6px">
                  <button class="btn sm" onclick="openEditAgentModal('${it.id}')" title="Chỉnh sửa cấu hình"><i class="ph ph-pencil-simple"></i> Sửa</button>
                  <button class="btn sm" onclick="switchSubtab('assistant', 'chat')" title="Thử nghiệm chat"><i class="ph ph-chat-teardrop-text"></i> Chat</button>
                </div>
              </div>
            </div>
          `;
        }).join('')}
      </div>
    </div>
  `;
}

async function setActiveAgentIdentity(agentId) {
  try {
    const res = await fetch('/api/agent_identities/set_active', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id: agentId })
    });
    if (res.ok) {
      const j = await res.json();
      state.active_agent_id = agentId;
      showToast(j.message || 'Đã kích hoạt Agent Identity!');
      await loadAgentIdentities();
      renderHub();
    }
  } catch (e) {
    showToast('Lỗi khi kích hoạt Agent Identity!');
  }
}

function openEditAgentModal(agentId) {
  const it = (state.agent_identities || []).find(x => x.id === agentId);
  if (!it) return;

  const html = `
    <div class="modal-overlay open" id="agent-edit-modal" onclick="closeAgentEditModal(event)">
      <div class="modal-card" style="max-width:640px" onclick="event.stopPropagation()">
        <div class="modal-header">
          <div style="font-weight:700;font-size:16px;display:flex;align-items:center;gap:8px">
            <span>⚙️ Chỉnh Sửa Agent Identity: ${escapeHtml(it.name)}</span>
          </div>
          <button class="modal-close" onclick="closeAgentEditModalDirect()">✕</button>
        </div>

        <div class="form-group">
          <label class="form-label">Tên Ngắn (Gọi Tên Trong Chat)</label>
          <input type="text" class="form-input" id="edit-agent-name" value="${escapeHtml(it.name || '')}">
        </div>

        <div class="form-group">
          <label class="form-label">Tên Hiển Thị Đầy Đủ (Display Name)</label>
          <input type="text" class="form-input" id="edit-agent-display-name" value="${escapeHtml(it.display_name || it.name || '')}">
        </div>

        <div class="form-group">
          <label class="form-label">Vai Trò Chuyên Trách (Role / Responsibility)</label>
          <input type="text" class="form-input" id="edit-agent-role" value="${escapeHtml(it.role || '')}">
        </div>

        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
          <div class="form-group">
            <label class="form-label">Phong Cách Giọng Điệu (Tone)</label>
            <select class="form-select" id="edit-agent-tone">
              <option value="professional" ${it.tone === 'professional' ? 'selected' : ''}>💼 Chuyên nghiệp (BLUF & MECE)</option>
              <option value="serious" ${it.tone === 'serious' ? 'selected' : ''}>🏛️ Nghiêm túc hành chính</option>
              <option value="sweet" ${it.tone === 'sweet' ? 'selected' : ''}>🥰 Ngọt ngào & Chu đáo</option>
              <option value="default" ${it.tone === 'default' ? 'selected' : ''}>🌸 Thân thiện duyên dáng</option>
              <option value="grumpy" ${it.tone === 'grumpy' ? 'selected' : ''}>😤 Tsundere cọc cằn</option>
              <option value="troll" ${it.tone === 'troll' ? 'selected' : ''}>🤡 Hài hước meme</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Mức Tự Trị (0 đến 6)</label>
            <select class="form-select" id="edit-agent-autonomy">
              <option value="0" ${it.autonomy_level === 0 ? 'selected' : ''}>Cấp 0: Chỉ ghi nhận</option>
              <option value="1" ${it.autonomy_level === 1 ? 'selected' : ''}>Cấp 1: Tóm tắt</option>
              <option value="2" ${it.autonomy_level === 2 ? 'selected' : ''}>Cấp 2: Chấm điểm & Giải thích</option>
              <option value="3" ${it.autonomy_level === 3 ? 'selected' : ''}>Cấp 3: Gợi ý hành động</option>
              <option value="4" ${it.autonomy_level === 4 ? 'selected' : ''}>Cấp 4: Soạn sẵn chờ duyệt (Khuyên dùng)</option>
              <option value="5" ${it.autonomy_level === 5 ? 'selected' : ''}>Cấp 5: Tự làm việc thấp rủi ro</option>
              <option value="6" ${it.autonomy_level === 6 ? 'selected' : ''}>Cấp 6: Tự thực thi việc whitelist</option>
            </select>
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">Lời Chào Khởi Đầu (Greeting Signature)</label>
          <textarea class="form-textarea" id="edit-agent-greeting" style="min-height:60px">${escapeHtml(it.greeting || '')}</textarea>
        </div>

        <div class="form-group">
          <label class="form-label">Các Điều Nghiêm Cấm (Forbidden Actions - Mỗi dòng 1 điều)</label>
          <textarea class="form-textarea" id="edit-agent-forbidden" style="min-height:70px">${escapeHtml((it.forbidden_actions || []).join('\\n'))}</textarea>
        </div>

        <div style="display:flex;justify-content:flex-end;gap:8px;margin-top:14px">
          <button class="btn" onclick="closeAgentEditModalDirect()">Hủy</button>
          <button class="btn primary" onclick="saveAgentEdit('${it.id}')">Lưu Thay Đổi</button>
        </div>
      </div>
    </div>
  `;

  const existing = $('#agent-edit-modal');
  if (existing) existing.remove();
  document.body.insertAdjacentHTML('beforeend', html);
}

function closeAgentEditModal(e) {
  const m = $('#agent-edit-modal');
  if (m) m.remove();
}

function closeAgentEditModalDirect() {
  const m = $('#agent-edit-modal');
  if (m) m.remove();
}

async function saveAgentEdit(agentId) {
  const it = (state.agent_identities || []).find(x => x.id === agentId);
  if (!it) return;

  const forbiddenText = $('#edit-agent-forbidden').value.trim();
  const forbiddenArr = forbiddenText ? forbiddenText.split('\\n').map(s => s.trim()).filter(Boolean) : [];

  it.name = $('#edit-agent-name').value.trim();
  it.display_name = $('#edit-agent-display-name').value.trim();
  it.role = $('#edit-agent-role').value.trim();
  it.tone = $('#edit-agent-tone').value;
  it.autonomy_level = parseInt($('#edit-agent-autonomy').value, 10);
  it.greeting = $('#edit-agent-greeting').value.trim();
  it.forbidden_actions = forbiddenArr;

  try {
    const res = await fetch('/api/agent_identities/save', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(it)
    });
    if (res.ok) {
      showToast('Đã lưu Agent Identity thành công!');
      closeAgentEditModalDirect();
      await loadAgentIdentities();
      renderHub();
    }
  } catch (e) {
    showToast('Lỗi khi lưu Agent Identity!');
  }
}
"""

if "function renderAgentIdentityStudioView" not in content:
    content = content.replace("</script>", agent_studio_code + "\n</script>")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Patched dashboard.html for Multi-Agent Identity Studio successfully!")
