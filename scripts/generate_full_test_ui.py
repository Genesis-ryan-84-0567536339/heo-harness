#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

source_file = "/home/ryan/heo-harness/heo_harness/plugins/ui_dashboard/dashboard.html"
target_file = "/home/ryan/heo-harness/artifacts/reports/gen_harness_test_ui.html"
wp_target_file = "/home/ryan/Documents/Ryan-Workplace/Heo-Harness/artifacts/reports/gen_harness_test_ui.html"

# Remove old console files
for old_f in [
    "/home/ryan/heo-harness/artifacts/reports/gen_harness_executive_console.html",
    "/home/ryan/Documents/Ryan-Workplace/Heo-Harness/artifacts/reports/gen_harness_executive_console.html"
]:
    if os.path.exists(old_f):
        os.remove(old_f)
        print(f"[REMOVED] {old_f}")

with open(source_file, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update Title
content = content.replace(
    "<title>AGY-ASSIS / HEO OS — V6 Executive Intelligence Console</title>",
    "<title>[BẢN TEST THỬ NGHIỆM] AGY-ASSIS / HEO OS — V6 Executive Console</title>"
)

# 2. Add Test CSS: Collapsible Sidebar, Topbar overflow prevention, Responsive height
test_css = """
    /* ==========================================================================
       BẢN TEST THỬ NGHIỆM: TỐI ƯU BỐ CỤC (COLLAPSIBLE SIDEBAR & TOPBAR OVERFLOW FIX)
       ========================================================================== */
    #sidebar {
      transition: width 0.22s cubic-bezier(0.16, 1, 0.3, 1), min-width 0.22s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }
    #sidebar.collapsed {
      width: 68px !important;
      min-width: 68px !important;
    }
    #sidebar.collapsed .brand-title,
    #sidebar.collapsed .brand-sub,
    #sidebar.collapsed .nav-section-label,
    #sidebar.collapsed .nav-hub-left span,
    #sidebar.collapsed .nav-badge,
    #sidebar.collapsed .user-name,
    #sidebar.collapsed .user-role {
      display: none !important;
    }
    #sidebar.collapsed .nav-hub-item {
      justify-content: center !important;
      padding: 10px 0 !important;
    }
    #sidebar.collapsed .nav-hub-left {
      margin: 0 !important;
    }
    #sidebar.collapsed .nav-hub-left i {
      margin-right: 0 !important;
      font-size: 20px !important;
    }
    #sidebar.collapsed .brand-header {
      padding: 12px 6px !important;
      justify-content: center !important;
    }
    #sidebar.collapsed .brand-logo {
      margin: 0 !important;
    }
    #sidebar.collapsed .sidebar-footer {
      padding: 10px 4px !important;
      justify-content: center !important;
    }
    #sidebar.collapsed .sidebar-footer button {
      display: none !important;
    }

    /* Topbar Overflow Fix */
    .topbar-left {
      max-width: 44vw !important;
      overflow: hidden !important;
      white-space: nowrap !important;
      text-overflow: ellipsis !important;
      display: flex !important;
      align-items: center !important;
      gap: 6px !important;
    }
    .topbar-title {
      overflow: hidden !important;
      text-overflow: ellipsis !important;
      white-space: nowrap !important;
      flex-shrink: 1 !important;
    }
    .topbar-subtitle {
      max-width: 22vw !important;
      overflow: hidden !important;
      text-overflow: ellipsis !important;
      white-space: nowrap !important;
      display: inline-block !important;
      vertical-align: middle !important;
      flex-shrink: 2 !important;
    }
    .topbar-right {
      flex-shrink: 0 !important;
    }

    /* Kanban Container Responsive Height */
    .kanban-board, .kanban-5col {
      min-height: calc(100vh - 220px) !important;
    }
  </style>"""

content = content.replace("</style>", test_css, 1)

# 3. Add Sidebar Collapse Toggle Button in brand-header
old_brand_header = """    <div class="brand-header">
      <div class="brand-logo"><i class="ph ph-cube-transparent"></i></div>
      <div>
        <div class="brand-title">GEN-HARNESS OS</div>
        <div class="brand-sub">Genesis Harness (HEO OS) v2.2</div>
      </div>
    </div>"""

new_brand_header = """    <div class="brand-header">
      <div class="brand-logo"><i class="ph ph-cube-transparent"></i></div>
      <div style="min-width:0">
        <div class="brand-title">GEN-HARNESS OS</div>
        <div class="brand-sub">Genesis Harness v2.2 · BẢN TEST</div>
      </div>
      <button id="btn-sidebar-collapse" class="btn sm" onclick="toggleSidebarCollapse()" title="Thu gọn / Mở rộng Sidebar (Phím [)" style="margin-left:auto; background:transparent; border:1px solid rgba(255,255,255,0.1); color:var(--color-neutral-400); padding:4px 6px; cursor:pointer; border-radius:6px; flex-shrink:0;">
        <i class="ph ph-sidebar-simple" style="font-size:16px;"></i>
      </button>
    </div>"""

content = content.replace(old_brand_header, new_brand_header, 1)

# 4. Add Topbar Test Badge
old_topbar_right = """    <header id="topbar">
      <div class="topbar-left">
        <span class="topbar-chassis-tag">CHASSIS</span>
        <i class="ph ph-caret-right topbar-caret"></i>
        <span class="topbar-title" id="top-title">Tổng quan</span>
        <span class="topbar-subtitle" id="top-subtitle">Điều gì cần Sếp ngay bây giờ</span>
      </div>
      <div class="topbar-right">
        <div class="topbar-pill">"""

new_topbar_right = """    <header id="topbar">
      <div class="topbar-left">
        <span class="topbar-chassis-tag" style="background:rgba(245,158,11,0.2); color:#fbbf24; border-color:rgba(245,158,11,0.4)">TEST</span>
        <i class="ph ph-caret-right topbar-caret"></i>
        <span class="topbar-title" id="top-title">Tổng quan</span>
        <span class="topbar-subtitle" id="top-subtitle">Điều gì cần Sếp ngay bây giờ</span>
      </div>
      <div class="topbar-right">
        <!-- TEST WATERMARK BADGE -->
        <div class="topbar-pill" style="background:rgba(245,158,11,0.18); border:1px solid rgba(245,158,11,0.5); color:#fbbf24; font-weight:700;">
          <i class="ph ph-flask"></i> <span>BẢN TEST THỬ NGHIỆM TỐI ƯU</span>
        </div>
        <div class="topbar-pill">"""

content = content.replace(old_topbar_right, new_topbar_right, 1)

# 5. Add JS for toggleSidebarCollapse and hotkey [
test_js = """
// BẢN TEST: TOGGLE SIDEBAR COLLAPSE
function toggleSidebarCollapse() {
  const sb = document.getElementById('sidebar');
  if (!sb) return;
  sb.classList.toggle('collapsed');
  const isCol = sb.classList.contains('collapsed');
  localStorage.setItem('heo_sidebar_collapsed_test', isCol ? '1' : '0');
  setTimeout(() => {
    window.dispatchEvent(new Event('resize'));
    if (typeof drawGraphCanvas === 'function') drawGraphCanvas();
  }, 240);
}

document.addEventListener('keydown', function(e) {
  if (e.key === '[' && !['INPUT', 'TEXTAREA'].includes(e.target.tagName)) {
    toggleSidebarCollapse();
  }
});

if (localStorage.getItem('heo_sidebar_collapsed_test') === '1') {
  const sb = document.getElementById('sidebar');
  if (sb) sb.classList.add('collapsed');
}
</script>
"""

content = content.replace("</script>\n</body>", test_js + "\n</body>", 1)

# Write to target
os.makedirs(os.path.dirname(target_file), exist_ok=True)
with open(target_file, "w", encoding="utf-8") as f:
    f.write(content)
print(f"[OK] Đã tạo thành công {target_file} ({len(content)} bytes)")

if os.path.exists(os.path.dirname(wp_target_file)):
    with open(wp_target_file, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[OK] Đã đồng bộ sang Workplace: {wp_target_file}")
