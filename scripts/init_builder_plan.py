# -*- coding: utf-8 -*-
import json
import os

with open("/home/ryan/heo-harness/data/spec_audit_data.json", "r", encoding="utf-8") as f:
    base_data = json.load(f)

items = base_data["items"]

# Milestone and Priority Mapping
MILESTONE_MAP = {
    "SPEC-01": {"ms": "MS-1", "prio": "P0 - Blocker", "sec": "Mục A, E13", "target": "2026-09-22"},
    "SPEC-02": {"ms": "MS-1", "prio": "P0 - Blocker", "sec": "Mục E13", "target": "2026-09-23"},
    "SPEC-03": {"ms": "MS-1", "prio": "P1 - High", "sec": "Mục E13", "target": "2026-09-24"},
    "SPEC-27": {"ms": "MS-1", "prio": "P0 - Blocker", "sec": "Mục F2.10, E13", "target": "2026-09-24"},
    
    "SPEC-06": {"ms": "MS-2", "prio": "P0 - Blocker", "sec": "Mục E2, G1", "target": "2026-09-26"},
    "SPEC-07": {"ms": "MS-2", "prio": "P0 - Blocker", "sec": "Mục E2, G1", "target": "2026-09-26"},
    "SPEC-08": {"ms": "MS-2", "prio": "P0 - Blocker", "sec": "Mục G3, C1", "target": "2026-09-27"},
    "SPEC-28": {"ms": "MS-2", "prio": "P1 - High", "sec": "Mục G1", "target": "2026-09-28"},
    "SPEC-30": {"ms": "MS-2", "prio": "P1 - High", "sec": "Mục G3", "target": "2026-09-28"},

    "SPEC-11": {"ms": "MS-3", "prio": "P0 - Blocker", "sec": "Mục E3", "target": "2026-10-01"},
    "SPEC-12": {"ms": "MS-3", "prio": "P1 - High", "sec": "Mục E3", "target": "2026-10-02"},
    "SPEC-18": {"ms": "MS-3", "prio": "P0 - Blocker", "sec": "Mục F2.2", "target": "2026-10-03"},
    "SPEC-21": {"ms": "MS-3", "prio": "P0 - Blocker", "sec": "Mục F2.5", "target": "2026-10-04"},
    "SPEC-13": {"ms": "MS-3", "prio": "P1 - High", "sec": "Mục E11", "target": "2026-10-05"},
    "SPEC-14": {"ms": "MS-3", "prio": "P2 - Normal", "sec": "Mục H1", "target": "2026-10-06"},

    "SPEC-19": {"ms": "MS-4", "prio": "P0 - Blocker", "sec": "Mục E4, F2.3", "target": "2026-10-10"},
    "SPEC-20": {"ms": "MS-4", "prio": "P0 - Blocker", "sec": "Mục E5, F2.4", "target": "2026-10-11"},
    "SPEC-29": {"ms": "MS-4", "prio": "P0 - Blocker", "sec": "Mục G2", "target": "2026-10-12"},
    "SPEC-09": {"ms": "MS-4", "prio": "P1 - High", "sec": "Mục E6", "target": "2026-10-13"},
    "SPEC-10": {"ms": "MS-4", "prio": "P1 - High", "sec": "Mục C3, E6", "target": "2026-10-14"},
    "SPEC-24": {"ms": "MS-4", "prio": "P1 - High", "sec": "Mục F2.8", "target": "2026-10-15"},

    "SPEC-22": {"ms": "MS-5", "prio": "P1 - High", "sec": "Mục E7, F2.6", "target": "2026-10-20"},
    "SPEC-23": {"ms": "MS-5", "prio": "P1 - High", "sec": "Mục E8, F2.7", "target": "2026-10-22"},
    "SPEC-15": {"ms": "MS-5", "prio": "P2 - Normal", "sec": "Mục C1.6", "target": "2026-10-25"},
    "SPEC-45": {"ms": "MS-5", "prio": "P2 - Normal", "sec": "Mục L (Phase 5)", "target": "2026-10-30"},
}

builder_items = []
for it in items:
    cid = it["id"]
    m_info = MILESTONE_MAP.get(cid, {"ms": "MS-0 (Foundation)", "prio": "P1 - High", "sec": "Spec Tổng Thể", "target": "2026-09-21"})
    
    # Define checklist for items
    checklist = [
        {"title": "Nghiên cứu & Đối chiếu chuẩn SSOT Spec LOCKED", "done": True},
        {"title": "Xây dựng cấu trúc dữ liệu và API", "done": it["status"] in ["DONE", "WIP"]},
        {"title": "Tích hợp giao diện điều khiển Console", "done": it["status"] == "DONE"},
        {"title": "Kiểm thử tự động `./doctor.sh` và nghiệm thu", "done": it["status"] == "DONE"}
    ]
    
    # Status normalization
    st = it["status"]
    if st == "DONE":
        status_key = "DONE"
        status_text = "🟢 Hoàn Thành"
    elif st == "WIP":
        status_key = "IN_PROGRESS"
        status_text = "🟡 Đang Thi Công"
    elif st == "REFACTOR":
        status_key = "REFACTOR"
        status_text = "🟣 Tái Cấu Trúc Nhận Diện"
    else:
        status_key = "PLANNED" if m_info["ms"] in ["MS-1", "MS-2"] else "BACKLOG"
        status_text = "🔵 Lên Kế Hoạch Sprint" if status_key == "PLANNED" else "⚪ Tồn Đọng (Backlog)"

    builder_items.append({
        "id": cid,
        "category": it["category"],
        "name": it["name"],
        "spec_req": it["spec_req"],
        "spec_section": m_info["sec"],
        "current_state": it["current_state"],
        "status": status_key,
        "status_label": status_text,
        "pct": it["pct"],
        "milestone": m_info["ms"],
        "priority": m_info["prio"],
        "target_date": m_info["target"],
        "owner": "AI Agent & Sếp Cơ La",
        "gap": it["gap"],
        "source_ref": it["source_ref"],
        "dev_notes": f"Tham chiếu trực tiếp Spec LOCKED v2.2 tại {m_info['sec']}.",
        "checklist": checklist
    })

milestones_meta = [
    {
        "id": "MS-1",
        "title": "Chặng 1: Chuẩn Hóa Nhận Diện & Đa Danh Tính (Brand & Multi-Agent Identity)",
        "goal": "Đổi tên sang Gen-Harness, biến Bé Heo thành optional template, xây dựng Agent Identity Studio độc lập.",
        "due": "24/09/2026",
        "status": "ACTIVE_SPRINT",
        "badge": "🚀 Sprint Hiện Tại"
    },
    {
        "id": "MS-2",
        "title": "Chặng 2: Conversation Data Factory & Sự Kiện Nguyên Tử (Data & Atomic Events)",
        "goal": "Tách Thực thể (Entities), Ý định (Intents), và lưu trữ chuỗi Sự kiện nguyên tử (AskedPrice, Complained...).",
        "due": "28/09/2026",
        "status": "QUEUED",
        "badge": "⏳ Kế Tiếp"
    },
    {
        "id": "MS-3",
        "title": "Chặng 3: Hàng Đợi Ý Nghĩa & Bảng Cơ Hội (Inbox of Meaning & Opportunity Board)",
        "goal": "Biến tin nhắn thô thành Thẻ ý nghĩa kèm nút duyệt hành động, dựng Kanban Opportunity Board 7 cột.",
        "due": "06/10/2026",
        "status": "PLANNED",
        "badge": "📋 Đã Lên Lịch"
    },
    {
        "id": "MS-4",
        "title": "Chặng 4: Bản Đồ Quan Hệ & Hồ Sơ Sống Đa Kênh (Graph & Living Profiles)",
        "goal": "Identity Resolution gộp Zalo + WhatsApp; vẽ đồ thị tương tác Node/Edge; AI tóm tắt 8-12 dòng.",
        "due": "15/10/2026",
        "status": "PLANNED",
        "badge": "📋 Đã Lên Lịch"
    },
    {
        "id": "MS-5",
        "title": "Chặng 5: Chất Lượng Chăm Sóc & Mở Rộng Quy Mô (Care Quality & Enterprise Scale)",
        "goal": "Đo độ trễ phản hồi, khách bỏ rơi; People Review 4 board; kết nối mở rộng Telegram, FB, ERP/CRM sâu.",
        "due": "30/10/2026",
        "status": "FUTURE",
        "badge": "🔮 Tầm Nhìn Dài"
    }
]

plan_data = {
    "project_name": "Genesis Harness OS (Gen-Harness)",
    "ssot_spec": "Gen-Harness-Product-Spec-LOCKED.md (v2.2 LOCKED)",
    "owner": "Anh Cơ La (Ryan) — genesis.corp.os@gmail.com",
    "updated_at": "2026-09-21 18:10:00",
    "milestones": milestones_meta,
    "items": builder_items
}

with open("/home/ryan/heo-harness/data/builder_plan.json", "w", encoding="utf-8") as f:
    json.dump(plan_data, f, ensure_ascii=False, indent=2)

print("Initialized data/builder_plan.json with 45 planned items and 5 milestones successfully!")
