# -*- coding: utf-8 -*-
"""
Script tinh chỉnh thuật toán Obsidian Graph View Physics:
- Phân cụm 5 vùng không gian biệt lập (Tây Bắc, Đông Bắc, Đông, Đông Nam, Tây Nam).
- Độ dài lò xo đàn hồi thích ứng theo cấp liên kết (HQ-Channel: 280px, Channel-Contact: 130px, Contact-Deal: 75px).
- Lực đẩy Coulomb mạnh mẽ chống chồng lấn.
- Khóa cố định HQ ở tâm.
"""
import re

html_path = "/home/ryan/heo-harness/heo_harness/plugins/ui_dashboard/dashboard.html"
with open(html_path, "r", encoding="utf-8") as f:
    content = f.read()

target_block_regex = r"function applyObsidianForces\(\)\s*\{[\s\S]*?^function drawObsidianGraph"

new_forces_code = '''function applyObsidianForces() {
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

  // 4. Cập nhật vị trí và giảm chấn (Damping)
  nodes.forEach(n => {
    if (n.type === 'hq') {
      n.x = cx;
      n.y = cy;
      n.vx = 0;
      n.vy = 0;
      return;
    }
    if (n === graphState.dragNode) return;

    n.vx *= 0.84;
    n.vy *= 0.84;
    n.x += n.vx;
    n.y += n.vy;
  });
}

function drawObsidianGraph'''

content = re.sub(target_block_regex, new_forces_code, content, flags=re.MULTILINE)

# Cập nhật clusterCentroids trong initRelationshipGraphCanvas
centroid_init_old = r"const clusterCentroids = \{[\s\S]*?\};"
centroid_init_new = """const clusterCentroids = {
      hq:      { x: cx,       y: cy },
      channel: { x: cx - 350, y: cy - 140 }, // Cụm Tây Bắc: Kênh & Nhóm
      hot:     { x: cx + 330, y: cy - 150 }, // Cụm Đông Bắc: Khách Nóng VIP
      warm:    { x: cx + 330, y: cy + 180 }, // Cụm Đông Nam: Đối Tác Ấm
      cold:    { x: cx - 330, y: cy + 180 }, // Cụm Tây Nam: Khách Im Lặng
      deal:    { x: cx + 450, y: cy - 20 }   // Cụm Đông: Deals Cơ Hội
    };"""

content = re.sub(centroid_init_old, centroid_init_new, content)

with open(html_path, "w", encoding="utf-8") as f:
    f.write(content)

print("✓ Đã tinh chỉnh thành công lực vật lý và phân cụm không gian Obsidian")
