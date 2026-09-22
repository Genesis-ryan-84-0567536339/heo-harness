import json
import os
from datetime import datetime

log_file = "/home/ryan/heo-harness/data/agent_build_logs.json"
wp_log_file = "/home/ryan/Documents/Ryan-Workplace/Heo-Harness/data/agent_build_logs.json"

with open(log_file, "r", encoding="utf-8") as f:
    logs = json.load(f)

new_entry = {
    "id": "BUILD-20260921-07",
    "timestamp": datetime.now().isoformat(),
    "agent_name": "Antigravity Executive UI/UX Specialist",
    "milestone": "Console Re-Architecture & SSOT Optimization (SPEC v2.2)",
    "title": "Khởi tạo Giao Diện Console Điều Hành Độc Lập Chuẩn 10 Màn Hình SSOT (Không Tổn Hại Mã Nguồn Gốc)",
    "summary": "Tạo giao diện Console tối ưu hoàn toàn mới tại http://127.0.0.1:5088/console và /download/reports/gen_harness_executive_console.html mà không sửa đổi hay gây tổn hại dashboard.html gốc: 1) Thu gọn Sidebar linh hoạt (260px <-> 68px mini icon bar) trả lại 100% diện tích màn hình; 2) Bố cục chuẩn 10 Màn hình Console theo Spec Mục F2; 3) Màn hình 10 Phút North Star (Nhiệt kế hội thoại đa kênh Zalo/WhatsApp, Top 5 đối tượng đáng chú ý, Top 5 tín hiệu thị trường, Data Confidence 94.2%); 4) Đồ thị Obsidian Graph dãn cách hoàn hảo, Deal vệ tinh bán kính 135px quạt đều 360 độ chống va chạm nhãn; 5) Kanban 7 Cột lấp đầy chiều cao viewport; 6) Agent Identity Studio loại bỏ độc tôn Bé Heo; 7) Universal Conversation Trace Modal soi chứng cứ chat gốc tức thì.",
    "specs_completed": [
        "SPEC-01",
        "SPEC-02",
        "SPEC-19",
        "SPEC-22",
        "SPEC-20"
    ],
    "files_modified": [
        "artifacts/reports/gen_harness_executive_console.html",
        "heo_harness/plugins/ui_dashboard/__init__.py",
        "data/agent_build_logs.json"
    ],
    "verification_status": "./doctor.sh PASS 100% (16/16 tests SSOT), Playwright Screenshots Verified",
    "next_agent_instructions": "Bản giao diện Console tối ưu đã hoạt động trơn tru tại cổng 5088/console. Các ca làm việc sau có thể tham khảo layout này để áp dụng ngược lại vào dashboard.html chính hoặc duy trì phiên bản song song phục vụ Sếp Ryan."
}

logs.append(new_entry)

with open(log_file, "w", encoding="utf-8") as f:
    json.dump(logs, f, ensure_ascii=False, indent=2)

if os.path.exists(os.path.dirname(wp_log_file)):
    with open(wp_log_file, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)

print("[OK] Đã ghi nhật ký BUILD-20260921-07 thành công!")
