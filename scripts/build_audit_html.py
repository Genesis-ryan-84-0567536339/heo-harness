# -*- coding: utf-8 -*-
import json
import os

with open("/home/ryan/heo-harness/data/spec_audit_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

stats = data["stats"]
items = data["items"]

items_json = json.dumps(items, ensure_ascii=False)

html_content = f"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Bảng Đối Chiếu Tiến Độ: Gen-Harness vs. Spec LOCKED v2.2</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg-base: #0a0c10;
      --bg-surface: #11141b;
      --bg-elevated: #161b24;
      --bg-hover: #1f2633;
      --border: rgba(255, 255, 255, 0.08);
      --border-focus: rgba(99, 102, 241, 0.4);
      --text-main: #f3f4f6;
      --text-muted: #9ca3af;
      --text-dim: #6b7280;
      --accent: #6366f1;
      --accent-glow: rgba(99, 102, 241, 0.15);
      --green: #10b981;
      --green-glow: rgba(16, 185, 129, 0.15);
      --amber: #f59e0b;
      --amber-glow: rgba(245, 158, 11, 0.15);
      --red: #ef4444;
      --red-glow: rgba(239, 68, 68, 0.15);
      --blue: #3b82f6;
      --blue-glow: rgba(59, 130, 246, 0.15);
      --cyan: #06b6d4;
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      background-color: var(--bg-base);
      color: var(--text-main);
      line-height: 1.5;
      padding: 24px;
      min-height: 100vh;
    }}

    .container {{
      max-width: 1720px;
      margin: 0 auto;
    }}

    /* Header */
    .header {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 24px;
      padding-bottom: 20px;
      border-bottom: 1px solid var(--border);
    }}

    .brand-group {{
      display: flex;
      align-items: center;
      gap: 16px;
    }}

    .brand-badge {{
      width: 48px;
      height: 48px;
      background: linear-gradient(135deg, #4f46e5, #06b6d4);
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 24px;
      box-shadow: 0 0 20px rgba(99, 102, 241, 0.35);
    }}

    .title-area h1 {{
      font-size: 22px;
      font-weight: 700;
      letter-spacing: -0.02em;
      display: flex;
      align-items: center;
      gap: 10px;
    }}

    .version-tag {{
      font-size: 11px;
      text-transform: uppercase;
      font-weight: 700;
      background: rgba(99, 102, 241, 0.2);
      color: #a5b4fc;
      border: 1px solid rgba(99, 102, 241, 0.4);
      padding: 2px 8px;
      border-radius: 6px;
    }}

    .title-area p {{
      color: var(--text-muted);
      font-size: 13px;
      margin-top: 4px;
    }}

    .header-actions {{
      display: flex;
      gap: 10px;
      align-items: center;
    }}

    .btn {{
      background: var(--bg-elevated);
      color: var(--text-main);
      border: 1px solid var(--border);
      padding: 8px 14px;
      border-radius: 8px;
      font-size: 13px;
      font-weight: 500;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      transition: all 0.15s ease;
    }}

    .btn:hover {{
      background: var(--bg-hover);
      border-color: rgba(255, 255, 255, 0.2);
    }}

    .btn-primary {{
      background: var(--accent);
      border-color: var(--accent);
      color: #fff;
    }}

    .btn-primary:hover {{
      background: #4f46e5;
    }}

    /* KPI Summary Cards */
    .kpi-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
      gap: 16px;
      margin-bottom: 24px;
    }}

    .kpi-card {{
      background: var(--bg-surface);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 16px 20px;
      position: relative;
      overflow: hidden;
    }}

    .kpi-card::before {{
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 3px;
      background: var(--card-accent, var(--accent));
    }}

    .kpi-label {{
      font-size: 12px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--text-dim);
      margin-bottom: 6px;
    }}

    .kpi-value-row {{
      display: flex;
      align-items: baseline;
      gap: 10px;
    }}

    .kpi-value {{
      font-size: 28px;
      font-weight: 800;
      font-family: 'JetBrains Mono', monospace;
      color: var(--text-main);
    }}

    .kpi-desc {{
      font-size: 12px;
      color: var(--text-muted);
      margin-top: 6px;
    }}

    .progress-bar-wrap {{
      width: 100%;
      height: 6px;
      background: rgba(255, 255, 255, 0.06);
      border-radius: 3px;
      margin-top: 10px;
      overflow: hidden;
    }}

    .progress-bar-fill {{
      height: 100%;
      border-radius: 3px;
      background: var(--card-accent, var(--accent));
      transition: width 0.4s ease;
    }}

    /* Controls Bar */
    .controls-bar {{
      background: var(--bg-surface);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 14px 18px;
      margin-bottom: 20px;
      display: flex;
      flex-direction: column;
      gap: 14px;
    }}

    .controls-row-top {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
      flex-wrap: wrap;
    }}

    .search-wrap {{
      position: relative;
      flex: 1;
      max-width: 420px;
    }}

    .search-input {{
      width: 100%;
      background: var(--bg-base);
      border: 1px solid var(--border);
      color: var(--text-main);
      padding: 8px 12px 8px 34px;
      border-radius: 8px;
      font-size: 13px;
      outline: none;
      transition: border-color 0.15s ease;
    }}

    .search-input:focus {{
      border-color: var(--accent);
      box-shadow: 0 0 0 2px var(--accent-glow);
    }}

    .search-icon {{
      position: absolute;
      left: 11px;
      top: 50%;
      transform: translateY(-50%);
      color: var(--text-dim);
      font-size: 14px;
    }}

    .filter-pills {{
      display: flex;
      gap: 8px;
      align-items: center;
      flex-wrap: wrap;
    }}

    .pill {{
      background: var(--bg-base);
      border: 1px solid var(--border);
      color: var(--text-muted);
      padding: 5px 12px;
      border-radius: 20px;
      font-size: 12px;
      font-weight: 500;
      cursor: pointer;
      user-select: none;
      transition: all 0.15s ease;
    }}

    .pill:hover {{
      color: var(--text-main);
      border-color: rgba(255, 255, 255, 0.2);
    }}

    .pill.active {{
      background: var(--accent);
      color: #fff;
      border-color: var(--accent);
      box-shadow: 0 0 10px var(--accent-glow);
    }}

    .pill-green.active {{
      background: var(--green);
      border-color: var(--green);
    }}
    .pill-amber.active {{
      background: var(--amber);
      border-color: var(--amber);
    }}
    .pill-red.active {{
      background: var(--red);
      border-color: var(--red);
    }}
    .pill-blue.active {{
      background: var(--blue);
      border-color: var(--blue);
    }}

    .category-tabs {{
      display: flex;
      gap: 6px;
      border-top: 1px solid rgba(255, 255, 255, 0.05);
      padding-top: 12px;
      overflow-x: auto;
      scrollbar-width: thin;
    }}

    .cat-tab {{
      padding: 6px 12px;
      border-radius: 6px;
      font-size: 12px;
      font-weight: 500;
      color: var(--text-dim);
      cursor: pointer;
      white-space: nowrap;
      transition: all 0.15s ease;
    }}

    .cat-tab:hover {{
      color: var(--text-main);
      background: rgba(255, 255, 255, 0.04);
    }}

    .cat-tab.active {{
      color: #a5b4fc;
      background: rgba(99, 102, 241, 0.15);
      font-weight: 600;
    }}

    /* Spreadsheet Table */
    .sheet-card {{
      background: var(--bg-surface);
      border: 1px solid var(--border);
      border-radius: 12px;
      overflow: hidden;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
    }}

    .table-responsive {{
      max-height: 720px;
      overflow-y: auto;
      overflow-x: auto;
    }}

    table.spec-sheet {{
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
      text-align: left;
    }}

    table.spec-sheet thead th {{
      position: sticky;
      top: 0;
      background: #151922;
      color: var(--text-muted);
      font-weight: 600;
      text-transform: uppercase;
      font-size: 11px;
      letter-spacing: 0.05em;
      padding: 12px 14px;
      border-bottom: 2px solid var(--border);
      border-right: 1px solid rgba(255, 255, 255, 0.04);
      z-index: 10;
    }}

    table.spec-sheet tbody tr {{
      border-bottom: 1px solid rgba(255, 255, 255, 0.05);
      transition: background-color 0.12s ease;
      cursor: pointer;
    }}

    table.spec-sheet tbody tr:hover {{
      background-color: var(--bg-hover);
    }}

    table.spec-sheet tbody td {{
      padding: 12px 14px;
      border-right: 1px solid rgba(255, 255, 255, 0.03);
      vertical-align: top;
    }}

    .col-id {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      color: #818cf8;
      font-weight: 600;
      white-space: nowrap;
      width: 90px;
    }}

    .col-cat {{
      width: 150px;
    }}

    .cat-badge {{
      display: inline-block;
      font-size: 11px;
      font-weight: 500;
      padding: 2px 7px;
      border-radius: 4px;
      background: rgba(255, 255, 255, 0.05);
      color: var(--text-muted);
      border: 1px solid rgba(255, 255, 255, 0.07);
      white-space: nowrap;
    }}

    .col-name {{
      font-weight: 600;
      color: var(--text-main);
      width: 220px;
    }}

    .col-spec {{
      color: #d1d5db;
      font-size: 12.5px;
      min-width: 280px;
    }}

    .col-current {{
      color: var(--text-muted);
      font-size: 12px;
      min-width: 260px;
    }}

    .col-status {{
      width: 130px;
      white-space: nowrap;
    }}

    .status-badge {{
      display: inline-flex;
      align-items: center;
      gap: 5px;
      font-size: 11.5px;
      font-weight: 600;
      padding: 3px 9px;
      border-radius: 6px;
    }}

    .status-done {{
      background: var(--green-glow);
      color: #34d399;
      border: 1px solid rgba(16, 185, 129, 0.3);
    }}

    .status-wip {{
      background: var(--amber-glow);
      color: #fbbf24;
      border: 1px solid rgba(245, 158, 11, 0.3);
    }}

    .status-missing {{
      background: var(--red-glow);
      color: #f87171;
      border: 1px solid rgba(239, 68, 68, 0.3);
    }}

    .status-refactor {{
      background: var(--blue-glow);
      color: #60a5fa;
      border: 1px solid rgba(59, 130, 246, 0.3);
    }}

    .col-pct {{
      width: 120px;
    }}

    .pct-row {{
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .pct-number {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 12px;
      font-weight: 700;
      width: 38px;
    }}

    .pct-bar {{
      flex: 1;
      height: 6px;
      background: rgba(255, 255, 255, 0.08);
      border-radius: 3px;
      overflow: hidden;
    }}

    .pct-fill {{
      height: 100%;
      border-radius: 3px;
    }}

    .col-gap {{
      color: #94a3b8;
      font-size: 12px;
      min-width: 250px;
    }}

    /* Detail Drawer/Modal */
    .modal-overlay {{
      display: none;
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0, 0, 0, 0.75);
      backdrop-filter: blur(4px);
      z-index: 100;
      justify-content: center;
      align-items: center;
      padding: 20px;
    }}

    .modal-overlay.open {{
      display: flex;
    }}

    .modal-card {{
      background: var(--bg-surface);
      border: 1px solid var(--border);
      border-radius: 14px;
      width: 100%;
      max-width: 780px;
      max-height: 85vh;
      overflow-y: auto;
      box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6);
      padding: 24px;
    }}

    .modal-header {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 20px;
      padding-bottom: 14px;
      border-bottom: 1px solid var(--border);
    }}

    .modal-title {{
      font-size: 18px;
      font-weight: 700;
    }}

    .modal-close {{
      background: none;
      border: none;
      color: var(--text-dim);
      font-size: 22px;
      cursor: pointer;
      line-height: 1;
    }}

    .modal-close:hover {{
      color: var(--text-main);
    }}

    .modal-field {{
      margin-bottom: 16px;
    }}

    .modal-field-label {{
      font-size: 11.5px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--text-dim);
      margin-bottom: 4px;
    }}

    .modal-field-content {{
      background: var(--bg-base);
      border: 1px solid var(--border);
      padding: 12px 14px;
      border-radius: 8px;
      font-size: 13.5px;
      color: var(--text-main);
      line-height: 1.6;
    }}

    .source-tag {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 12px;
      color: #38bdf8;
    }}

    /* Strategic Summary Box */
    .strategy-section {{
      margin-top: 24px;
      background: var(--bg-surface);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 20px 24px;
    }}

    .strategy-title {{
      font-size: 16px;
      font-weight: 700;
      margin-bottom: 12px;
      color: #a5b4fc;
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .strategy-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      gap: 16px;
      margin-top: 14px;
    }}

    .strategy-box {{
      background: var(--bg-base);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 14px 16px;
    }}

    .strategy-box h4 {{
      font-size: 13.5px;
      font-weight: 600;
      color: var(--text-main);
      margin-bottom: 6px;
    }}

    .strategy-box p {{
      font-size: 12.5px;
      color: var(--text-muted);
      line-height: 1.5;
    }}

    @media print {{
      body {{
        background: #fff;
        color: #000;
        padding: 10px;
      }}
      .controls-bar, .header-actions, .modal-overlay {{
        display: none !important;
      }}
      .sheet-card {{
        box-shadow: none;
        border: 1px solid #ddd;
      }}
      table.spec-sheet thead th {{
        background: #f0f0f0;
        color: #000;
      }}
      table.spec-sheet tbody td {{
        color: #000;
        border-color: #eee;
      }}
    }}
  </style>
</head>
<body>
  <div class="container">
    
    <!-- Header -->
    <header class="header">
      <div class="brand-group">
        <div class="brand-badge">⚡</div>
        <div class="title-area">
          <h1>
            GENESIS HARNESS OS (GEN-HARNESS)
            <span class="version-tag">Spec v2.2 LOCKED Audit</span>
          </h1>
          <p>Đối Chiếu Toàn Diện Tiến Độ Hiện Tại vs. Bản Đặc Tả Sản Phẩm Chốt · Tác quyền: <strong>Anh Cơ La (Ryan)</strong></p>
        </div>
      </div>
      <div class="header-actions">
        <button class="btn" onclick="exportCSV()">📥 Xuất CSV</button>
        <button class="btn" onclick="window.print()">🖨️ In / Lưu PDF</button>
        <button class="btn btn-primary" onclick="filterMissing()">⚠️ Lọc Mục Còn Thiếu ({stats['missing_items']})</button>
      </div>
    </header>

    <!-- KPI Metrics Cards -->
    <section class="kpi-grid">
      <div class="kpi-card" style="--card-accent: #6366f1;">
        <div class="kpi-label">Tiến Độ Tổng Thể Toàn Bộ Spec</div>
        <div class="kpi-value-row">
          <div class="kpi-value">{stats['total_pct']}%</div>
          <span style="font-size: 13px; color: #a5b4fc;">{stats['total_items']} Tiêu Chí Đối Chiếu</span>
        </div>
        <div class="progress-bar-wrap">
          <div class="progress-bar-fill" style="width: {stats['total_pct']}%;"></div>
        </div>
        <div class="kpi-desc">Tổng hợp cả Khung sườn kỹ thuật + Năng lực sản phẩm</div>
      </div>

      <div class="kpi-card" style="--card-accent: #10b981;">
        <div class="kpi-label">Khung Kỹ Thuật Chassis & Hạ Tầng</div>
        <div class="kpi-value-row">
          <div class="kpi-value" style="color: #34d399;">{stats['tech_pct']}%</div>
          <span style="font-size: 13px; color: #34d399;">Vững chắc 100% Phase 0</span>
        </div>
        <div class="progress-bar-wrap">
          <div class="progress-bar-fill" style="width: {stats['tech_pct']}%; background: #10b981;"></div>
        </div>
        <div class="kpi-desc">DSH Chassis, 11 Plugins, Policy 5 tầng, PIN, MCP, Doctor PASS</div>
      </div>

      <div class="kpi-card" style="--card-accent: #f59e0b;">
        <div class="kpi-label">Năng Lực Sản Phẩm & Trí Tuệ Hội Thoại</div>
        <div class="kpi-value-row">
          <div class="kpi-value" style="color: #fbbf24;">{stats['product_pct']}%</div>
          <span style="font-size: 13px; color: #fbbf24;">Giai đoạn chuyển mình</span>
        </div>
        <div class="progress-bar-wrap">
          <div class="progress-bar-fill" style="width: {stats['product_pct']}%; background: #f59e0b;"></div>
        </div>
        <div class="kpi-desc">Operating Loop, Data Factory, Living Profile, Opportunity Engine</div>
      </div>

      <div class="kpi-card" style="--card-accent: #06b6d4;">
        <div class="kpi-label">Phân Bổ 45 Hạng Mục Đối Chiếu</div>
        <div style="display: flex; gap: 10px; margin-top: 6px; font-size: 13px; font-weight: 600;">
          <span style="color: #34d399;">🟢 {stats['done_items']} Đạt</span>
          <span style="color: #fbbf24;">🟡 {stats['wip_items']} Đang làm</span>
          <span style="color: #f87171;">🔴 {stats['missing_items']} Thiếu</span>
          <span style="color: #60a5fa;">🔵 {stats['refactor_items']} Đổi tên</span>
        </div>
        <div class="progress-bar-wrap" style="display: flex;">
          <div style="width: {(stats['done_items']/stats['total_items'])*100}%; background: #10b981; height: 100%;"></div>
          <div style="width: {(stats['wip_items']/stats['total_items'])*100}%; background: #f59e0b; height: 100%;"></div>
          <div style="width: {(stats['missing_items']/stats['total_items'])*100}%; background: #ef4444; height: 100%;"></div>
          <div style="width: {(stats['refactor_items']/stats['total_items'])*100}%; background: #3b82f6; height: 100%;"></div>
        </div>
        <div class="kpi-desc">Tập trung lớn nhất nằm ở lớp Business Meaning & Đồ thị quan hệ</div>
      </div>
    </section>

    <!-- Controls Bar -->
    <div class="controls-bar">
      <div class="controls-row-top">
        <div class="search-wrap">
          <span class="search-icon">🔍</span>
          <input type="text" id="searchInput" class="search-input" placeholder="Tìm kiếm tính năng, ID, khoảng cách, từ khóa..." oninput="filterTable()">
        </div>
        <div class="filter-pills">
          <span style="font-size: 12px; color: var(--text-dim); margin-right: 4px;">Trạng thái:</span>
          <div class="pill active" data-status="ALL" onclick="setStatusFilter('ALL', this)">Tất cả (45)</div>
          <div class="pill pill-green" data-status="DONE" onclick="setStatusFilter('DONE', this)">🟢 Đạt Chuẩn ({stats['done_items']})</div>
          <div class="pill pill-amber" data-status="WIP" onclick="setStatusFilter('WIP', this)">🟡 Đang Làm ({stats['wip_items']})</div>
          <div class="pill pill-red" data-status="MISSING" onclick="setStatusFilter('MISSING', this)">🔴 Còn Thiếu ({stats['missing_items']})</div>
          <div class="pill pill-blue" data-status="REFACTOR" onclick="setStatusFilter('REFACTOR', this)">🔵 Tái Cấu Trúc ({stats['refactor_items']})</div>
        </div>
      </div>

      <div class="category-tabs">
        <div class="cat-tab active" data-cat="ALL" onclick="setCategoryFilter('ALL', this)">Tất cả Phân Hệ</div>
        <div class="cat-tab" data-cat="Brand & Identity" onclick="setCategoryFilter('Brand & Identity', this)">Brand & Danh Tính (3)</div>
        <div class="cat-tab" data-cat="Operating Loop" onclick="setCategoryFilter('Operating Loop', this)">Chu Trình 6 Bước (12)</div>
        <div class="cat-tab" data-cat="Console Screens" onclick="setCategoryFilter('Console Screens', this)">10 Màn Hình Console (12)</div>
        <div class="cat-tab" data-cat="Data & SSOT" onclick="setCategoryFilter('Data & SSOT', this)">Dữ Liệu & Hợp Nhất (4)</div>
        <div class="cat-tab" data-cat="MCP & Enterprise" onclick="setCategoryFilter('MCP & Enterprise', this)">MCP & Doanh Nghiệp (4)</div>
        <div class="cat-tab" data-cat="Security & Ethics" onclick="setCategoryFilter('Security & Ethics', this)">Bảo Mật & Đạo Đức (4)</div>
        <div class="cat-tab" data-cat="Phases Roadmap" onclick="setCategoryFilter('Phases Roadmap', this)">Lộ Trình 6 Pha (6)</div>
      </div>
    </div>

    <!-- Sheet Card / Table View -->
    <div class="sheet-card">
      <div class="table-responsive">
        <table class="spec-sheet" id="specTable">
          <thead>
            <tr>
              <th style="width: 85px;">ID Spec</th>
              <th style="width: 140px;">Phân Hệ</th>
              <th style="width: 220px;">Hạng Mục Tính Năng</th>
              <th style="min-width: 290px;">Đặc Tả Yêu Cầu (Spec LOCKED v2.2)</th>
              <th style="min-width: 260px;">Hiện Trạng Heo-Harness Hiện Tại</th>
              <th style="width: 140px;">Trạng Thái</th>
              <th style="width: 130px;">% Đạt</th>
              <th style="min-width: 250px;">Khoảng Cách (Gap) & Việc Cần Làm</th>
            </tr>
          </thead>
          <tbody id="tableBody">
            <!-- Rendered by JS -->
          </tbody>
        </table>
      </div>
    </div>

    <!-- Strategic Insights -->
    <section class="strategy-section">
      <div class="strategy-title">
        <span>💡</span> Nhận Định Chiến Lược & Lộ Trình 3 Bước Để Đạt 100% Gen-Harness OS
      </div>
      <div class="strategy-grid">
        <div class="strategy-box">
          <h4>1. Chuyển Dịch Tên & Đa Danh Tính (Brand & Multi-Agent)</h4>
          <p>Đổi tên nhận diện toàn hệ thống từ <strong>Heo-Harness</strong> sang <strong>Gen-Harness (Genesis Harness OS)</strong>. Tách Bé Heo thành một template tùy chọn; cho phép user tạo và quản lý nhiều Agent Identity (Trợ lý mậu dịch, CSKH, HR) với giọng điệu và mức tự trị độc lập.</p>
        </div>
        <div class="strategy-box">
          <h4>2. Xây Dựng "Conversation Data Factory" (Data & Meaning)</h4>
          <p>Chuyển từ lưu tin nhắn thô (raw chat logs) sang bóc tách Sự kiện nguyên tử (Atomic Events: Hỏi giá, Báo giá, Than phiền, Chốt lịch) và Entity. Đây là điều kiện tiên quyết để tạo <strong>Inbox of Meaning</strong> và <strong>Opportunity Board</strong> đúng nghĩa.</p>
        </div>
        <div class="strategy-box">
          <h4>3. Kích Hoạt Bản Đồ Quan Hệ & Gộp Danh Tính (Graph & Living Profile)</h4>
          <p>Triển khai thuật toán <strong>Identity Resolution</strong> gộp Zalo + WhatsApp thành 1 người thật duy nhất. Tích hợp trực quan hóa Đồ thị mạng lưới quan hệ (Relationship Graph) để lãnh đạo nắm ngay ai đang nắm ball, khách nào đang lạnh.</p>
        </div>
      </div>
    </section>

  </div>

  <!-- Detail Modal -->
  <div class="modal-overlay" id="detailModal" onclick="closeModal(event)">
    <div class="modal-card" onclick="event.stopPropagation()">
      <div class="modal-header">
        <div>
          <span class="version-tag" id="modalId">SPEC-00</span>
          <h3 class="modal-title" id="modalName" style="margin-top: 6px;">Tên Hạng Mục</h3>
        </div>
        <button class="modal-close" onclick="closeModalDirect()">×</button>
      </div>
      <div class="modal-field">
        <div class="modal-field-label">Phân Hệ</div>
        <div style="color: #a5b4fc; font-weight: 600;" id="modalCat"></div>
      </div>
      <div class="modal-field">
        <div class="modal-field-label">Yêu Cầu Đặc Tả (Spec LOCKED v2.2)</div>
        <div class="modal-field-content" id="modalSpec"></div>
      </div>
      <div class="modal-field">
        <div class="modal-field-label">Hiện Trạng Dự Án Hiện Tại</div>
        <div class="modal-field-content" id="modalCurrent"></div>
      </div>
      <div class="modal-field">
        <div class="modal-field-label">Khoảng Cách Kỹ Thuật / Sản Phẩm (Gap Analysis)</div>
        <div class="modal-field-content" style="border-left: 3px solid #f59e0b;" id="modalGap"></div>
      </div>
      <div class="modal-field">
        <div class="modal-field-label">Tài Liệu / File Mã Nguồn Đối Ứng</div>
        <div class="modal-field-content source-tag" id="modalSource"></div>
      </div>
      <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 20px; border-top: 1px solid var(--border); padding-top: 14px;">
        <span id="modalStatusBadge"></span>
        <button class="btn" onclick="closeModalDirect()">Đóng Lại</button>
      </div>
    </div>
  </div>

  <script>
    const AUDIT_DATA = {items_json};
    let currentStatus = 'ALL';
    let currentCategory = 'ALL';
    let searchQuery = '';

    function getStatusClass(status) {{
      switch(status) {{
        case 'DONE': return 'status-done';
        case 'WIP': return 'status-wip';
        case 'MISSING': return 'status-missing';
        case 'REFACTOR': return 'status-refactor';
        default: return '';
      }}
    }}

    function getPctColor(pct) {{
      if (pct >= 80) return '#10b981';
      if (pct >= 40) return '#f59e0b';
      if (pct >= 20) return '#3b82f6';
      return '#ef4444';
    }}

    function renderTable() {{
      const tbody = document.getElementById('tableBody');
      const filtered = AUDIT_DATA.filter(item => {{
        const matchStatus = currentStatus === 'ALL' || item.status === currentStatus;
        const matchCat = currentCategory === 'ALL' || item.category === currentCategory;
        const matchSearch = !searchQuery || 
          item.id.toLowerCase().includes(searchQuery) ||
          item.name.toLowerCase().includes(searchQuery) ||
          item.spec_req.toLowerCase().includes(searchQuery) ||
          item.current_state.toLowerCase().includes(searchQuery) ||
          item.gap.toLowerCase().includes(searchQuery);
        return matchStatus && matchCat && matchSearch;
      }});

      if (filtered.length === 0) {{
        tbody.innerHTML = `<tr><td colspan="8" style="text-align: center; padding: 40px; color: var(--text-dim);">Không tìm thấy tiêu chí nào phù hợp với bộ lọc.</td></tr>`;
        return;
      }}

      tbody.innerHTML = filtered.map(item => {{
        const statusClass = getStatusClass(item.status);
        const pctColor = getPctColor(item.pct);
        return `
          <tr onclick="openModal('${{item.id}}')">
            <td class="col-id">${{item.id}}</td>
            <td class="col-cat"><span class="cat-badge">${{item.category}}</span></td>
            <td class="col-name">${{item.name}}</td>
            <td class="col-spec">${{item.spec_req}}</td>
            <td class="col-current">${{item.current_state}}</td>
            <td class="col-status">
              <span class="status-badge ${{statusClass}}">${{item.status_label}}</span>
            </td>
            <td class="col-pct">
              <div class="pct-row">
                <span class="pct-number" style="color: ${{pctColor}};">${{item.pct}}%</span>
                <div class="pct-bar">
                  <div class="pct-fill" style="width: ${{item.pct}}%; background: ${{pctColor}};"></div>
                </div>
              </div>
            </td>
            <td class="col-gap">${{item.gap}}</td>
          </tr>
        `;
      }}).join('');
    }}

    function setStatusFilter(status, el) {{
      currentStatus = status;
      document.querySelectorAll('.filter-pills .pill').forEach(p => p.classList.remove('active'));
      el.classList.add('active');
      renderTable();
    }}

    function setCategoryFilter(cat, el) {{
      currentCategory = cat;
      document.querySelectorAll('.category-tabs .cat-tab').forEach(t => t.classList.remove('active'));
      el.classList.add('active');
      renderTable();
    }}

    function filterTable() {{
      searchQuery = document.getElementById('searchInput').value.trim().toLowerCase();
      renderTable();
    }}

    function filterMissing() {{
      currentStatus = 'MISSING';
      document.querySelectorAll('.filter-pills .pill').forEach(p => {{
        if (p.dataset.status === 'MISSING') p.classList.add('active');
        else p.classList.remove('active');
      }});
      renderTable();
    }}

    function openModal(id) {{
      const item = AUDIT_DATA.find(x => x.id === id);
      if (!item) return;

      document.getElementById('modalId').innerText = item.id;
      document.getElementById('modalName').innerText = item.name;
      document.getElementById('modalCat').innerText = item.category;
      document.getElementById('modalSpec').innerText = item.spec_req;
      document.getElementById('modalCurrent').innerText = item.current_state;
      document.getElementById('modalGap').innerText = item.gap;
      document.getElementById('modalSource').innerText = item.source_ref;

      const statusClass = getStatusClass(item.status);
      document.getElementById('modalStatusBadge').innerHTML = `
        <span class="status-badge ${{statusClass}}">${{item.status_label}} · ${{item.pct}}% Đạt</span>
      `;

      document.getElementById('detailModal').classList.add('open');
    }}

    function closeModal(e) {{
      document.getElementById('detailModal').classList.remove('open');
    }}

    function closeModalDirect() {{
      document.getElementById('detailModal').classList.remove('open');
    }}

    function exportCSV() {{
      let csv = "ID,Phân Hệ,Tên Tính Năng,Yêu Cầu Spec LOCKED,Hiện Trạng Dự Án,Trạng Thái,% Hoàn Thành,Khoảng Cách (Gap),Mã Nguồn Đối Ứng\\n";
      AUDIT_DATA.forEach(row => {{
        const clean = str => '"' + (str || '').replace(/"/g, '""') + '"';
        csv += [
          clean(row.id),
          clean(row.category),
          clean(row.name),
          clean(row.spec_req),
          clean(row.current_state),
          clean(row.status_label),
          clean(row.pct + "%"),
          clean(row.gap),
          clean(row.source_ref)
        ].join(",") + "\\n";
      }});

      const blob = new Blob([csv], {{ type: 'text/csv;charset=utf-8;' }});
      const link = document.createElement("a");
      link.href = URL.createObjectURL(blob);
      link.setAttribute("download", "Gen-Harness_Spec_Audit_Locked_v2.2.csv");
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }}

    // Initial render
    renderTable();
  </script>
</body>
</html>
"""

output_path_1 = "/home/ryan/heo-harness/artifacts/reports/gen_harness_spec_audit.html"
output_path_2 = "/home/ryan/Documents/Ryan-Workplace/Heo-Harness/artifacts/reports/gen_harness_spec_audit.html"

with open(output_path_1, "w", encoding="utf-8") as f:
    f.write(html_content)

with open(output_path_2, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Generated HTML audit sheet successfully at:\n  - {output_path_1}\n  - {output_path_2}")
