import re

html_path = "heo_harness/plugins/ui_dashboard/dashboard.html"

with open(html_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Tối ưu hóa hàm applyObsidianForces với Từ Trường HQ & Lò xo Phân Tầng
old_forces = """// Thuật toán Vật Lý Lực Đẩy - Hút - Hướng Tâm Phân Cụm (Obsidian Force Physics)
function applyObsidianForces() {
  const nodes = graphState.nodes;
  const edges = graphState.edges;
  const nLen = nodes.length;
  const cx = graphState.width / 2;
  const cy = graphState.height / 2;

  // 1. Lực đẩy Coulomb mạnh mẽ giữa các node (Ngăn chặn triệt để chồng đè)
  for (let i = 0; i < nLen; i++) {
    const n1 = nodes[i];
    if (isNodeHidden(n1)) continue;

    for (let j = i + 1; j < nLen; j++) {
      const n2 = nodes[j];
      if (isNodeHidden(n2)) continue;

      const dx = n2.x - n1.x;
      const dy = n2.y - n1.y;
      const distSq = dx * dx + dy * dy + 4;
      const dist = Math.sqrt(distSq);

      // Bán kính đẩy tối thiểu
      const minDist = (n1.size || 16) + (n2.size || 16) + 40;
      if (dist < 320) {
        const force = 12000 / distSq;
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

    // 2. Lực hút về Đảo Centroid của từng cụm (Cluster Centroid Attraction)
    if (n1.targetCluster && n1 !== graphState.dragNode && n1.type !== 'hq') {
      const cdx = n1.targetCluster.x - n1.x;
      const cdy = n1.targetCluster.y - n1.y;
      n1.vx += cdx * 0.028;
      n1.vy += cdy * 0.028;
    }
  }

  // 3. Lực đàn hồi thích ứng theo phân cấp liên kết (Hierarchical Spring Physics)
  edges.forEach(e => {
    const fromNode = nodes.find(n => n.id === e.from);
    const toNode = nodes.find(n => n.id === e.to);
    if (!fromNode || !toNode || isNodeHidden(fromNode) || isNodeHidden(toNode)) return;

    let targetDist = 130;
    let strength = 0.035;

    if (fromNode.type === 'hq' || toNode.type === 'hq') {
      targetDist = 290; // Giữ khoảng cách lớn giữa HQ và các cụm để không bị co cụm!
      strength = 0.009;
    } else if (e.category === 'deal_link' || toNode.type === 'opportunity') {
      targetDist = 75;  // Deals quay gần xung quanh liên hệ của mình
      strength = 0.055;
    }

    const dx = toNode.x - fromNode.x;
    const dy = toNode.y - fromNode.y;
    const dist = Math.sqrt(dx * dx + dy * dy) || 1;
    const displacement = dist - targetDist;
    const springForce = displacement * strength;

    const fx = (dx / dist) * springForce;
    const fy = (dy / dist) * springForce;

    if (fromNode !== graphState.dragNode && fromNode.type !== 'hq') {
      fromNode.vx += fx;
      fromNode.vy += fy;
    }
    if (toNode !== graphState.dragNode && toNode.type !== 'hq') {
      toNode.vx -= fx;
      toNode.vy -= fy;
    }
  });

  // 4. Cập nhật vị trí và ma sát giảm chấn (Velocity Damping)
  const friction = 0.82;
  const maxVelocity = 8.0;

  nodes.forEach(n => {
    if (n.type === 'hq') {
      // Khóa vị trí HQ Sếp Ryan bất biến tại tâm vũ trụ Obsidian
      n.x = cx;
      n.y = cy;
      n.vx = 0;
      n.vy = 0;
      return;
    }

    if (n === graphState.dragNode) return;

    // Giới hạn vận tốc cực đại
    const v = Math.sqrt(n.vx * n.vx + n.vy * n.vy);
    if (v > maxVelocity) {
      n.vx = (n.vx / v) * maxVelocity;
      n.vy = (n.vy / v) * maxVelocity;
    }

    n.x += n.vx;
    n.y += n.vy;
    n.vx *= friction;
    n.vy *= friction;

    // Ranh giới biên mềm giữ node trong khung nhìn
    const pad = 50;
    if (n.x < pad) n.vx += (pad - n.x) * 0.05;
    if (n.x > graphState.width - pad) n.vx -= (n.x - (graphState.width - pad)) * 0.05;
    if (n.y < pad) n.vy += (pad - n.y) * 0.05;
    if (n.y > graphState.height - pad) n.vy -= (n.y - (graphState.height - pad)) * 0.05;
  });
}"""

new_forces = """// Thuật toán Vật Lý Lực Đẩy - Hút - Hướng Tâm Phân Cụm (Obsidian Force Physics V3)
function applyObsidianForces() {
  const nodes = graphState.nodes;
  const edges = graphState.edges;
  const nLen = nodes.length;
  const cx = graphState.width / 2;
  const cy = graphState.height / 2;
  const hqNode = nodes.find(n => n.type === 'hq');

  // 1. Lực đẩy Coulomb giữa các node & Vành đai bảo vệ HQ
  for (let i = 0; i < nLen; i++) {
    const n1 = nodes[i];
    if (isNodeHidden(n1)) continue;

    // Vành đai đẩy từ trường HQ (Ngăn node khác tiến vào bán kính < 190px quanh HQ)
    if (n1.type !== 'hq' && hqNode) {
      const hdx = n1.x - hqNode.x;
      const hdy = n1.y - hqNode.y;
      const hdist = Math.hypot(hdx, hdy) || 1;
      const hqSafeRadius = 190;
      if (hdist < hqSafeRadius) {
        const repelForce = ((hqSafeRadius - hdist) / hqSafeRadius) * 4.5;
        n1.vx += (hdx / hdist) * repelForce;
        n1.vy += (hdy / hdist) * repelForce;
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
        const force = 9000 / distSq;
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

    // 2. Lực hút về Đảo Centroid của từng cụm (Cluster Centroid Attraction)
    if (n1.targetCluster && n1 !== graphState.dragNode && n1.type !== 'hq') {
      const cdx = n1.targetCluster.x - n1.x;
      const cdy = n1.targetCluster.y - n1.y;
      n1.vx += cdx * 0.032;
      n1.vy += cdy * 0.032;
    }
  }

  // 3. Lực đàn hồi thích ứng theo phân cấp liên kết (Hierarchical Spring Physics)
  edges.forEach(e => {
    const fromNode = nodes.find(n => n.id === e.from);
    const toNode = nodes.find(n => n.id === e.to);
    if (!fromNode || !toNode || isNodeHidden(fromNode) || isNodeHidden(toNode)) return;

    let targetDist = 140;
    let strength = 0.03;

    if (fromNode.type === 'hq' || toNode.type === 'hq') {
      targetDist = 240; // Giữ khoảng cách rộng từ HQ ra Kênh
      strength = 0.025;
    } else if (e.category === 'deal_link' || toNode.type === 'opportunity') {
      targetDist = 65;  // Deals bám sát quanh Contact như chùm vệ tinh
      strength = 0.07;
    } else if (e.category === 'group_link') {
      targetDist = 150; // Kênh -> Contact
      strength = 0.022;
    }

    const dx = toNode.x - fromNode.x;
    const dy = toNode.y - fromNode.y;
    const dist = Math.sqrt(dx * dx + dy * dy) || 1;
    const displacement = dist - targetDist;
    const springForce = displacement * strength;

    const fx = (dx / dist) * springForce;
    const fy = (dy / dist) * springForce;

    if (fromNode !== graphState.dragNode && fromNode.type !== 'hq') {
      fromNode.vx += fx;
      fromNode.vy += fy;
    }
    if (toNode !== graphState.dragNode && toNode.type !== 'hq') {
      toNode.vx -= fx;
      toNode.vy -= fy;
    }
  });

  // 4. Cập nhật vị trí và ma sát giảm chấn (Velocity Damping)
  const friction = 0.80;
  const maxVelocity = 7.0;

  nodes.forEach(n => {
    if (n.type === 'hq') {
      // Khóa vị trí HQ Sếp Ryan bất biến tại tâm vũ trụ Obsidian
      n.x = cx;
      n.y = cy;
      n.vx = 0;
      n.vy = 0;
      return;
    }

    if (n === graphState.dragNode) return;

    // Giới hạn vận tốc cực đại
    const v = Math.sqrt(n.vx * n.vx + n.vy * n.vy);
    if (v > maxVelocity) {
      n.vx = (n.vx / v) * maxVelocity;
      n.vy = (n.vy / v) * maxVelocity;
    }

    n.x += n.vx;
    n.y += n.vy;
    n.vx *= friction;
    n.vy *= friction;

    // Ranh giới biên mềm giữ node trong khung nhìn
    const pad = 40;
    if (n.x < pad) n.vx += (pad - n.x) * 0.06;
    if (n.x > graphState.width - pad) n.vx -= (n.x - (graphState.width - pad)) * 0.06;
    if (n.y < pad) n.vy += (pad - n.y) * 0.06;
    if (n.y > graphState.height - pad) n.vy -= (n.y - (graphState.height - pad)) * 0.06;
  });
}"""

if old_forces in content:
    content = content.replace(old_forces, new_forces)
    print("✓ Đã nâng cấp applyObsidianForces V3")
else:
    print("! Không tìm thấy old_forces")

with open(html_path, "w", encoding="utf-8") as f:
    f.write(content)
