# -*- coding: utf-8 -*-
import sqlite3
import os

db_path = "/home/ryan/heo-harness/data/heo.db"
conn = sqlite3.connect(db_path)

# Add owner and win_probability columns if not present
try:
    conn.execute("ALTER TABLE opportunities ADD COLUMN owner TEXT DEFAULT 'Anh Cơ La (Ryan)';")
except Exception:
    pass

try:
    conn.execute("ALTER TABLE opportunities ADD COLUMN win_probability REAL DEFAULT 50.0;")
except Exception:
    pass

try:
    conn.execute("ALTER TABLE atomic_events ADD COLUMN archived INTEGER DEFAULT 0;")
except Exception:
    pass

# Update sample opportunities across the 7 stages so Sếp sees a rich, active Kanban pipeline!
now_str = "2026-09-21 18:30:00"

sample_opps = [
    ("OPP-101", "Cung cấp giải pháp AI Điều Phối Tin Nhắn Đa Kênh", "Anh Hoàng Bách", "CNT-002", "whatsapp", "LogiTech Executive", "Nhu cầu trang bị giải pháp tự động bắt tín hiệu và báo cáo tức thì cho 3 chi nhánh logistics.", 185000000.0, "QUALIFIED", 85.0, 92.0, "Khách có ngân sách sẵn, cần chốt trong tuần tới.", "EVT-9742687", "Anh Cơ La (Ryan)", 75.0),
    ("OPP-102", "Gia công & Tích hợp ERP/CRM sang Hub Điều Hành", "Trần Thu Hà", "CNT-003", "whatsapp", "Hợp Tác Cung Ứng", "Cần kết nối 15 đầu việc từ ERP sang giao diện quản trị điều hành của Ban Giám Đốc.", 1200000000.0, "MATCHED", 80.0, 88.0, "Đã khớp với dịch vụ Enterprise App Connector của Gen-Harness.", "EVT-9742856", "Phòng Kỹ Thuật & Sếp Ryan", 60.0),
    ("OPP-103", "Báo giá Dịch vụ Báo Cáo Tài Chính & Phân Tích Kafi", "Anh Minh (Kafi)", "usr-kafi-01", "zalo", "Chứng khoán Kafi", "Yêu cầu xuất tự động báo cáo Word/Excel định kỳ hàng tuần cho danh mục đầu tư.", 50000000.0, "OUTREACH", 80.0, 85.0, "Đã gửi bản demo sơ bộ, chờ phản hồi feedback.", "EVT-9599405", "Trợ Lý Thương Mại", 70.0),
    ("OPP-104", "Triển khai Bộ Nhận Diện AI & Giọng Đọc Độc Quyền", "Chị Thảo (Viễn Thông)", "CNT-005", "zalo", "Đối Tác Hạ Tầng", "Muốn đặt hàng 3 giọng đọc AI Audio cho tổng đài chăm sóc khách hàng VIP.", 85000000.0, "NEGOTIATING", 90.0, 95.0, "Đang thương thảo chiết khấu thanh toán 1 lần.", "EVT-104", "Anh Cơ La (Ryan)", 85.0),
    ("OPP-105", "Thẩm định Dự án Hạ Tầng Server Cục Bộ Chạy Offline", "Giám Đốc CNTT Viettel", "CNT-006", "manual", "Direct Meeting", "Dự án chạy mô hình Gemini & DeepSeek on-premise an toàn thông tin nội bộ.", 350000000.0, "INTERNAL_REVIEW", 85.0, 80.0, "Đang trình duyệt Ban Giám Đốc phê duyệt bảng thông số kỹ thuật.", "EVT-105", "Anh Cơ La (Ryan)", 80.0),
    ("OPP-106", "Hợp đồng Cung Cấp Bản Quyền Gen-Harness Doanh Nghiệp Gói Pro", "Tập Đoàn Tân Á", "CNT-007", "zalo", "Tân Á Holdings", "Đã ký kết hợp đồng triển khai 1 năm cho 50 nhân viên kinh doanh sử dụng Copilot.", 240000000.0, "WON", 99.0, 100.0, "Đã nhận thanh toán đợt 1 (50%). Đang bàn giao license.", "EVT-106", "Anh Cơ La (Ryan)", 100.0),
    ("OPP-107", "Tín hiệu hỏi thăm gói cước Cloud Server từ nhóm Startup", "Phạm Văn Long", "CNT-008", "zalo", "Cộng Đồng Khởi Nghiệp", "Hỏi xem bên mình có cung cấp máy chủ GPU thuê theo giờ không.", 15000000.0, "RAW_SIGNAL", 60.0, 65.0, "Mới bắt tín hiệu, cần xác thực xem có nhu cầu thật không.", "EVT-107", "Trợ Lý Bán Hàng", 30.0)
]

for opp in sample_opps:
    conn.execute("""
    INSERT OR REPLACE INTO opportunities (
        id, title, contact_name, contact_id, channel, group_name,
        need_summary, estimated_value, stage, confidence_score,
        heat_score, risk_notes, source_event_id, owner, win_probability,
        created_at, updated_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        opp[0], opp[1], opp[2], opp[3], opp[4], opp[5],
        opp[6], opp[7], opp[8], opp[9], opp[10], opp[11],
        opp[12], opp[13], opp[14], now_str, now_str
    ))

conn.commit()
conn.close()

# Also sync DB to workplace
wp_db = "/home/ryan/Documents/Ryan-Workplace/Heo-Harness/data/heo.db"
if os.path.exists(os.path.dirname(wp_db)):
    import shutil
    shutil.copy2(db_path, wp_db)

print("Patched database schema and seeded rich 7-stage Kanban opportunities successfully!")
