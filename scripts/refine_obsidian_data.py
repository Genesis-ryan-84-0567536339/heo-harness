import sqlite3
import os
import json

db_path = "data/heo.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 1. Bổ sung Contacts cho các Opportunities còn thiếu để triệt để nối Deal vào Contact
new_contacts = [
    (
        "CNT-006", "Anh Minh (Kafi)", "Kafi Securities", "Trưởng Phòng Phân Tích & Đầu Tư",
        "0908889999", "kafi.minh", "+84908889999", "minh.nguyen@kafi.vn",
        75.0, 2, 1, "THEM", 18.0,
        "Khách hàng tiềm năng mảng dữ liệu tài chính & báo cáo phân tích đầu tư",
        "Tương tác tích cực qua kênh tài chính, nhiệt độ 75° ổn định"
    ),
    (
        "CNT-007", "Giám Đốc CNTT Viettel", "Tập Đoàn Viettel", "Giám Đốc Trung Tâm CNTT & Đám Mây",
        "0988112233", "viettel.cio", "+84988112233", "cio@viettel.vn",
        86.0, 3, 0, "US", 10.0,
        "Đối tác chiến lược cấp cao hạ tầng máy chủ AI & viễn thông",
        "Điểm nhiệt độ rất cao (86°), cần ưu tiên phản hồi đề xuất kỹ thuật"
    ),
    (
        "CNT-008", "Tập Đoàn Tân Á", "Tân Á Đại Thành", "Đại Diện Ban Chuyển Đổi Số",
        "0912334455", "tana.digital", "+84912334455", "digital@tanadaithanh.vn",
        62.0, 2, 2, "THEM", 22.0,
        "Quan tâm bản quyền triển khai hệ thống Gen-Harness quy mô doanh nghiệp",
        "Đang xem xét hợp đồng chuyển giao bản quyền Q4"
    ),
    (
        "CNT-009", "Phạm Văn Long", "CloudOps Co", "Chuyên Viên Hệ Thống Cấp Cao",
        "0933778899", "long.cloudops", "+84933778899", "long.pham@cloudops.io",
        32.0, 1, 6, "THEM", 45.0,
        "Đã ngắt tương tác 6 ngày sau khi nhận tín hiệu bảng giá Cloud Server",
        "Cảnh báo: Đối tác im lặng >3 ngày, nguy cơ rớt giao dịch cao"
    )
]

for c in new_contacts:
    cursor.execute("""
    INSERT OR REPLACE INTO contacts (
        id, full_name, company, role, phone, zalo_id, whatsapp_id, email,
        heat_score, autonomy_level, went_silent_days, ball_owner, churn_risk,
        ai_summary, score_explanation
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, c)

# Cập nhật contact_id chuẩn cho các opportunities
cursor.execute("UPDATE opportunities SET contact_id = 'CNT-006' WHERE id IN ('OPP-599405', 'OPP-103')")
cursor.execute("UPDATE opportunities SET contact_id = 'CNT-007' WHERE id = 'OPP-105'")
cursor.execute("UPDATE opportunities SET contact_id = 'CNT-008' WHERE id = 'OPP-106'")
cursor.execute("UPDATE opportunities SET contact_id = 'CNT-009' WHERE id = 'OPP-107'")

conn.commit()
conn.close()
print("✓ Đã cập nhật xong dữ liệu contacts và opportunities liên kết!")
