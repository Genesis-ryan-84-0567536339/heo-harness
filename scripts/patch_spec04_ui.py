#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script: patch_spec04_ui.py
Tích hợp giao diện điều khiển Radar Thu Nạp Đa Kênh (SPEC-04) vào dashboard.html.
Tác giả & Chủ nhân duy nhất: Anh Cơ La (genesis.corp.os@gmail.com)
"""

import sys

DASHBOARD_FILE = "heo_harness/plugins/ui_dashboard/dashboard.html"

with open(DASHBOARD_FILE, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Thêm tab subnav vào renderRelationshipRadarHub
target_subnav = """        <button class="btn ${curSub === 'profiles' ? 'primary' : 'subtle'} sm" onclick="switchSubtab('relationship_radar', 'profiles')">
          <i class="ph ph-user-list"></i> 👤 Hồ Sơ Sống 360 (${contacts.length})
        </button>"""

replacement_subnav = """        <button class="btn ${curSub === 'profiles' ? 'primary' : 'subtle'} sm" onclick="switchSubtab('relationship_radar', 'profiles')">
          <i class="ph ph-user-list"></i> 👤 Hồ Sơ Sống 360 (${contacts.length})
        </button>
        <button class="btn ${curSub === 'multi_channel' ? 'primary' : 'subtle'} sm" onclick="switchSubtab('relationship_radar', 'multi_channel')">
          <i class="ph ph-broadcast"></i> 📡 Radar Thu Nạp Đa Kênh (SPEC-04)
        </button>"""

if target_subnav in content and "📡 Radar Thu Nạp Đa Kênh" not in content:
    content = content.replace(target_subnav, replacement_subnav, 1)
    print("✓ Added multi_channel subnav button")
else:
    print("! Subnav already patched or target not found")

# 2. Thêm view render
target_view = "${curSub === 'profiles' ? renderLivingProfilesTableView(contacts) : ''}"
replacement_view = "${curSub === 'profiles' ? renderLivingProfilesTableView(contacts) : ''}\n    ${curSub === 'multi_channel' ? renderMultiChannelRadarView() : ''}"

if target_view in content and "renderMultiChannelRadarView()" not in content:
    content = content.replace(target_view, replacement_view, 1)
    print("✓ Added renderMultiChannelRadarView container hook")
else:
    print("! View hook already patched or target not found")

# 3. Thêm code Javascript cho Multi-Channel Radar trước thẻ </script> cuối cùng
js_code = """
// =============================================================================
// SPEC-04: MULTI-CHANNEL RADAR & UNIVERSAL INGESTION HUB
// =============================================================================

let radarCachedChannels = [];
let radarCachedLogs = [];

function renderMultiChannelRadarView() {
  setTimeout(initMultiChannelRadarView, 50);
  return `
    <div id="radar-multichannel-container" style="display:flex;flex-direction:column;gap:18px;margin-top:16px">
      <div style="padding:40px;text-align:center;color:var(--color-neutral-400)">
        <i class="ph ph-spinner ph-spin" style="font-size:32px;color:#f43f5e;margin-bottom:12px;display:block"></i>
        Đang khởi tạo Radar thu nạp đa kênh (Zalo, WhatsApp, Telegram, Facebook, Generic Webhook)...
      </div>
    </div>
  `;
}

async function initMultiChannelRadarView() {
  const container = document.getElementById('radar-multichannel-container');
  if (!container) return;

  try {
    const [chRes, logsRes] = await Promise.all([
      fetch('/api/radar/channels').then(r => r.json()).catch(() => ({ channels: [] })),
      fetch('/api/radar/logs?limit=30').then(r => r.json()).catch(() => ({ logs: [] }))
    ]);

    const channels = chRes.channels || [];
    const logs = logsRes.logs || [];
    radarCachedChannels = channels;
    radarCachedLogs = logs;

    const totalInbound = channels.reduce((sum, c) => sum + (c.total_inbound || 0), 0);
    const activeChannels = channels.filter(c => c.status === 'ONLINE' || c.status === 'CONNECTED').length;

    const channelMeta = {
      zalo: { icon: '💬', color: '#0068ff', bg: 'rgba(0,104,255,0.1)' },
      whatsapp: { icon: '📱', color: '#25d366', bg: 'rgba(37,211,102,0.1)' },
      telegram: { icon: '✈️', color: '#229ed9', bg: 'rgba(34,158,217,0.1)' },
      facebook: { icon: '🌐', color: '#1877f2', bg: 'rgba(24,119,242,0.1)' },
      generic_webhook: { icon: '⚡', color: '#a855f7', bg: 'rgba(168,85,247,0.1)' }
    };

    container.innerHTML = `
      <!-- KPI Top Summary -->
      <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(200px, 1fr));gap:14px">
        <div class="card" style="padding:14px;background:rgba(244,63,94,0.08);border:1px solid rgba(244,63,94,0.2)">
          <div style="font-size:11px;color:#fda4af;text-transform:uppercase;font-weight:700">Kênh Trực Tuyến</div>
          <div style="font-size:24px;font-weight:800;color:#f43f5e;margin-top:4px">${activeChannels} / ${channels.length} Kênh</div>
          <div style="font-size:11px;color:#94a3b8;margin-top:2px">Sẵn sàng nhận tín hiệu 24/7</div>
        </div>
        <div class="card" style="padding:14px;background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.2)">
          <div style="font-size:11px;color:#6ee7b7;text-transform:uppercase;font-weight:700">Tổng Tin Đã Thu Nạp</div>
          <div style="font-size:24px;font-weight:800;color:#10b981;margin-top:4px">${totalInbound} Tin</div>
          <div style="font-size:11px;color:#94a3b8;margin-top:2px">Đồng bộ Conversation Data Factory</div>
        </div>
        <div class="card" style="padding:14px;background:rgba(56,189,248,0.08);border:1px solid rgba(56,189,248,0.2)">
          <div style="font-size:11px;color:#7dd3fc;text-transform:uppercase;font-weight:700">Sự Kiện Radar 24h</div>
          <div style="font-size:24px;font-weight:800;color:#38bdf8;margin-top:4px">${logs.length} Tín hiệu</div>
          <div style="font-size:11px;color:#94a3b8;margin-top:2px">Phân loại Intent tự động</div>
        </div>
        <div class="card" style="padding:14px;background:rgba(168,85,247,0.08);border:1px solid rgba(168,85,247,0.2)">
          <div style="font-size:11px;color:#d8b4fe;text-transform:uppercase;font-weight:700">Mức Tự Trị Radar</div>
          <div style="font-size:24px;font-weight:800;color:#c084fc;margin-top:4px">Level 4-5</div>
          <div style="font-size:11px;color:#94a3b8;margin-top:2px">Chế độ Proactive Signal Catch</div>
        </div>
      </div>

      <!-- Danh Sách Kênh Radar Thu Nạp (Grid) -->
      <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(280px, 1fr));gap:14px">
        ${channels.map(c => {
          const m = channelMeta[c.channel] || { icon: '📡', color: '#cbd5e1', bg: 'rgba(255,255,255,0.05)' };
          const isLive = c.status === 'ONLINE' || c.status === 'CONNECTED';
          const badgeClass = isLive ? 'badge success sm' : 'badge warning sm';
          return `
            <div class="card" style="padding:16px;background:rgba(15,23,42,0.9);border:1px solid rgba(255,255,255,0.1);border-radius:10px;display:flex;flex-direction:column;justify-content:space-between">
              <div>
                <div style="display:flex;justify-content:space-between;align-items:flex-start">
                  <div style="display:flex;align-items:center;gap:10px">
                    <div style="width:36px;height:36px;border-radius:8px;background:${m.bg};color:${m.color};display:flex;align-items:center;justify-content:center;font-size:18px">
                      ${m.icon}
                    </div>
                    <div>
                      <div style="font-weight:700;font-size:13.5px;color:#f8fafc">${escapeHtml(c.name)}</div>
                      <div style="font-size:11px;color:#94a3b8;font-family:var(--mono)">${c.channel}</div>
                    </div>
                  </div>
                  <span class="${badgeClass}">${c.status}</span>
                </div>

                <div style="margin-top:14px;display:flex;flex-direction:column;gap:6px;font-size:11.5px;color:#cbd5e1">
                  <div style="display:flex;justify-content:space-between">
                    <span style="color:#94a3b8">Chế độ lắng nghe:</span>
                    <span style="font-weight:600;color:#38bdf8">${c.listen_mode}</span>
                  </div>
                  <div style="display:flex;justify-content:space-between">
                    <span style="color:#94a3b8">Tin đã thu nạp:</span>
                    <span style="font-weight:700;color:#10b981">${c.total_inbound || 0} tin</span>
                  </div>
                  <div style="display:flex;justify-content:space-between">
                    <span style="color:#94a3b8">Webhook Endpoint:</span>
                    <span style="font-family:var(--mono);font-size:10.5px;color:#e2e8f0;background:rgba(255,255,255,0.06);padding:1px 4px;border-radius:3px">${c.webhook_path}</span>
                  </div>
                </div>
              </div>

              <div style="display:flex;gap:8px;margin-top:14px;border-top:1px solid rgba(255,255,255,0.06);padding-top:10px">
                <button class="btn sm" onclick="openChannelConfigModal('${c.channel}')" style="flex:1;font-size:11px">
                  <i class="ph ph-gear"></i> Cấu Hình
                </button>
                <button class="btn sm" onclick="copyWebhookUrl('${c.webhook_path}')" style="font-size:11px" title="Sao chép URL Webhook">
                  <i class="ph ph-copy"></i> URL
                </button>
              </div>
            </div>
          `;
        }).join('')}
      </div>

      <!-- Bàn Bắn Tín Hiệu Thử Nghiệm Qua Radar (Simulation Sandbox) -->
      <div class="card" style="padding:16px;background:rgba(15,23,42,0.9);border:1px solid rgba(255,255,255,0.1);border-radius:10px">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
          <div>
            <span style="font-weight:700;font-size:13.5px;color:#f8fafc"><i class="ph ph-paper-plane-tilt" style="color:#38bdf8;margin-right:6px"></i> Bắn Tín Hiệu Thử Nghiệm Qua Radar (Radar Sandbox Simulator)</span>
            <span style="font-size:11.5px;color:#94a3b8;margin-left:8px">Kiểm thử bóc tách Intent & tạo Atomic Event tức thì</span>
          </div>
        </div>

        <div style="display:grid;grid-template-columns:1fr 1.2fr 2fr auto;gap:10px;align-items:center">
          <select id="sim-radar-channel" style="background:var(--color-surface);color:var(--color-text);font-size:12px;border:1px solid var(--color-divider);padding:7px 10px;border-radius:6px">
            <option value="telegram">✈️ Telegram Bot API</option>
            <option value="facebook">🌐 Facebook Messenger</option>
            <option value="discord">🎮 Discord Webhook</option>
            <option value="linkedin">💼 LinkedIn InMail</option>
            <option value="generic_webhook">⚡ Generic API Webhook</option>
          </select>
          <input type="text" id="sim-radar-sender" placeholder="Tên đối tác / người gửi" value="Anh Tuấn (Công nghệ Số)" style="background:var(--color-surface);color:var(--color-text);font-size:12px;border:1px solid var(--color-divider);padding:7px 10px;border-radius:6px">
          <input type="text" id="sim-radar-text" placeholder="Nội dung tin nhắn thử nghiệm..." value="Tôi đang cần giải pháp AI Executive cho 30 nhân sự, báo giá giúp tôi" style="background:var(--color-surface);color:var(--color-text);font-size:12px;border:1px solid var(--color-divider);padding:7px 10px;border-radius:6px">
          <button class="btn sm primary" onclick="sendSimulatedRadarPing()" style="font-size:12px;padding:7px 14px">
            <i class="ph ph-broadcast"></i> Bắn Tín Hiệu
          </button>
        </div>
      </div>

      <!-- Bảng Nhật Ký Tín Hiệu Radar Thu Nạp (Live Activity Stream) -->
      <div class="card" style="padding:0;overflow:hidden;background:rgba(15,23,42,0.95);border:1px solid rgba(255,255,255,0.12);border-radius:10px">
        <div style="padding:14px 18px;border-bottom:1px solid rgba(255,255,255,0.1);display:flex;justify-content:space-between;align-items:center;background:rgba(255,255,255,0.02)">
          <div>
            <span style="font-weight:700;font-size:13.5px;color:#f8fafc"><i class="ph ph-clock-counter-clockwise" style="color:#f43f5e;margin-right:6px"></i> Nhật Ký Tín Hiệu Thu Nạp Thời Gian Thực (Live Ingestion Stream)</span>
            <span style="font-size:11.5px;color:#94a3b8;margin-left:8px">(SPEC-04 Radar Pipeline)</span>
          </div>
          <button class="btn sm" onclick="initMultiChannelRadarView()" style="font-size:11px">
            <i class="ph ph-arrows-clockwise"></i> Làm Mới
          </button>
        </div>

        <div style="overflow-x:auto">
          <table style="width:100%;border-collapse:collapse;font-size:12px;text-align:left">
            <thead>
              <tr style="background:rgba(0,0,0,0.5);border-bottom:1px solid rgba(255,255,255,0.15);color:#94a3b8;text-transform:uppercase;font-size:10.5px;letter-spacing:0.5px">
                <th style="padding:12px 14px;width:120px">MÃ LOG</th>
                <th style="padding:12px 14px;width:110px">KÊNH</th>
                <th style="padding:12px 14px;width:160px">NGƯỜI GỬI / NHÓM</th>
                <th style="padding:12px 14px">NỘI DUNG TÍN HIỆU</th>
                <th style="padding:12px 14px;text-align:center;width:130px">Ý ĐỊNH (INTENT)</th>
                <th style="padding:12px 14px;text-align:right;width:110px">THỜI GIAN</th>
              </tr>
            </thead>
            <tbody>
              ${logs.length === 0 ? `
                <tr><td colspan="6" style="padding:30px;text-align:center;color:#94a3b8">Chưa có tín hiệu nào thu nạp. Hãy bấm nút Bắn Tín Hiệu ở trên để thử nghiệm!</td></tr>
              ` : logs.map(l => {
                const intentBadge = l.intent && l.intent.includes('Hỏi Giá') 
                  ? `<span class="badge warning sm">${escapeHtml(l.intent)}</span>`
                  : l.intent && l.intent.includes('Phàn Nàn')
                  ? `<span class="badge danger sm">${escapeHtml(l.intent)}</span>`
                  : `<span class="badge primary sm">${escapeHtml(l.intent || 'Thông thường')}</span>`;
                const dateStr = l.created_at ? new Date(l.created_at * 1000).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit', second: '2-digit' }) : 'N/A';
                return `
                  <tr style="border-bottom:1px solid rgba(255,255,255,0.05)">
                    <td style="padding:10px 14px;font-family:var(--mono);color:#38bdf8;font-size:11px">${l.id}</td>
                    <td style="padding:10px 14px">
                      <span class="badge neutral sm" style="text-transform:uppercase">${escapeHtml(l.channel)}</span>
                    </td>
                    <td style="padding:10px 14px">
                      <div style="font-weight:600;color:#f8fafc">${escapeHtml(l.sender_name || 'Khách')}</div>
                      <div style="font-size:10.5px;color:#94a3b8">${escapeHtml(l.group_id || 'direct')}</div>
                    </td>
                    <td style="padding:10px 14px;color:#cbd5e1;max-width:320px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">
                      ${escapeHtml(l.message_text)}
                    </td>
                    <td style="padding:10px 14px;text-align:center">
                      ${intentBadge}
                    </td>
                    <td style="padding:10px 14px;text-align:right;color:#94a3b8;font-family:var(--mono);font-size:11px">
                      ${dateStr}
                    </td>
                  </tr>
                `;
              }).join('')}
            </tbody>
          </table>
        </div>
      </div>
    `;
  } catch (e) {
    container.innerHTML = `<div class="card" style="padding:20px;color:#ef4444">Lỗi tải dữ liệu Radar: ${e.message}</div>`;
  }
}

function copyWebhookUrl(path) {
  const fullUrl = window.location.origin + path;
  navigator.clipboard.writeText(fullUrl).then(() => {
    showToast('✓ Đã sao chép Webhook URL: ' + fullUrl);
  }).catch(() => {
    prompt('Sao chép Webhook URL:', fullUrl);
  });
}

function openChannelConfigModal(channelKey) {
  const channel = radarCachedChannels.find(c => c.channel === channelKey) || { channel: channelKey, name: channelKey, listen_mode: 'PROACTIVE' };
  openModal(`⚙️ Cấu Hình Kênh Radar: ${channel.name}`, `
    <div style="display:flex;flex-direction:column;gap:12px;font-size:12px">
      <div>
        <label style="color:#94a3b8;display:block;margin-bottom:4px">Tên hiển thị kênh:</label>
        <input type="text" id="modal-cfg-name" value="${escapeHtml(channel.name || '')}" style="width:100%;padding:8px;background:var(--color-surface);border:1px solid var(--color-divider);border-radius:6px;color:var(--color-text)">
      </div>
      <div>
        <label style="color:#94a3b8;display:block;margin-bottom:4px">Token xác thực / Bot API Token:</label>
        <input type="password" id="modal-cfg-token" value="${escapeHtml(channel.token || '')}" placeholder="Ví dụ: Bot Father token hoặc Webhook API Key" style="width:100%;padding:8px;background:var(--color-surface);border:1px solid var(--color-divider);border-radius:6px;color:var(--color-text)">
      </div>
      <div>
        <label style="color:#94a3b8;display:block;margin-bottom:4px">Verify Token (Dành cho Meta Webhook):</label>
        <input type="text" id="modal-cfg-verify" value="${escapeHtml(channel.verify_token || '')}" placeholder="Token xác thực webhook từ Facebook" style="width:100%;padding:8px;background:var(--color-surface);border:1px solid var(--color-divider);border-radius:6px;color:var(--color-text)">
      </div>
      <div>
        <label style="color:#94a3b8;display:block;margin-bottom:4px">Chế độ lắng nghe Radar:</label>
        <select id="modal-cfg-mode" style="width:100%;padding:8px;background:var(--color-surface);border:1px solid var(--color-divider);border-radius:6px;color:var(--color-text)">
          <option value="PROACTIVE" ${channel.listen_mode === 'PROACTIVE' ? 'selected' : ''}>Chủ động bắt tín hiệu (Proactive Signal Catch)</option>
          <option value="MENTION_ONLY" ${channel.listen_mode === 'MENTION_ONLY' ? 'selected' : ''}>Chỉ phản hồi khi @tag (Mention Only)</option>
          <option value="PASSIVE" ${channel.listen_mode === 'PASSIVE' ? 'selected' : ''}>Lắng nghe thụ động (Passive Monitor)</option>
        </select>
      </div>
      <div style="display:flex;justify-content:flex-end;gap:8px;margin-top:10px">
        <button class="btn sm" onclick="closeModal()">Huỷ</button>
        <button class="btn sm primary" onclick="saveChannelConfig('${channelKey}')">Lưu Cấu Hình</button>
      </div>
    </div>
  `);
}

async function saveChannelConfig(channelKey) {
  const name = document.getElementById('modal-cfg-name')?.value;
  const token = document.getElementById('modal-cfg-token')?.value;
  const verify_token = document.getElementById('modal-cfg-verify')?.value;
  const listen_mode = document.getElementById('modal-cfg-mode')?.value;

  try {
    const res = await fetch('/api/radar/channel/configure', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        channel: channelKey,
        updates: { name, token, verify_token, listen_mode }
      })
    }).then(r => r.json());

    if (res.ok) {
      showToast('✓ Đã cập nhật cấu hình kênh ' + channelKey);
      closeModal();
      initMultiChannelRadarView();
    } else {
      showToast('Lỗi: ' + (res.error || 'Không thể lưu'));
    }
  } catch (e) {
    showToast('Lỗi mạng: ' + e.message);
  }
}

async function sendSimulatedRadarPing() {
  const channel = document.getElementById('sim-radar-channel')?.value || 'telegram';
  const sender_name = document.getElementById('sim-radar-sender')?.value || 'Khách Thử Nghiệm';
  const text = document.getElementById('sim-radar-text')?.value || 'Xin chào';

  showToast('📡 Đang gửi tín hiệu thu nạp qua Radar ' + channel + '...');
  try {
    const res = await fetch('/api/radar/simulate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        channel: channel,
        sender_name: sender_name,
        text: text,
        group_name: 'Nhóm Doanh Nghiệp Thử Nghiệm'
      })
    }).then(r => r.json());

    if (res.ok) {
      showToast(`✓ Radar đã thu nạp thành công! Intent: [${res.intent || 'Chitchat'}] · Log: ${res.log_id}`);
      initMultiChannelRadarView();
    } else {
      showToast('Lỗi bắn tín hiệu: ' + (res.error || 'Thao tác thất bại'));
    }
  } catch (e) {
    showToast('Lỗi kết nối: ' + e.message);
  }
}
"""

# Chèn js_code trước </script>
last_script_tag = "</script>"
idx = content.rfind(last_script_tag)
if idx != -1 and "SPEC-04: MULTI-CHANNEL RADAR" not in content:
    content = content[:idx] + js_code + "\n" + content[idx:]
    print("✓ Appended SPEC-04 JavaScript functions before </script>")
else:
    print("! JavaScript code already present or script tag not found")

with open(DASHBOARD_FILE, "w", encoding="utf-8") as f:
    f.write(content)

print("Finished patching SPEC-04 UI in dashboard.html successfully!")
