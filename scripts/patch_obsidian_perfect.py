import re

html_path = "heo_harness/plugins/ui_dashboard/dashboard.html"

with open(html_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Cập nhật khởi tạo centroid và gắn deal vào contact chủ quản
old_init_centroid = """    // Thiết lập tọa độ Centroid Phân Cụm Obsidian (Cluster Centroids)
    const clusterCentroids = {
      hq:      { x: cx,       y: cy },
      channel: { x: cx - 350, y: cy - 140 }, // Cụm Tây Bắc: Kênh & Nhóm
      hot:     { x: cx + 330, y: cy - 150 }, // Cụm Đông Bắc: Khách Nóng VIP
      warm:    { x: cx + 330, y: cy + 180 }, // Cụm Đông Nam: Đối Tác Ấm
      cold:    { x: cx - 330, y: cy + 180 }, // Cụm Tây Nam: Khách Im Lặng
      deal:    { x: cx + 450, y: cy - 20 }   // Cụm Đông: Deals Cơ Hội
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
    });"""

new_init_centroid = """    // Thiết lập tọa độ Centroid Phân Cụm Obsidian (Cluster Centroids)
    const clusterCentroids = {
      hq:      { x: cx,       y: cy },
      channel: { x: cx - 340, y: cy - 120 }, // Cụm Tây Bắc: Kênh & Nhóm
      hot:     { x: cx + 320, y: cy - 140 }, // Cụm Đông Bắc: Khách Nóng VIP
      warm:    { x: cx + 320, y: cy + 160 }, // Cụm Đông Nam: Đối Tác Ấm
      cold:    { x: cx - 320, y: cy + 160 }, // Cụm Tây Nam: Khách Im Lặng
      deal:    { x: cx + 380, y: cy }        // Cụm Đông: Deals
    };

    // Khởi tạo vị trí ban đầu theo từng cụm
    rawNodes.forEach((n, idx) => {
      const cat = n.category || 'warm';
      let c = clusterCentroids[cat] || clusterCentroids.warm;
      
      // Nếu là deal, ưu tiên gắn centroid theo Contact chủ quản
      if (cat === 'deal') {
        const parentEdge = rawEdges.find(e => e.to === n.id);
        if (parentEdge) {
          const parent = rawNodes.find(pn => pn.id === parentEdge.from);
          if (parent && clusterCentroids[parent.category]) {
            c = clusterCentroids[parent.category];
          }
        }
      }

      const angle = (idx * 1.25) % (Math.PI * 2);
      const r = (idx % 4) * 25 + 20;

      n.x = c.x + Math.cos(angle) * r;
      n.y = c.y + Math.sin(angle) * r;
      n.vx = 0;
      n.vy = 0;
      n.targetCluster = c;
    });"""

if old_init_centroid in content:
    content = content.replace(old_init_centroid, new_init_centroid)
    print("✓ Đã cập nhật xong init centroids")
else:
    print("! Không tìm thấy old_init_centroid chính xác, kiểm tra lại")

# 2. Cập nhật toggleObsidianCategory để lọc thông minh
old_toggle = """function toggleObsidianCategory(catKey) {
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
}"""

new_toggle = """function toggleObsidianCategory(catKey) {
  if (catKey === 'all') {
    Object.keys(graphState.activeCategories).forEach(k => {
      graphState.activeCategories[k] = true;
    });
  } else {
    // Chế độ Solo Filter: Bấm vào 1 cụm sẽ chỉ bật cụm đó (và HQ), trừ khi đang solo thì bật lại tất cả
    const isCurrentlySolo = Object.entries(graphState.activeCategories).filter(([k, v]) => v && k !== 'hq').length === 1 && graphState.activeCategories[catKey];
    if (isCurrentlySolo) {
      Object.keys(graphState.activeCategories).forEach(k => {
        graphState.activeCategories[k] = true;
      });
    } else {
      Object.keys(graphState.activeCategories).forEach(k => {
        graphState.activeCategories[k] = (k === 'hq' || k === catKey);
      });
    }
  }

  // Cập nhật trạng thái nút UI
  const allOn = ['channel', 'hot', 'warm', 'cold', 'deal'].every(k => graphState.activeCategories[k]);
  ['all', 'channel', 'hot', 'warm', 'cold', 'deal'].forEach(k => {
    const btn = document.getElementById('grp-toggle-' + k);
    if (btn) {
      const active = k === 'all' ? allOn : graphState.activeCategories[k];
      btn.style.opacity = active ? '1' : '0.35';
      btn.style.boxShadow = active ? '0 0 8px rgba(255,255,255,0.15)' : 'none';
    }
  });

  const statBadge = document.getElementById('graph-stat-badge');
  if (statBadge && graphState.nodes) {
    const visibleCount = graphState.nodes.filter(n => !isNodeHidden(n)).length;
    statBadge.innerHTML = `<b style="color:#38bdf8">${visibleCount}/${graphState.nodes.length} Nodes</b> · <b>Obsidian Focus</b>`;
  }
}"""

if old_toggle in content:
    content = content.replace(old_toggle, new_toggle)
    print("✓ Đã cập nhật xong toggle category")
else:
    print("! Không tìm thấy old_toggle")

# 3. Cập nhật drawObsidianGraph: Dot Grid sắc sảo & Nhãn Pill sang trọng
old_draw_labels = """    // Nhãn văn bản (Labels): Chỉ hiển thị nếu showLabels=true hoặc là node đang focus
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
    }"""

new_draw_labels = """    // Nhãn văn bản (Labels) phong cách Obsidian Dark Pill Tag
    if (graphState.showLabels || isFocused || isNeighbor) {
      const text = n.label || '';
      ctx.font = isFocused ? '600 11.5px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif' : '500 10.5px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
      
      const metrics = ctx.measureText(text);
      const padX = 7;
      const padY = 3;
      const bgW = metrics.width + padX * 2;
      const bgH = 17;
      const bgX = n.x - bgW / 2;
      const bgY = n.y + r + 6;

      // Nền Pill bo góc mờ tinh tế
      ctx.beginPath();
      const radius = 4;
      ctx.fillStyle = isFocused ? 'rgba(15, 23, 42, 0.95)' : 'rgba(15, 23, 42, 0.8)';
      ctx.roundRect ? ctx.roundRect(bgX, bgY, bgW, bgH, radius) : ctx.rect(bgX, bgY, bgW, bgH);
      ctx.fill();

      if (isFocused || isNeighbor) {
        ctx.strokeStyle = isFocused ? (n.color || '#38bdf8') : 'rgba(255, 255, 255, 0.15)';
        ctx.lineWidth = 1;
        ctx.stroke();
      }

      ctx.fillStyle = isFocused ? '#ffffff' : (isNeighbor ? '#f1f5f9' : 'rgba(226, 232, 240, 0.85)');
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(text, n.x, bgY + bgH / 2);

      // Điểm phụ (Nhiệt độ / Giá trị deal)
      if (n.type === 'contact' && n.heat !== undefined) {
        const sub = `${n.heat}° · Cấp ${n.autonomy_level||1}`;
        ctx.font = '500 9.5px sans-serif';
        ctx.fillStyle = n.heat >= 80 ? '#fb7185' : (n.heat >= 50 ? '#fbbf24' : '#94a3b8');
        ctx.fillText(sub, n.x, bgY + bgH + 8);
      } else if (n.type === 'opportunity' && n.value) {
        ctx.font = '500 9.5px sans-serif';
        ctx.fillStyle = '#c084fc';
        const valStr = n.value >= 1e9 ? `${(n.value/1e9).toFixed(1)} Tỷ ₫` : `${(n.value/1e6).toFixed(0)} Tr ₫`;
        ctx.fillText(valStr, n.x, bgY + bgH + 8);
      }
    }"""

if old_draw_labels in content:
    content = content.replace(old_draw_labels, new_draw_labels)
    print("✓ Đã cập nhật xong nhãn Dark Pill Tag")
else:
    print("! Không tìm thấy old_draw_labels")

with open(html_path, "w", encoding="utf-8") as f:
    f.write(content)

print("✓ Hoàn thành nâng cấp giao diện Obsidian!")
