import re

html_path = "heo_harness/plugins/ui_dashboard/dashboard.html"

with open(html_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Mở rộng graphState với các biến điều khiển bộ lọc giảm nhiễu
old_graph_state = """let graphState = {
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
};"""

new_graph_state = """let graphState = {
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
  // Noise Reduction & Contrast Settings
  hideDeals: false,           // Tắt Deals vệ tinh để giảm 60% nhiễu
  minHeatThreshold: 0,        // Lọc nhiệt độ tối thiểu (0-100°)
  channelFilter: 'all',       // 'all' | 'zalo' | 'whatsapp'
  canvasTheme: 'navy_bright', // 'navy_bright' (sáng rõ) | 'void_dark' (đen sâu)
  // Physics Parameters
  repulsion: 85,
  springLength: 95,
  springStrength: 0.045,
  clusterGravity: 0.035,
  damping: 0.86
};"""

if old_graph_state in content:
    content = content.replace(old_graph_state, new_graph_state)
    print("✓ Đã cập nhật graphState với các thuộc tính lọc giảm nhiễu")
else:
    print("! Không tìm thấy old_graph_state")

# 2. Thay thế renderRelationshipGraphView bằng giao diện Split-View 2 Cột hiện đại
old_render_view = """function renderRelationshipGraphView() {
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
}"""

new_render_view = """function renderRelationshipGraphView() {
  return `
    <div style="display:grid;grid-template-columns:310px 1fr;gap:16px;margin-bottom:24px;align-items:start">
      
      <!-- CỘT TRÁI: BẢNG ĐIỀU KHIỂN BỘ LỌC GIẢM NHIỄU (NOISE REDUCTION PANEL) -->
      <div class="card" style="padding:16px;background:rgba(15,23,42,0.92);border:1px solid rgba(255,255,255,0.12);box-shadow:0 8px 30px rgba(0,0,0,0.4);border-radius:12px;display:flex;flex-direction:column;gap:16px">
        
        <!-- Header Panel -->
        <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid rgba(255,255,255,0.08);padding-bottom:10px">
          <div style="display:flex;align-items:center;gap:8px">
            <div style="width:28px;height:28px;border-radius:6px;background:rgba(56,189,248,0.15);display:flex;align-items:center;justify-content:center;color:#38bdf8">
              <i class="ph ph-funnel" style="font-size:16px"></i>
            </div>
            <div>
              <div style="font-size:13px;font-weight:700;color:#f8fafc">BỘ LỌC GIẢM NHIỄU</div>
              <div style="font-size:10.5px;color:#94a3b8">Kiểm soát mật độ hiển thị</div>
            </div>
          </div>
          <button class="btn sm subtle" onclick="resetAllGraphFilters()" title="Đặt lại bộ lọc về mặc định" style="font-size:11px;padding:3px 8px">
            <i class="ph ph-arrow-counter-clockwise"></i> Đặt Lại
          </button>
        </div>

        <!-- 1. KỊCH BẢN LỌC NHANH (1-CLICK PRESETS) -->
        <div>
          <div style="font-size:11px;font-weight:700;color:#cbd5e1;margin-bottom:8px;text-transform:uppercase;letter-spacing:0.5px;display:flex;align-items:center;gap:6px">
            <i class="ph ph-lightning" style="color:#fbbf24"></i> Kịch Bản Nhanh (Presets)
          </div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px">
            <button class="btn sm" id="preset-btn-all" onclick="applyGraphPreset('all')" style="font-size:11px;padding:6px 8px;background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.15);justify-content:center">
              🌟 Toàn Mạng
            </button>
            <button class="btn sm primary" id="preset-btn-core" onclick="applyGraphPreset('core')" style="font-size:11px;padding:6px 8px;justify-content:center;background:#0284c7" title="Tắt deals vệ tinh, chỉ xem cấu trúc quan hệ chính">
              🎯 Tinh Gọn (Gốc)
            </button>
            <button class="btn sm" id="preset-btn-hot" onclick="applyGraphPreset('hot')" style="font-size:11px;padding:6px 8px;background:rgba(244,63,94,0.12);border:1px solid rgba(244,63,94,0.3);color:#fb7185;justify-content:center">
              🔥 Khách Nóng VIP
            </button>
            <button class="btn sm" id="preset-btn-silent" onclick="applyGraphPreset('silent')" style="font-size:11px;padding:6px 8px;background:rgba(100,116,139,0.15);border:1px solid rgba(100,116,139,0.3);color:#94a3b8;justify-content:center">
              ⚠️ Im Lặng (>3d)
            </button>
          </div>
        </div>

        <!-- 2. BẬT/TẮT NHÓM THỰC THỂ (ENTITY CHECKBOXES) -->
        <div>
          <div style="font-size:11px;font-weight:700;color:#cbd5e1;margin-bottom:8px;text-transform:uppercase;letter-spacing:0.5px;display:flex;justify-content:space-between;align-items:center">
            <span style="display:flex;align-items:center;gap:6px"><i class="ph ph-stack" style="color:#38bdf8"></i> Phân Nhóm Loại</span>
            <span style="font-size:10px;color:#64748b" id="filter-node-count-badge">26 Nodes</span>
          </div>

          <div style="display:flex;flex-direction:column;gap:6px;background:rgba(0,0,0,0.25);padding:8px 10px;border-radius:8px;border:1px solid rgba(255,255,255,0.06)">
            <!-- Checkbox HQ -->
            <label style="display:flex;align-items:center;justify-content:space-between;font-size:11.5px;cursor:pointer;color:#e2e8f0;padding:2px 0">
              <span style="display:flex;align-items:center;gap:8px">
                <input type="checkbox" id="chk-cat-hq" checked onchange="toggleCategoryCheckbox('hq', this.checked)" style="accent-color:#818cf8;width:14px;height:14px">
                <span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#818cf8"></span>
                <span>👑 HQ Sếp Ryan (Tâm)</span>
              </span>
              <span style="font-size:10px;padding:1px 6px;border-radius:10px;background:rgba(129,140,248,0.2);color:#818cf8;font-weight:700">1</span>
            </label>

            <!-- Checkbox Channels -->
            <label style="display:flex;align-items:center;justify-content:space-between;font-size:11.5px;cursor:pointer;color:#e2e8f0;padding:2px 0">
              <span style="display:flex;align-items:center;gap:8px">
                <input type="checkbox" id="chk-cat-channel" checked onchange="toggleCategoryCheckbox('channel', this.checked)" style="accent-color:#0ea5e9;width:14px;height:14px">
                <span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#0ea5e9"></span>
                <span>💬 Kênh Zalo & WA</span>
              </span>
              <span style="font-size:10px;padding:1px 6px;border-radius:10px;background:rgba(14,165,233,0.2);color:#38bdf8;font-weight:700">4</span>
            </label>

            <!-- Checkbox Hot -->
            <label style="display:flex;align-items:center;justify-content:space-between;font-size:11.5px;cursor:pointer;color:#e2e8f0;padding:2px 0">
              <span style="display:flex;align-items:center;gap:8px">
                <input type="checkbox" id="chk-cat-hot" checked onchange="toggleCategoryCheckbox('hot', this.checked)" style="accent-color:#f43f5e;width:14px;height:14px">
                <span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#f43f5e"></span>
                <span>🔥 Khách Nóng (>=80°)</span>
              </span>
              <span style="font-size:10px;padding:1px 6px;border-radius:10px;background:rgba(244,63,94,0.2);color:#fb7185;font-weight:700">4</span>
            </label>

            <!-- Checkbox Warm -->
            <label style="display:flex;align-items:center;justify-content:space-between;font-size:11.5px;cursor:pointer;color:#e2e8f0;padding:2px 0">
              <span style="display:flex;align-items:center;gap:8px">
                <input type="checkbox" id="chk-cat-warm" checked onchange="toggleCategoryCheckbox('warm', this.checked)" style="accent-color:#f59e0b;width:14px;height:14px">
                <span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#f59e0b"></span>
                <span>🟡 Đối Tác Ấm (50-79°)</span>
              </span>
              <span style="font-size:10px;padding:1px 6px;border-radius:10px;background:rgba(245,158,11,0.2);color:#fbbf24;font-weight:700">3</span>
            </label>

            <!-- Checkbox Cold -->
            <label style="display:flex;align-items:center;justify-content:space-between;font-size:11.5px;cursor:pointer;color:#e2e8f0;padding:2px 0">
              <span style="display:flex;align-items:center;gap:8px">
                <input type="checkbox" id="chk-cat-cold" checked onchange="toggleCategoryCheckbox('cold', this.checked)" style="accent-color:#64748b;width:14px;height:14px">
                <span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#64748b"></span>
                <span>⚪ Im Lặng (>3 ngày)</span>
              </span>
              <span style="font-size:10px;padding:1px 6px;border-radius:10px;background:rgba(100,116,139,0.2);color:#94a3b8;font-weight:700">2</span>
            </label>

            <!-- Checkbox Deal -->
            <label style="display:flex;align-items:center;justify-content:space-between;font-size:11.5px;cursor:pointer;color:#e2e8f0;padding:2px 0">
              <span style="display:flex;align-items:center;gap:8px">
                <input type="checkbox" id="chk-cat-deal" checked onchange="toggleCategoryCheckbox('deal', this.checked)" style="accent-color:#c084fc;width:14px;height:14px">
                <span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#c084fc"></span>
                <span>💼 Cơ Hội Deals Vệ Tinh</span>
              </span>
              <span style="font-size:10px;padding:1px 6px;border-radius:10px;background:rgba(192,132,252,0.2);color:#c084fc;font-weight:700">12</span>
            </label>
          </div>
        </div>

        <!-- 3. CÔNG TẮC GIẢM NHIỄU DEALS (TẮT NHANH 12 DEALS) -->
        <div style="background:rgba(192,132,252,0.08);border:1px solid rgba(192,132,252,0.25);border-radius:8px;padding:10px 12px;display:flex;justify-content:space-between;align-items:center">
          <div>
            <div style="font-size:11.5px;font-weight:700;color:#e9d5ff;display:flex;align-items:center;gap:5px">
              <i class="ph ph-eye-slash"></i> Giấu Deals Vệ Tinh
            </div>
            <div style="font-size:10px;color:#c084fc">Giảm 60% liên kết chằng chịt</div>
          </div>
          <label class="switch" style="position:relative;display:inline-block;width:34px;height:18px">
            <input type="checkbox" id="toggle-hide-deals" onchange="toggleHideDeals(this.checked)" style="opacity:0;width:0;height:0">
            <span class="slider round" style="position:absolute;cursor:pointer;top:0;left:0;right:0;bottom:0;background-color:#334155;border-radius:18px;transition:0.3s"></span>
          </label>
        </div>

        <!-- 4. LỌC NHIỆT ĐỘ TỐI THIỂU (HEAT SCORE SLIDER) -->
        <div>
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">
            <span style="font-size:11px;font-weight:700;color:#cbd5e1;text-transform:uppercase;letter-spacing:0.5px;display:flex;align-items:center;gap:6px">
              <i class="ph ph-thermometer-hot" style="color:#f43f5e"></i> Điểm Nhiệt Độ
            </span>
            <span id="heat-slider-val" style="font-size:11px;font-weight:700;color:#fb7185">Từ 0° trở lên</span>
          </div>
          <input type="range" min="0" max="95" value="0" step="5" class="form-range" id="heat-filter-slider" style="width:100%;accent-color:#f43f5e;cursor:pointer" oninput="updateHeatFilter(this.value)">
          <div style="display:flex;justify-content:space-between;font-size:9.5px;color:#64748b;margin-top:2px">
            <span>0° (Tất cả)</span>
            <span>50° (Ấm)</span>
            <span>80°+ (Rất nóng)</span>
          </div>
        </div>

        <!-- 5. LỌC THEO KÊNH HỘI THOẠI -->
        <div>
          <div style="font-size:11px;font-weight:700;color:#cbd5e1;margin-bottom:6px;text-transform:uppercase;letter-spacing:0.5px;display:flex;align-items:center;gap:6px">
            <i class="ph ph-chats" style="color:#10b981"></i> Kênh Hội Thoại
          </div>
          <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:4px">
            <button class="btn sm primary" id="channel-btn-all" onclick="updateChannelFilter('all')" style="font-size:10.5px;padding:4px 0;justify-content:center">
              Tất Cả
            </button>
            <button class="btn sm" id="channel-btn-zalo" onclick="updateChannelFilter('zalo')" style="font-size:10.5px;padding:4px 0;justify-content:center;background:rgba(14,165,233,0.15);color:#38bdf8;border:1px solid rgba(14,165,233,0.3)">
              Zalo
            </button>
            <button class="btn sm" id="channel-btn-wa" onclick="updateChannelFilter('whatsapp')" style="font-size:10.5px;padding:4px 0;justify-content:center;background:rgba(16,185,129,0.15);color:#34d399;border:1px solid rgba(16,185,129,0.3)">
              WhatsApp
            </button>
          </div>
        </div>

        <!-- 6. TÙY CHỌN HIỂN THỊ -->
        <div style="border-top:1px solid rgba(255,255,255,0.08);padding-top:10px;display:flex;flex-direction:column;gap:6px">
          <label style="display:flex;align-items:center;justify-content:space-between;font-size:11px;color:#94a3b8;cursor:pointer">
            <span>Hiển thị nhãn tên (Labels)</span>
            <input type="checkbox" id="chk-show-labels" checked onchange="toggleObsidianLabels(this.checked)" style="accent-color:#38bdf8">
          </label>
          <label style="display:flex;align-items:center;justify-content:space-between;font-size:11px;color:#94a3b8;cursor:pointer">
            <span>Lực đàn hồi vật lý (Physics)</span>
            <input type="checkbox" id="chk-physics-active" checked onchange="toggleObsidianPhysics(this.checked)" style="accent-color:#38bdf8">
          </label>
        </div>

      </div>

      <!-- CỘT PHẢI: KHÔNG GIAN CANVAS ĐỒ THỊ HIGH-CONTRAST SÁNG RÕ -->
      <div class="card" style="padding:0;background:#0d1527;border:1px solid rgba(255,255,255,0.12);box-shadow:0 8px 32px rgba(0,0,0,0.5);border-radius:12px;overflow:hidden;position:relative">
        
        <!-- Header Toolbar trên đầu Canvas -->
        <div style="padding:10px 16px;background:rgba(15,23,42,0.85);backdrop-filter:blur(10px);border-bottom:1px solid rgba(255,255,255,0.1);display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap">
          
          <!-- Left: Live Search Box -->
          <div style="position:relative;width:240px">
            <input type="text" class="form-input" id="graph-search-input" placeholder="Tìm tên đối tác, dự án..." style="width:100%;height:30px;font-size:11.5px;padding:3px 8px 3px 28px;background:rgba(0,0,0,0.4);border:1px solid rgba(255,255,255,0.18);color:#fff" oninput="searchGraphNode(this.value)">
            <i class="ph ph-magnifying-glass" style="position:absolute;left:9px;top:8px;font-size:13px;color:#94a3b8"></i>
            <span id="search-clear-btn" onclick="clearGraphSearch()" style="position:absolute;right:8px;top:6px;cursor:pointer;color:#64748b;display:none;font-size:13px">✕</span>
          </div>

          <!-- Center: Canvas Background Theme Toggle -->
          <div style="display:flex;align-items:center;gap:6px">
            <span style="font-size:11px;color:#94a3b8;font-weight:600">Độ Tương Phản:</span>
            <button class="btn sm primary" id="theme-btn-navy" onclick="setGraphTheme('navy_bright')" style="font-size:10.5px;padding:3px 8px;background:#0369a1">
              🌌 Slate Navy (Sáng Rõ)
            </button>
            <button class="btn sm subtle" id="theme-btn-void" onclick="setGraphTheme('void_dark')" style="font-size:10.5px;padding:3px 8px">
              🌑 Obsidian Void
            </button>
          </div>

          <!-- Right: Zoom Controls & Reload -->
          <div style="display:flex;align-items:center;gap:4px">
            <button class="btn sm subtle" onclick="zoomGraphCanvas(1.2)" title="Phóng to" style="padding:4px 8px"><i class="ph ph-plus"></i></button>
            <button class="btn sm subtle" onclick="zoomGraphCanvas(0.8)" title="Thu nhỏ" style="padding:4px 8px"><i class="ph ph-minus"></i></button>
            <button class="btn sm subtle" onclick="resetGraphCanvasView()" title="Căn giữa màn hình" style="padding:4px 8px"><i class="ph ph-corners-out"></i> Căn Giữa</button>
            <button class="btn sm primary" onclick="initRelationshipGraphCanvas()" title="Tải lại toàn bộ dữ liệu đồ thị" style="padding:4px 10px"><i class="ph ph-arrows-clockwise"></i> Nạp Lại</button>
          </div>
        </div>

        <!-- Canvas Viewport -->
        <div style="position:relative;width:100%;height:680px;background:#0d1527;overflow:hidden" id="graph-viewport-box">
          <canvas id="relationship-graph-canvas" style="display:block;cursor:grab;width:100%;height:100%"></canvas>
          
          <!-- Bottom Floating Status Badge -->
          <div style="position:absolute;bottom:14px;left:16px;background:rgba(15,23,42,0.92);backdrop-filter:blur(10px);border:1px solid rgba(255,255,255,0.15);padding:6px 14px;border-radius:20px;font-size:11px;color:#e2e8f0;display:flex;align-items:center;gap:10px;pointer-events:none;z-index:5;box-shadow:0 4px 16px rgba(0,0,0,0.4)">
            <div style="display:flex;align-items:center;gap:6px">
              <span style="display:inline-block;width:7px;height:7px;border-radius:50%;background:#38bdf8;box-shadow:0 0 8px #38bdf8"></span>
              <span id="graph-stat-badge">Đang tải đồ thị...</span>
            </div>
            <span style="opacity:0.3">|</span>
            <span style="color:#94a3b8">💡 Hover vào node để <b>Focus Spotlight</b> · Nhấp đúp để mở <b>Living 360</b></span>
          </div>

          <!-- Top-Right Legend Box -->
          <div style="position:absolute;top:14px;right:14px;background:rgba(15,23,42,0.92);backdrop-filter:blur(10px);border:1px solid rgba(255,255,255,0.12);padding:10px 14px;border-radius:10px;font-size:11px;color:#cbd5e1;pointer-events:none;z-index:5;display:flex;flex-direction:column;gap:5px;box-shadow:0 4px 20px rgba(0,0,0,0.5)">
            <div style="font-weight:700;font-size:10.5px;color:#94a3b8;border-bottom:1px solid rgba(255,255,255,0.08);padding-bottom:4px;margin-bottom:2px">CHÚ GIẢI 5 CỤM KHÔNG GIAN</div>
            <div><span style="color:#818cf8;font-weight:700">● Tâm:</span> HQ Tổng Chỉ Huy Sếp Ryan</div>
            <div><span style="color:#38bdf8;font-weight:700">● Tây-Bắc:</span> Kênh Zalo & WhatsApp</div>
            <div><span style="color:#fb7185;font-weight:700">● Đông-Bắc:</span> Khách Hàng Nóng VIP (>=80°)</div>
            <div><span style="color:#fbbf24;font-weight:700">● Đông-Nam:</span> Đối Tác Tiềm Năng (50-79°)</div>
            <div><span style="color:#94a3b8;font-weight:700">● Tây-Nam:</span> Khách Im Lặng (>3 ngày)</div>
            <div><span style="color:#c084fc;font-weight:700">● Vệ Tinh:</span> Cơ Hội Deals Đang Mở</div>
          </div>
        </div>

      </div>

    </div>
  `;
}"""

if old_render_view in content:
    content = content.replace(old_render_view, new_render_view)
    print("✓ Đã cập nhật renderRelationshipGraphView với giao diện Split-View 2 Cột")
else:
    print("! Không tìm thấy old_render_view")

with open(html_path, "w", encoding="utf-8") as f:
    f.write(content)
