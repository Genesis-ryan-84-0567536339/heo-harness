import os

file_path = "/home/ryan/heo-harness/artifacts/reports/gen_harness_executive_console.html"
wp_path = "/home/ryan/Documents/Ryan-Workplace/Heo-Harness/artifacts/reports/gen_harness_executive_console.html"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update Title
content = content.replace(
    "<title>GEN-HARNESS — Executive Intelligence Console (SSOT v2.2)</title>",
    "<title>[BẢN TEST / LABS PREVIEW] GEN-HARNESS — Executive Intelligence Console (SSOT v2.2)</title>"
)

# 2. Update Sidebar Brand
content = content.replace(
    "<span>SPEC v2.2 LOCKED</span>",
    "<span>SPEC v2.2 · BẢN TEST</span>"
)

# 3. Add Topbar Test Badge
old_topbar_badge = """      <div class="topbar-right">
        <!-- Live status -->
        <div class="status-pill">"""

new_topbar_badge = """      <div class="topbar-right">
        <!-- Test Badge Prominent -->
        <div class="status-pill" style="background: rgba(245, 158, 11, 0.15); border: 1px solid rgba(245, 158, 11, 0.4); color: #fbbf24; font-weight: 700;">
          <i class="ph ph-flask"></i>
          <span>BẢN TEST / LABS PREVIEW</span>
        </div>
        <!-- Live status -->
        <div class="status-pill">"""

content = content.replace(old_topbar_badge, new_topbar_badge)

# 4. Add Banner Test Notice
old_banner = """<h2><i class="ph ph-compass" style="color:var(--accent-primary)"></i> Trung Tâm Chỉ Huy 10 Phút (Executive 10-Minute Radar)</h2>"""
new_banner = """<h2><i class="ph ph-compass" style="color:var(--accent-primary)"></i> Trung Tâm Chỉ Huy 10 Phút (Executive 10-Minute Radar) <span style="background:rgba(245,158,11,0.2); color:#fbbf24; border:1px solid rgba(245,158,11,0.4); padding:2px 8px; border-radius:4px; font-size:11px; font-weight:700; margin-left:8px;">BẢN TEST THỬ NGHIỆM</span></h2>"""
content = content.replace(old_banner, new_banner)

# Write back
with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

if os.path.exists(os.path.dirname(wp_path)):
    with open(wp_path, "w", encoding="utf-8") as f:
        f.write(content)

print("[OK] Đã gắn nhãn BẢN TEST nổi bật trên giao diện thành công!")
