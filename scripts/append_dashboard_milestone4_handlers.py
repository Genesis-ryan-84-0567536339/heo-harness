# -*- coding: utf-8 -*-
"""
Script bổ sung toàn bộ JavaScript handlers cho Chặng 4:
- initRelationshipGraphCanvas, drawRelationshipGraph, drag/drop, zoom, pan, tooltip
- openLivingProfile360Modal, saveContactAutonomy, regenerateContactSummary
- filterChatIntelIntent, toggleChatIntelSilent
"""
import os

html_path = "/home/ryan/heo-harness/heo_harness/plugins/ui_dashboard/dashboard.html"
with open(html_path, "r", encoding="utf-8") as f:
    content = f.read()

handlers_code = '''
// =============================================================================
// CHẶNG 4 (MS-4): RELATIONSHIP GRAPH CANVAS & LIVING PROFILES 360 HANDLERS
// =============================================================================

let graphState = {
  canvas: null,
  ctx: null,
  nodes: [],
  edges: [],
  filter: 'all',
  searchQuery: '',
  scale: 1.0,
  panX: 0,
  panY: 0,
  isDragging: false,
  isPanning: false,
  dragNode: null,
  hoveredNode: null,
  startX: 0,
  startY: 0,
  animFrameId: null,
  pulseTick: 0
};

async function initRelationshipGraphCanvas() {
  const canvas = document.getElementById('relationship-graph-canvas');
  if (!canvas) return;

  const rect = canvas.getBoundingClientRect();
  const dpr = window.devicePixelRatio || 1;
  canvas.width = rect.width * dpr;
  canvas.height = (rect.height || 620) * dpr;
  const ctx = canvas.getContext('2d');
  ctx.scale(dpr, dpr);

  graphState.canvas = canvas;
  graphState.ctx = ctx;
  graphState.width = rect.width;
  graphState.height = rect.height || 620;
  graphState.panX = 0;
  graphState.panY = 0;
  graphState.scale = 1.0;

  const statBadge = document.getElementById('graph-stat-badge');
  if (statBadge) statBadge.textContent = 'Đang tải dữ liệu mạng lưới...';

  try {
    const res = await fetch('/api/relationship/graph');
    const data = await res.json();
    if (!data.ok) throw new Error(data.error || 'Lỗi nạp đồ thị');

    const rawNodes = data.nodes || [];
    const rawEdges = data.edges || [];

    // Bố trí tọa độ thông minh theo mô hình vệ tinh không gian đa tầng (Orbital Force Layout)
    const cx = graphState.width / 2;
    const cy = graphState.height / 2;

    const groups = rawNodes.filter(n => n.type === 'group');
    const contacts = rawNodes.filter(n => n.type === 'contact');
    const opps = rawNodes.filter(n => n.type === 'opportunity');

    rawNodes.forEach(n => {
      if (n.type === 'hq') {
        n.x = cx;
        n.y = cy;
      }
    });

    // Vòng 1: Groups (Bán kính ~130px)
    const rGroups = Math.min(130, graphState.width * 0.22);
    groups.forEach((g, idx) => {
      const angle = (idx / Math.max(1, groups.length)) * Math.PI * 2 - Math.PI / 2;
      g.x = cx + Math.cos(angle) * rGroups;
      g.y = cy + Math.sin(angle) * rGroups;
    });

    // Vòng 2: Contacts (Bán kính ~230px)
    const rContacts = Math.min(230, graphState.width * 0.38);
    contacts.forEach((c, idx) => {
      const angle = (idx / Math.max(1, contacts.length)) * Math.PI * 2 - Math.PI / 3;
      c.x = cx + Math.cos(angle) * rContacts;
      c.y = cy + Math.sin(angle) * rContacts;
    });

    // Vòng 3: Opportunities (Gắn gần contact tương ứng hoặc bán kính ~320px)
    const rOpps = Math.min(320, graphState.width * 0.46);
    opps.forEach((o, idx) => {
      const matchEdge = rawEdges.find(e => e.to === o.id);
      const parentNode = matchEdge ? rawNodes.find(n => n.id === matchEdge.from) : null;
      if (parentNode) {
        const offsetAngle = (idx % 3 - 1) * 0.4;
        const angle = Math.atan2(parentNode.y - cy, parentNode.x - cx) + offsetAngle;
        o.x = parentNode.x + Math.cos(angle) * 75;
        o.y = parentNode.y + Math.sin(angle) * 75;
      } else {
        const angle = (idx / Math.max(1, opps.length)) * Math.PI * 2;
        o.x = cx + Math.cos(angle) * rOpps;
        o.y = cy + Math.sin(angle) * rOpps;
      }
    });

    graphState.nodes = rawNodes;
    graphState.edges = rawEdges;

    if (statBadge) {
      statBadge.innerHTML = `<span style="color:#6366f1;font-weight:700">${rawNodes.length} Nodes</span> · <span style="color:#10b981">${rawEdges.length} Liên Kết</span> · <span style="color:#ef4444">${contacts.filter(c => (c.heat||0)>=80).length} Khách Nóng</span>`;
    }

    setupGraphEventListeners();
    startGraphRenderLoop();
  } catch (err) {
    if (statBadge) statBadge.textContent = 'Lỗi nạp đồ thị: ' + err.message;
  }
}

function setupGraphEventListeners() {
  const canvas = graphState.canvas;
  if (!canvas || canvas._listenersAttached) return;
  canvas._listenersAttached = true;

  canvas.addEventListener('mousedown', (e) => {
    const pt = getCanvasMousePos(e);
    const clickedNode = findNodeAt(pt.x, pt.y);

    if (clickedNode) {
      graphState.isDragging = true;
      graphState.dragNode = clickedNode;
      canvas.style.cursor = 'grabbing';
    } else {
      graphState.isPanning = true;
      graphState.startX = e.clientX - graphState.panX;
      graphState.startY = e.clientY - graphState.panY;
      canvas.style.cursor = 'move';
    }
  });

  window.addEventListener('mousemove', (e) => {
    if (graphState.isDragging && graphState.dragNode) {
      const pt = getCanvasMousePos(e);
      graphState.dragNode.x = pt.x;
      graphState.dragNode.y = pt.y;
      return;
    }

    if (graphState.isPanning) {
      graphState.panX = e.clientX - graphState.startX;
      graphState.panY = e.clientY - graphState.startY;
      return;
    }

    // Hover detection
    if (canvas && e.target === canvas) {
      const pt = getCanvasMousePos(e);
      const hovered = findNodeAt(pt.x, pt.y);
      if (hovered !== graphState.hoveredNode) {
        graphState.hoveredNode = hovered;
        canvas.style.cursor = hovered ? 'pointer' : 'grab';
      }
    }
  });

  window.addEventListener('mouseup', () => {
    if (graphState.isDragging) {
      graphState.isDragging = false;
      graphState.dragNode = null;
    }
    if (graphState.isPanning) {
      graphState.isPanning = false;
    }
    if (canvas) canvas.style.cursor = 'grab';
  });

  canvas.addEventListener('wheel', (e) => {
    e.preventDefault();
    const zoomFactor = e.deltaY < 0 ? 1.1 : 0.9;
    zoomGraphCanvas(zoomFactor);
  }, { passive: false });

  // Double click / Click to open Modal
  canvas.addEventListener('click', (e) => {
    const pt = getCanvasMousePos(e);
    const clickedNode = findNodeAt(pt.x, pt.y);
    if (!clickedNode) return;

    if (clickedNode.type === 'contact') {
      openLivingProfile360Modal(clickedNode.raw_id);
    } else if (clickedNode.type === 'opportunity') {
      showToast(`🎯 Deal: ${clickedNode.label} (${(clickedNode.value||0).toLocaleString()} ₫)`);
    } else if (clickedNode.type === 'hq') {
      showToast('👑 HQ Executive Hub của Sếp Cơ La (Ryan) — Tổng Chỉ Huy Tối Cao!');
    }
  });
}

function getCanvasMousePos(e) {
  const rect = graphState.canvas.getBoundingClientRect();
  const screenX = e.clientX - rect.left;
  const screenY = e.clientY - rect.top;
  // Convert screen coordinates taking into account pan and scale
  const x = (screenX - graphState.panX - graphState.width / 2) / graphState.scale + graphState.width / 2;
  const y = (screenY - graphState.panY - graphState.height / 2) / graphState.scale + graphState.height / 2;
  return { x, y };
}

function findNodeAt(x, y) {
  for (let i = graphState.nodes.length - 1; i >= 0; i--) {
    const n = graphState.nodes[i];
    if (isNodeFiltered(n)) continue;
    const r = (n.size || 20) + 4;
    const dx = n.x - x;
    const dy = n.y - y;
    if (dx * dx + dy * dy <= r * r) {
      return n;
    }
  }
  return null;
}

function isNodeFiltered(n) {
  if (graphState.filter === 'hot') {
    if (n.type === 'contact' && (n.heat || 0) < 80) return true;
  } else if (graphState.filter === 'deal') {
    if (n.type === 'contact') {
      const hasDeal = graphState.edges.some(e => e.from === n.id && e.to.startsWith('opp-'));
      if (!hasDeal) return true;
    }
  }
  if (graphState.searchQuery) {
    const q = graphState.searchQuery.toLowerCase();
    const matchName = (n.label || '').toLowerCase().includes(q);
    const matchCompany = (n.company || '').toLowerCase().includes(q);
    if (!matchName && !matchCompany) return true;
  }
  return false;
}

function startGraphRenderLoop() {
  if (graphState.animFrameId) cancelAnimationFrame(graphState.animFrameId);

  function loop() {
    graphState.pulseTick = (graphState.pulseTick + 1) % 360;
    drawRelationshipGraph();
    graphState.animFrameId = requestAnimationFrame(loop);
  }
  loop();
}

function drawRelationshipGraph() {
  const ctx = graphState.ctx;
  if (!ctx) return;

  const w = graphState.width;
  const h = graphState.height;

  ctx.save();
  ctx.clearRect(0, 0, w, h);

  // Background Grid Matrix
  ctx.fillStyle = '#060a12';
  ctx.fillRect(0, 0, w, h);

  // Apply Camera Transform
  ctx.translate(w / 2 + graphState.panX, h / 2 + graphState.panY);
  ctx.scale(graphState.scale, graphState.scale);
  ctx.translate(-w / 2, -h / 2);

  // Draw Space Grid Dots
  ctx.fillStyle = 'rgba(255, 255, 255, 0.04)';
  const gridStep = 40;
  for (let x = -w; x < w * 2; x += gridStep) {
    for (let y = -h; y < h * 2; y += gridStep) {
      ctx.fillRect(x, y, 1.5, 1.5);
    }
  }

  // Draw Orbital Rings around HQ
  const cx = w / 2;
  const cy = h / 2;
  ctx.strokeStyle = 'rgba(99, 102, 241, 0.08)';
  ctx.lineWidth = 1;
  ctx.setLineDash([4, 6]);
  [130, 230, 320].forEach(radius => {
    ctx.beginPath();
    ctx.arc(cx, cy, radius, 0, Math.PI * 2);
    ctx.stroke();
  });
  ctx.setLineDash([]);

  // 1. Draw Edges
  graphState.edges.forEach(e => {
    const fromNode = graphState.nodes.find(n => n.id === e.from);
    const toNode = graphState.nodes.find(n => n.id === e.to);
    if (!fromNode || !toNode) return;
    if (isNodeFiltered(fromNode) || isNodeFiltered(toNode)) return;

    const isConnectedHover = graphState.hoveredNode && (fromNode.id === graphState.hoveredNode.id || toNode.id === graphState.hoveredNode.id);

    ctx.beginPath();
    ctx.moveTo(fromNode.x, fromNode.y);
    ctx.lineTo(toNode.x, toNode.y);
    ctx.strokeStyle = isConnectedHover ? '#38bdf8' : (e.color || 'rgba(148, 163, 184, 0.25)');
    ctx.lineWidth = isConnectedHover ? 2.5 : 1.2;
    ctx.stroke();

    // Pulse Particle along edge
    const pulseOffset = ((graphState.pulseTick * 0.015) % 1);
    const px = fromNode.x + (toNode.x - fromNode.x) * pulseOffset;
    const py = fromNode.y + (toNode.y - fromNode.y) * pulseOffset;
    ctx.beginPath();
    ctx.arc(px, py, isConnectedHover ? 3 : 1.8, 0, Math.PI * 2);
    ctx.fillStyle = isConnectedHover ? '#38bdf8' : 'rgba(255, 255, 255, 0.6)';
    ctx.fill();

    // Edge label
    if (e.label && (isConnectedHover || e.label.includes('tr'))) {
      const mx = (fromNode.x + toNode.x) / 2;
      const my = (fromNode.y + toNode.y) / 2;
      ctx.font = '9.5px sans-serif';
      ctx.fillStyle = isConnectedHover ? '#38bdf8' : '#94a3b8';
      ctx.textAlign = 'center';
      ctx.fillText(e.label, mx, my - 4);
    }
  });

  // 2. Draw Nodes
  graphState.nodes.forEach(n => {
    if (isNodeFiltered(n)) return;

    const isHovered = graphState.hoveredNode && graphState.hoveredNode.id === n.id;
    const r = (n.size || 20) + (isHovered ? 4 : 0);

    // Glow Effect
    ctx.save();
    ctx.beginPath();
    ctx.arc(n.x, n.y, r + (isHovered ? 10 : 4), 0, Math.PI * 2);
    ctx.fillStyle = n.color || '#6366f1';
    ctx.globalAlpha = isHovered ? 0.4 : 0.15;
    ctx.fill();
    ctx.restore();

    // Node Circle Body
    ctx.beginPath();
    ctx.arc(n.x, n.y, r, 0, Math.PI * 2);
    ctx.fillStyle = '#0f172a';
    ctx.fill();
    ctx.strokeStyle = n.color || '#6366f1';
    ctx.lineWidth = isHovered ? 3.5 : 2;
    ctx.stroke();

    // Inner Icon or Initial
    ctx.font = `bold ${Math.round(r * 0.75)}px sans-serif`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillStyle = n.color || '#fff';

    if (n.type === 'hq') {
      ctx.fillText('👑', n.x, n.y);
    } else if (n.type === 'group') {
      ctx.fillText(n.channel === 'whatsapp' ? '📱' : '💬', n.x, n.y);
    } else if (n.type === 'opportunity') {
      ctx.fillText('💼', n.x, n.y);
    } else {
      ctx.fillText((n.label || 'U').slice(0, 2).toUpperCase(), n.x, n.y);
    }

    // Node Label under
    ctx.font = isHovered ? 'bold 12px sans-serif' : '11px sans-serif';
    ctx.fillStyle = isHovered ? '#ffffff' : '#e2e8f0';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'top';
    ctx.fillText(n.label, n.x, n.y + r + 6);

    // Heat or Value Badge
    if (n.type === 'contact' && n.heat !== undefined) {
      ctx.font = '10px sans-serif';
      ctx.fillStyle = n.heat >= 80 ? '#ef4444' : (n.heat >= 50 ? '#f59e0b' : '#94a3b8');
      ctx.fillText(`${n.heat}° · Cấp ${n.autonomy_level||1}`, n.x, n.y + r + 20);
    } else if (n.type === 'opportunity' && n.value) {
      ctx.font = '10px sans-serif';
      ctx.fillStyle = '#c084fc';
      ctx.fillText(`${(n.value/1000000).toFixed(0)}tr VND`, n.x, n.y + r + 20);
    }
  });

  // 3. Draw Floating Tooltip if Hovered
  if (graphState.hoveredNode) {
    const hn = graphState.hoveredNode;
    ctx.save();
    const tooltipX = hn.x + 25;
    const tooltipY = hn.y - 45;
    const boxW = 220;
    const boxH = hn.type === 'contact' ? 90 : 65;

    ctx.fillStyle = 'rgba(15, 23, 42, 0.92)';
    ctx.strokeStyle = hn.color || '#6366f1';
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.roundRect(tooltipX, tooltipY, boxW, boxH, 8);
    ctx.fill();
    ctx.stroke();

    ctx.font = 'bold 12px sans-serif';
    ctx.fillStyle = '#ffffff';
    ctx.textAlign = 'left';
    ctx.textBaseline = 'top';
    ctx.fillText(hn.label, tooltipX + 12, tooltipY + 10);

    ctx.font = '11px sans-serif';
    ctx.fillStyle = '#94a3b8';
    if (hn.type === 'contact') {
      ctx.fillText(`${hn.role || 'Đại diện'} · ${hn.company || 'Doanh nghiệp'}`, tooltipX + 12, tooltipY + 28);
      ctx.fillText(`Nhiệt độ: ${hn.heat}° · Tự trị: Cấp ${hn.autonomy_level||1}/6`, tooltipX + 12, tooltipY + 46);
      ctx.fillStyle = '#38bdf8';
      ctx.fillText('👉 Nhấp chuột để mở Hồ Sơ Sống 360', tooltipX + 12, tooltipY + 66);
    } else if (hn.type === 'opportunity') {
      ctx.fillText(`Giai đoạn: ${hn.stage || 'SIGNAL'}`, tooltipX + 12, tooltipY + 28);
      ctx.fillText(`Giá trị: ${(hn.value||0).toLocaleString()} VND`, tooltipX + 12, tooltipY + 44);
    } else if (hn.type === 'group') {
      ctx.fillText(`Kênh hội thoại: ${(hn.channel||'zalo').toUpperCase()}`, tooltipX + 12, tooltipY + 28);
      ctx.fillText(`Đầu mối tiếp nhận tín hiệu trực tiếp`, tooltipX + 12, tooltipY + 44);
    } else {
      ctx.fillText(`Tổng Chỉ Huy Sếp Ryan (HQ)`, tooltipX + 12, tooltipY + 28);
      ctx.fillText(`Quyền điều hành tối cao`, tooltipX + 12, tooltipY + 44);
    }
    ctx.restore();
  }

  ctx.restore();
}

function zoomGraphCanvas(factor) {
  graphState.scale = Math.max(0.5, Math.min(2.5, graphState.scale * factor));
}

function resetGraphCanvasView() {
  graphState.scale = 1.0;
  graphState.panX = 0;
  graphState.panY = 0;
}

function filterGraphNodes(filterType) {
  graphState.filter = filterType;
  ['all', 'hot', 'deal'].forEach(f => {
    const btn = document.getElementById('btn-filter-' + f);
    if (btn) {
      if (f === filterType) {
        btn.classList.add('primary');
        btn.classList.remove('subtle');
      } else {
        btn.classList.remove('primary');
        btn.classList.add('subtle');
      }
    }
  });
}

function searchGraphNode(q) {
  graphState.searchQuery = q.trim();
  if (q.trim()) {
    const found = graphState.nodes.find(n => (n.label||'').toLowerCase().includes(q.toLowerCase()));
    if (found) {
      graphState.panX = (graphState.width / 2 - found.x) * graphState.scale;
      graphState.panY = (graphState.height / 2 - found.y) * graphState.scale;
      graphState.hoveredNode = found;
    }
  }
}

// -----------------------------------------------------------------------------
// MODAL LIVING PROFILE 360 & EXPLAINABLE AI (SPEC-20, SPEC-10)
// -----------------------------------------------------------------------------
async function openLivingProfile360Modal(contactId) {
  showToast('Đang tải hồ sơ sống 360...');
  try {
    const res = await fetch(`/api/contacts/detail?id=${encodeURIComponent(contactId)}`);
    const data = await res.json();
    if (!data.ok) throw new Error(data.error || 'Không tìm thấy hồ sơ');

    const c = data.contact;
    const events = data.events || [];
    const opps = data.opportunities || [];

    const autonomyLevels = [
      { lvl: 0, title: "Cấp 0: Chỉ Lắng Nghe", desc: "Agent chỉ thu thập dữ liệu, tuyệt đối không gửi tin nhắn tự động." },
      { lvl: 1, title: "Cấp 1: Dự Thảo Nháp", desc: "Agent soạn thảo bản nháp, Sếp duyệt tay 100% trước khi gửi." },
      { lvl: 2, title: "Cấp 2: Kịch Bản Mẫu", desc: "Tự động phản hồi các câu chào hỏi, thông tin dịch vụ theo kịch bản chuẩn." },
      { lvl: 3, title: "Cấp 3: Bán Tự Trị & Đặt Hẹn", desc: "Tự động đàm phán lịch hẹn, nhắc hẹn và thu thập nhu cầu cơ bản." },
      { lvl: 4, title: "Cấp 4: Báo Giá & Theo Dõi", desc: "Tự động gửi báo giá trong hạn mức chuẩn và bám sát tiến độ đơn hàng." },
      { lvl: 5, title: "Cấp 5: Tác Nghiệp Cao", desc: "Toàn quyền điều phối hội thoại thông thường, gửi báo cáo tổng kết định kỳ." },
      { lvl: 6, title: "Cấp 6: Tự Trị Toàn Diện", desc: "Executive Agent đại diện toàn quyền theo ủy thác của Sếp Cơ La." }
    ];

    const curLvl = c.autonomy_level !== undefined ? c.autonomy_level : 1;

    openModal(`👤 Living Profile 360 · ${escapeHtml(c.full_name)}`, `
      <div style="display:flex;flex-direction:column;gap:18px">
        <!-- Header Card -->
        <div style="display:flex;align-items:center;justify-content:space-between;background:var(--color-bg);padding:14px 18px;border-radius:8px;border:1px solid var(--color-divider)">
          <div style="display:flex;align-items:center;gap:14px">
            <div style="width:48px;height:48px;border-radius:50%;background:rgba(99,102,241,0.2);border:2px solid var(--color-accent);color:var(--color-accent);display:flex;align-items:center;justify-content:center;font-size:18px;font-weight:800">
              ${(c.full_name||'U').slice(0,2).toUpperCase()}
            </div>
            <div>
              <div style="font-size:16px;font-weight:700;color:var(--color-text)">${escapeHtml(c.full_name)}</div>
              <div style="font-size:12px;color:var(--color-neutral-300)">${escapeHtml(c.role || 'Đại diện')} · <b style="color:var(--color-accent)">${escapeHtml(c.company || 'Doanh nghiệp')}</b></div>
              <div style="display:flex;gap:10px;margin-top:4px;font-size:11px;color:var(--color-neutral-400)">
                ${c.phone ? `<span>📞 ${escapeHtml(c.phone)}</span>` : ''}
                ${c.zalo_id ? `<span style="color:#0284c7">💬 Zalo: ${escapeHtml(c.zalo_id)}</span>` : ''}
                ${c.whatsapp_id ? `<span style="color:#10b981">📱 WA: ${escapeHtml(c.whatsapp_id)}</span>` : ''}
                ${c.email ? `<span>✉️ ${escapeHtml(c.email)}</span>` : ''}
              </div>
            </div>
          </div>
          <div style="text-align:right">
            <span class="badge ${c.ball_owner === 'US' ? 'danger' : 'neutral'}" style="font-size:11px;padding:4px 8px">
              ${c.ball_owner === 'US' ? '🎾 Lượt bóng: PHÍA TA (US)' : '⚽ Lượt bóng: ĐỐI TÁC (THEM)'}
            </span>
            <div style="font-size:11px;color:var(--color-neutral-400);margin-top:4px">Đã tương tác ${c.interaction_count || 1} lần</div>
          </div>
        </div>

        <!-- 4 KPI Metrics Row -->
        <div style="display:grid;grid-template-columns:repeat(4, 1fr);gap:10px">
          <div class="card card-pad" style="border-left:3px solid ${(c.heat_score||50)>=80 ? '#ef4444' : '#f59e0b'}">
            <div style="font-size:10.5px;color:var(--color-neutral-400)">NHIỆT ĐỘ QUAN HỆ</div>
            <div style="font-size:22px;font-weight:800;color:${(c.heat_score||50)>=80 ? '#ef4444' : '#f59e0b'};margin:2px 0">${c.heat_score || 50}°</div>
            <div style="font-size:10px;color:var(--color-neutral-400)">Thang điểm 0 - 100°</div>
          </div>

          <div class="card card-pad" style="border-left:3px solid #10b981">
            <div style="font-size:10.5px;color:var(--color-neutral-400)">MỨC ĐỘ GẮN KẾT</div>
            <div style="font-size:22px;font-weight:800;color:#10b981;margin:2px 0">${c.engagement_score || 85}%</div>
            <div style="font-size:10px;color:var(--color-neutral-400)">Phản hồi tích cực</div>
          </div>

          <div class="card card-pad" style="border-left:3px solid ${(c.churn_risk||10)>30 ? '#ef4444' : '#38bdf8'}">
            <div style="font-size:10.5px;color:var(--color-neutral-400)">RỦI RO CHURN</div>
            <div style="font-size:22px;font-weight:800;color:${(c.churn_risk||10)>30 ? '#ef4444' : '#38bdf8'};margin:2px 0">${c.churn_risk || 15}%</div>
            <div style="font-size:10px;color:var(--color-neutral-400)">${c.went_silent_days ? `Im lặng ${c.went_silent_days} ngày` : 'Đang duy trì tốt'}</div>
          </div>

          <div class="card card-pad" style="border-left:3px solid #a855f7">
            <div style="font-size:10.5px;color:var(--color-neutral-400)">MỨC TỰ TRỊ AGENT</div>
            <div style="font-size:22px;font-weight:800;color:#a855f7;margin:2px 0">Cấp ${curLvl}/6</div>
            <div style="font-size:10px;color:var(--color-neutral-400)">Hạn mức quyền hạn</div>
          </div>
        </div>

        <!-- SPEC-10: Explainable AI Box -->
        <div style="background:rgba(2,132,199,0.08);border:1px solid rgba(2,132,199,0.25);border-radius:8px;padding:12px 16px">
          <div style="display:flex;align-items:center;gap:6px;font-weight:700;font-size:12px;color:#38bdf8;margin-bottom:6px">
            <i class="ph ph-sparkle"></i> LẬP LUẬN MINH BẠCH CỦA AI (EXPLAINABLE AI REASONING - SPEC-10)
          </div>
          <div style="font-size:12px;color:var(--color-text);line-height:1.5">
            ${escapeHtml(c.score_explanation || `Hệ thống chấm ${c.heat_score}° dựa trên: Tần suất trao đổi 12 tin nhắn gần đây, thời gian phản hồi trung bình dưới 15 phút, đang mở 1 yêu cầu dịch vụ và chưa có khiếu nại trễ hạn.`)}
          </div>
        </div>

        <!-- SPEC-20: AI Executive Summary (8-12 dòng) -->
        <div class="card card-pad">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">
            <div style="font-weight:700;font-size:13px;display:flex;align-items:center;gap:6px">
              <i class="ph ph-brain" style="color:var(--color-accent)"></i> Tóm Tắt Trí Tuệ Chiến Lược (AI Executive Summary — 8-12 Dòng)
            </div>
            <button class="btn sm" onclick="regenerateContactSummary('${c.id}')"><i class="ph ph-arrows-clockwise"></i> AGY AI Phân Tích Lại</button>
          </div>
          <div id="ai-summary-text-${c.id}" style="font-size:12px;color:var(--color-text);line-height:1.6;white-space:pre-wrap;background:var(--color-bg);padding:12px 14px;border-radius:6px;border:1px solid var(--color-divider)">
            ${escapeHtml(c.ai_summary || "Chưa có bản phân tích chuyên sâu. Bấm 'AGY AI Phân Tích Lại' để sinh hồ sơ chân dung.")}
          </div>
        </div>

        <!-- Slider 6 Mức Tự Trị (Autonomy Level 0-6) -->
        <div class="card card-pad">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">
            <div>
              <div style="font-weight:700;font-size:13px;display:flex;align-items:center;gap:6px">
                <i class="ph ph-sliders" style="color:#a855f7"></i> Thang Trượt Phân Quyền Tự Trị (Autonomy Level 0 - 6)
              </div>
              <div style="font-size:11px;color:var(--color-neutral-400)">Thiết lập quyền tự quyết cho Heo-Harness khi tương tác với đối tác này</div>
            </div>
            <button class="btn sm primary" onclick="saveContactAutonomy('${c.id}')"><i class="ph ph-floppy-disk"></i> Lưu Mức Tự Trị</button>
          </div>

          <div style="margin:16px 0 10px 0">
            <input type="range" id="autonomy-slider-${c.id}" min="0" max="6" value="${curLvl}" step="1" style="width:100%;cursor:pointer" oninput="updateAutonomyDesc('${c.id}', this.value)">
            <div style="display:flex;justify-content:space-between;font-size:10px;color:var(--color-neutral-400);margin-top:6px">
              <span>0 (Lắng nghe)</span>
              <span>1 (Nháp)</span>
              <span>2 (Kịch bản)</span>
              <span>3 (Bán tự trị)</span>
              <span>4 (Báo giá)</span>
              <span>5 (Tác nghiệp)</span>
              <span>6 (Toàn quyền)</span>
            </div>
          </div>

          <div id="autonomy-desc-${c.id}" style="background:rgba(168,85,247,0.08);border:1px solid rgba(168,85,247,0.2);padding:10px 14px;border-radius:6px">
            <div style="font-weight:700;font-size:12px;color:#c084fc" id="autonomy-title-${c.id}">${autonomyLevels[curLvl].title}</div>
            <div style="font-size:11.5px;color:var(--color-neutral-300);margin-top:3px" id="autonomy-detail-${c.id}">${autonomyLevels[curLvl].desc}</div>
          </div>
        </div>

        <!-- Atomic Events Timeline & Opportunities -->
        <div style="display:grid;grid-template-columns:1.2fr 0.8fr;gap:14px">
          <!-- Events Stream -->
          <div class="card card-pad">
            <div style="font-weight:700;font-size:12.5px;margin-bottom:10px;display:flex;align-items:center;gap:6px">
              <i class="ph ph-clock-counter-clockwise"></i> Chuỗi Sự Kiện Nguyên Tử Gần Nhất (${events.length})
            </div>
            <div style="display:flex;flex-direction:column;gap:8px;max-height:220px;overflow-y:auto">
              ${events.length === 0 ? `
                <div style="font-size:11.5px;color:var(--color-neutral-400);padding:12px;text-align:center">Chưa có sự kiện hội thoại nguyên tử</div>
              ` : events.map(e => `
                <div style="background:var(--color-bg);padding:8px 10px;border-radius:6px;border:1px solid var(--color-divider);font-size:11.5px">
                  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px">
                    <span class="badge ${e.type === 'Complained' ? 'danger' : (e.type === 'AskedPrice' ? 'primary' : 'neutral')}" style="font-size:9.5px">${e.type}</span>
                    <span style="font-size:10px;color:var(--color-neutral-400)">${escapeHtml(e.timestamp || '')}</span>
                  </div>
                  <div style="color:var(--color-text)">${escapeHtml(e.content || '')}</div>
                </div>
              `).join('')}
            </div>
          </div>

          <!-- Opportunities Deals -->
          <div class="card card-pad">
            <div style="font-weight:700;font-size:12.5px;margin-bottom:10px;display:flex;align-items:center;gap:6px">
              <i class="ph ph-kanban" style="color:#a855f7"></i> Cơ Hội Deals Liên Quan (${opps.length})
            </div>
            <div style="display:flex;flex-direction:column;gap:8px;max-height:220px;overflow-y:auto">
              ${opps.length === 0 ? `
                <div style="font-size:11.5px;color:var(--color-neutral-400);padding:12px;text-align:center">Chưa liên kết deal nào</div>
              ` : opps.map(o => `
                <div style="background:var(--color-bg);padding:8px 10px;border-radius:6px;border:1px solid var(--color-divider);font-size:11.5px">
                  <div style="font-weight:600;color:var(--color-text)">${escapeHtml(o.title)}</div>
                  <div style="display:flex;justify-content:space-between;margin-top:4px;font-size:10.5px">
                    <span style="color:#a855f7;font-weight:700">${(o.estimated_value||0).toLocaleString()} ₫</span>
                    <span class="badge neutral">${o.stage}</span>
                  </div>
                </div>
              `).join('')}
            </div>
          </div>
        </div>
      </div>
    `, null, 'large');
  } catch (err) {
    showToast('Lỗi nạp hồ sơ: ' + err.message);
  }
}

function updateAutonomyDesc(contactId, val) {
  const autonomyLevels = [
    { lvl: 0, title: "Cấp 0: Chỉ Lắng Nghe", desc: "Agent chỉ thu thập dữ liệu, tuyệt đối không gửi tin nhắn tự động." },
    { lvl: 1, title: "Cấp 1: Dự Thảo Nháp", desc: "Agent soạn thảo bản nháp, Sếp duyệt tay 100% trước khi gửi." },
    { lvl: 2, title: "Cấp 2: Kịch Bản Mẫu", desc: "Tự động phản hồi các câu chào hỏi, thông tin dịch vụ theo kịch bản chuẩn." },
    { lvl: 3, title: "Cấp 3: Bán Tự Trị & Đặt Hẹn", desc: "Tự động đàm phán lịch hẹn, nhắc hẹn và thu thập nhu cầu cơ bản." },
    { lvl: 4, title: "Cấp 4: Báo Giá & Theo Dõi", desc: "Tự động gửi báo giá trong hạn mức chuẩn và bám sát tiến độ đơn hàng." },
    { lvl: 5, title: "Cấp 5: Tác Nghiệp Cao", desc: "Toàn quyền điều phối hội thoại thông thường, gửi báo cáo tổng kết định kỳ." },
    { lvl: 6, title: "Cấp 6: Tự Trị Toàn Diện", desc: "Executive Agent đại diện toàn quyền theo ủy thác của Sếp Cơ La." }
  ];
  const info = autonomyLevels[parseInt(val)] || autonomyLevels[1];
  const titleEl = document.getElementById(`autonomy-title-${contactId}`);
  const descEl = document.getElementById(`autonomy-detail-${contactId}`);
  if (titleEl) titleEl.textContent = info.title;
  if (descEl) descEl.textContent = info.desc;
}

async function saveContactAutonomy(contactId) {
  const slider = document.getElementById(`autonomy-slider-${contactId}`);
  if (!slider) return;
  const lvl = parseInt(slider.value);

  showToast('Đang cập nhật mức tự trị...');
  try {
    const res = await fetch('/api/contacts/update_autonomy', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ contact_id: contactId, autonomy_level: lvl })
    });
    const d = await res.json();
    if (d.ok) {
      showToast(d.message || `Đã lưu thành công Mức Tự Trị Cấp ${lvl}!`);
      await fetchAllData();
      if ((state.subtabs.relationship_radar || 'graph') === 'graph') {
        initRelationshipGraphCanvas();
      }
    } else {
      showToast('Lỗi: ' + d.error);
    }
  } catch (e) {
    showToast('Lỗi lưu mức tự trị: ' + e.message);
  }
}

async function regenerateContactSummary(contactId) {
  showToast('AGY Brain đang tái lập luận hồ sơ chân dung...');
  const textEl = document.getElementById(`ai-summary-text-${contactId}`);
  if (textEl) textEl.textContent = 'Đang phân tích sự kiện tương tác và lập luận chiến lược 8-12 dòng...';

  try {
    const res = await fetch('/api/contacts/generate_summary', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ contact_id: contactId })
    });
    const d = await res.json();
    if (d.ok && d.ai_summary) {
      if (textEl) textEl.textContent = d.ai_summary;
      showToast('Đã hoàn tất phân tích Living Profile 360!');
      await fetchAllData();
    } else {
      showToast('Lỗi phân tích: ' + (d.error || 'Không rõ'));
    }
  } catch (e) {
    showToast('Lỗi gọi AI: ' + e.message);
  }
}

// -----------------------------------------------------------------------------
// SPEC-24: CHAT INTELLIGENCE FILTER BY INTENT & WENT SILENT
// -----------------------------------------------------------------------------
function setChatIntelIntent(intent) {
  state.chat_intel_filter = state.chat_intel_filter || {};
  state.chat_intel_filter.intent = intent;
  renderActiveHub();
}

function toggleChatIntelSilent() {
  state.chat_intel_filter = state.chat_intel_filter || {};
  state.chat_intel_filter.only_silent = !state.chat_intel_filter.only_silent;
  showToast(state.chat_intel_filter.only_silent ? 'Đang lọc khách im lặng > 3 ngày' : 'Đã tắt bộ lọc im lặng');
  renderActiveHub();
}
'''

# Chèn handlers_code vào ngay trước </script> cuối cùng
if "</script>" in content:
    idx = content.rfind("</script>")
    content = content[:idx] + "\n" + handlers_code + "\n" + content[idx:]
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("✓ Đã chèn toàn bộ JavaScript Handlers Chặng 4 vào dashboard.html")
else:
    print("! Lỗi: Không tìm thấy thẻ </script>")
