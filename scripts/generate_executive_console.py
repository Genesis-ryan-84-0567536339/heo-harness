#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gen-Harness Executive Console Generator (SSOT Spec v2.2 Compliant)
Tác quyền: Anh Cơ La (genesis.corp.os@gmail.com)
Mục tiêu: Tạo giao diện Console 10 Màn hình độc lập tại artifacts/reports/gen_harness_executive_console.html
Hoàn toàn không sửa đổi dashboard.html gốc hay phá hủy mã nguồn hiện tại.
"""

import os
import shutil

OUTPUT_PATH = "/home/ryan/heo-harness/artifacts/reports/gen_harness_executive_console.html"
WORKPLACE_PATH = "/home/ryan/Documents/Ryan-Workplace/Heo-Harness/artifacts/reports/gen_harness_executive_console.html"

HTML_CONTENT = """<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>GEN-HARNESS — Executive Intelligence Console (SSOT v2.2)</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <script src="https://unpkg.com/@phosphor-icons/web"></script>
  <style>
    :root {
      --bg-base: #07090e;
      --bg-surface: #0e131f;
      --bg-card: #141b2d;
      --bg-card-hover: #1c263f;
      --bg-subtle: rgba(255, 255, 255, 0.03);
      --border-subtle: rgba(255, 255, 255, 0.07);
      --border-focus: rgba(99, 102, 241, 0.5);
      
      --accent-primary: #6366f1;
      --accent-primary-hover: #4f46e5;
      --accent-glow: rgba(99, 102, 241, 0.25);
      
      --accent-success: #10b981;
      --accent-warning: #f59e0b;
      --accent-danger: #f43f5e;
      --accent-cyan: #06b6d4;
      --accent-purple: #a855f7;
      
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
      --text-sub: #64748b;
      
      --sidebar-width: 270px;
      --sidebar-collapsed-width: 72px;
      --topbar-height: 60px;
      --radius-sm: 6px;
      --radius-md: 10px;
      --radius-lg: 14px;
      --transition: all 0.22s cubic-bezier(0.16, 1, 0.3, 1);
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }
    
    body {
      background-color: var(--bg-base);
      color: var(--text-main);
      font-family: 'Plus Jakarta Sans', sans-serif;
      overflow: hidden;
      height: 100vh;
      width: 100vw;
      display: flex;
    }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.12); border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.22); }

    /* LAYOUT SHELL */
    #app-sidebar {
      width: var(--sidebar-width);
      height: 100vh;
      background: var(--bg-surface);
      border-right: 1px solid var(--border-subtle);
      display: flex;
      flex-direction: column;
      flex-shrink: 0;
      transition: var(--transition);
      z-index: 100;
      position: relative;
    }

    #app-sidebar.collapsed {
      width: var(--sidebar-collapsed-width);
    }

    #app-sidebar.collapsed .hide-on-collapse {
      display: none !important;
    }

    #app-sidebar.collapsed .sidebar-header {
      justify-content: center;
      padding: 0 12px;
    }

    #app-sidebar.collapsed .nav-item {
      justify-content: center;
      padding: 10px 0;
    }

    #app-sidebar.collapsed .nav-item i {
      margin-right: 0;
      font-size: 20px;
    }

    #app-sidebar.collapsed .section-title {
      display: none;
    }

    #app-sidebar.collapsed .user-footer-card {
      justify-content: center;
      padding: 10px 0;
    }

    /* Sidebar Brand */
    .sidebar-header {
      height: var(--topbar-height);
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 18px;
      border-bottom: 1px solid var(--border-subtle);
    }

    .brand-group {
      display: flex;
      align-items: center;
      gap: 10px;
      text-decoration: none;
      color: inherit;
    }

    .brand-logo-badge {
      width: 34px;
      height: 34px;
      border-radius: var(--radius-sm);
      background: linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%);
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 0 14px var(--accent-glow);
      color: #fff;
      font-size: 18px;
      font-weight: 800;
      flex-shrink: 0;
    }

    .brand-text h1 {
      font-size: 14px;
      font-weight: 800;
      letter-spacing: 0.04em;
      color: #fff;
    }

    .brand-text span {
      font-size: 10px;
      font-family: 'JetBrains Mono', monospace;
      color: var(--accent-cyan);
      background: rgba(6, 182, 212, 0.1);
      padding: 1px 5px;
      border-radius: 4px;
    }

    .sidebar-toggle-btn {
      background: transparent;
      border: 1px solid var(--border-subtle);
      color: var(--text-muted);
      width: 26px;
      height: 26px;
      border-radius: 6px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: var(--transition);
    }

    .sidebar-toggle-btn:hover {
      background: rgba(255,255,255,0.06);
      color: #fff;
      border-color: rgba(255,255,255,0.2);
    }

    /* Navigation Sections */
    .sidebar-nav-container {
      flex: 1;
      overflow-y: auto;
      padding: 14px 10px;
      display: flex;
      flex-direction: column;
      gap: 16px;
    }

    .nav-section {
      display: flex;
      flex-direction: column;
      gap: 2px;
    }

    .section-title {
      font-size: 10px;
      font-weight: 700;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: var(--text-sub);
      padding: 6px 10px;
    }

    .nav-item {
      display: flex;
      align-items: center;
      padding: 8px 12px;
      border-radius: var(--radius-sm);
      color: var(--text-muted);
      text-decoration: none;
      font-size: 13px;
      font-weight: 500;
      cursor: pointer;
      border: 1px solid transparent;
      transition: var(--transition);
      position: relative;
    }

    .nav-item:hover {
      background: var(--bg-subtle);
      color: var(--text-main);
    }

    .nav-item.active {
      background: rgba(99, 102, 241, 0.12);
      color: #fff;
      border-color: rgba(99, 102, 241, 0.3);
      font-weight: 600;
    }

    .nav-item.active i {
      color: var(--accent-primary);
    }

    .nav-item i {
      font-size: 17px;
      margin-right: 11px;
      flex-shrink: 0;
      transition: var(--transition);
    }

    .nav-badge {
      margin-left: auto;
      font-size: 10px;
      padding: 2px 7px;
      border-radius: 999px;
      font-family: 'JetBrains Mono', monospace;
      font-weight: 600;
      background: rgba(255,255,255,0.06);
      color: var(--text-muted);
    }

    .nav-badge.hot {
      background: rgba(244, 63, 94, 0.15);
      color: var(--accent-danger);
    }

    .nav-badge.live {
      background: rgba(16, 185, 129, 0.15);
      color: var(--accent-success);
    }

    /* Sidebar Footer User Info */
    .sidebar-footer {
      padding: 12px;
      border-top: 1px solid var(--border-subtle);
      background: rgba(0,0,0,0.15);
    }

    .user-footer-card {
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .user-avatar {
      width: 32px;
      height: 32px;
      border-radius: 50%;
      background: #1e293b;
      border: 1px solid var(--accent-primary);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 12px;
      font-weight: 700;
      color: #fff;
      flex-shrink: 0;
    }

    .user-info h4 {
      font-size: 12px;
      font-weight: 600;
      color: #fff;
    }

    .user-info p {
      font-size: 10px;
      color: var(--text-sub);
    }

    /* MAIN CONTENT VIEWPORT */
    #app-main {
      flex: 1;
      height: 100vh;
      display: flex;
      flex-direction: column;
      overflow: hidden;
      background: var(--bg-base);
    }

    /* TOPBAR */
    #app-topbar {
      height: var(--topbar-height);
      background: var(--bg-surface);
      border-bottom: 1px solid var(--border-subtle);
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 24px;
      flex-shrink: 0;
      gap: 16px;
    }

    .topbar-left {
      display: flex;
      align-items: center;
      gap: 14px;
      min-width: 0;
    }

    .breadcrumb-group {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 13px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .breadcrumb-root {
      color: var(--text-sub);
      font-weight: 500;
    }

    .breadcrumb-sep {
      color: var(--border-subtle);
    }

    .breadcrumb-current {
      color: #fff;
      font-weight: 700;
      display: flex;
      align-items: center;
      gap: 6px;
    }

    .spec-tag {
      font-family: 'JetBrains Mono', monospace;
      font-size: 10px;
      padding: 2px 6px;
      background: rgba(99,102,241,0.12);
      border: 1px solid rgba(99,102,241,0.3);
      color: #a5b4fc;
      border-radius: 4px;
    }

    .topbar-right {
      display: flex;
      align-items: center;
      gap: 10px;
      flex-shrink: 0;
    }

    /* Status Badges */
    .status-pill {
      display: flex;
      align-items: center;
      gap: 6px;
      padding: 5px 10px;
      border-radius: 999px;
      background: rgba(255,255,255,0.04);
      border: 1px solid var(--border-subtle);
      font-size: 11px;
      color: var(--text-muted);
    }

    .status-dot {
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background: var(--accent-success);
      box-shadow: 0 0 8px var(--accent-success);
    }

    /* Agent Identity Switcher */
    .agent-identity-picker {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 4px 10px 4px 6px;
      border-radius: var(--radius-sm);
      background: rgba(99, 102, 241, 0.1);
      border: 1px solid rgba(99, 102, 241, 0.3);
      cursor: pointer;
      transition: var(--transition);
    }

    .agent-identity-picker:hover {
      background: rgba(99, 102, 241, 0.18);
      border-color: rgba(99, 102, 241, 0.5);
    }

    .agent-avatar {
      width: 24px;
      height: 24px;
      border-radius: 5px;
      background: var(--accent-primary);
      display: flex;
      align-items: center;
      justify-content: center;
      color: #fff;
      font-size: 13px;
    }

    .agent-title {
      font-size: 12px;
      font-weight: 600;
      color: #e0e7ff;
    }

    /* Action Buttons */
    .action-link-btn {
      display: flex;
      align-items: center;
      gap: 6px;
      padding: 6px 12px;
      border-radius: var(--radius-sm);
      font-size: 12px;
      font-weight: 600;
      text-decoration: none;
      color: #fff;
      background: rgba(255,255,255,0.06);
      border: 1px solid var(--border-subtle);
      transition: var(--transition);
      cursor: pointer;
    }

    .action-link-btn:hover {
      background: rgba(255,255,255,0.12);
      border-color: rgba(255,255,255,0.25);
    }

    .action-link-btn.primary {
      background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%);
      border: none;
      box-shadow: 0 2px 8px var(--accent-glow);
    }

    .action-link-btn.primary:hover {
      opacity: 0.92;
      transform: translateY(-1px);
    }

    /* VIEW CONTAINER */
    #app-workspace {
      flex: 1;
      overflow-y: auto;
      padding: 24px;
      position: relative;
    }

    .screen-view {
      display: none;
      animation: fadeIn 0.2s ease-out;
    }

    .screen-view.active {
      display: block;
    }

    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(4px); }
      to { opacity: 1; transform: translateY(0); }
    }

    /* SCREEN 1: COMMAND OVERVIEW (10-MINUTE SCREEN) */
    .overview-grid {
      display: flex;
      flex-direction: column;
      gap: 20px;
      max-width: 1600px;
      margin: 0 auto;
    }

    .north-star-banner {
      background: linear-gradient(90deg, rgba(99,102,241,0.12) 0%, rgba(6,182,212,0.05) 100%);
      border: 1px solid rgba(99,102,241,0.25);
      border-radius: var(--radius-md);
      padding: 14px 20px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }

    .banner-text h2 {
      font-size: 15px;
      font-weight: 700;
      color: #fff;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .banner-text p {
      font-size: 12px;
      color: var(--text-muted);
      margin-top: 2px;
    }

    /* 4 KPI Metrics */
    .kpi-row {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 16px;
    }

    .kpi-card {
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-md);
      padding: 18px;
      display: flex;
      flex-direction: column;
      gap: 8px;
      position: relative;
      overflow: hidden;
      transition: var(--transition);
    }

    .kpi-card:hover {
      border-color: rgba(255,255,255,0.18);
      transform: translateY(-2px);
      box-shadow: 0 8px 24px rgba(0,0,0,0.25);
    }

    .kpi-card-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      color: var(--text-muted);
      font-size: 12px;
      font-weight: 600;
    }

    .kpi-value {
      font-size: 28px;
      font-weight: 800;
      color: #fff;
      font-family: 'JetBrains Mono', monospace;
      display: flex;
      align-items: baseline;
      gap: 6px;
    }

    .kpi-sub {
      font-size: 11px;
      color: var(--text-sub);
    }

    /* THERMOMETER & DATA CONFIDENCE */
    .thermometer-row {
      display: grid;
      grid-template-columns: 2fr 1fr;
      gap: 16px;
    }

    .panel-card {
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-md);
      padding: 20px;
      display: flex;
      flex-direction: column;
      gap: 14px;
    }

    .panel-title {
      font-size: 14px;
      font-weight: 700;
      color: #fff;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }

    .channels-thermometer {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
    }

    .channel-heat-item {
      background: var(--bg-card);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-sm);
      padding: 12px 14px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }

    .channel-heat-left {
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .channel-icon-pill {
      width: 32px;
      height: 32px;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 16px;
    }

    .channel-icon-pill.zalo { background: rgba(0, 104, 255, 0.15); color: #38bdf8; }
    .channel-icon-pill.wa { background: rgba(37, 211, 102, 0.15); color: #4ade80; }

    /* TWO COLUMNS: 5 FOCUS ENTITIES & 5 MARKET SIGNALS */
    .two-col-grid {
      display: grid;
      grid-template-columns: 1.2fr 0.8fr;
      gap: 16px;
    }

    .entity-item {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 12px 14px;
      border-radius: var(--radius-sm);
      background: var(--bg-card);
      border: 1px solid var(--border-subtle);
      margin-bottom: 8px;
      transition: var(--transition);
    }

    .entity-item:hover {
      background: var(--bg-card-hover);
      border-color: rgba(255,255,255,0.16);
    }

    .entity-left {
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .heat-pill {
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      font-weight: 700;
      padding: 2px 8px;
      border-radius: 999px;
    }

    .heat-pill.hot { background: rgba(244,63,94,0.18); color: #fb7185; }
    .heat-pill.warm { background: rgba(245,158,11,0.18); color: #fbbf24; }

    /* SCREEN 3: RELATIONSHIP MAP (GRAPH CANVAS FULLSCREEN) */
    .graph-screen-container {
      position: relative;
      height: calc(100vh - var(--topbar-height) - 48px);
      background: #06080d;
      border-radius: var(--radius-md);
      border: 1px solid var(--border-subtle);
      overflow: hidden;
    }

    #graphCanvas {
      width: 100%;
      height: 100%;
      display: block;
      cursor: grab;
    }

    #graphCanvas:active {
      cursor: grabbing;
    }

    /* Floating Graph Controls */
    .graph-top-controls {
      position: absolute;
      top: 16px;
      left: 16px;
      right: 16px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      pointer-events: none;
    }

    .graph-control-group {
      pointer-events: auto;
      display: flex;
      align-items: center;
      gap: 8px;
      background: rgba(14, 19, 31, 0.88);
      backdrop-filter: blur(12px);
      padding: 6px 10px;
      border-radius: var(--radius-sm);
      border: 1px solid var(--border-subtle);
      box-shadow: 0 8px 24px rgba(0,0,0,0.4);
    }

    .graph-search-input {
      background: rgba(255,255,255,0.06);
      border: 1px solid var(--border-subtle);
      color: #fff;
      padding: 6px 10px;
      border-radius: 4px;
      font-size: 12px;
      outline: none;
      width: 180px;
    }

    .graph-search-input:focus {
      border-color: var(--accent-primary);
      width: 220px;
    }

    /* Slide-out Drawer for Filter */
    .filter-drawer {
      position: absolute;
      top: 60px;
      left: 16px;
      width: 280px;
      background: rgba(14, 19, 31, 0.94);
      backdrop-filter: blur(14px);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-md);
      padding: 16px;
      display: flex;
      flex-direction: column;
      gap: 12px;
      box-shadow: 0 16px 36px rgba(0,0,0,0.5);
      transition: var(--transition);
      z-index: 20;
    }

    .filter-drawer.hidden {
      transform: translateX(-310px);
      opacity: 0;
      pointer-events: none;
    }

    /* Floating Legend Badge */
    .legend-floating-card {
      position: absolute;
      bottom: 16px;
      right: 16px;
      background: rgba(14, 19, 31, 0.88);
      backdrop-filter: blur(10px);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-sm);
      padding: 10px 14px;
      font-size: 11px;
      color: var(--text-muted);
      display: flex;
      flex-direction: column;
      gap: 6px;
      box-shadow: 0 6px 18px rgba(0,0,0,0.3);
    }

    .legend-row {
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .legend-color-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
    }

    /* SCREEN 5: KANBAN 7 COLUMNS */
    .kanban-board-container {
      display: grid;
      grid-template-columns: repeat(7, minmax(260px, 1fr));
      gap: 14px;
      overflow-x: auto;
      height: calc(100vh - var(--topbar-height) - 48px);
      padding-bottom: 10px;
    }

    .kanban-col {
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-md);
      display: flex;
      flex-direction: column;
      height: 100%;
      overflow: hidden;
    }

    .kanban-col-header {
      padding: 12px 14px;
      background: rgba(255,255,255,0.02);
      border-bottom: 1px solid var(--border-subtle);
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-size: 12px;
      font-weight: 700;
    }

    .kanban-cards-wrapper {
      flex: 1;
      overflow-y: auto;
      padding: 10px;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }

    .opp-card {
      background: var(--bg-card);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-sm);
      padding: 12px;
      display: flex;
      flex-direction: column;
      gap: 8px;
      cursor: pointer;
      transition: var(--transition);
    }

    .opp-card:hover {
      background: var(--bg-card-hover);
      border-color: rgba(99, 102, 241, 0.4);
      transform: translateY(-2px);
      box-shadow: 0 6px 16px rgba(0,0,0,0.3);
    }

    /* MODAL CONVERSATION TRACE (DRILL-DOWN) */
    .modal-overlay {
      position: fixed;
      inset: 0;
      background: rgba(0,0,0,0.7);
      backdrop-filter: blur(8px);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 1000;
      opacity: 0;
      pointer-events: none;
      transition: var(--transition);
    }

    .modal-overlay.active {
      opacity: 1;
      pointer-events: auto;
    }

    .modal-dialog {
      background: var(--bg-surface);
      border: 1px solid var(--border-focus);
      border-radius: var(--radius-lg);
      width: 740px;
      max-width: 92vw;
      max-height: 88vh;
      display: flex;
      flex-direction: column;
      box-shadow: 0 24px 64px rgba(0,0,0,0.6);
      overflow: hidden;
      transform: scale(0.95);
      transition: var(--transition);
    }

    .modal-overlay.active .modal-dialog {
      transform: scale(1);
    }

    .modal-header {
      padding: 16px 20px;
      border-bottom: 1px solid var(--border-subtle);
      display: flex;
      align-items: center;
      justify-content: space-between;
    }

    .modal-body {
      padding: 20px;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 16px;
    }

    .chat-bubble-raw {
      background: var(--bg-card);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-sm);
      padding: 14px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 12px;
      line-height: 1.6;
      color: #e2e8f0;
    }

    .ai-reasoning-box {
      background: rgba(99, 102, 241, 0.08);
      border: 1px solid rgba(99, 102, 241, 0.25);
      border-radius: var(--radius-sm);
      padding: 14px;
      font-size: 12px;
    }
  </style>
</head>
<body>

  <!-- SIDEBAR (COLLAPSIBLE) -->
  <aside id="app-sidebar">
    <div class="sidebar-header">
      <a href="#" class="brand-group">
        <div class="brand-logo-badge">G</div>
        <div class="brand-text hide-on-collapse">
          <h1>GEN-HARNESS</h1>
          <span>SPEC v2.2 LOCKED</span>
        </div>
      </a>
      <button class="sidebar-toggle-btn" id="btnToggleSidebar" title="Thu gọn/Mở rộng Sidebar (Phím [)">
        <i class="ph ph-sidebar-simple"></i>
      </button>
    </div>

    <div class="sidebar-nav-container">
      <!-- PHÂN HỆ I: ĐIỀU HÀNH & RA QUYẾT ĐỊNH -->
      <div class="nav-section">
        <div class="section-title">I. Điều Hành & Ra Quyết Định</div>
        <a class="nav-item active" data-screen="overview" onclick="switchScreen('overview')">
          <i class="ph ph-gauge"></i>
          <span class="hide-on-collapse">Command Overview</span>
          <span class="nav-badge live hide-on-collapse">10m</span>
        </a>
        <a class="nav-item" data-screen="inbox" onclick="switchScreen('inbox')">
          <i class="ph ph-tray"></i>
          <span class="hide-on-collapse">Inbox of Meaning</span>
          <span class="nav-badge hot hide-on-collapse">4 việc</span>
        </a>
        <a class="nav-item" data-screen="relationship_map" onclick="switchScreen('relationship_map')">
          <i class="ph ph-graph"></i>
          <span class="hide-on-collapse">Relationship Map & Radar</span>
          <span class="nav-badge hide-on-collapse">Obsidian</span>
        </a>
        <a class="nav-item" data-screen="living_profiles" onclick="switchScreen('living_profiles')">
          <i class="ph ph-user-focus"></i>
          <span class="hide-on-collapse">Living Profiles 360</span>
          <span class="nav-badge hide-on-collapse">9 hồ sơ</span>
        </a>
      </div>

      <!-- PHÂN HỆ II: THƯƠNG MẠI & CON NGƯỜI -->
      <div class="nav-section">
        <div class="section-title">II. Thương Mại & Con Người</div>
        <a class="nav-item" data-screen="opportunities" onclick="switchScreen('opportunities')">
          <i class="ph ph-kanban"></i>
          <span class="hide-on-collapse">Opportunity Board & Matcher</span>
          <span class="nav-badge hide-on-collapse">2.28B</span>
        </a>
        <a class="nav-item" data-screen="people_review" onclick="switchScreen('people_review')">
          <i class="ph ph-users-three"></i>
          <span class="hide-on-collapse">People Review Board</span>
        </a>
        <a class="nav-item" data-screen="care_quality" onclick="switchScreen('care_quality')">
          <i class="ph ph-heartbeat"></i>
          <span class="hide-on-collapse">Care Quality Audit</span>
        </a>
      </div>

      <!-- PHÂN HỆ III: TRI THỨC & HÀNH ĐỘNG -->
      <div class="nav-section">
        <div class="section-title">III. Tri Thức & Hành Động</div>
        <a class="nav-item" data-screen="knowledge" onclick="switchScreen('knowledge')">
          <i class="ph ph-magnifying-glass"></i>
          <span class="hide-on-collapse">Conversation Knowledge</span>
        </a>
        <a class="nav-item" data-screen="workbench" onclick="switchScreen('workbench')">
          <i class="ph ph-compass-tool"></i>
          <span class="hide-on-collapse">Workbench & Autonomy</span>
        </a>
      </div>

      <!-- PHÂN HỆ IV: HỆ THỐNG & ĐA DANH TÍNH -->
      <div class="nav-section">
        <div class="section-title">IV. Đa Danh Tính & Khung Gầm</div>
        <a class="nav-item" data-screen="identities" onclick="switchScreen('identities')">
          <i class="ph ph-fingerprint"></i>
          <span class="hide-on-collapse">Agent Identity Studio</span>
          <span class="nav-badge live hide-on-collapse">SPEC-02</span>
        </a>
      </div>
    </div>

    <!-- SIDEBAR FOOTER -->
    <div class="sidebar-footer">
      <div class="user-footer-card">
        <div class="user-avatar">CL</div>
        <div class="user-info hide-on-collapse">
          <h4>Cola (Anh Cơ La / Ryan)</h4>
          <p>Tác quyền duy nhất · genesis.corp.os</p>
        </div>
      </div>
    </div>
  </aside>

  <!-- MAIN VIEWPORT -->
  <main id="app-main">
    <!-- TOPBAR -->
    <header id="app-topbar">
      <div class="topbar-left">
        <div class="breadcrumb-group">
          <span class="breadcrumb-root">GENESIS HARNESS OS</span>
          <span class="breadcrumb-sep">/</span>
          <span class="breadcrumb-current" id="currentScreenTitle">
            <i class="ph ph-gauge"></i> Command Overview
          </span>
          <span class="spec-tag" id="currentSpecTag">SSOT GOAL · A4</span>
        </div>
      </div>

      <div class="topbar-right">
        <!-- Live status -->
        <div class="status-pill">
          <span class="status-dot"></span>
          <span>11/11 Plugins</span>
        </div>

        <div class="status-pill">
          <i class="ph ph-currency-dollar-simple" style="color:#10b981"></i>
          <span>0đ Token (Antigravity Brain)</span>
        </div>

        <!-- Agent Identity Picker -->
        <div class="agent-identity-picker" onclick="switchScreen('identities')" title="Chuyển đổi hoặc quản trị Bot Identity">
          <div class="agent-avatar"><i class="ph ph-robot"></i></div>
          <div class="agent-title">Trợ Lý Mậu Dịch Pro</div>
          <i class="ph ph-caret-down" style="font-size:10px; color:var(--text-sub)"></i>
        </div>

        <!-- Quick Switchers to Builder & V6 -->
        <a href="/builder" target="_blank" class="action-link-btn" title="Mở Gen-Harness Builder OS">
          <i class="ph ph-hammer"></i>
          <span>Builder OS</span>
        </a>
        <a href="/" target="_blank" class="action-link-btn" title="Mở V6 Executive Console Gốc">
          <i class="ph ph-arrow-square-out"></i>
          <span>V6 Gốc</span>
        </a>
      </div>
    </header>

    <!-- WORKSPACE -->
    <div id="app-workspace">

      <!-- SCREEN 1: COMMAND OVERVIEW (MÀN HÌNH 10 PHÚT - NORTH STAR) -->
      <section id="view-overview" class="screen-view active">
        <div class="overview-grid">
          
          <div class="north-star-banner">
            <div class="banner-text">
              <h2><i class="ph ph-compass" style="color:var(--accent-primary)"></i> Trung Tâm Chỉ Huy 10 Phút (Executive 10-Minute Radar)</h2>
              <p>Hợp nhất dòng chảy hội thoại số đa kênh từ Zalo & WhatsApp. Nhìn toàn cảnh, bắt cơ hội, giải quyết vướng mắc.</p>
            </div>
            <button class="action-link-btn primary" onclick="openTraceModal('TRACE-NOW')">
              <i class="ph ph-lightning"></i> Cập nhật tức thời
            </button>
          </div>

          <!-- 4 KPI CARDS -->
          <div class="kpi-row">
            <div class="kpi-card">
              <div class="kpi-card-header">
                <span>HÀNG ĐỢI Ý NGHĨA CẦN XỬ LÝ</span>
                <i class="ph ph-warning-circle" style="color:var(--accent-danger)"></i>
              </div>
              <div class="kpi-value" style="color:var(--accent-danger)">
                4 <span style="font-size:14px; font-weight:500; color:var(--text-sub)">mục ưu tiên P1/P2</span>
              </div>
              <div class="kpi-sub">1 báo giá chờ duyệt · 1 than phiền · 2 cơ hội nóng</div>
            </div>

            <div class="kpi-card">
              <div class="kpi-card-header">
                <span>TÍN HIỆU CƠ HỘI PIPELINE</span>
                <i class="ph ph-chart-line-up" style="color:var(--accent-success)"></i>
              </div>
              <div class="kpi-value" style="color:var(--accent-success)">
                2.28 <span style="font-size:15px; font-weight:600">Tỷ đ</span>
              </div>
              <div class="kpi-sub">12 cơ hội đang vận hành · 240Tr đã chốt (Won)</div>
            </div>

            <div class="kpi-card">
              <div class="kpi-card-header">
                <span>MỐI QUAN HỆ & HỒ SƠ ACTIVE</span>
                <i class="ph ph-users" style="color:var(--accent-cyan)"></i>
              </div>
              <div class="kpi-value" style="color:var(--accent-cyan)">
                26 <span style="font-size:14px; font-weight:500; color:var(--text-sub)">nodes mạng lưới</span>
              </div>
              <div class="kpi-sub">4 Khách VIP Nóng (≥80°) · 3 Đối tác ấm · 2 Cần Follow</div>
            </div>

            <div class="kpi-card">
              <div class="kpi-card-header">
                <span>ĐỘ TIN CẬY DỮ LIỆU (CONFIDENCE)</span>
                <i class="ph ph-shield-check" style="color:var(--accent-purple)"></i>
              </div>
              <div class="kpi-value" style="color:var(--accent-purple)">
                94.2<span style="font-size:18px">%</span>
              </div>
              <div class="kpi-sub">Giải thích minh bạch 100% · Drill-down bằng chứng gốc</div>
            </div>
          </div>

          <!-- THERMOMETER & DATA CONFIDENCE ROW -->
          <div class="thermometer-row">
            <div class="panel-card">
              <div class="panel-title">
                <span><i class="ph ph-broadcast" style="color:var(--accent-cyan)"></i> Nhiệt Kế Hội Thoại Đa Kênh (Live Conversation Thermometer)</span>
                <span class="spec-tag">SPEC-04 · SPEC-05</span>
              </div>
              <div class="channels-thermometer">
                <div class="channel-heat-item">
                  <div class="channel-heat-left">
                    <div class="channel-icon-pill zalo"><i class="ph ph-chat-circle-dots"></i></div>
                    <div>
                      <div style="font-size:13px; font-weight:700; color:#fff">Zalo Cá Nhân (Gateway)</div>
                      <div style="font-size:11px; color:var(--text-sub)">4 nhóm · 18 tin nhắn hôm nay</div>
                    </div>
                  </div>
                  <span class="heat-pill hot">Nhiệt độ 88°</span>
                </div>

                <div class="channel-heat-item">
                  <div class="channel-heat-left">
                    <div class="channel-icon-pill wa"><i class="ph ph-whatsapp-logo"></i></div>
                    <div>
                      <div style="font-size:13px; font-weight:700; color:#fff">WhatsApp Multi-Device</div>
                      <div style="font-size:11px; color:var(--text-sub)">2 đối tác quốc tế · Baileys Live</div>
                    </div>
                  </div>
                  <span class="heat-pill warm">Nhiệt độ 75°</span>
                </div>
              </div>
            </div>

            <div class="panel-card">
              <div class="panel-title">
                <span><i class="ph ph-cpu" style="color:var(--accent-primary)"></i> Mức Độ Tự Trị & An Toàn</span>
                <span class="spec-tag">E11 · RBAC</span>
              </div>
              <div style="display:flex; flex-direction:column; gap:8px;">
                <div style="display:flex; justify-content:space-between; font-size:12px;">
                  <span style="color:var(--text-muted)">Cấp độ tự trị hiện tại:</span>
                  <strong style="color:var(--accent-cyan)">Cấp 3 (Soạn sẵn chờ duyệt)</strong>
                </div>
                <div style="background:rgba(255,255,255,0.06); height:6px; border-radius:3px; overflow:hidden">
                  <div style="background:var(--accent-cyan); width:60%; height:100%"></div>
                </div>
                <div style="font-size:11px; color:var(--text-sub)">Tường lửa Policy Gate 5 tầng bảo vệ 100% tài chính và danh dự của Sếp.</div>
              </div>
            </div>
          </div>

          <!-- TWO COLUMNS: 5 FOCUS ENTITIES & 5 MARKET SIGNALS -->
          <div class="two-col-grid">
            <div class="panel-card">
              <div class="panel-title">
                <span><i class="ph ph-crosshair" style="color:var(--accent-danger)"></i> 5 Đối Tượng Đáng Chú Ý Nhất Hôm Nay (Key Focus Entities)</span>
                <span class="spec-tag">F2.1 · SSOT</span>
              </div>

              <div class="entity-item">
                <div class="entity-left">
                  <span class="heat-pill hot">95°</span>
                  <div>
                    <div style="font-size:13px; font-weight:700; color:#fff">Chị Thảo (Viễn Thông Viettel)</div>
                    <div style="font-size:11px; color:var(--text-sub)">Hỏi giá nhận diện AI & Giọng đọc độc quyền · 85 Tr đ</div>
                  </div>
                </div>
                <button class="action-link-btn" onclick="openTraceModal('CNT-005')">
                  <i class="ph ph-magnifying-glass"></i> Soi chứng cứ
                </button>
              </div>

              <div class="entity-item">
                <div class="entity-left">
                  <span class="heat-pill hot">92°</span>
                  <div>
                    <div style="font-size:13px; font-weight:700; color:#fff">Anh Hoàng Bách (LogiTech Executive)</div>
                    <div style="font-size:11px; color:var(--text-sub)">Cần giải pháp AI Điều Phối Tin Nhắn Đa Kênh · 185 Tr đ</div>
                  </div>
                </div>
                <button class="action-link-btn" onclick="openTraceModal('CNT-002')">
                  <i class="ph ph-magnifying-glass"></i> Soi chứng cứ
                </button>
              </div>

              <div class="entity-item">
                <div class="entity-left">
                  <span class="heat-pill hot">88°</span>
                  <div>
                    <div style="font-size:13px; font-weight:700; color:#fff">Tập Đoàn Tân Á (Holdings)</div>
                    <div style="font-size:11px; color:var(--text-sub)">Đã chốt bản quyền Gen-Harness Doanh Nghiệp · 240 Tr đ</div>
                  </div>
                </div>
                <button class="action-link-btn" onclick="openTraceModal('CNT-008')">
                  <i class="ph ph-magnifying-glass"></i> Soi chứng cứ
                </button>
              </div>

              <div class="entity-item">
                <div class="entity-left">
                  <span class="heat-pill warm">62°</span>
                  <div>
                    <div style="font-size:13px; font-weight:700; color:#fff">Trần Thu Hà (Hợp Tác Cung Ứng)</div>
                    <div style="font-size:11px; color:var(--text-sub)">Nhu cầu gia công & Tích hợp ERP/CRM · 1.2 Tỷ đ (Cần Follow)</div>
                  </div>
                </div>
                <button class="action-link-btn" onclick="openTraceModal('CNT-003')">
                  <i class="ph ph-magnifying-glass"></i> Soi chứng cứ
                </button>
              </div>
            </div>

            <div class="panel-card">
              <div class="panel-title">
                <span><i class="ph ph-trend-up" style="color:var(--accent-success)"></i> 5 Tín Hiệu Thị Trường Đang Nổi (Market Signals)</span>
                <span class="spec-tag">E3 · OPPORTUNITY</span>
              </div>

              <div style="display:flex; flex-direction:column; gap:10px;">
                <div style="padding:10px; background:var(--bg-card); border-radius:6px; font-size:12px;">
                  <div style="font-weight:600; color:#fff; display:flex; justify-content:space-between">
                    <span>1. Tích hợp AI vào Zalo Bán Hàng</span>
                    <span style="color:var(--accent-success)">+300% hỏi giá</span>
                  </div>
                  <div style="color:var(--text-sub); margin-top:4px">Nhu cầu auto-reply thông minh có kiểm soát theo tag.</div>
                </div>

                <div style="padding:10px; background:var(--bg-card); border-radius:6px; font-size:12px;">
                  <div style="font-weight:600; color:#fff; display:flex; justify-content:space-between">
                    <span>2. Đồng bộ Kho ERP với Chat WhatsApp</span>
                    <span style="color:var(--accent-cyan)">MCP Connector</span>
                  </div>
                  <div style="color:var(--text-sub); margin-top:4px">Khách thương mại muốn tra cứu tồn kho ngay trong đoạn chat.</div>
                </div>

                <div style="padding:10px; background:var(--bg-card); border-radius:6px; font-size:12px;">
                  <div style="font-weight:600; color:#fff; display:flex; justify-content:space-between">
                    <span>3. Đồ họa Obsidian Graph Quan Hệ</span>
                    <span style="color:var(--accent-purple)">Trực quan hóa</span>
                  </div>
                  <div style="color:var(--text-sub); margin-top:4px">Quản trị toàn bộ vệ tinh deal theo từng đối tác trọng yếu.</div>
                </div>
              </div>
            </div>
          </div>

        </div>
      </section>

      <!-- SCREEN 3: RELATIONSHIP MAP (GRAPH CANVAS DÃN KHOẢNG CÁCH HOÀN HẢO) -->
      <section id="view-relationship_map" class="screen-view">
        <div class="graph-screen-container">
          <canvas id="graphCanvas"></canvas>

          <!-- Top Floating Controls -->
          <div class="graph-top-controls">
            <div class="graph-control-group">
              <button class="action-link-btn" id="btnToggleFilterDrawer" onclick="toggleFilterDrawer()">
                <i class="ph ph-sliders"></i> Bộ lọc giảm nhiễu
              </button>
              <input type="text" class="graph-search-input" id="graphSearchInput" placeholder="Tìm node, đối tác, deal..." oninput="onGraphSearch(this.value)">
            </div>

            <div class="graph-control-group">
              <button class="action-link-btn" onclick="zoomGraph(1.2)" title="Phóng to"><i class="ph ph-plus"></i></button>
              <button class="action-link-btn" onclick="zoomGraph(0.8)" title="Thu nhỏ"><i class="ph ph-minus"></i></button>
              <button class="action-link-btn" onclick="resetGraphView()" title="Căn giữa"><i class="ph ph-arrows-out-cardinal"></i> Căn Giữa</button>
            </div>
          </div>

          <!-- Slide-out Filter Drawer -->
          <div class="filter-drawer hidden" id="filterDrawer">
            <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid var(--border-subtle); padding-bottom:8px;">
              <strong style="font-size:13px; color:#fff"><i class="ph ph-funnel"></i> BỘ LỌC GIẢM NHIỄU</strong>
              <button onclick="toggleFilterDrawer()" style="background:transparent; border:none; color:var(--text-sub); cursor:pointer"><i class="ph ph-x"></i></button>
            </div>

            <div style="display:flex; flex-direction:column; gap:8px; font-size:12px;">
              <label style="display:flex; align-items:center; gap:8px; cursor:pointer;">
                <input type="checkbox" id="chkHot" checked onchange="redrawGraph()">
                <span style="color:#fb7185">● Khách Nóng VIP (≥80°)</span>
              </label>
              <label style="display:flex; align-items:center; gap:8px; cursor:pointer;">
                <input type="checkbox" id="chkWarm" checked onchange="redrawGraph()">
                <span style="color:#fbbf24">● Đối Tác Ấm (50-79°)</span>
              </label>
              <label style="display:flex; align-items:center; gap:8px; cursor:pointer;">
                <input type="checkbox" id="chkDeals" checked onchange="redrawGraph()">
                <span style="color:#c084fc">● Deal Vệ Tinh (Hợp đồng)</span>
              </label>
              <label style="display:flex; align-items:center; gap:8px; cursor:pointer;">
                <input type="checkbox" id="chkChannels" checked onchange="redrawGraph()">
                <span style="color:#38bdf8">● Nhóm & Kênh Chat</span>
              </label>
            </div>

            <div style="margin-top:8px; padding-top:8px; border-top:1px solid var(--border-subtle); font-size:11px; color:var(--text-sub)">
              Mẹo: Nhấp đúp vào bất kỳ node nào để mở hồ sơ sống 360 và soi câu chat gốc.
            </div>
          </div>

          <!-- Floating Legend Badge -->
          <div class="legend-floating-card">
            <div style="font-weight:700; color:#fff; margin-bottom:2px">CHÚ GIẢI OBSIDIAN GRAPH</div>
            <div class="legend-row"><span class="legend-color-dot" style="background:#818cf8"></span> Tâm: HQ Anh Cơ La (Ryan)</div>
            <div class="legend-row"><span class="legend-color-dot" style="background:#fb7185"></span> Đông-Bắc: Khách Nóng VIP (≥80°)</div>
            <div class="legend-row"><span class="legend-color-dot" style="background:#fbbf24"></span> Đông-Nam: Đối Tác Ấm (50-79°)</div>
            <div class="legend-row"><span class="legend-color-dot" style="background:#c084fc"></span> Tím: Deal Vệ Tinh Tỏa Tròn 140px</div>
          </div>
        </div>
      </section>

      <!-- SCREEN 5: OPPORTUNITY BOARD & MATCHER (KANBAN 7 CỘT) -->
      <section id="view-opportunities" class="screen-view">
        <div class="kanban-board-container" id="kanbanContainer">
          <!-- Render dynamically via JS -->
        </div>
      </section>

      <!-- SCREEN 10: AGENT IDENTITY STUDIO (SPEC-02 & E13) -->
      <section id="view-identities" class="screen-view">
        <div style="max-width:1200px; margin:0 auto; display:flex; flex-direction:column; gap:20px;">
          <div class="north-star-banner">
            <div class="banner-text">
              <h2><i class="ph ph-fingerprint" style="color:var(--accent-primary)"></i> Agent Identity Studio (Đa Danh Tính & Không Mặc Định Bé Heo)</h2>
              <p>Tuân thủ tuyệt đối SPEC-02 & Mục E13: User tự định nghĩa tên, vai trò, xưng hô, giọng điệu và phạm vi kênh.</p>
            </div>
            <button class="action-link-btn primary" onclick="alert('Đã sẵn sàng tạo Agent Identity mới!')">
              <i class="ph ph-plus"></i> Tạo Identity Mới
            </button>
          </div>

          <div style="display:grid; grid-template-columns:repeat(3, 1fr); gap:16px;" id="identityCardsGrid">
            <!-- Render cards via JS -->
          </div>
        </div>
      </section>

      <!-- OTHER SCREENS PLACEHOLDER -->
      <section id="view-inbox" class="screen-view">
        <div class="panel-card" style="max-width:1000px; margin:0 auto">
          <div class="panel-title"><span><i class="ph ph-tray"></i> Inbox of Meaning — Hàng Đợi Ý Nghĩa</span><span class="spec-tag">SPEC-17 · F2.2</span></div>
          <div id="inboxMeaningList" style="display:flex; flex-direction:column; gap:10px; margin-top:12px;"></div>
        </div>
      </section>

      <section id="view-living_profiles" class="screen-view">
        <div class="panel-card" style="max-width:1100px; margin:0 auto">
          <div class="panel-title"><span><i class="ph ph-user-focus"></i> Living Profiles 360 (Hồ Sơ Sống Đa Kênh)</span><span class="spec-tag">SPEC-20 · F2.4</span></div>
          <div id="livingProfilesGrid" style="display:grid; grid-template-columns:repeat(2, 1fr); gap:14px; margin-top:12px;"></div>
        </div>
      </section>

      <section id="view-people_review" class="screen-view">
        <div class="panel-card" style="max-width:1100px; margin:0 auto">
          <div class="panel-title"><span><i class="ph ph-users-three"></i> People Review Board (Đánh Giá Con Người)</span><span class="spec-tag">F2.6</span></div>
          <p style="font-size:13px; color:var(--text-muted); margin-top:6px;">Bảng quan sát 4 nhóm: Nhân viên, Khách hàng, Ứng viên và Học viên từ hành vi trao đổi thật trên Zalo/WhatsApp.</p>
        </div>
      </section>

      <section id="view-care_quality" class="screen-view">
        <div class="panel-card" style="max-width:1100px; margin:0 auto">
          <div class="panel-title"><span><i class="ph ph-heartbeat"></i> Care Quality Audit (Kiểm Định Cách Chăm Sóc)</span><span class="spec-tag">F2.7</span></div>
          <p style="font-size:13px; color:var(--text-muted); margin-top:6px;">Đo lường độ trễ phản hồi, tỷ lệ follow sau báo giá, phát hiện khách bị bỏ rơi trước khi mất deal.</p>
        </div>
      </section>

      <section id="view-knowledge" class="screen-view">
        <div class="panel-card" style="max-width:1100px; margin:0 auto">
          <div class="panel-title"><span><i class="ph ph-magnifying-glass"></i> Conversation Knowledge & Search (Kho Hội Thoại Có Não)</span><span class="spec-tag">F2.8</span></div>
          <p style="font-size:13px; color:var(--text-muted); margin-top:6px;">Tìm kiếm hội thoại theo ý định, phân khúc giá, cảm xúc, khách đã từng hỏi báo giá nhưng chưa chốt.</p>
        </div>
      </section>

      <section id="view-workbench" class="screen-view">
        <div class="panel-card" style="max-width:1100px; margin:0 auto">
          <div class="panel-title"><span><i class="ph ph-compass-tool"></i> Workbench & Autonomy Control (Bàn Soạn Thảo & Tự Trị)</span><span class="spec-tag">F2.9 · E11</span></div>
          <p style="font-size:13px; color:var(--text-muted); margin-top:6px;">Soạn thảo tự động báo giá, hợp đồng, dịch thuật đàm phán mậu dịch với 5 cấp độ tự trị có kiểm soát.</p>
        </div>
      </section>

    </div>
  </main>

  <!-- UNIVERSAL CONVERSATION TRACE MODAL (DRILL-DOWN CHỨNG CỨ GỐC) -->
  <div class="modal-overlay" id="traceModal">
    <div class="modal-dialog">
      <div class="modal-header">
        <div style="display:flex; align-items:center; gap:10px;">
          <i class="ph ph-tree-structure" style="color:var(--accent-primary); font-size:20px;"></i>
          <div>
            <h3 style="font-size:14px; font-weight:700; color:#fff" id="modalTraceTitle">Soi Chứng Cứ Gốc & Explainable AI</h3>
            <p style="font-size:11px; color:var(--text-sub)" id="modalTraceSubtitle">Trích xuất hội thoại nguyên văn từ Zalo Gateway</p>
          </div>
        </div>
        <button onclick="closeTraceModal()" style="background:transparent; border:none; color:var(--text-muted); cursor:pointer; font-size:18px"><i class="ph ph-x"></i></button>
      </div>

      <div class="modal-body">
        <div>
          <span style="font-size:11px; font-weight:700; color:var(--text-sub); text-transform:uppercase; letter-spacing:0.06em">Đoạn Chat Zalo Gốc (Verbatim Proof)</span>
          <div class="chat-bubble-raw" id="modalRawChat">
            [14:22:15] Chị Thảo (Viễn Thông Viettel): "Anh Cơ La ơi, bên em đang cần triển khai bộ nhận diện thương hiệu AI và tạo 3 giọng đọc độc quyền cho hệ thống tổng đài CSKH VIP. Nhờ bên anh gửi báo giá gấp trong ngày mai nhé!"
          </div>
        </div>

        <div class="ai-reasoning-box">
          <div style="font-weight:700; color:#c7d2fe; display:flex; align-items:center; gap:6px; margin-bottom:6px">
            <i class="ph ph-sparkle"></i> Vì Sao Hệ Thống Chấm Điểm Này? (Explainable AI Rationale)
          </div>
          <div style="color:var(--text-muted); line-height:1.5;" id="modalReasoningText">
            - <strong>Ý định (Intent):</strong> Hỏi Báo Giá Cấp Bách (Quote Request - Urgent).<br>
            - <strong>Thực thể trích xuất:</strong> Dịch vụ Voice AI, 3 Giọng Độc Quyền, Khách VIP Viettel.<br>
            - <strong>Điểm số Nhiệt độ:</strong> 95° (Rất Nóng do có từ khóa chốt deadline 'ngày mai', thẩm quyền cấp quyết định).<br>
            - <strong>Khuyến nghị hành động:</strong> Sinh báo giá Word tự động qua <code>heo-tool-office-reporter</code> và chuyển Sếp Ryan duyệt.
          </div>
        </div>

        <div style="display:flex; justify-content:flex-end; gap:10px; margin-top:8px;">
          <button class="action-link-btn" onclick="closeTraceModal()">Đóng</button>
          <button class="action-link-btn primary" onclick="alert('Đã kích hoạt tạo báo giá tự động!'); closeTraceModal();">
            <i class="ph ph-file-doc"></i> Sinh Báo Giá Khớp Lệnh Ngay
          </button>
        </div>
      </div>
    </div>
  </div>

  <script>
    // GLOBAL STATE
    const state = {
      sidebarCollapsed: false,
      currentScreen: 'overview',
      nodes: [],
      edges: [],
      opportunities: [],
      contacts: [],
      identities: [
        { id: 'ident-01', name: 'Trợ Lý Mậu Dịch Pro', role: 'Thương Mại & Đàm Phán', tone: 'Chuẩn mực, quyết đoán, nhạy bén', channels: ['zalo', 'whatsapp'], level: 3, isDefault: true },
        { id: 'ident-02', name: 'Key Account Junior', role: 'Chăm Sóc & Follow Khách', tone: 'Ân cần, tỉ mỉ, nhanh nhẹn', channels: ['zalo'], level: 2, isDefault: false },
        { id: 'ident-03', name: 'Admin Hậu Cần Thông Tin', role: 'Lịch Hẹn, Báo Giá, Văn Bản', tone: 'Ngắn gọn, chính xác, lịch thiệp', channels: ['zalo', 'whatsapp'], level: 4, isDefault: false },
        { id: 'ident-04', name: 'Bé Heo (Hoài Niệm)', role: 'Persona Thân Thiết', tone: 'Dạ em chào Sếp Cơ La 🐷', channels: ['internal'], level: 1, isDefault: false, isOptional: true }
      ]
    };

    // SIDEBAR TOGGLE
    const sidebar = document.getElementById('app-sidebar');
    const btnToggleSidebar = document.getElementById('btnToggleSidebar');

    function toggleSidebar() {
      state.sidebarCollapsed = !state.sidebarCollapsed;
      sidebar.classList.toggle('collapsed', state.sidebarCollapsed);
      if (state.currentScreen === 'relationship_map') {
        setTimeout(resizeCanvas, 240);
      }
    }

    btnToggleSidebar.addEventListener('click', toggleSidebar);
    document.addEventListener('keydown', (e) => {
      if (e.key === '[' && !['INPUT', 'TEXTAREA'].includes(e.target.tagName)) {
        toggleSidebar();
      } else if (e.key === 'Escape') {
        closeTraceModal();
      }
    });

    // SCREEN SWITCHER
    const screenTitles = {
      overview: { title: 'Command Overview', icon: 'ph-gauge', spec: 'SSOT GOAL · A4' },
      inbox: { title: 'Inbox of Meaning', icon: 'ph-tray', spec: 'SPEC-17 · F2.2' },
      relationship_map: { title: 'Relationship Map & Radar', icon: 'ph-graph', spec: 'SPEC-19 · F2.3' },
      living_profiles: { title: 'Living Profiles 360', icon: 'ph-user-focus', spec: 'SPEC-20 · F2.4' },
      opportunities: { title: 'Opportunity Board & Matcher', icon: 'ph-kanban', spec: 'SPEC-22 · F2.5' },
      people_review: { title: 'People Review Board', icon: 'ph-users-three', spec: 'F2.6' },
      care_quality: { title: 'Care Quality Audit', icon: 'ph-heartbeat', spec: 'F2.7' },
      knowledge: { title: 'Conversation Knowledge & Search', icon: 'ph-magnifying-glass', spec: 'F2.8' },
      workbench: { title: 'Workbench & Autonomy Control', icon: 'ph-compass-tool', spec: 'F2.9 · E11' },
      identities: { title: 'Agent Identity Studio', icon: 'ph-fingerprint', spec: 'SPEC-02 · E13' }
    };

    function switchScreen(screenId) {
      state.currentScreen = screenId;
      document.querySelectorAll('.screen-view').forEach(el => el.classList.remove('active'));
      const target = document.getElementById('view-' + screenId);
      if (target) target.classList.add('active');

      document.querySelectorAll('.nav-item').forEach(el => {
        el.classList.toggle('active', el.dataset.screen === screenId);
      });

      const meta = screenTitles[screenId] || { title: screenId, icon: 'ph-app-window', spec: 'CONSOLE' };
      document.getElementById('currentScreenTitle').innerHTML = `<i class="ph ${meta.icon}"></i> ${meta.title}`;
      document.getElementById('currentSpecTag').textContent = meta.spec;

      if (screenId === 'relationship_map') {
        setTimeout(() => {
          resizeCanvas();
          initGraphSimulation();
        }, 100);
      } else if (screenId === 'opportunities') {
        renderKanban();
      } else if (screenId === 'identities') {
        renderIdentities();
      } else if (screenId === 'inbox') {
        renderInbox();
      } else if (screenId === 'living_profiles') {
        renderLivingProfiles();
      }
    }

    // MODAL DRILL-DOWN TRACE
    function openTraceModal(traceId) {
      const modal = document.getElementById('traceModal');
      const title = document.getElementById('modalTraceTitle');
      const sub = document.getElementById('modalTraceSubtitle');
      const chat = document.getElementById('modalRawChat');
      const reason = document.getElementById('modalReasoningText');

      if (traceId === 'CNT-002') {
        title.textContent = 'Soi Chứng Cứ: Anh Hoàng Bách (LogiTech Executive)';
        sub.textContent = 'Kênh WhatsApp Gateway · Nhóm Logistics Partner Group';
        chat.textContent = '[10:15:30] Anh Hoàng Bách: "Chào Ryan, bên anh đang muốn mở rộng 3 chi nhánh logistics mới và cần bộ điều phối tin nhắn đa kênh AI tự động phân bổ deal. Dự toán tầm 180-200 triệu, bên em có sẵn giải pháp không?"';
        reason.innerHTML = '- <strong>Intent:</strong> Tìm Giải Pháp Công Nghệ & Báo Giá.<br>- <strong>Giá trị dự toán:</strong> 185.0 Tr đ.<br>- <strong>Nhiệt độ:</strong> 92° (Khách VIP sẵn sàng ngân sách).';
      } else if (traceId === 'CNT-008') {
        title.textContent = 'Soi Chứng Cứ: Hợp Đồng Tân Á Holdings (240 Tr đ)';
        sub.textContent = 'Kênh Zalo Gateway · Nhóm Dự Án CRM';
        chat.textContent = '[16:40:12] Ban Giám Đốc Tân Á: "Đã hoàn tất ký biên bản nghiệm thu hợp đồng bản quyền Gen-Harness Doanh Nghiệp gói Pro. Kế toán sẽ giải ngân đợt 1 hôm nay."';
        reason.innerHTML = '- <strong>Intent:</strong> Ký Hợp Đồng & Thanh Toán Thành Công (Won Deal).<br>- <strong>Giá trị:</strong> 240.0 Tr đ.<br>- <strong>Trạng thái:</strong> Thành công 100%.';
      } else {
        title.textContent = 'Soi Chứng Cứ: Chị Thảo (Viễn Thông Viettel)';
        sub.textContent = 'Kênh Zalo Gateway · Nhóm Ban Viễn Thông';
        chat.textContent = '[14:22:15] Chị Thảo (Viễn Thông Viettel): "Anh Cơ La ơi, bên em đang cần triển khai bộ nhận diện thương hiệu AI và tạo 3 giọng đọc độc quyền cho hệ thống tổng đài CSKH VIP. Nhờ bên anh gửi báo giá gấp trong ngày mai nhé!"';
        reason.innerHTML = '- <strong>Intent:</strong> Quote Request Urgent.<br>- <strong>Độ nóng:</strong> 95°.<br>- <strong>Hành động tiếp theo:</strong> Soạn thảo báo giá & lên lịch hẹn.';
      }

      modal.classList.add('active');
    }

    function closeTraceModal() {
      document.getElementById('traceModal').classList.remove('active');
    }

    // ==========================================
    // OBSIDIAN GRAPH CANVAS (DÃN KHOẢNG CÁCH HOÀN HẢO)
    // ==========================================
    const canvas = document.getElementById('graphCanvas');
    const ctx = canvas.getContext('2d');
    let graphWidth, graphHeight;
    let graphScale = 0.85;
    let panX = 0, panY = 0;
    let isDragging = false;
    let dragStartX = 0, dragStartY = 0;
    let hoveredNode = null;
    let searchQuery = '';

    function resizeCanvas() {
      const container = canvas.parentElement;
      graphWidth = container.clientWidth;
      graphHeight = container.clientHeight;
      canvas.width = graphWidth * window.devicePixelRatio;
      canvas.height = graphHeight * window.devicePixelRatio;
      ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
      panX = graphWidth / 2;
      panY = graphHeight / 2;
      drawGraph();
    }

    window.addEventListener('resize', () => {
      if (state.currentScreen === 'relationship_map') resizeCanvas();
    });

    function toggleFilterDrawer() {
      document.getElementById('filterDrawer').classList.toggle('hidden');
    }

    function zoomGraph(factor) {
      graphScale = Math.max(0.4, Math.min(2.5, graphScale * factor));
      drawGraph();
    }

    function resetGraphView() {
      graphScale = 0.85;
      panX = graphWidth / 2;
      panY = graphHeight / 2;
      drawGraph();
    }

    function onGraphSearch(val) {
      searchQuery = val.trim().toLowerCase();
      drawGraph();
    }

    // LOAD GRAPH DATA TỪ API HOẶC FALLBACK
    async function initGraphSimulation() {
      try {
        const res = await fetch('/api/relationship/graph');
        const data = await res.json();
        if (data.ok && data.nodes && data.nodes.length > 0) {
          setupNodeCoordinates(data.nodes, data.edges || []);
          return;
        }
      } catch (e) {
        console.warn('Dùng dữ liệu graph chuẩn SSOT:', e);
      }
      setupFallbackGraph();
    }

    function setupNodeCoordinates(rawNodes, rawEdges) {
      state.nodes = rawNodes;
      state.edges = rawEdges;

      // 1. Tọa độ 5 Cụm không gian DÃN RỘNG (Wide Spacing)
      // HQ ở tâm (0, 0)
      // Khách Nóng VIP: Đông-Bắc (+380, -220)
      // Đối Tác Ấm: Đông-Nam (+360, +260)
      // Kênh & Nhóm: Tây (-360, 0)
      // Khách Im Lặng: Tây-Nam (-320, +240)

      const clusterOffsets = {
        'cnt-CNT-005': { x: 320, y: -240 }, // Chị Thảo (Viettel)
        'cnt-CNT-007': { x: 480, y: -160 }, // GĐ Viettel
        'cnt-CNT-001': { x: 520, y: -30 },  // Chị Mai Phương
        'cnt-CNT-002': { x: 440, y: 110 },  // Anh Hoàng Bách

        'cnt-CNT-006': { x: 380, y: 260 },  // Anh Minh Kafi
        'cnt-CNT-008': { x: 200, y: 300 },  // Tập Đoàn Tân Á
        'cnt-CNT-003': { x: 20,  y: 330 },  // Trần Thu Hà

        'cnt-CNT-004': { x: -180, y: 300 }, // Nguyễn Đức Trí
        'cnt-CNT-009': { x: -320, y: 240 }, // Phạm Văn Long

        'grp-zalo-telecom': { x: -360, y: -180 },
        'grp-zalo-crm':     { x: -440, y: -40 },
        'grp-wa-logitech':  { x: -440, y: 80 },
        'grp-wa-fashion':   { x: -340, y: 200 }
      };

      state.nodes.forEach(n => {
        if (n.type === 'hq') {
          n.x = 0; n.y = 0;
        } else if (clusterOffsets[n.id]) {
          n.x = clusterOffsets[n.id].x;
          n.y = clusterOffsets[n.id].y;
        } else {
          n.x = (Math.random() - 0.5) * 600;
          n.y = (Math.random() - 0.5) * 400;
        }
      });

      // 2. DÃN NỞ DEAL VỆ TINH BÁN KÍNH 140px & PHÂN BỔ ĐỀU GÓC 360 ĐỘ (CHỐNG DÍNH CHÙM)
      const dealsByContact = {};
      state.edges.forEach(e => {
        if (e.category === 'deal_link') {
          if (!dealsByContact[e.from]) dealsByContact[e.from] = [];
          dealsByContact[e.from].push(e.to);
        }
      });

      Object.entries(dealsByContact).forEach(([contactId, dealIds]) => {
        const parent = state.nodes.find(n => n.id === contactId);
        if (!parent) return;
        const total = dealIds.length;
        const baseAngle = Math.atan2(parent.y, parent.x); // Hướng ra xa tâm HQ

        dealIds.forEach((dId, idx) => {
          const dealNode = state.nodes.find(n => n.id === dId);
          if (!dealNode) return;
          // Quạt góc 70 độ đối xứng hướng ra ngoài
          const angleOffset = (idx - (total - 1) / 2) * (Math.PI / 3.2);
          const finalAngle = baseAngle + angleOffset;
          const radius = 135; // Khoảng cách dãn rộng thoáng đãng

          dealNode.x = parent.x + Math.cos(finalAngle) * radius;
          dealNode.y = parent.y + Math.sin(finalAngle) * radius;
        });
      });

      drawGraph();
    }

    function setupFallbackGraph() {
      // Fallback chuẩn SSOT nếu API đang tải
      const sampleNodes = [
        { id: 'node-hq', label: 'Anh Cơ La (Ryan) / HQ', type: 'hq', heat: 100, x: 0, y: 0, color: '#818cf8', size: 28 },
        { id: 'cnt-CNT-005', label: 'Chị Thảo (Viễn Thông)', type: 'contact', heat: 95, x: 320, y: -240, color: '#fb7185', size: 20 },
        { id: 'deal-005', label: 'Bộ Nhận Diện AI (85tr)', type: 'deal', x: 440, y: -320, color: '#c084fc', size: 12 },
        { id: 'cnt-CNT-002', label: 'Anh Hoàng Bách', type: 'contact', heat: 92, x: 440, y: 110, color: '#fb7185', size: 20 },
        { id: 'deal-002', label: 'AI Điều Phối Đa Kênh (185tr)', type: 'deal', x: 570, y: 150, color: '#c084fc', size: 12 },
        { id: 'cnt-CNT-008', label: 'Tập Đoàn Tân Á', type: 'contact', heat: 88, x: 200, y: 300, color: '#fbbf24', size: 20 },
        { id: 'deal-008', label: 'Bản Quyền Gen-Harness (240tr)', type: 'deal', x: 240, y: 430, color: '#c084fc', size: 12 },
        { id: 'grp-zalo-crm', label: 'Dự Án CRM (Zalo)', type: 'group', x: -440, y: -40, color: '#38bdf8', size: 16 }
      ];
      const sampleEdges = [
        { from: 'node-hq', to: 'cnt-CNT-005' },
        { from: 'cnt-CNT-005', to: 'deal-005', category: 'deal_link' },
        { from: 'node-hq', to: 'cnt-CNT-002' },
        { from: 'cnt-CNT-002', to: 'deal-002', category: 'deal_link' },
        { from: 'node-hq', to: 'cnt-CNT-008' },
        { from: 'cnt-CNT-008', to: 'deal-008', category: 'deal_link' },
        { from: 'node-hq', to: 'grp-zalo-crm' }
      ];
      setupNodeCoordinates(sampleNodes, sampleEdges);
    }

    function drawGraph() {
      if (!ctx || !graphWidth) return;
      ctx.clearRect(0, 0, graphWidth, graphHeight);

      ctx.save();
      ctx.translate(panX, panY);
      ctx.scale(graphScale, graphScale);

      // 1. Vẽ Edges
      state.edges.forEach(e => {
        const fromNode = state.nodes.find(n => n.id === e.from);
        const toNode = state.nodes.find(n => n.id === e.to);
        if (!fromNode || !toNode) return;

        const isDealLink = e.category === 'deal_link';
        const isHighlight = hoveredNode && (hoveredNode.id === fromNode.id || hoveredNode.id === toNode.id);

        ctx.beginPath();
        ctx.moveTo(fromNode.x, fromNode.y);
        ctx.lineTo(toNode.x, toNode.y);

        if (isDealLink) {
          ctx.strokeStyle = isHighlight ? '#e879f9' : 'rgba(192, 132, 252, 0.45)';
          ctx.lineWidth = isHighlight ? 2 : 1.2;
          ctx.setLineDash([4, 4]);
        } else {
          ctx.strokeStyle = isHighlight ? '#818cf8' : 'rgba(255, 255, 255, 0.12)';
          ctx.lineWidth = isHighlight ? 2.5 : 1;
          ctx.setLineDash([]);
        }
        ctx.stroke();
      });

      // 2. Vẽ Nodes
      state.nodes.forEach(n => {
        const isMatch = searchQuery && n.label.toLowerCase().includes(searchQuery);
        const isHover = hoveredNode && hoveredNode.id === n.id;
        const radius = (n.size || 14) * (isHover ? 1.25 : 1);

        // Glow
        ctx.beginPath();
        ctx.arc(n.x, n.y, radius + (isHover ? 8 : 4), 0, Math.PI * 2);
        ctx.fillStyle = n.color ? n.color + '22' : 'rgba(99,102,241,0.15)';
        ctx.fill();

        // Circle
        ctx.beginPath();
        ctx.arc(n.x, n.y, radius, 0, Math.PI * 2);
        ctx.fillStyle = n.color || '#6366f1';
        ctx.fill();
        ctx.lineWidth = isHover ? 2.5 : 1;
        ctx.strokeStyle = '#fff';
        ctx.stroke();

        // Label Pill Box (Sắc nét, không đè nhau)
        ctx.font = isHover ? 'bold 12px Plus Jakarta Sans' : '11px Plus Jakarta Sans';
        const textMetrics = ctx.measureText(n.label);
        const textWidth = textMetrics.width;
        const paddingX = 6, paddingY = 3;
        const pillY = n.y + radius + 14;

        ctx.fillStyle = 'rgba(7, 9, 14, 0.88)';
        ctx.beginPath();
        ctx.roundRect(n.x - textWidth/2 - paddingX, pillY - 10, textWidth + paddingX*2, 18, 4);
        ctx.fill();
        ctx.strokeStyle = isHover ? '#818cf8' : 'rgba(255,255,255,0.15)';
        ctx.lineWidth = 1;
        ctx.stroke();

        ctx.fillStyle = isHover ? '#fff' : (isMatch ? '#38bdf8' : '#e2e8f0');
        ctx.textAlign = 'center';
        ctx.fillText(n.label, n.x, pillY + 3);
      });

      ctx.restore();
    }

    // CANVAS INTERACTIONS (PAN & ZOOM & CLICK)
    canvas.addEventListener('mousedown', (e) => {
      isDragging = true;
      dragStartX = e.clientX - panX;
      dragStartY = e.clientY - panY;
    });

    window.addEventListener('mousemove', (e) => {
      if (isDragging) {
        panX = e.clientX - dragStartX;
        panY = e.clientY - dragStartY;
        drawGraph();
        return;
      }

      // Check Hover
      const rect = canvas.getBoundingClientRect();
      const mouseX = (e.clientX - rect.left - panX) / graphScale;
      const mouseY = (e.clientY - rect.top - panY) / graphScale;

      let found = null;
      for (const n of state.nodes) {
        const dx = n.x - mouseX;
        const dy = n.y - mouseY;
        if (Math.sqrt(dx*dx + dy*dy) < (n.size || 14) + 6) {
          found = n;
          break;
        }
      }

      if (found !== hoveredNode) {
        hoveredNode = found;
        canvas.style.cursor = found ? 'pointer' : 'grab';
        drawGraph();
      }
    });

    window.addEventListener('mouseup', () => { isDragging = false; });
    canvas.addEventListener('wheel', (e) => {
      e.preventDefault();
      const zoomFactor = e.deltaY < 0 ? 1.08 : 0.92;
      zoomGraph(zoomFactor);
    }, { passive: false });

    canvas.addEventListener('dblclick', () => {
      if (hoveredNode) {
        openTraceModal(hoveredNode.id);
      }
    });

    // ==========================================
    // KANBAN OPPORTUNITY BOARD (7 CỘT CHUẨN SPEC-22)
    // ==========================================
    const KANBAN_COLS = [
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
    }

    // ==========================================
    // AGENT IDENTITY STUDIO (SPEC-02)
    // ==========================================
    function renderIdentities() {
      const grid = document.getElementById('identityCardsGrid');
      grid.innerHTML = state.identities.map(id => `
        <div class="panel-card" style="border-color:${id.isDefault ? 'rgba(99,102,241,0.5)' : 'var(--border-subtle)'}">
          <div class="panel-title">
            <div style="display:flex; align-items:center; gap:8px;">
              <i class="ph ph-robot" style="color:var(--accent-primary); font-size:20px;"></i>
              <div>
                <div style="font-size:14px; font-weight:700; color:#fff">${id.name}</div>
                <div style="font-size:11px; color:var(--text-sub)">${id.role}</div>
              </div>
            </div>
            ${id.isDefault ? '<span class="spec-tag" style="background:rgba(99,102,241,0.2)">MẶC ĐỊNH</span>' : ''}
          </div>
          <div style="font-size:12px; color:var(--text-muted); line-height:1.5;">
            <strong>Giọng điệu:</strong> ${id.tone}
          </div>
          <div style="display:flex; justify-content:space-between; font-size:11px; color:var(--text-sub); border-top:1px solid var(--border-subtle); padding-top:8px;">
            <span>Kênh: <strong>${id.channels.join(', ').toUpperCase()}</strong></span>
            <span>Tự trị: <strong>Cấp ${id.level}</strong></span>
          </div>
          <button class="action-link-btn" style="margin-top:6px; justify-content:center" onclick="selectIdentity('${id.id}')">
            ${id.isDefault ? 'Đang kích hoạt' : 'Chọn danh tính này'}
          </button>
        </div>
      `).join('');
    }

    function selectIdentity(id) {
      state.identities.forEach(i => i.isDefault = (i.id === id));
      const active = state.identities.find(i => i.isDefault);
      if (active) {
        document.querySelector('.agent-title').textContent = active.name;
      }
      renderIdentities();
    }

    // INBOX OF MEANING
    function renderInbox() {
      const list = document.getElementById('inboxMeaningList');
      list.innerHTML = `
        <div class="entity-item" onclick="openTraceModal('CNT-005')">
          <div class="entity-left">
            <span class="heat-pill hot">95°</span>
            <div>
              <div style="font-weight:700; color:#fff">Yêu cầu báo giá: Bộ Nhận Diện AI 3 Giọng Độc Quyền</div>
              <div style="font-size:11px; color:var(--text-sub)">Nguồn: Zalo · Chị Thảo Viettel · Hạn chót: 18h hôm nay</div>
            </div>
          </div>
          <button class="action-link-btn primary">Duyệt & Gửi</button>
        </div>
        <div class="entity-item" onclick="openTraceModal('CNT-002')">
          <div class="entity-left">
            <span class="heat-pill hot">92°</span>
            <div>
              <div style="font-weight:700; color:#fff">Khách hỏi giải pháp AI Điều Phối Tin Nhắn 3 Chi Nhánh</div>
              <div style="font-size:11px; color:var(--text-sub)">Nguồn: WhatsApp · Anh Hoàng Bách LogiTech · Dự toán 185Tr</div>
            </div>
          </div>
          <button class="action-link-btn">Ráp Nối</button>
        </div>
      `;
    }

    // LIVING PROFILES
    function renderLivingProfiles() {
      const grid = document.getElementById('livingProfilesGrid');
      grid.innerHTML = `
        <div class="panel-card" onclick="openTraceModal('CNT-005')">
          <div class="panel-title"><span>Chị Thảo (Viễn Thông Viettel)</span><span class="heat-pill hot">95°</span></div>
          <p style="font-size:12px; color:var(--text-muted); line-height:1.5">
            Key Account VIP ngành viễn thông. Đang phụ trách dự án nâng cấp đài CSKH 2026. Tần suất tương tác: 4 lần/tuần trên Zalo. Chưa từng trễ hẹn.
          </p>
          <div style="font-size:11px; color:var(--text-sub); border-top:1px solid var(--border-subtle); padding-top:6px;">
            Đã chốt: 1 HĐ · Đang mở: 1 Deal 85Tr · Tự trị: Cấp 3
          </div>
        </div>
        <div class="panel-card" onclick="openTraceModal('CNT-002')">
          <div class="panel-title"><span>Anh Hoàng Bách (LogiTech)</span><span class="heat-pill hot">92°</span></div>
          <p style="font-size:12px; color:var(--text-muted); line-height:1.5">
            Giám đốc vận hành chuỗi Logistics quốc tế. Tương tác đa kênh qua WhatsApp + Zalo. Ngân sách công nghệ dồi dào, cần giải pháp nhanh và bảo mật.
          </p>
          <div style="font-size:11px; color:var(--text-sub); border-top:1px solid var(--border-subtle); padding-top:6px;">
            Đang mở: 1 Deal 185Tr · Người chạm: Anh Cơ La
          </div>
        </div>
      `;
    }

    // BOOTSTRAP INIT
    window.addEventListener('DOMContentLoaded', () => {
      renderKanban();
      renderIdentities();
    });
  </script>
</body>
</html>
"""

def main():
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(HTML_CONTENT)
    print(f"[OK] Đã tạo file Console tối ưu: {OUTPUT_PATH} ({len(HTML_CONTENT)} bytes)")

    if os.path.exists(os.path.dirname(WORKPLACE_PATH)):
        with open(WORKPLACE_PATH, "w", encoding="utf-8") as f:
            f.write(HTML_CONTENT)
        print(f"[OK] Đã đồng bộ sang Workplace: {WORKPLACE_PATH}")

if __name__ == "__main__":
    main()
