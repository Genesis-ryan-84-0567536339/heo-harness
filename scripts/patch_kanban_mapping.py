import re

file_path = "/home/ryan/heo-harness/artifacts/reports/gen_harness_executive_console.html"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace KANBAN_COLS and render logic
old_kanban_block = """    const KANBAN_COLS = [
      { id: 'raw', title: '1. Tín Hiệu Thô', color: '#94a3b8' },
      { id: 'verified', title: '2. Đã Xác Thực', color: '#38bdf8' },
      { id: 'matched', title: '3. Đã Ráp Khớp', color: '#c084fc' },
      { id: 'approaching', title: '4. Đang Tiếp Cận', color: '#fbbf24' },
      { id: 'negotiating', title: '5. Đang Đàm Phán', color: '#fb7185' },
      { id: 'won', title: '6. Thắng Deal (Won)', color: '#4ade80' },
      { id: 'dormant', title: '7. Ngủ Đông / Lưu', color: '#64748b' }
    ];

    async function renderKanban() {
      const container = document.getElementById('kanbanContainer');
      container.innerHTML = '';

      let opps = [];
      try {
        const res = await fetch('/api/data_factory/opportunities');
        const data = await res.json();
        if (data.ok && data.opportunities) opps = data.opportunities;
      } catch (e) {
        console.warn('Dùng sample opportunities:', e);
      }

      if (opps.length === 0) {
        opps = [
          { id: 'OPP-101', title: 'AI Điều Phối Tin Nhắn Đa Kênh', contact_name: 'Anh Hoàng Bách', stage: 'matched', value_est: 185000000, heat: 92 },
          { id: 'OPP-103', title: 'Báo Cáo Phân Tích Kafi', contact_name: 'Anh Minh Kafi', stage: 'approaching', value_est: 50000000, heat: 85 },
          { id: 'OPP-104', title: 'Bộ Nhận Diện AI & Giọng Đọc', contact_name: 'Chị Thảo (Viettel)', stage: 'negotiating', value_est: 85000000, heat: 95 },
          { id: 'OPP-106', title: 'Bản Quyền Gen-Harness Pro', contact_name: 'Tập Đoàn Tân Á', stage: 'won', value_est: 240000000, heat: 100 },
          { id: 'OPP-102', title: 'Tích Hợp ERP/CRM Hub', contact_name: 'Trần Thu Hà', stage: 'raw', value_est: 1200000000, heat: 62 }
        ];
      }

      KANBAN_COLS.forEach(col => {
        const colOpps = opps.filter(o => (o.stage || 'raw') === col.id);
        const colEl = document.createElement('div');
        colEl.className = 'kanban-col';
        colEl.innerHTML = `
          <div class="kanban-col-header" style="border-top:3px solid ${col.color}">
            <span style="color:#fff">${col.title}</span>
            <span class="nav-badge">${colOpps.length}</span>
          </div>
          <div class="kanban-cards-wrapper">
            ${colOpps.map(o => `
              <div class="opp-card" onclick="openTraceModal('${o.id}')">
                <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                  <strong style="font-size:13px; color:#fff; line-height:1.4">${o.title}</strong>
                  <span class="heat-pill hot" style="font-size:10px">${o.heat || 85}°</span>
                </div>
                <div style="font-size:11px; color:var(--text-sub)">${o.contact_name}</div>
                <div style="display:flex; justify-content:space-between; align-items:center; margin-top:4px">
                  <span style="font-family:'JetBrains Mono'; font-weight:700; color:var(--accent-success); font-size:12px">
                    ${(o.value_est / 1000000).toLocaleString('vi-VN')} Tr đ
                  </span>
                  <span style="font-size:10px; color:var(--text-muted)"><i class="ph ph-magnifying-glass"></i> Soi</span>
                </div>
              </div>
            `).join('')}
          </div>
        `;
        container.appendChild(colEl);
      });
    }"""

new_kanban_block = """    const KANBAN_COLS = [
      { id: 'signal', title: '1. Tín Hiệu Thô', stages: ['SIGNAL', 'RAW_SIGNAL', 'raw'], color: '#94a3b8' },
      { id: 'verified', title: '2. Đã Xác Thực', stages: ['VERIFIED', 'verified'], color: '#38bdf8' },
      { id: 'matched', title: '3. Đã Ráp Khớp', stages: ['MATCHED', 'matched'], color: '#c084fc' },
      { id: 'outreach', title: '4. Đang Tiếp Cận', stages: ['OUTREACH', 'approaching'], color: '#fbbf24' },
      { id: 'negotiating', title: '5. Đang Đàm Phán', stages: ['NEGOTIATING', 'negotiating'], color: '#fb7185' },
      { id: 'review', title: '6. Soát Xét Nội Bộ', stages: ['INTERNAL_REVIEW', 'review'], color: '#818cf8' },
      { id: 'won', title: '7. Thắng Deal (Won)', stages: ['WON', 'won'], color: '#4ade80' }
    ];

    async function renderKanban() {
      const container = document.getElementById('kanbanContainer');
      container.innerHTML = '';

      let opps = [];
      try {
        const res = await fetch('/api/data_factory/opportunities');
        const data = await res.json();
        if (data.ok && data.opportunities) opps = data.opportunities;
      } catch (e) {
        console.warn('Dùng sample opportunities:', e);
      }

      KANBAN_COLS.forEach(col => {
        const colOpps = opps.filter(o => col.stages.includes(o.stage || ''));
        const colEl = document.createElement('div');
        colEl.className = 'kanban-col';
        colEl.innerHTML = `
          <div class="kanban-col-header" style="border-top:3px solid ${col.color}">
            <span style="color:#fff">${col.title}</span>
            <span class="nav-badge ${colOpps.length > 0 ? 'live' : ''}">${colOpps.length}</span>
          </div>
          <div class="kanban-cards-wrapper">
            ${colOpps.map(o => {
              const val = o.estimated_value || o.value_est || 0;
              const heat = o.heat_score || o.heat || 80;
              return `
              <div class="opp-card" onclick="openTraceModal('${o.id || o.contact_id}')">
                <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                  <strong style="font-size:12px; color:#fff; line-height:1.4">${o.title}</strong>
                  <span class="heat-pill ${heat >= 85 ? 'hot' : 'warm'}" style="font-size:10px">${Math.round(heat)}°</span>
                </div>
                <div style="font-size:11px; color:var(--text-sub)">${o.contact_name} · ${o.channel ? o.channel.toUpperCase() : ''}</div>
                <div style="display:flex; justify-content:space-between; align-items:center; margin-top:4px">
                  <span style="font-family:'JetBrains Mono'; font-weight:700; color:var(--accent-success); font-size:12px">
                    ${val >= 1000000 ? (val / 1000000).toLocaleString('vi-VN') + ' Tr đ' : (val > 0 ? val.toLocaleString('vi-VN') + ' đ' : 'Chưa định giá')}
                  </span>
                  <span style="font-size:10px; color:var(--text-muted); cursor:pointer"><i class="ph ph-magnifying-glass"></i> Soi</span>
                </div>
              </div>
              `;
            }).join('')}
          </div>
        `;
        container.appendChild(colEl);
      });
    }"""

if old_kanban_block in content:
    content = content.replace(old_kanban_block, new_kanban_block)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    # copy to workplace
    wp_path = "/home/ryan/Documents/Ryan-Workplace/Heo-Harness/artifacts/reports/gen_harness_executive_console.html"
    with open(wp_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("[OK] Đã cập nhật Kanban mapping thành công!")
else:
    print("[WARN] Không tìm thấy block kanban cũ")
