import json

log_file = "/home/ryan/heo-harness/data/agent_build_logs.json"
wp_log_file = "/home/ryan/Documents/Ryan-Workplace/Heo-Harness/data/agent_build_logs.json"

with open(log_file, "r", encoding="utf-8") as f:
    logs = json.load(f)

for l in logs:
    if l.get("id") == "BUILD-20260921-07":
        l["title"] = "[BẢN TEST / LABS PREVIEW] Khởi tạo Giao Diện Console Điều Hành Thử Nghiệm Chuẩn 10 Màn Hình SSOT (Không Tổn Hại Mã Nguồn Gốc)"
        l["summary"] = "[BẢN TEST / THỬ NGHIỆM ĐỘC LẬP] Tạo giao diện Console thử nghiệm UI/UX tối ưu tại http://127.0.0.1:5088/console và /download/reports/gen_harness_executive_console.html nhằm phục vụ Sếp Ryan đánh giá layout mà hoàn toàn không sửa đổi hay tổn hại dashboard.html gốc: 1) Thu gọn Sidebar linh hoạt (260px <-> 68px); 2) Bố cục 10 Màn hình Console; 3) Màn hình 10 Phút North Star; 4) Đồ thị Obsidian Graph dãn cách 135px chống va chạm nhãn; 5) Kanban 7 Cột lấp đầy viewport; 6) Gắn nhãn BẢN TEST rõ ràng trên toàn bộ giao diện."

with open(log_file, "w", encoding="utf-8") as f:
    json.dump(logs, f, ensure_ascii=False, indent=2)

if os.path.exists(os.path.dirname(wp_log_file)):
    with open(wp_log_file, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)

print("[OK] Đã cập nhật nhãn [BẢN TEST] vào nhật ký BUILD-20260921-07 thành công!")
