import re

html_path = "heo_harness/plugins/ui_dashboard/dashboard.html"

with open(html_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Cập nhật khởi tạo tọa độ dàn trải khoa học và scale ban đầu 0.85
old_init_coords = """    // Thiết lập tọa độ Centroid Phân Cụm Obsidian (Cluster Centroids)
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

new_init_coords = """    // Thiết lập Tọa Độ Dàn Trải Rộng Rãi (Wide Spacing Coordinates)
    graphState.scale = 0.82; // Zoom tỷ lệ vàng giúp bao quát toàn màn hình thoáng đãng

    // 1. Phân bố vị trí cho Kênh & Nhóm (Cánh Tây, bán kính 290px, giãn cách 120px)
    const channelPositions = {
      'grp-zalo-telecom': { x: cx - 260, y: cy - 160 },
      'grp-zalo-crm':     { x: cx - 310, y: cy - 50 },
      'grp-wa-logitech':  { x: cx - 310, y: cy + 60 },
      'grp-wa-fashion':   { x: cx - 260, y: cy + 170 }
    };

    // 2. Phân bố vị trí Khách Hàng Nóng VIP (Cánh Đông-Bắc, bán kính 380-420px, giãn cách 140px)
    const hotPositions = {
      'cnt-CNT-005': { x: cx + 290, y: cy - 250 }, // Chị Thảo (Viễn Thông)
      'cnt-CNT-007': { x: cx + 390, y: cy - 150 }, // Giám Đốc CNTT Viettel
      'cnt-CNT-001': { x: cx + 430, y: cy - 20 },  // Chị Mai Phương
      'cnt-CNT-002': { x: cx + 390, y: cy + 110 }  // Anh Hoàng Bách
    };

    // 3. Phân bố vị trí Đối Tác Tiềm Năng (Cánh Đông-Nam, bán kính 380px, giãn cách 130px)
    const warmPositions = {
      'cnt-CNT-006': { x: cx + 300, y: cy + 240 }, // Anh Minh (Kafi)
      'cnt-CNT-008': { x: cx + 180, y: cy + 320 }, // Tập Đoàn Tân Á
      'cnt-CNT-003': { x: cx + 50,  y: cy + 350 }  // Trần Thu Hà
    };

    // 4. Phân bố vị trí Khách Im Lặng (Cánh Tây-Nam, bán kính 340px, giãn cách 130px)
    const coldPositions = {
      'cnt-CNT-004': { x: cx - 120, y: cy + 310 }, // Nguyễn Đức Trí
      'cnt-CNT-009': { x: cx - 230, y: cy + 250 }  // Phạm Văn Long
    };

    // Gán vị trí cho từng node
    rawNodes.forEach(n => {
      n.vx = 0;
      n.vy = 0;

      if (n.type === 'hq') {
        n.x = cx;
        n.y = cy;
        n.targetCluster = { x: cx, y: cy };
      } else if (channelPositions[n.id]) {
        n.x = channelPositions[n.id].x;
        n.y = channelPositions[n.id].y;
        n.targetCluster = { ...channelPositions[n.id] };
      } else if (hotPositions[n.id]) {
        n.x = hotPositions[n.id].x;
        n.y = hotPositions[n.id].y;
        n.targetCluster = { ...hotPositions[n.id] };
      } else if (warmPositions[n.id]) {
        n.x = warmPositions[n.id].x;
        n.y = warmPositions[n.id].y;
        n.targetCluster = { ...warmPositions[n.id] };
      } else if (coldPositions[n.id]) {
        n.x = coldPositions[n.id].x;
        n.y = coldPositions[n.id].y;
        n.targetCluster = { ...coldPositions[n.id] };
      } else {
        // Fallback ngẫu nhiên xa
        n.x = cx + (Math.random() - 0.5) * 500;
        n.y = cy + (Math.random() - 0.5) * 400;
        n.targetCluster = { x: n.x, y: n.y };
      }
    });

    // 5. Bố trí các Deals vệ tinh tỏa đều quanh Contact chủ quản (Bán kính 110px)
    const contactDealsMap = {};
    rawEdges.forEach(e => {
      if (e.category === 'deal_link') {
        if (!contactDealsMap[e.from]) contactDealsMap[e.from] = [];
        contactDealsMap[e.from].push(e.to);
      }
    });

    Object.entries(contactDealsMap).forEach(([contactId, dealIds]) => {
      const parentNode = rawNodes.find(pn => pn.id === contactId);
      if (!parentNode) return;

      const count = dealIds.length;
      dealIds.forEach((dId, dIdx) => {
        const dealNode = rawNodes.find(dn => dn.id === dId);
        if (!dealNode) return;

        // Góc tỏa hướng ra phía ngoài tâm HQ
        const baseAngle = Math.atan2(parentNode.y - cy, parentNode.x - cx);
        const spreadAngle = (dIdx - (count - 1) / 2) * 0.75;
        const finalAngle = baseAngle + spreadAngle;
        const dealDistance = 110; // Khoảng cách 110px thoáng đãng

        dealNode.x = parentNode.x + Math.cos(finalAngle) * dealDistance;
        dealNode.y = parentNode.y + Math.sin(finalAngle) * dealDistance;
        dealNode.targetCluster = { x: dealNode.x, y: dealNode.y };
      });
    });"""

if old_init_coords in content:
    content = content.replace(old_init_coords, new_init_coords)
    print("✓ Đã cập nhật xong tọa độ phân bố Wide Spacing!")
else:
    print("! Không tìm thấy old_init_coords")

# 2. Cập nhật hàm applyObsidianForces với thuật toán Lực Đẩy Chống Đè Tuyến Tính (Linear Anti-Collision)
old_forces = """// Thuật toán Vật Lý Lực Đẩy - Hút - Hướng Tâm Phân Cụm
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
}"""

new_forces = """// Thuật toán Vật Lý Giãn Cách Rộng & Chống Đè Tuyến Tính (Wide Spacing Physics)
function applyObsidianForces() {
  const nodes = graphState.nodes;
  const edges = graphState.edges;
  const nLen = nodes.length;
  const cx = graphState.width / 2;
  const cy = graphState.height / 2;
  const hqNode = nodes.find(n => n.type === 'hq');

  // 1. Lực Chống Đè Cứng Tuyến Tính (Linear Anti-Collision) & Vành đai từ trường HQ
  for (let i = 0; i < nLen; i++) {
    const n1 = nodes[i];
    if (isNodeHidden(n1)) continue;

    // Vành đai từ trường HQ: Đẩy mọi node ra khỏi bán kính 220px của HQ
    if (n1.type !== 'hq' && hqNode) {
      const hdx = n1.x - hqNode.x;
      const hdy = n1.y - hqNode.y;
      const hdist = Math.hypot(hdx, hdy) || 1;
      const hqSafeRadius = 220;
      if (hdist < hqSafeRadius) {
        const repel = ((hqSafeRadius - hdist) / hqSafeRadius) * 4.0;
        n1.vx += (hdx / hdist) * repel;
        n1.vy += (hdy / hdist) * repel;
      }
    }

    for (let j = i + 1; j < nLen; j++) {
      const n2 = nodes[j];
      if (isNodeHidden(n2)) continue;

      const dx = n2.x - n1.x;
      const dy = n2.y - n1.y;
      const dist = Math.hypot(dx, dy) || 1;

      // Khoảng cách an toàn tối thiểu (Minimum Safe Distance):
      // - Contact với Contact: Tối thiểu 165px (hoàn toàn không chạm nhãn chữ)
      // - Contact với Deal: Tối thiểu 115px
      // - Deal với Deal: Tối thiểu 95px
      // - Group với Group: Tối thiểu 140px
      let minSafeDist = 165;
      if (n1.type === 'opportunity' && n2.type === 'opportunity') {
        minSafeDist = 95;
      } else if (n1.type === 'opportunity' || n2.type === 'opportunity') {
        minSafeDist = 115;
      } else if (n1.type === 'group' && n2.type === 'group') {
        minSafeDist = 140;
      }

      if (dist < minSafeDist) {
        const overlap = minSafeDist - dist;
        // Lực đẩy trực tiếp mạnh mẽ tỉ lệ với độ lấn
        const pushForce = (overlap / minSafeDist) * 3.8;
        const fx = (dx / dist) * pushForce;
        const fy = (dy / dist) * pushForce;

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

    // 2. Lực neo mềm giữ vùng định hướng (Soft Anchor - Lực rất nhẹ 0.008 để không bị co cụm)
    if (n1.targetCluster && n1 !== graphState.dragNode && n1.type !== 'hq') {
      const cdx = n1.targetCluster.x - n1.x;
      const cdy = n1.targetCluster.y - n1.y;
      n1.vx += cdx * 0.008;
      n1.vy += cdy * 0.008;
    }
  }

  // 3. Lực đàn hồi thích ứng theo phân cấp liên kết (Spring Forces)
  edges.forEach(e => {
    const fromNode = nodes.find(n => n.id === e.from);
    const toNode = nodes.find(n => n.id === e.to);
    if (!fromNode || !toNode || isNodeHidden(fromNode) || isNodeHidden(toNode)) return;

    let targetDist = 180;
    let strength = 0.02;

    if (fromNode.type === 'hq' || toNode.type === 'hq') {
      targetDist = 290; // HQ -> Kênh giãn 290px
      strength = 0.015;
    } else if (e.category === 'deal_link' || toNode.type === 'opportunity') {
      targetDist = 110; // Contact -> Deal giãn 110px (thay vì 65px chật chội)
      strength = 0.045;
    } else if (e.category === 'group_link') {
      targetDist = 210; // Kênh -> Contact giãn 210px
      strength = 0.018;
    }

    const dx = toNode.x - fromNode.x;
    const dy = toNode.y - fromNode.y;
    const dist = Math.hypot(dx, dy) || 1;
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

  // 4. Cập nhật vị trí và giảm chấn ma sát cao (High Damping = 0.78) giúp đồ thị đứng yên vững vàng
  const maxVel = 5.0;
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

    n.vx *= 0.78;
    n.vy *= 0.78;
    n.x += n.vx;
    n.y += n.vy;

    // Giữ node trong khung nhìn
    const pad = 35;
    if (n.x < pad) n.vx += (pad - n.x) * 0.08;
    if (n.x > graphState.width - pad) n.vx -= (n.x - (graphState.width - pad)) * 0.08;
    if (n.y < pad) n.vy += (pad - n.y) * 0.08;
    if (n.y > graphState.height - pad) n.vy -= (n.y - (graphState.height - pad)) * 0.08;
  });
}"""

if old_forces in content:
    content = content.replace(old_forces, new_forces)
    print("✓ Đã cập nhật applyObsidianForces với thuật toán Wide Spacing Physics!")
else:
    print("! Không tìm thấy old_forces")

with open(html_path, "w", encoding="utf-8") as f:
    f.write(content)
