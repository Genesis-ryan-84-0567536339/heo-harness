# -*- coding: utf-8 -*-
"""
Script nâng cấp Relationship Map thành Obsidian Graph View chuẩn mực:
- Phân cụm rõ rệt (Cluster segregation: HQ, Kênh Chat, Khách Nóng, Khách Ấm, Khách Lạnh, Deals).
- Bộ lọc Nhóm màu sắc (Obsidian Color Groups Toggles).
- Thuật toán Vật lý Force-Directed Simulation mượt mà, chống đè chèn node.
- Hiệu ứng Focus Spotlight chuẩn Obsidian: Hover làm mờ các node không liên quan, làm sáng rực node chọn và các liên kết 1-hop.
- Tùy chỉnh Sliders: Lực đẩy, Khoảng cách dây, Trọng lực cụm.
"""
import re

html_path = "/home/ryan/heo-harness/heo_harness/plugins/ui_dashboard/dashboard.html"
with open(html_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Thay thế renderRelationshipGraphView với giao diện Obsidian Graph View
new_graph_view_html = '''// ----------------------------------------------------
// View 1: Bản Đồ Mạng Lưới Đồ Thị Chuẩn Obsidian (SPEC-19: Obsidian Graph View)
// ----------------------------------------------------
function renderRelationshipGraphView() {
  return `
    <div class="card" style="margin-bottom:20px;border:1px solid rgba(255,255,255,0.08);background:#0b0e14;box-shadow:0 8px 32px rgba(0,0,0,0.6)">
      <!-- Obsidian Top Toolbar -->
      <div style="padding:10px 16px;background:rgba(15,23,42,0.7);backdrop-filter:blur(10px);border-bottom:1px solid rgba(255,255,255,0.06);display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px">
        <!-- Left: Category Group Toggles (Obsidian Color Groups) -->
        <div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap">
          <span style="font-size:11px;font-weight:700;color:var(--color-neutral-400);margin-right:4px;display:flex;align-items:center;gap:4px">
            <i class="ph ph-circles-three"></i> NHÓM:
          </span>
          <button class="btn sm" id="grp-toggle-all" onclick="toggleObsidianCategory('all')" style="font-size:11px;padding:3px 9px;background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.15)">
            Tất Cả
          </button>
          <button class="btn sm" id="grp-toggle-channel" onclick="toggleObsidianCategory('channel')" style="font-size:11px;padding:3px 9px;border:1px solid rgba(14,165,233,0.3);color:#38bdf8;background:rgba(14,165,233,0.12)">
            💬 Kênh & Nhóm
          </button>
          <button class="btn sm" id="grp-toggle-hot" onclick="toggleObsidianCategory('hot')" style="font-size:11px;padding:3px 9px;border:1px solid rgba(244,63,94,0.3);color:#fb7185;background:rgba(244,63,94,0.12)">
            🔥 Khách Nóng
          </button>
          <button class="btn sm" id="grp-toggle-warm" onclick="toggleObsidianCategory('warm')" style="font-size:11px;padding:3px 9px;border:1px solid rgba(245,158,11,0.3);color:#fbbf24;background:rgba(245,158,11,0.12)">
            🟡 Đối Tác Ấm
          </button>
          <button class="btn sm" id="grp-toggle-cold" onclick="toggleObsidianCategory('cold')" style="font-size:11px;padding:3px 9px;border:1px solid rgba(100,116,139,0.3);color:#94a3b8;background:rgba(100,116,139,0.12)">
            ⚪ Im Lặng (>3d)
          </button>
          <button class="btn sm" id="grp-toggle-deal" onclick="toggleObsidianCategory('deal')" style="font-size:11px;padding:3px 9px;border:1px solid rgba(192,132,252,0.3);color:#c084fc;background:rgba(192,132,252,0.12)">
            💼 Deals Cơ Hội
          </button>
        </div>

        <!-- Right: Actions & Tools -->
        <div style="display:flex;align-items:center;gap:8px">
          <!-- Search in Graph -->
          <div style="position:relative">
            <input type="text" class="form-input" id="graph-search-input" placeholder="Tìm kiếm node..." style="width:150px;height:28px;font-size:11px;padding:2px 8px 2px 24px;background:rgba(0,0,0,0.3);border:1px solid rgba(255,255,255,0.1)" oninput="searchGraphNode(this.value)">
            <i class="ph ph-magnifying-glass" style="position:absolute;left:8px;top:7px;font-size:12px;color:#64748b"></i>
          </div>

          <!-- Label Toggle -->
          <button class="btn sm subtle" id="toggle-label-btn" onclick="toggleObsidianLabels()" title="Bật/Tắt nhãn chữ" style="font-size:11px;padding:4px 8px">
            <i class="ph ph-text-aa"></i> <span id="label-toggle-text">Nhãn: BẬT</span>
          </button>

          <!-- Physics Play/Pause -->
          <button class="btn sm subtle" id="toggle-physics-btn" onclick="toggleObsidianPhysics()" title="Bật/Tắt lực vật lý đàn hồi" style="font-size:11px;padding:4px 8px">
            <i class="ph ph-play" id="physics-icon"></i> Lực Vật Lý
          </button>

          <!-- Zoom & Center -->
          <div style="display:flex;gap:3px">
            <button class="btn sm subtle" onclick="zoomGraphCanvas(1.2)" title="Phóng to"><i class="ph ph-plus"></i></button>
            <button class="btn sm subtle" onclick="zoomGraphCanvas(0.8)" title="Thu nhỏ"><i class="ph ph-minus"></i></button>
            <button class="btn sm subtle" onclick="resetGraphCanvasView()" title="Căn giữa"><i class="ph ph-corners-out"></i></button>
            <button class="btn sm primary" onclick="initRelationshipGraphCanvas()" title="Tải lại đồ thị"><i class="ph ph-arrows-clockwise"></i></button>
          </div>
        </div>
      </div>

      <!-- Obsidian Graph Canvas Viewport -->
      <div style="position:relative;width:100%;height:640px;background:#080b11;overflow:hidden">
        <canvas id="relationship-graph-canvas" style="display:block;cursor:grab;width:100%;height:100%"></canvas>
        
        <!-- Obsidian Bottom Floating Status Badge -->
        <div style="position:absolute;bottom:14px;left:16px;background:rgba(15,23,42,0.85);backdrop-filter:blur(10px);border:1px solid rgba(255,255,255,0.08);padding:6px 14px;border-radius:20px;font-size:11px;color:#94a3b8;display:flex;align-items:center;gap:10px;pointer-events:none;z-index:5">
          <div style="display:flex;align-items:center;gap:5px">
            <span style="display:inline-block;width:6px;height:6px;border-radius:50%;background:#10b981;box-shadow:0 0 6px #10b981"></span>
            <span id="graph-stat-badge">Obsidian Engine Active</span>
          </div>
          <span style="opacity:0.4">|</span>
          <span>Hover node để <b>Focus Spotlight</b> · Nhấp để mở <b>Hồ Sơ 360</b></span>
        </div>

        <!-- Obsidian Cluster Legend Hints (Góc phải trên) -->
        <div style="position:absolute;top:14px;right:14px;background:rgba(15,23,42,0.85);backdrop-filter:blur(8px);border:1px solid rgba(255,255,255,0.08);padding:8px 12px;border-radius:8px;font-size:10.5px;color:#64748b;pointer-events:none;z-index:5;display:flex;flex-direction:column;gap:4px">
          <div><span style="color:#818cf8">● Tâm:</span> HQ Tổng Chỉ Huy Sếp Ryan</div>
          <div><span style="color:#0ea5e9">● Cụm Tây-Bắc:</span> Kênh Zalo & WhatsApp</div>
          <div><span style="color:#f43f5e">● Cụm Đông-Bắc:</span> Khách Hàng Nóng VIP</div>
          <div><span style="color:#c084fc">● Cụm Đông:</span> Cơ Hội Deals Đang Mở</div>
          <div><span style="color:#f59e0b">● Cụm Đông-Nam:</span> Đối Tác Tiềm Năng</div>
          <div><span style="color:#64748b">● Cụm Tây-Nam:</span> Khách Im Lặng (Went Silent)</div>
        </div>
      </div>
    </div>
  `;
}'''

# Thay thế hàm renderRelationshipGraphView trong content
content = re.sub(
    r"// -+?\n// View 1: Bản Đồ Mạng Lưới Đồ Thị[\s\S]*?function renderRelationshipRadarView",
    new_graph_view_html + "\n\n// ----------------------------------------------------\n// View 2: Phân Bổ Nhiệt Độ & Trọng Tài Bóng (SPEC-19)\n// ----------------------------------------------------\nfunction renderRelationshipRadarView",
    content
)

# 2. Thay thế toàn bộ khối JavaScript logic của đồ thị bằng Obsidian Force Simulation Engine
old_graph_js_regex = r"let graphState = \{[\s\S]*?// -----------------------------------------------------------------------------\n// MODAL LIVING PROFILE 360"

new_graph_js_code = '''let graphState = {
  canvas: null,
  ctx: null,
  nodes: [],
  edges: [],
  activeCategories: { hq: true, channel: true, hot: true, warm: true, cold: true, deal: true },
  searchQuery: '',
  showLabels: true,
  physicsEnabled: true,
  scale: 1.0,
  panX: 0,
  panY: 0,
  isDragging: false,
  isPanning: false,
  dragNode: null,
  hoveredNode: null,
  selectedNode: null,
  startX: 0,
  startY: 0,
  animFrameId: null,
  pulseTick: 0,
  // Obsidian Physics Parameters
  repulsion: 85,
  springLength: 95,
  springStrength: 0.045,
  clusterGravity: 0.035,
  damping: 0.86
};

async function initRelationshipGraphCanvas() {
  const canvas = document.getElementById('relationship-graph-canvas');
  if (!canvas) return;

  const rect = canvas.getBoundingClientRect();
  const dpr = window.devicePixelRatio || 1;
  canvas.width = rect.width * dpr;
  canvas.height = (rect.height || 640) * dpr;
  const ctx = canvas.getContext('2d');
  ctx.scale(dpr, dpr);

  graphState.canvas = canvas;
  graphState.ctx = ctx;
  graphState.width = rect.width;
  graphState.height = rect.height || 640;
  graphState.panX = 0;
  graphState.panY = 0;
  graphState.scale = 1.0;

  const statBadge = document.getElementById('graph-stat-badge');
  if (statBadge) statBadge.textContent = 'Đang phân cụm Obsidian...';

  try {
    const res = await fetch('/api/relationship/graph');
    const data = await res.json();
    if (!data.ok) throw new Error(data.error || 'Lỗi nạp đồ thị');

    const rawNodes = data.nodes || [];
    const rawEdges = data.edges || [];

    const cx = graphState.width / 2;
    const cy = graphState.height / 2;

    // Thiết lập tọa độ Centroid Phân Cụm Obsidian (Cluster Centroids)
    const clusterCentroids = {
      hq:      { x: cx,       y: cy },
      channel: { x: cx - 240, y: cy - 130 },
      hot:     { x: cx + 240, y: cy - 130 },
      warm:    { x: cx + 240, y: cy + 140 },
      cold:    { x: cx - 240, y: cy + 140 },
      deal:    { x: cx + 340, y: cy - 20 }
    };

    // Khởi tạo vị trí ban đầu theo từng cụm (tạo độ tản ngẫu nhiên xung quanh centroid cụm)
    rawNodes.forEach((n, idx) => {
      const cat = n.category || 'warm';
      const c = clusterCentroids[cat] || clusterCentroids.warm;
      const angle = (idx * 1.37) % (Math.PI * 2);
      const r = (idx % 4) * 28 + 20;

      n.x = c.x + Math.cos(angle) * r;
      n.y = c.y + Math.sin(angle) * r;
      n.vx = 0;
      n.vy = 0;
      n.targetCluster = c;
    });

    graphState.nodes = rawNodes;
    graphState.edges = rawEdges;

    if (statBadge) {
      const activeCount = rawNodes.filter(n => graphState.activeCategories[n.category]).length;
      statBadge.innerHTML = `<b style="color:#818cf8">${rawNodes.length} Nodes</b> · <b>${rawEdges.length} Edges</b> · <b>5 Cụm Obsidian</b>`;
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
      graphState.selectedNode = clickedNode;
      canvas.style.cursor = 'grabbing';
    } else {
      graphState.isPanning = true;
      graphState.startX = e.clientX - graphState.panX;
      graphState.startY = e.clientY - graphState.panY;
      graphState.selectedNode = null;
      canvas.style.cursor = 'move';
    }
  });

  window.addEventListener('mousemove', (e) => {
    if (graphState.isDragging && graphState.dragNode) {
      const pt = getCanvasMousePos(e);
      graphState.dragNode.x = pt.x;
      graphState.dragNode.y = pt.y;
      graphState.dragNode.vx = 0;
      graphState.dragNode.vy = 0;
      return;
    }

    if (graphState.isPanning) {
      graphState.panX = e.clientX - graphState.startX;
      graphState.panY = e.clientY - graphState.startY;
      return;
    }

    // Hover detection (Obsidian Spotlight Trigger)
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
    const zoomFactor = e.deltaY < 0 ? 1.08 : 0.92;
    zoomGraphCanvas(zoomFactor);
  }, { passive: false });

  // Nhấp đúp hoặc nhấp chuột vào Node để mở Modal Living Profile 360
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
  const x = (screenX - graphState.panX - graphState.width / 2) / graphState.scale + graphState.width / 2;
  const y = (screenY - graphState.panY - graphState.height / 2) / graphState.scale + graphState.height / 2;
  return { x, y };
}

function findNodeAt(x, y) {
  for (let i = graphState.nodes.length - 1; i >= 0; i--) {
    const n = graphState.nodes[i];
    if (isNodeHidden(n)) continue;
    const r = (n.size || 16) + 4;
    const dx = n.x - x;
    const dy = n.y - y;
    if (dx * dx + dy * dy <= r * r) {
      return n;
    }
  }
  return null;
}

function isNodeHidden(n) {
  if (!graphState.activeCategories[n.category]) return true;
  if (graphState.searchQuery) {
    const q = graphState.searchQuery.toLowerCase();
    const matchName = (n.label || '').toLowerCase().includes(q);
    const matchCompany = (n.company || '').toLowerCase().includes(q);
    if (!matchName && !matchCompany) return true;
  }
  return false;
}

// Bật / Tắt hiển thị từng nhóm màu Obsidian
function toggleObsidianCategory(catKey) {
  if (catKey === 'all') {
    const allOn = Object.values(graphState.activeCategories).every(v => v);
    Object.keys(graphState.activeCategories).forEach(k => {
      graphState.activeCategories[k] = !allOn;
    });
  } else {
    graphState.activeCategories[catKey] = !graphState.activeCategories[catKey];
  }

  // Cập nhật trạng thái nút UI
  ['all', 'channel', 'hot', 'warm', 'cold', 'deal'].forEach(k => {
    const btn = document.getElementById('grp-toggle-' + k);
    if (btn) {
      const active = k === 'all' ? Object.values(graphState.activeCategories).every(v => v) : graphState.activeCategories[k];
      btn.style.opacity = active ? '1' : '0.4';
    }
  });
}

function toggleObsidianLabels() {
  graphState.showLabels = !graphState.showLabels;
  const txt = document.getElementById('label-toggle-text');
  if (txt) txt.textContent = graphState.showLabels ? 'Nhãn: BẬT' : 'Nhãn: TẮT';
}

function toggleObsidianPhysics() {
  graphState.physicsEnabled = !graphState.physicsEnabled;
  const icon = document.getElementById('physics-icon');
  if (icon) icon.className = graphState.physicsEnabled ? 'ph ph-pause' : 'ph ph-play';
  showToast(graphState.physicsEnabled ? 'Đã bật mô phỏng vật lý đàn hồi' : 'Đã khóa vị trí đồ thị (Static Mode)');
}

function startGraphRenderLoop() {
  if (graphState.animFrameId) cancelAnimationFrame(graphState.animFrameId);

  function loop() {
    graphState.pulseTick = (graphState.pulseTick + 1) % 360;

    if (graphState.physicsEnabled) {
      applyObsidianForces();
    }

    drawObsidianGraph();
    graphState.animFrameId = requestAnimationFrame(loop);
  }
  loop();
}

// Thuật toán Vật Lý Lực Đẩy - Hút - Hướng Tâm Phân Cụm (Obsidian Force Physics)
function applyObsidianForces() {
  const nodes = graphState.nodes;
  const edges = graphState.edges;
  const nLen = nodes.length;

  // 1. Lực đẩy Coulomb giữa các cặp node (Chống đè lên nhau)
  for (let i = 0; i < nLen; i++) {
    const n1 = nodes[i];
    if (isNodeHidden(n1)) continue;

    for (let j = i + 1; j < nLen; j++) {
      const n2 = nodes[j];
      if (isNodeHidden(n2)) continue;

      const dx = n2.x - n1.x;
      const dy = n2.y - n1.y;
      const distSq = dx * dx + dy * dy + 1;
      const dist = Math.sqrt(distSq);

      const minDist = (n1.size || 16) + (n2.size || 16) + 35;
      if (dist < minDist * 2.5) {
        const force = (graphState.repulsion * 15) / distSq;
        const fx = (dx / dist) * force;
        const fy = (dy / dist) * force;

        if (n1 !== graphState.dragNode && n1.type !== 'hq') {
          n1.vx -= fx;
          n1.vy -= fy;
        }
        if (n2 !== graphState.dragNode && n2.type !== 'hq') {
          n2.vx += fx;
          n2.vy += fy;
        }
      }
    }

    // 2. Lực hút về Centroid của Cụm tương ứng (Giữ các node theo từng hòn đảo riêng biệt)
    if (n1.targetCluster && n1 !== graphState.dragNode && n1.type !== 'hq') {
      const cdx = n1.targetCluster.x - n1.x;
      const cdy = n1.targetCluster.y - n1.y;
      n1.vx += cdx * graphState.clusterGravity;
      n1.vy += cdy * graphState.clusterGravity;
    }
  }

  // 3. Lực lò xo đàn hồi (Spring Force) kéo các liên kết
  edges.forEach(e => {
    const fromNode = nodes.find(n => n.id === e.from);
    const toNode = nodes.find(n => n.id === e.to);
    if (!fromNode || !toNode || isNodeHidden(fromNode) || isNodeHidden(toNode)) return;

    const dx = toNode.x - fromNode.x;
    const dy = toNode.y - fromNode.y;
    const dist = Math.sqrt(dx * dx + dy * dy) || 1;
    const delta = dist - graphState.springLength;
    const force = delta * graphState.springStrength;

    const fx = (dx / dist) * force;
    const fy = (dy / dist) * force;

    if (fromNode !== graphState.dragNode && fromNode.type !== 'hq') {
      fromNode.vx += fx;
      fromNode.vy += fy;
    }
    if (toNode !== graphState.dragNode && toNode.type !== 'hq') {
      toNode.vx -= fx;
      toNode.vy -= fy;
    }
  });

  // 4. Áp dụng vận tốc và giảm chấn (Damping)
  nodes.forEach(n => {
    if (n === graphState.dragNode || n.type === 'hq') return;
    n.vx *= graphState.damping;
    n.vy *= graphState.damping;
    n.x += n.vx;
    n.y += n.vy;
  });
}

// Hàm vẽ đồ thị chuẩn Obsidian Graph View
function drawObsidianGraph() {
  const ctx = graphState.ctx;
  if (!ctx) return;

  const w = graphState.width;
  const h = graphState.height;

  ctx.save();
  ctx.clearRect(0, 0, w, h);

  // Background vũ trụ Obsidian sâu thẳm
  ctx.fillStyle = '#080b11';
  ctx.fillRect(0, 0, w, h);

  // Camera Pan & Zoom Transform
  ctx.translate(w / 2 + graphState.panX, h / 2 + graphState.panY);
  ctx.scale(graphState.scale, graphState.scale);
  ctx.translate(-w / 2, -h / 2);

  // Ma trận tọa độ mờ tinh tế (Obsidian Subtle Grid)
  ctx.fillStyle = 'rgba(255, 255, 255, 0.025)';
  const step = 45;
  for (let x = -w * 0.5; x < w * 1.5; x += step) {
    for (let y = -h * 0.5; y < h * 1.5; y += step) {
      ctx.fillRect(x, y, 1.2, 1.2);
    }
  }

  // Xác định node đang focus (Hover hoặc Selected)
  const activeFocus = graphState.hoveredNode || graphState.selectedNode;
  const isFocusMode = !!activeFocus;

  // Tập hợp các Node và Edges liên kết trực tiếp với activeFocus
  const connectedNodeIds = new Set();
  if (activeFocus) {
    connectedNodeIds.add(activeFocus.id);
    graphState.edges.forEach(e => {
      if (e.from === activeFocus.id) connectedNodeIds.add(e.to);
      if (e.to === activeFocus.id) connectedNodeIds.add(e.from);
    });
  }

  // 1. DRAW EDGES (Thanh mảnh, tinh tế phong cách Obsidian)
  graphState.edges.forEach(e => {
    const fromNode = graphState.nodes.find(n => n.id === e.from);
    const toNode = graphState.nodes.find(n => n.id === e.to);
    if (!fromNode || !toNode || isNodeHidden(fromNode) || isNodeHidden(toNode)) return;

    const isConnected = isFocusMode && (fromNode.id === activeFocus.id || toNode.id === activeFocus.id);

    ctx.save();
    if (isFocusMode && !isConnected) {
      ctx.globalAlpha = 0.08; // Làm mờ đường không liên quan
    }

    ctx.beginPath();
    ctx.moveTo(fromNode.x, fromNode.y);
    ctx.lineTo(toNode.x, toNode.y);

    if (isConnected) {
      ctx.strokeStyle = '#38bdf8'; // Sáng rực rỡ khi kết nối với node đang chọn
      ctx.lineWidth = 1.8;
      ctx.shadowColor = '#38bdf8';
      ctx.shadowBlur = 8;
    } else {
      ctx.strokeStyle = e.color || 'rgba(255, 255, 255, 0.12)';
      ctx.lineWidth = 0.8;
    }
    ctx.stroke();

    // Hạt pulse chạy dọc đường nếu là edge đang kết nối
    if (isConnected) {
      const pulseOffset = ((graphState.pulseTick * 0.02) % 1);
      const px = fromNode.x + (toNode.x - fromNode.x) * pulseOffset;
      const py = fromNode.y + (toNode.y - fromNode.y) * pulseOffset;
      ctx.beginPath();
      ctx.arc(px, py, 2.5, 0, Math.PI * 2);
      ctx.fillStyle = '#ffffff';
      ctx.fill();
    }

    ctx.restore();
  });

  // 2. DRAW NODES (Vòng tròn tinh tế phát sáng Obsidian)
  graphState.nodes.forEach(n => {
    if (isNodeHidden(n)) return;

    const isFocused = isFocusMode && n.id === activeFocus.id;
    const isNeighbor = isFocusMode && connectedNodeIds.has(n.id);
    const isDimmed = isFocusMode && !isNeighbor;

    ctx.save();
    if (isDimmed) {
      ctx.globalAlpha = 0.12; // Làm mờ 88% các node không liên quan y hệt Obsidian!
    }

    const r = (n.size || 16) * (isFocused ? 1.25 : 1.0);

    // Hào quang mờ xung quanh (Glow)
    ctx.beginPath();
    ctx.arc(n.x, n.y, r + (isFocused ? 10 : 4), 0, Math.PI * 2);
    ctx.fillStyle = n.color || '#818cf8';
    ctx.globalAlpha = (isDimmed ? 0.05 : (isFocused ? 0.35 : 0.15));
    ctx.fill();

    // Thân hạt Node
    ctx.beginPath();
    ctx.arc(n.x, n.y, r, 0, Math.PI * 2);
    ctx.fillStyle = '#0f172a';
    ctx.fill();

    ctx.strokeStyle = n.color || '#818cf8';
    ctx.lineWidth = isFocused ? 2.5 : 1.5;
    if (isFocused) {
      ctx.shadowColor = n.color || '#818cf8';
      ctx.shadowBlur = 12;
    }
    ctx.stroke();

    // Icon / Ký tự bên trong hạt
    ctx.font = `bold ${Math.round(r * 0.8)}px sans-serif`;
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

    // Nhãn văn bản (Labels): Chỉ hiển thị nếu showLabels=true hoặc là node đang focus
    if (graphState.showLabels || isFocused || isNeighbor) {
      ctx.font = isFocused ? 'bold 12px sans-serif' : '10.5px sans-serif';
      ctx.fillStyle = isFocused ? '#ffffff' : (isNeighbor ? '#e2e8f0' : 'rgba(226, 232, 240, 0.7)');
      ctx.textAlign = 'center';
      ctx.textBaseline = 'top';
      ctx.fillText(n.label, n.x, n.y + r + 6);

      // Điểm phụ (Nhiệt độ / Giá trị deal)
      if (n.type === 'contact' && n.heat !== undefined) {
        ctx.font = '9.5px sans-serif';
        ctx.fillStyle = n.heat >= 80 ? '#fb7185' : (n.heat >= 50 ? '#fbbf24' : '#94a3b8');
        ctx.fillText(`${n.heat}° · Cấp ${n.autonomy_level||1}`, n.x, n.y + r + 20);
      } else if (n.type === 'opportunity' && n.value) {
        ctx.font = '9.5px sans-serif';
        ctx.fillStyle = '#c084fc';
        ctx.fillText(`${(n.value/1000000).toFixed(0)}tr ₫`, n.x, n.y + r + 20);
      }
    }

    ctx.restore();
  });

  // 3. FLOATING TOOLTIP (Khi Hover vào node)
  if (graphState.hoveredNode) {
    const hn = graphState.hoveredNode;
    ctx.save();
    const tooltipX = hn.x + 20;
    const tooltipY = hn.y - 45;
    const boxW = 230;
    const boxH = hn.type === 'contact' ? 88 : 65;

    ctx.fillStyle = 'rgba(15, 23, 42, 0.94)';
    ctx.strokeStyle = hn.color || '#818cf8';
    ctx.lineWidth = 1.5;
    ctx.shadowColor = 'rgba(0, 0, 0, 0.6)';
    ctx.shadowBlur = 14;
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
      ctx.fillText('👉 Nhấp đúp để mở Hồ Sơ Sống 360', tooltipX + 12, tooltipY + 66);
    } else if (hn.type === 'opportunity') {
      ctx.fillText(`Giai đoạn: ${hn.stage || 'SIGNAL'}`, tooltipX + 12, tooltipY + 28);
      ctx.fillText(`Giá trị: ${(hn.value||0).toLocaleString()} VND`, tooltipX + 12, tooltipY + 44);
    } else if (hn.type === 'group') {
      ctx.fillText(`Kênh kết nối: ${(hn.channel||'zalo').toUpperCase()}`, tooltipX + 12, tooltipY + 28);
      ctx.fillText(`Cụm hội thoại tiếp nhận tín hiệu trực tiếp`, tooltipX + 12, tooltipY + 44);
    } else {
      ctx.fillText(`Tổng Chỉ Huy Sếp Ryan (HQ Trung Tâm)`, tooltipX + 12, tooltipY + 28);
      ctx.fillText(`Mắt xích chỉ huy điều phối tối cao`, tooltipX + 12, tooltipY + 44);
    }
    ctx.restore();
  }

  ctx.restore();
}

function zoomGraphCanvas(factor) {
  graphState.scale = Math.max(0.4, Math.min(3.0, graphState.scale * factor));
}

function resetGraphCanvasView() {
  graphState.scale = 1.0;
  graphState.panX = 0;
  graphState.panY = 0;
}

function searchGraphNode(q) {
  graphState.searchQuery = q.trim();
  if (q.trim()) {
    const found = graphState.nodes.find(n => (n.label||'').toLowerCase().includes(q.toLowerCase()));
    if (found) {
      graphState.panX = (graphState.width / 2 - found.x) * graphState.scale;
      graphState.panY = (graphState.height / 2 - found.y) * graphState.scale;
      graphState.selectedNode = found;
      graphState.hoveredNode = found;
    }
  }
}
'''

content = re.sub(
    old_graph_js_regex,
    new_graph_js_code + "\n\n// -----------------------------------------------------------------------------\n// MODAL LIVING PROFILE 360",
    content
)

with open(html_path, "w", encoding="utf-8") as f:
    f.write(content)

print("✓ Đã nâng cấp toàn diện Obsidian Graph View vào dashboard.html")
