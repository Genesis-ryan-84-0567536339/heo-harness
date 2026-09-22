# -*- coding: utf-8 -*-
"""
Script cập nhật tiến độ Chặng 4 (MS-4) trong data/builder_plan.json:
- SPEC-19: [UI-03] Relationship Map -> DONE (100%)
- SPEC-20: [UI-04] Living Profile 360 -> DONE (100%)
- SPEC-10: [CR-06] Explainable AI -> DONE (100%)
- SPEC-24: [UI-08] Knowledge & Search -> DONE (100%)
- Milestone 4: COMPLETED (100%)
"""
import json
import os
import time

plan_file = "/home/ryan/heo-harness/data/builder_plan.json"
with open(plan_file, "r", encoding="utf-8") as f:
    plan = json.load(f)

# Cập nhật Milestone 4
for ms in plan.get("milestones", []):
    if ms.get("id") == "MS-4":
        ms["status"] = "COMPLETED"
        ms["badge"] = "🟢 Đã Hoàn Thành"

# Cập nhật các items/specs của Chặng 4
now_str = time.strftime("%d/%m/%Y %H:%M")
spec_updates = {
    "SPEC-19": {
        "status": "DONE",
        "status_label": "Hoàn thành 100%",
        "pct": 100,
        "dev_notes": "Canvas HTML5 Node/Edge trực quan: HQ Sếp Ryan -> Channels/Groups -> Contacts VIP -> Deals Cơ hội. Tương tác zoom, pan, drag-and-drop, tooltip và click mở hồ sơ 360.",
        "checklist": [
            {"text": "Canvas HTML5 vẽ đồ thị Node/Edge trực quan", "done": True},
            {"text": "Phân tầng HQ -> Kênh/Nhóm -> Đối tác -> Cơ hội Deals", "done": True},
            {"text": "Tương tác kéo thả hạt Node, Zoom in/out, Căn giữa", "done": True},
            {"text": "Bộ lọc nhanh Khách Nóng, Kèm Deals, Tìm kiếm Node", "done": True}
        ]
    },
    "SPEC-20": {
        "status": "DONE",
        "status_label": "Hoàn thành 100%",
        "pct": 100,
        "dev_notes": "Living Profile 360 Drawer/Modal: Tóm tắt AI Executive Summary 8-12 dòng, Timeline sự kiện nguyên tử, Thang đo 6 cấp tự trị (0-6) có API lưu trữ.",
        "checklist": [
            {"text": "Hồ sơ sống 360 đầy đủ kênh liên lạc Zalo/WA/SĐT/Email", "done": True},
            {"text": "Tóm tắt AI Executive Summary 8-12 dòng chuyên sâu", "done": True},
            {"text": "Thang trượt 6 mức tự trị (Autonomy Level 0-6) & lưu API", "done": True},
            {"text": "Dòng thời gian sự kiện nguyên tử tương tác của đối tác", "done": True}
        ]
    },
    "SPEC-10": {
        "status": "DONE",
        "status_label": "Hoàn thành 100%",
        "pct": 100,
        "dev_notes": "Explainable AI: Lập luận minh bạch lý do AI chấm điểm Heat Score, Engagement %, Churn Risk % và Ball Ownership.",
        "checklist": [
            {"text": "Giải thích chi tiết công thức tính điểm nóng/lạnh", "done": True},
            {"text": "Minh bạch yếu tố rủi ro churn và chu kỳ phản hồi", "done": True},
            {"text": "Tích hợp thẳng vào Modal Living Profile 360", "done": True}
        ]
    },
    "SPEC-24": {
        "status": "DONE",
        "status_label": "Hoàn thành 100%",
        "pct": 100,
        "dev_notes": "Chat Intelligence Filter: Bổ sung bộ lọc Intent (Hỏi giá, Khiếu nại, Đặt hẹn, Hợp đồng) và lọc khách hàng Went Silent > 3 ngày.",
        "checklist": [
            {"text": "Bộ lọc Intent trong Chat Intelligence", "done": True},
            {"text": "Nút bật/tắt lọc nhanh khách im lặng > 3 ngày", "done": True}
        ]
    }
}

for it in plan.get("items", []):
    item_id = it.get("id")
    if item_id in spec_updates:
        u = spec_updates[item_id]
        it["status"] = u["status"]
        it["status_label"] = u["status_label"]
        it["pct"] = u["pct"]
        it["dev_notes"] = u["dev_notes"]
        it["checklist"] = u["checklist"]

# Cập nhật updated_at
total_specs = len(plan.get("items", []))
done_specs = len([it for it in plan.get("items", []) if it.get("status") == "DONE"])
overall_pct = round((done_specs / max(1, total_specs)) * 100, 1)

plan["updated_at"] = now_str

with open(plan_file, "w", encoding="utf-8") as f:
    json.dump(plan, f, ensure_ascii=False, indent=2)

print(f"✓ Đã cập nhật builder_plan.json: {done_specs}/{total_specs} SPECs hoàn thành ({overall_pct}%)")
