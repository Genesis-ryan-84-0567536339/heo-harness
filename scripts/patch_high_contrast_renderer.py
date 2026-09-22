import re

html_path = "heo_harness/plugins/ui_dashboard/dashboard.html"

with open(html_path, "r", encoding="utf-8") as f:
    content = f.read()

# Thay thế từ findNodeAt đến hết drawObsidianGraph
pattern = r"function findNodeAt\(x, y\) \{[\s\S]*?ctx\.restore\(\);\s*\}\s*function"

replacement_code = """function findNodeAt(x, y) {
  for (let i = graphState.nodes.length - 1; i >= 0; i--) {
    const n = graphState.nodes[i];
    if (isNodeHidden(n)) continue;
    const r = (n.size || 18) + 6;
    const dx = n.x - x;
    const dy = n.y - y;
    if (dx * dx + dy * dy <= r * r) {
      return n;
    }
  }
  return null;
}

// BỘ LỌC GIẢM NHIỄU TOÀN DIỆN (SPEC-19 & SPEC-24)
function isNodeHidden(n) {
  // 1. Kiểm tra nhóm loại cơ bản
  if (!graphState.activeCategories[n.category]) return true;

  // 2. Tùy chọn giấu Deals vệ tinh để giảm 60% nhiễu
  if (graphState.hideDeals && n.type === 'opportunity') return true;

  // 3. Lọc theo nhiệt độ quan hệ (chỉ áp dụng cho Contact)
  if (n.type === 'contact' && n.heat !== undefined && n.heat < graphState.minHeatThreshold) {
    return true;
  }

  // 4. Lọc theo Kênh Hội Thoại (Zalo / WhatsApp)
  if (graphState.channelFilter !== 'all') {
    if (n.type === 'group' && n.channel !== graphState.channelFilter) {
      return true;
    }
    if (n.type === 'contact') {
      // Kiểm tra xem contact này có liên kết với group kênh đang chọn không
      const matchChannel = graphState.edges.some(e => {
        if (e.to === n.id || e.from === n.id) {
          const otherId = e.to === n.id ? e.from : e.to;
          if (graphState.channelFilter === 'zalo' && otherId.includes('zalo')) return true;
          if (graphState.channelFilter === 'whatsapp' && otherId.includes('wa')) return true;
        }
        return false;
      });
      if (!matchChannel) return true;
    }
    if (n.type === 'opportunity') {
      // Nếu là deal của contact bị ẩn thì ẩn deal
      const parentEdge = graphState.edges.find(e => e.to === n.id);
      if (parentEdge) {
        const parentNode = graphState.nodes.find(pn => pn.id === parentEdge.from);
        if (parentNode && isNodeHidden(parentNode)) return true;
      }
    }
  }

  // 5. Tìm kiếm từ khóa (Họ tên, công ty, tiêu đề deal)
  if (graphState.searchQuery) {
    const q = graphState.searchQuery.toLowerCase();
    const matchName = (n.label || '').toLowerCase().includes(q);
    const matchCompany = (n.company || '').toLowerCase().includes(q);
    const matchTitle = (n.full_title || '').toLowerCase().includes(q);
    if (!matchName && !matchCompany && !matchTitle) return true;
  }

  return false;
}

// 1. Kịch Bản Nhanh (1-Click Presets)
function applyGraphPreset(preset) {
  // Reset trạng thái nút preset
  ['all', 'core', 'hot', 'silent'].forEach(p => {
    const btn = document.getElementById('preset-btn-' + p);
    if (btn) btn.className = 'btn sm ' + (p === preset ? 'primary' : 'subtle');
  });

  if (preset === 'all') {
    // Toàn mạng: Bật tất cả, hiện deals, nhiệt độ 0
    Object.keys(graphState.activeCategories).forEach(k => graphState.activeCategories[k] = true);
    graphState.hideDeals = false;
    graphState.minHeatThreshold = 0;
    graphState.channelFilter = 'all';
  } else if (preset === 'core') {
    // Tinh gọn: Bật tất cả nhưng ẨN DEALS VỆ TINH để giảm 60% liên kết chằng chịt!
    Object.keys(graphState.activeCategories).forEach(k => graphState.activeCategories[k] = true);
    graphState.hideDeals = true;
    graphState.minHeatThreshold = 0;
    graphState.channelFilter = 'all';
  } else if (preset === 'hot') {
    // Khách Nóng: Chỉ hiện HQ, Kênh và Khách >=80°
    Object.keys(graphState.activeCategories).forEach(k => {
      graphState.activeCategories[k] = (k === 'hq' || k === 'channel' || k === 'hot' || k === 'deal');
    });
    graphState.hideDeals = false;
    graphState.minHeatThreshold = 80;
  } else if (preset === 'silent') {
    // Khách im lặng >3 ngày
    Object.keys(graphState.activeCategories).forEach(k => {
      graphState.activeCategories[k] = (k === 'hq' || k === 'channel' || k === 'cold' || k === 'deal');
    });
    graphState.hideDeals = false;
    graphState.minHeatThreshold = 0;
  }

  syncFilterUIControls();
  updateGraphStatBadges();
}

// 2. Bật/Tắt Checkbox Nhóm Loại
function toggleCategoryCheckbox(catKey, isChecked) {
  graphState.activeCategories[catKey] = isChecked;
  updateGraphStatBadges();
}

// 3. Công Tắc Gạt Giấu Deals Vệ Tinh
function toggleHideDeals(hide) {
  graphState.hideDeals = hide;
  updateGraphStatBadges();
}

// 4. Lọc Nhiệt Độ Quan Hệ
function updateHeatFilter(val) {
  graphState.minHeatThreshold = parseInt(val, 10) || 0;
  const label = document.getElementById('heat-slider-val');
  if (label) {
    label.textContent = graphState.minHeatThreshold === 0 ? 'Từ 0° trở lên' : `Từ ${graphState.minHeatThreshold}° trở lên`;
  }
  updateGraphStatBadges();
}

// 5. Lọc Theo Kênh (All / Zalo / WhatsApp)
function updateChannelFilter(ch) {
  graphState.channelFilter = ch;
  ['all', 'zalo', 'wa'].forEach(k => {
    const btn = document.getElementById('channel-btn-' + k);
    if (btn) {
      const match = (k === 'all' && ch === 'all') || (k === 'zalo' && ch === 'zalo') || (k === 'wa' && ch === 'whatsapp');
      btn.className = 'btn sm ' + (match ? 'primary' : 'subtle');
    }
  });
  updateGraphStatBadges();
}

// 6. Đổi Theme Nền Canvas (Sáng Rõ vs Void Tối)
function setGraphTheme(theme) {
  graphState.canvasTheme = theme;
  const btnNavy = document.getElementById('theme-btn-navy');
  const btnVoid = document.getElementById('theme-btn-void');
  if (btnNavy && btnVoid) {
    btnNavy.className = 'btn sm ' + (theme === 'navy_bright' ? 'primary' : 'subtle');
    btnVoid.className = 'btn sm ' + (theme === 'void_dark' ? 'primary' : 'subtle');
  }
}

// 7. Đồng Bộ Giao Diện Điều Khiển Lọc
function syncFilterUIControls() {
  // Sync checkboxes
  Object.keys(graphState.activeCategories).forEach(k => {
    const chk = document.getElementById('chk-cat-' + k);
    if (chk) chk.checked = graphState.activeCategories[k];
  });
  // Sync hide deals switch
  const dealSwitch = document.getElementById('toggle-hide-deals');
  if (dealSwitch) dealSwitch.checked = graphState.hideDeals;
  // Sync heat slider
  const heatSlider = document.getElementById('heat-filter-slider');
  if (heatSlider) heatSlider.value = graphState.minHeatThreshold;
  const heatLabel = document.getElementById('heat-slider-val');
  if (heatLabel) heatLabel.textContent = graphState.minHeatThreshold === 0 ? 'Từ 0° trở lên' : `Từ ${graphState.minHeatThreshold}° trở lên`;
}

// 8. Đặt Lại Mặc Định Tất Cả Bộ Lọc
function resetAllGraphFilters() {
  applyGraphPreset('all');
  const searchInput = document.getElementById('graph-search-input');
  if (searchInput) searchInput.value = '';
  graphState.searchQuery = '';
  const clearBtn = document.getElementById('search-clear-btn');
  if (clearBtn) clearBtn.style.display = 'none';
  showToast('Đã khôi phục bộ lọc đồ thị về mặc định');
}

function clearGraphSearch() {
  const searchInput = document.getElementById('graph-search-input');
  if (searchInput) searchInput.value = '';
  graphState.searchQuery = '';
  const clearBtn = document.getElementById('search-clear-btn');
  if (clearBtn) clearBtn.style.display = 'none';
  updateGraphStatBadges();
}

function searchGraphNode(query) {
  graphState.searchQuery = query ? query.trim() : '';
  const clearBtn = document.getElementById('search-clear-btn');
  if (clearBtn) clearBtn.style.display = graphState.searchQuery ? 'block' : 'none';
  updateGraphStatBadges();
}

function toggleObsidianLabels(show) {
  graphState.showLabels = show !== undefined ? show : !graphState.showLabels;
}

function toggleObsidianPhysics(enable) {
  graphState.physicsEnabled = enable !== undefined ? enable : !graphState.physicsEnabled;
  showToast(graphState.physicsEnabled ? 'Đã bật mô phỏng vật lý đàn hồi' : 'Đã khóa vị trí đồ thị (Static Mode)');
}

function updateGraphStatBadges() {
  if (!graphState.nodes) return;
  const visibleNodes = graphState.nodes.filter(n => !isNodeHidden(n));
  const total = graphState.nodes.length;
  
  const statBadge = document.getElementById('graph-stat-badge');
  if (statBadge) {
    statBadge.innerHTML = `<b style="color:#38bdf8">${visibleNodes.length}/${total} Nodes Hiển Thị</b> · <b>Giảm Nhiễu Active</b>`;
  }
  const countBadge = document.getElementById('filter-node-count-badge');
  if (countBadge) {
    countBadge.textContent = `${visibleNodes.length}/${total} Nodes`;
  }
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

// Thuật toán Vật Lý Lực Đẩy - Hút - Hướng Tâm Phân Cụm
function applyObsidianForces() {
  const nodes = graphState.nodes;
  const edges = graphState.edges;
  const nLen = nodes.length;
  const cx = graphState.width / 2;
  const cy = graphState.height / 2;
  const hqNode = nodes.find(n => n.type === 'hq');

  // 1. Lực đẩy Coulomb giữa các node & Vành đai từ trường HQ
  for (let i = 0; i < nLen; i++) {
    const n1 = nodes[i];
    if (isNodeHidden(n1)) continue;

    // Vành đai từ trường HQ (Đẩy êm ái mọi node ra khỏi bán kính 200px của HQ)
    if (n1.type !== 'hq' && hqNode) {
      const hdx = n1.x - hqNode.x;
      const hdy = n1.y - hqNode.y;
      const hdist = Math.hypot(hdx, hdy) || 1;
      const hqSafeRadius = 200;
      if (hdist < hqSafeRadius) {
        const repel = ((hqSafeRadius - hdist) / hqSafeRadius) * 5.0;
        n1.vx += (hdx / hdist) * repel;
        n1.vy += (hdy / hdist) * repel;
      }
    }

    for (let j = i + 1; j < nLen; j++) {
      const n2 = nodes[j];
      if (isNodeHidden(n2)) continue;

      const dx = n2.x - n1.x;
      const dy = n2.y - n1.y;
      const distSq = dx * dx + dy * dy + 4;
      const dist = Math.sqrt(distSq);

      // Bán kính đẩy tối thiểu
      if (dist < 260) {
        const force = 9500 / distSq;
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

    // 2. Lực hút về Đảo Centroid của từng cụm
    if (n1.targetCluster && n1 !== graphState.dragNode && n1.type !== 'hq') {
      const cdx = n1.targetCluster.x - n1.x;
      const cdy = n1.targetCluster.y - n1.y;
      n1.vx += cdx * 0.035;
      n1.vy += cdy * 0.035;
    }
  }

  // 3. Lực đàn hồi thích ứng theo phân cấp liên kết
  edges.forEach(e => {
    const fromNode = nodes.find(n => n.id === e.from);
    const toNode = nodes.find(n => n.id === e.to);
    if (!fromNode || !toNode || isNodeHidden(fromNode) || isNodeHidden(toNode)) return;

    let targetDist = 140;
    let strength = 0.03;

    if (fromNode.type === 'hq' || toNode.type === 'hq') {
      targetDist = 240; // HQ -> Kênh
      strength = 0.02;
    } else if (e.category === 'deal_link' || toNode.type === 'opportunity') {
      targetDist = 65;  // Contact -> Deal
      strength = 0.07;
    } else if (e.category === 'group_link') {
      targetDist = 150; // Kênh -> Contact
      strength = 0.025;
    }

    const dx = toNode.x - fromNode.x;
    const dy = toNode.y - fromNode.y;
    const dist = Math.sqrt(dx * dx + dy * dy) || 1;
    const delta = dist - targetDist;
    const force = delta * strength;

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

  // 4. Cập nhật vị trí và giảm chấn
  const maxVel = 7.0;
  nodes.forEach(n => {
    if (n.type === 'hq') {
      n.x = cx;
      n.y = cy;
      n.vx = 0;
      n.vy = 0;
      return;
    }
    if (n === graphState.dragNode) return;

    const speed = Math.hypot(n.vx, n.vy);
    if (speed > maxVel) {
      n.vx = (n.vx / speed) * maxVel;
      n.vy = (n.vy / speed) * maxVel;
    }

    n.vx *= 0.82;
    n.vy *= 0.82;
    n.x += n.vx;
    n.y += n.vy;

    const pad = 40;
    if (n.x < pad) n.vx += (pad - n.x) * 0.05;
    if (n.x > graphState.width - pad) n.vx -= (n.x - (graphState.width - pad)) * 0.05;
    if (n.y < pad) n.vy += (pad - n.y) * 0.05;
    if (n.y > graphState.height - pad) n.vy -= (n.y - (graphState.height - pad)) * 0.05;
  });
}

// ----------------------------------------------------
// HÀM VẼ GRAPH CANVAS HIGH-CONTRAST SÁNG RÕ & CHUẨN MỰC
// ----------------------------------------------------
function drawObsidianGraph() {
  const ctx = graphState.ctx;
  if (!ctx) return;

  const w = graphState.width;
  const h = graphState.height;

  ctx.save();
  ctx.clearRect(0, 0, w, h);

  // 1. BACKGROUND GRADIENT SÁNG RÕ (Không còn đen ngòm mịt mù!)
  if (graphState.canvasTheme === 'navy_bright') {
    const grad = ctx.createRadialGradient(w / 2, h / 2, 40, w / 2, h / 2, Math.max(w, h) * 0.75);
    grad.addColorStop(0, '#16233b'); // Tâm xanh Slate Navy thanh nhã, sáng rõ
    grad.addColorStop(0.65, '#0d1527');
    grad.addColorStop(1, '#070b14'); // Rìa sẫm sang trọng
    ctx.fillStyle = grad;
  } else {
    ctx.fillStyle = '#06090f'; // Obsidian Void Dark
  }
  ctx.fillRect(0, 0, w, h);

  // Camera Pan & Zoom Transform
  ctx.translate(w / 2 + graphState.panX, h / 2 + graphState.panY);
  ctx.scale(graphState.scale, graphState.scale);
  ctx.translate(-w / 2, -h / 2);

  // 2. LƯỚI CHẤM OBSIDIAN DOT GRID SẮC NÉT
  ctx.fillStyle = 'rgba(255, 255, 255, 0.12)';
  const step = 36;
  const startX = Math.floor((-w * 0.6) / step) * step;
  const endX = Math.ceil((w * 1.6) / step) * step;
  const startY = Math.floor((-h * 0.6) / step) * step;
  const endY = Math.ceil((h * 1.6) / step) * step;
  for (let x = startX; x <= endX; x += step) {
    for (let y = startY; y <= endY; y += step) {
      ctx.fillRect(x, y, 1.4, 1.4);
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

  // 3. VẼ ĐƯỜNG LIÊN KẾT (EDGES) TƯƠNG PHẢN CAO, RÕ RÀNG
  graphState.edges.forEach(e => {
    const fromNode = graphState.nodes.find(n => n.id === e.from);
    const toNode = graphState.nodes.find(n => n.id === e.to);
    if (!fromNode || !toNode || isNodeHidden(fromNode) || isNodeHidden(toNode)) return;

    const isConnected = isFocusMode && (fromNode.id === activeFocus.id || toNode.id === activeFocus.id);

    ctx.save();
    if (isFocusMode && !isConnected) {
      ctx.globalAlpha = 0.28; // Làm mờ vừa phải (vẫn thấy rõ mạng lưới!)
    }

    ctx.beginPath();
    ctx.moveTo(fromNode.x, fromNode.y);
    ctx.lineTo(toNode.x, toNode.y);

    if (isConnected) {
      ctx.strokeStyle = '#38bdf8'; // Sáng rực rỡ khi kết nối
      ctx.lineWidth = 2.8;
      ctx.shadowColor = '#38bdf8';
      ctx.shadowBlur = 10;
    } else {
      // Màu sắc tươi sáng, tương phản cao
      if (e.category === 'deal_link') {
        ctx.strokeStyle = 'rgba(192, 132, 252, 0.75)'; // Tím lavender sáng
        ctx.lineWidth = 1.4;
      } else if (e.category === 'channel_link') {
        ctx.strokeStyle = 'rgba(129, 140, 248, 0.7)';  // Tím xanh HQ
        ctx.lineWidth = 2.0;
      } else if (fromNode.channel === 'whatsapp' || toNode.channel === 'whatsapp') {
        ctx.strokeStyle = 'rgba(52, 211, 153, 0.65)';  // Xanh lá WhatsApp
        ctx.lineWidth = 1.8;
      } else {
        ctx.strokeStyle = 'rgba(56, 189, 248, 0.65)';  // Xanh Zalo
        ctx.lineWidth = 1.8;
      }
    }
    ctx.stroke();

    // Hạt pulse chạy dọc đường nếu là edge đang kết nối
    if (isConnected) {
      const pulseOffset = ((graphState.pulseTick * 0.02) % 1);
      const px = fromNode.x + (toNode.x - fromNode.x) * pulseOffset;
      const py = fromNode.y + (toNode.y - fromNode.y) * pulseOffset;
      ctx.beginPath();
      ctx.arc(px, py, 3.2, 0, Math.PI * 2);
      ctx.fillStyle = '#ffffff';
      ctx.shadowColor = '#ffffff';
      ctx.shadowBlur = 6;
      ctx.fill();
    }

    ctx.restore();
  });

  // 4. VẼ CÁC HẠT NODE (NODES) SẮC NÉT, RỰC RỠ NEON
  graphState.nodes.forEach(n => {
    if (isNodeHidden(n)) return;

    const isFocused = isFocusMode && n.id === activeFocus.id;
    const isNeighbor = isFocusMode && connectedNodeIds.has(n.id);
    const isDimmed = isFocusMode && !isNeighbor;

    ctx.save();
    if (isDimmed) {
      ctx.globalAlpha = 0.32; // Không bị biến mất đen kịt
    }

    const baseSize = (n.type === 'hq' ? 34 : (n.type === 'group' ? 26 : (n.type === 'opportunity' ? 16 : 22)));
    const r = baseSize * (isFocused ? 1.25 : 1.0);

    // Xác định màu sắc thân đệm và viền Neon
    let strokeColor = n.color || '#818cf8';
    let fillColor = '#0f172a';
    if (n.type === 'hq') {
      strokeColor = '#818cf8';
      fillColor = '#2b2756';
    } else if (n.type === 'group') {
      strokeColor = n.channel === 'whatsapp' ? '#10b981' : '#0ea5e9';
      fillColor = n.channel === 'whatsapp' ? '#0b3323' : '#092b3d';
    } else if (n.category === 'hot') {
      strokeColor = '#f43f5e';
      fillColor = '#3b1018';
    } else if (n.category === 'warm') {
      strokeColor = '#f59e0b';
      fillColor = '#3b2a07';
    } else if (n.category === 'cold') {
      strokeColor = '#94a3b8';
      fillColor = '#1e2430';
    } else if (n.category === 'deal') {
      strokeColor = '#c084fc';
      fillColor = '#2d133d';
    }

    // Hào quang Neon rực rỡ xung quanh
    ctx.beginPath();
    ctx.arc(n.x, n.y, r + (isFocused ? 12 : 5), 0, Math.PI * 2);
    ctx.fillStyle = strokeColor;
    ctx.globalAlpha = isDimmed ? 0.08 : (isFocused ? 0.45 : 0.22);
    ctx.fill();

    // Thân hạt Node (Màu đệm sang trọng)
    ctx.globalAlpha = isDimmed ? 0.32 : 1.0;
    ctx.beginPath();
    ctx.arc(n.x, n.y, r, 0, Math.PI * 2);
    ctx.fillStyle = fillColor;
    ctx.fill();

    // Viền Neon sắc nét
    ctx.strokeStyle = strokeColor;
    ctx.lineWidth = isFocused ? 3.0 : 2.2;
    ctx.shadowColor = strokeColor;
    ctx.shadowBlur = isFocused ? 14 : 6;
    ctx.stroke();

    // Icon / Ký tự bên trong hạt to rõ ràng
    ctx.font = `bold ${Math.round(r * 0.85)}px sans-serif`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillStyle = '#ffffff';

    if (n.type === 'hq') {
      ctx.fillText('👑', n.x, n.y);
    } else if (n.type === 'group') {
      ctx.fillText(n.channel === 'whatsapp' ? '📱' : '💬', n.x, n.y);
    } else if (n.type === 'opportunity') {
      ctx.fillText('💼', n.x, n.y);
    } else {
      ctx.fillText((n.label || 'U').slice(0, 2).toUpperCase(), n.x, n.y);
    }

    // 5. NHÃN CHỮ DARK PILL TAG TRẮNG SÁNG RÕ NÉT (HIGH CONTRAST)
    if (graphState.showLabels || isFocused || isNeighbor) {
      const text = n.label || '';
      ctx.font = isFocused ? '600 12px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif' : '600 11px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
      
      const metrics = ctx.measureText(text);
      const padX = 8;
      const padY = 4;
      const bgW = metrics.width + padX * 2;
      const bgH = 19;
      const bgX = n.x - bgW / 2;
      const bgY = n.y + r + 6;

      // Nền Pill bo góc đen sâu tương phản cao
      ctx.beginPath();
      const radius = 5;
      ctx.fillStyle = isFocused ? 'rgba(7, 11, 20, 0.98)' : 'rgba(10, 15, 29, 0.94)';
      ctx.roundRect ? ctx.roundRect(bgX, bgY, bgW, bgH, radius) : ctx.rect(bgX, bgY, bgW, bgH);
      ctx.fill();

      // Viền Pill sắc nét
      ctx.strokeStyle = isFocused ? '#38bdf8' : 'rgba(255, 255, 255, 0.28)';
      ctx.lineWidth = isFocused ? 1.5 : 1.0;
      ctx.shadowColor = 'transparent';
      ctx.stroke();

      // Chữ Trắng Tuyết Rõ Nét
      ctx.fillStyle = '#ffffff';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(text, n.x, bgY + bgH / 2);

      // Nhãn phụ: Điểm nhiệt độ hoặc Giá trị Deal nổi bật
      if (n.type === 'contact' && n.heat !== undefined) {
        const sub = `${n.heat}° · Cấp ${n.autonomy_level||1}`;
        ctx.font = '700 10px sans-serif';
        ctx.fillStyle = n.heat >= 80 ? '#fb7185' : (n.heat >= 50 ? '#fbbf24' : '#cbd5e1');
        ctx.fillText(sub, n.x, bgY + bgH + 8);
      } else if (n.type === 'opportunity' && n.value) {
        ctx.font = '700 10px sans-serif';
        ctx.fillStyle = '#c084fc';
        const valStr = n.value >= 1e9 ? `${(n.value/1e9).toFixed(1)} Tỷ ₫` : `${(n.value/1e6).toFixed(0)} Tr ₫`;
        ctx.fillText(valStr, n.x, bgY + bgH + 8);
      }
    }

    ctx.restore();
  });

  ctx.restore();
}

function"""

# Tìm đoạn code cũ từ findNodeAt đến hết drawObsidianGraph
idx_start = content.find("function findNodeAt(x, y) {")
idx_end = content.find("function zoomGraphCanvas(factor) {")

if idx_start != -1 and idx_end != -1:
    content = content[:idx_start] + replacement_code + " " + content[idx_end:]
    print("✓ Đã thay thế thành công hàm vẽ drawObsidianGraph và bộ lọc giảm nhiễu!")
else:
    print(f"! Không tìm thấy vị trí thay thế: idx_start={idx_start}, idx_end={idx_end}")

with open(html_path, "w", encoding="utf-8") as f:
    f.write(content)
