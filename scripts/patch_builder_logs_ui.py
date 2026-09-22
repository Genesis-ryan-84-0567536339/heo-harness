# -*- coding: utf-8 -*-
import os
import json
import re

html_path = "/home/ryan/heo-harness/artifacts/reports/gen_harness_builder.html"
with open(html_path, "r", encoding="utf-8") as f:
    content = f.read()

new_log_modal_html = """
  <!-- New Agent Build Log Modal -->
  <div class="modal-overlay" id="newLogModal" onclick="closeNewLogModal(event)">
    <div class="drawer-card" style="max-width: 820px;" onclick="event.stopPropagation()">
      <div class="drawer-header">
        <div>
          <span class="ssot-badge" style="background: rgba(245, 158, 11, 0.2); color: #fbbf24; border-color: rgba(245, 158, 11, 0.4);">📜 AGENT BUILD & HANDOVER LEDGER</span>
          <h3 style="font-size: 18px; font-weight: 700; margin-top: 4px;">Ghi Nhật Ký Xây Dựng & Bàn Giao Ca Agent</h3>
        </div>
        <button class="icon-btn" onclick="closeNewLogModalDirect()">✕</button>
      </div>

      <div class="bootstrap-alert" style="margin-bottom: 14px; font-size: 12px; padding: 10px 14px;">
        <span style="font-size: 18px;">⚠️</span>
        <div><strong>Quy tắc Bootstrap SSOT:</strong> Ghi chép trung thực, súc tích (BLUF & MECE) để AI agent phiên kế tiếp lập tức nối tiếp dòng chảy công việc mà không làm lệch mục tiêu toàn cục (SSOT Goal).</div>
      </div>

      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
        <div class="form-group">
          <label class="form-label">Tên Agent / Phiên Thực Thi</label>
          <input type="text" id="newLogAgentName" class="form-input" value="Antigravity Executive Agent">
        </div>
        <div class="form-group">
          <label class="form-label">Chặng Milestone</label>
          <input type="text" id="newLogMilestone" class="form-input" placeholder="Ví dụ: MS-1, MS-2, MS-3 hoặc MS-General">
        </div>
      </div>

      <div class="form-group">
        <label class="form-label">Tiêu Đề Lượt Xây Dựng (Headline)</label>
        <input type="text" id="newLogTitle" class="form-input" placeholder="Ví dụ: Hoàn thiện Data Factory, Inbox of Meaning & Opportunity Kanban">
      </div>

      <div class="form-group">
        <label class="form-label">Tóm Tắt Khối Lượng Đã Thi Công (Summary - BLUF & MECE)</label>
        <textarea id="newLogSummary" class="form-textarea" rows="3" placeholder="Mô tả súc tích những gì đã xây dựng, cải tiến, giải quyết khoảng cách gap trong phiên này..."></textarea>
      </div>

      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
        <div class="form-group">
          <label class="form-label">Các SPEC Đã Xong (phân cách bằng dấu phẩy)</label>
          <input type="text" id="newLogSpecs" class="form-input" placeholder="SPEC-06, SPEC-07, SPEC-08...">
        </div>
        <div class="form-group">
          <label class="form-label">Trạng Thái Kiểm Thử Nghiệm Thu</label>
          <input type="text" id="newLogVerification" class="form-input" value="./doctor.sh PASS 100% (16/16 tests) + 22 unit tests PASS">
        </div>
      </div>

      <div class="form-group">
        <label class="form-label">Các File Mã Nguồn Đã Thay Đổi (cách nhau dấu phẩy hoặc xuống dòng)</label>
        <textarea id="newLogFiles" class="form-textarea" rows="2" placeholder="heo_harness/core/data_factory.py, tests/test_data_factory_milestones.py..."></textarea>
      </div>

      <div class="form-group">
        <label class="form-label" style="color: #a5b4fc; font-weight: 700;">🤖 Lời Dặn Bàn Giao Cho Agent Sau (Next Agent Instructions)</label>
        <textarea id="newLogInstructions" class="form-textarea" rows="3" placeholder="Chỉ dẫn cụ thể cho phiên tiếp theo: Làm gì tiếp theo, file nào cần chú ý, rủi ro tiềm ẩn..."></textarea>
      </div>

      <div style="display: flex; justify-content: flex-end; gap: 10px; margin-top: 16px; border-top: 1px solid var(--border); padding-top: 14px;">
        <button class="btn" onclick="closeNewLogModalDirect()">Hủy Bỏ</button>
        <button class="btn btn-primary" onclick="submitNewLog()">💾 Lưu Nhật Ký & Đồng Bộ SSOT</button>
      </div>
    </div>
  </div>
"""

js_logic = """
    // ==========================================
    // AGENT BUILD LOGS & HANDOVER MANAGEMENT
    // ==========================================
    let AGENT_LOGS = [];

    function switchMainView(view) {
      const tabMatrix = document.getElementById('tabBtnMatrix');
      const tabLogs = document.getElementById('tabBtnLogs');
      const viewMatrix = document.getElementById('viewMatrix');
      const viewLogs = document.getElementById('viewLogs');
      const logsActions = document.getElementById('logsActionsGroup');

      if (view === 'logs') {
        tabMatrix.classList.remove('active');
        tabLogs.classList.add('active');
        viewMatrix.style.display = 'none';
        viewLogs.style.display = 'block';
        logsActions.style.display = 'flex';
        loadAgentLogs();
      } else {
        tabLogs.classList.remove('active');
        tabMatrix.classList.add('active');
        viewLogs.style.display = 'none';
        viewMatrix.style.display = 'block';
        logsActions.style.display = 'none';
      }
    }

    async function loadAgentLogs() {
      try {
        const res = await fetch('/api/builder/logs');
        if (res.ok) {
          const j = await res.json();
          if (j.ok && Array.isArray(j.logs)) {
            AGENT_LOGS = j.logs;
            renderAgentLogs();
            return;
          }
        }
      } catch (e) {
        console.warn('Lỗi kết nối /api/builder/logs:', e);
      }

      // Fallback nếu mở qua file://
      if (!AGENT_LOGS || AGENT_LOGS.length === 0) {
        try {
          const resLocal = await fetch('../../data/agent_build_logs.json');
          if (resLocal.ok) {
            AGENT_LOGS = await resLocal.json();
          }
        } catch(e) {}
      }
      renderAgentLogs();
    }

    function renderAgentLogs() {
      const badge = document.getElementById('countLogsBadge');
      if (badge) badge.innerText = AGENT_LOGS.length;

      const container = document.getElementById('agentLogsList');
      if (!container) return;

      if (!AGENT_LOGS || AGENT_LOGS.length === 0) {
        container.innerHTML = `
          <div style="text-align: center; padding: 40px; color: var(--text-dim); background: var(--bg-surface); border-radius: 8px; border: 1px dashed var(--border);">
            Chưa có lượt nhật ký xây dựng nào được ghi nhận. Bấm <strong>+ Thêm Nhật Ký Mới</strong> để ghi nhận ca làm việc đầu tiên.
          </div>
        `;
        return;
      }

      // Render descending (mới nhất lên trên)
      const sortedLogs = [...AGENT_LOGS].reverse();
      let html = '';

      sortedLogs.forEach(log => {
        const specs = Array.isArray(log.specs_completed) ? log.specs_completed : [];
        const files = Array.isArray(log.files_modified) ? log.files_modified : [];

        const specsHtml = specs.map(s => `
          <span style="font-size: 11px; font-family: 'JetBrains Mono', monospace; font-weight: 600; background: rgba(99, 102, 241, 0.15); color: #a5b4fc; border: 1px solid rgba(99, 102, 241, 0.3); padding: 2px 7px; border-radius: 4px;">
            ${escapeHtml(s)}
          </span>
        `).join('') || '<span style="font-size: 12px; color: var(--text-dim);">Chưa gắn SPEC</span>';

        const filesHtml = files.map(f => `
          <span style="font-size: 11px; font-family: 'JetBrains Mono', monospace; background: rgba(255, 255, 255, 0.05); color: #93c5fd; border: 1px solid rgba(255, 255, 255, 0.1); padding: 2px 6px; border-radius: 4px; white-space: nowrap;">
            ${escapeHtml(f)}
          </span>
        `).join('') || '<span style="font-size: 12px; color: var(--text-dim);">Không rõ files</span>';

        html += `
          <div class="log-card">
            <div class="log-header">
              <div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">
                <span class="ssot-badge" style="font-size: 13px; font-weight: 700; background: rgba(99, 102, 241, 0.2); border-color: rgba(99, 102, 241, 0.5); color: #c7d2fe;">${escapeHtml(log.id)}</span>
                <span style="font-size: 12px; color: var(--text-dim);"><i class="ph ph-clock"></i> ${escapeHtml(log.timestamp)}</span>
                <span class="priority-tag prio-p0" style="background: rgba(16, 185, 129, 0.15); color: #34d399; border-color: rgba(16, 185, 129, 0.3);">${escapeHtml(log.milestone)}</span>
                <span style="font-size: 12px; color: #a5b4fc; background: rgba(99, 102, 241, 0.1); padding: 2px 8px; border-radius: 4px; border: 1px solid rgba(99, 102, 241, 0.2);"><i class="ph ph-robot"></i> ${escapeHtml(log.agent_name)}</span>
              </div>
              <div style="display: flex; gap: 8px; align-items: center;">
                <span style="font-size: 11.5px; font-weight: 600; color: #10b981; background: rgba(16, 185, 129, 0.15); padding: 3px 10px; border-radius: 999px; border: 1px solid rgba(16, 185, 129, 0.3);">
                  ✓ ${escapeHtml(log.verification_status || 'PASS')}
                </span>
                <button class="btn" style="padding: 4px 10px; font-size: 11.5px;" onclick="copySingleHandover('${escapeHtml(log.id)}')">📋 Copy Ca Bàn Giao</button>
              </div>
            </div>

            <div style="font-size: 15.5px; font-weight: 700; color: #f3f4f6; margin-top: 2px;">
              ${escapeHtml(log.title)}
            </div>

            <div style="font-size: 13px; color: #d1d5db; line-height: 1.6; background: rgba(0, 0, 0, 0.25); padding: 10px 14px; border-radius: 6px; border: 1px solid rgba(255, 255, 255, 0.05);">
              ${escapeHtml(log.summary)}
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 14px;">
              <div>
                <div style="font-size: 11px; font-weight: 700; text-transform: uppercase; color: #9ca3af; margin-bottom: 6px;">🎯 Các SPEC Đã Xong (${specs.length})</div>
                <div style="display: flex; flex-wrap: wrap; gap: 5px;">
                  ${specsHtml}
                </div>
              </div>
              <div>
                <div style="font-size: 11px; font-weight: 700; text-transform: uppercase; color: #9ca3af; margin-bottom: 6px;">📁 Files Đã Thay Đổi (${files.length})</div>
                <div style="display: flex; flex-wrap: wrap; gap: 5px; max-height: 80px; overflow-y: auto;">
                  ${filesHtml}
                </div>
              </div>
            </div>

            <div class="handover-box">
              <div style="font-size: 12px; font-weight: 700; color: #a5b4fc; display: flex; align-items: center; gap: 6px; margin-bottom: 6px;">
                <span>🤖 HƯỚNG DẪN BÀN GIAO CHO AGENT CA SAU (HANDOVER DIRECTIVES):</span>
              </div>
              <div style="font-size: 12.5px; color: #e0e7ff; line-height: 1.5; font-family: 'Inter', sans-serif; white-space: pre-wrap;">
${escapeHtml(log.next_agent_instructions || 'Tiếp tục thực thi theo kế hoạch')}
              </div>
            </div>
          </div>
        `;
      });

      container.innerHTML = html;
    }

    function openNewLogModal() {
      document.getElementById('newLogMilestone').value = 'MS-2, MS-3, MS-4';
      document.getElementById('newLogTitle').value = '';
      document.getElementById('newLogSummary').value = '';
      document.getElementById('newLogSpecs').value = '';
      document.getElementById('newLogFiles').value = '';
      document.getElementById('newLogInstructions').value = '';
      document.getElementById('newLogModal').classList.add('open');
    }

    function closeNewLogModalDirect() {
      document.getElementById('newLogModal').classList.remove('open');
    }

    function closeNewLogModal(e) {
      document.getElementById('newLogModal').classList.remove('open');
    }

    async function submitNewLog() {
      const agentName = document.getElementById('newLogAgentName').value.trim() || 'Antigravity Executive Agent';
      const milestone = document.getElementById('newLogMilestone').value.trim() || 'MS-General';
      const title = document.getElementById('newLogTitle').value.trim();
      const summary = document.getElementById('newLogSummary').value.trim();
      const specsRaw = document.getElementById('newLogSpecs').value.trim();
      const filesRaw = document.getElementById('newLogFiles').value.trim();
      const verification = document.getElementById('newLogVerification').value.trim() || './doctor.sh PASS 100%';
      const instructions = document.getElementById('newLogInstructions').value.trim();

      if (!title || !summary) {
        alert('Vui lòng điền Tiêu Đề và Tóm Tắt nội dung thi công!');
        return;
      }

      const specs = specsRaw ? specsRaw.split(/[,\\n]+/).map(s => s.trim()).filter(Boolean) : [];
      const files = filesRaw ? filesRaw.split(/[,\\n]+/).map(f => f.trim()).filter(Boolean) : [];

      const payload = {
        agent_name: agentName,
        milestone: milestone,
        title: title,
        summary: summary,
        specs_completed: specs,
        files_modified: files,
        verification_status: verification,
        next_agent_instructions: instructions
      };

      try {
        const res = await fetch('/api/builder/logs', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const j = await res.json();
        if (j.ok) {
          showToast('✅ Đã ghi nhận nhật ký thi công và đồng bộ SSOT!');
          closeNewLogModalDirect();
          await loadAgentLogs();
          return;
        } else {
          alert('Lỗi khi lưu: ' + (j.error || 'Không xác định'));
        }
      } catch (e) {
        alert('Không thể kết nối máy chủ để lưu nhật ký: ' + e);
      }
    }

    function copySingleHandover(id) {
      const log = AGENT_LOGS.find(l => l.id === id);
      if (!log) return;
      const specs = (log.specs_completed || []).join(', ');
      const files = (log.files_modified || []).join(', ');
      const text = `[BÀN GIAO CA LÀM VIỆC TỪ AGENT TRƯỚC - GEN-HARNESS BUILDER]
Phiên build: ${log.id} (${log.timestamp}) bởi ${log.agent_name}
Milestone: ${log.milestone} | Nghiệm thu: ${log.verification_status}
Tiêu đề: ${log.title}

TÓM TẮT ĐÃ LÀM (BLUF & MECE):
${log.summary}

CÁC SPEC ĐÃ XONG: ${specs}
CÁC FILE ĐÃ SỬA: ${files}

HƯỚNG DẪN TIẾP NỐI CHO AGENT CA NÀY (NEXT AGENT INSTRUCTIONS):
${log.next_agent_instructions}

MỤC TIÊU TOÀN CỤC & QUY TẮC BẮT BUỘC:
1. Tham chiếu SSOT Spec LOCKED: Gen-Harness-Product-Spec-LOCKED.md v2.2
2. Mọi thay đổi phải PASS 100% ./doctor.sh (16/16 SSOT tests) và bộ unit tests.
3. Everything is a Plugin, kế thừa BasePlugin, bọc CircuitBreaker, lưu trữ qua store SQLite.
4. QUY TẮC BOOTSTRAP: Trước khi in hoàn tất kết thúc ca lên CLI, BẮT BUỘC phải ghi nhật ký mới qua giao diện Builder hoặc POST /api/builder/logs.`;

      navigator.clipboard.writeText(text);
      showToast('📋 Đã copy Handover Prompt cho Agent ca tiếp theo!');
    }

    function copyHandoverPrompt() {
      if (!AGENT_LOGS || AGENT_LOGS.length === 0) {
        alert('Chưa có nhật ký nào để copy!');
        return;
      }
      // Lấy phiên gần nhất (phần tử cuối của mảng gốc)
      const latest = AGENT_LOGS[AGENT_LOGS.length - 1];
      copySingleHandover(latest.id);
    }
"""

# Insert modal
if '<div class="modal-overlay" id="newLogModal"' not in content:
    content = content.replace('<!-- Spec Viewer Modal -->', new_log_modal_html + '\n  <!-- Spec Viewer Modal -->')

# Insert JS logic
if 'function switchMainView' not in content:
    content = content.replace('// Initial boot\n    loadFreshPlan();', js_logic + '\n    // Initial boot\n    loadFreshPlan();\n    loadAgentLogs();')

# Write back
with open(html_path, "w", encoding="utf-8") as f:
    f.write(content)

# Workplace sync
wp_path = "/home/ryan/Documents/Ryan-Workplace/Heo-Harness/artifacts/reports/gen_harness_builder.html"
if os.path.exists(os.path.dirname(wp_path)):
    with open(wp_path, "w", encoding="utf-8") as f:
        f.write(content)

print("Patch applied successfully to both HTML files!")
