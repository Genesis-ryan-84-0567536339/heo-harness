import re

html_path = "heo_harness/plugins/ui_dashboard/dashboard.html"

with open(html_path, "r", encoding="utf-8") as f:
    content = f.read()

# Thay thế đoạn channelPositions đến hết dealIds spreadAngle
pattern = r"// 1\. Phân bố vị trí cho Kênh & Nhóm[\s\S]*?dealNode\.targetCluster = \{ x: dealNode\.x, y: dealNode\.y \};\s*\}\);\s*\}\);"

replacement_code = """// 1. Phân bố vị trí Kênh & Nhóm (Cánh Tây Widescreen, x: cx - 320 đến - 390)
    const channelPositions = {
      'grp-zalo-telecom': { x: cx - 320, y: cy - 140 },
      'grp-zalo-crm':     { x: cx - 390, y: cy - 40 },
      'grp-wa-logitech':  { x: cx - 390, y: cy + 60 },
      'grp-wa-fashion':   { x: cx - 320, y: cy + 160 }
    };

    // 2. Phân bố vị trí Khách Hàng Nóng VIP (Cánh Đông-Bắc Widescreen, x: cx + 330 đến + 480)
    const hotPositions = {
      'cnt-CNT-005': { x: cx + 330, y: cy - 200 }, // Chị Thảo
      'cnt-CNT-007': { x: cx + 450, y: cy - 120 }, // Giám Đốc Viettel
      'cnt-CNT-001': { x: cx + 490, y: cy - 10 },  // Chị Mai Phương
      'cnt-CNT-002': { x: cx + 450, y: cy + 100 }  // Anh Hoàng Bách
    };

    // 3. Phân bố vị trí Đối Tác Tiềm Năng (Cánh Đông-Nam Widescreen, y tối đa cy + 210, không chạm đáy)
    const warmPositions = {
      'cnt-CNT-006': { x: cx + 340, y: cy + 190 }, // Anh Minh Kafi
      'cnt-CNT-008': { x: cx + 210, y: cy + 210 }, // Tập Đoàn Tân Á
      'cnt-CNT-003': { x: cx + 70,  y: cy + 220 }  // Trần Thu Hà
    };

    // 4. Phân bố vị trí Khách Im Lặng (Cánh Tây-Nam Widescreen)
    const coldPositions = {
      'cnt-CNT-004': { x: cx - 110, y: cy + 210 }, // Nguyễn Đức Trí
      'cnt-CNT-009': { x: cx - 220, y: cy + 190 }  // Phạm Văn Long
    };

    // Gán vị trí giãn rộng cho từng node
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
        n.x = cx + (Math.random() - 0.5) * 500;
        n.y = cy + (Math.random() - 0.5) * 350;
        n.targetCluster = { x: n.x, y: n.y };
      }
    });

    // 5. Bố trí các Deals vệ tinh tỏa đều ra phía NGOÀI (bán kính 115px)
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

        // Góc tỏa hướng ra ngoài tâm HQ (Outward Radial Direction)
        const baseAngle = Math.atan2(parentNode.y - cy, parentNode.x - cx);
        const spreadOffset = (dIdx - (count - 1) / 2) * 0.85;
        const finalAngle = baseAngle + spreadOffset;
        const dealDistance = 115;

        dealNode.x = parentNode.x + Math.cos(finalAngle) * dealDistance;
        dealNode.y = parentNode.y + Math.sin(finalAngle) * dealDistance;
        dealNode.targetCluster = { x: dealNode.x, y: dealNode.y };
      });
    });"""

match = re.search(pattern, content)
if match:
    content = content[:match.start()] + replacement_code + content[match.end():]
    print("✓ Đã cập nhật xong tọa độ Elip Widescreen và hướng tỏa Deals!")
else:
    print("! Không tìm thấy regex pattern")

with open(html_path, "w", encoding="utf-8") as f:
    f.write(content)
