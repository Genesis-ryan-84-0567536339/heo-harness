# -*- coding: utf-8 -*-
import sqlite3
import os

db_path = "/home/ryan/heo-harness/data/heo.db"
conn = sqlite3.connect(db_path)

# 1. Add extra columns to contacts for Living Profiles & Explainable AI (SPEC E5, C3)
try:
    conn.execute("ALTER TABLE contacts ADD COLUMN autonomy_level INTEGER DEFAULT 1;")
except Exception:
    pass

try:
    conn.execute("ALTER TABLE contacts ADD COLUMN engagement_score REAL DEFAULT 80.0;")
except Exception:
    pass

try:
    conn.execute("ALTER TABLE contacts ADD COLUMN churn_risk REAL DEFAULT 15.0;")
except Exception:
    pass

try:
    conn.execute("ALTER TABLE contacts ADD COLUMN score_explanation TEXT;")
except Exception:
    pass

# 2. Enrich contacts with detailed Living Profiles & Explainable AI data
contacts_data = [
    {
        "id": "CNT-001",
        "full_name": "Chị Mai Phương",
        "phone": "0908123456",
        "zalo_id": "zalo-mp-88",
        "whatsapp_id": "wa-maiphuong",
        "email": "maiphuong@vinasupply.com",
        "company": "VinaSupply Corp",
        "role": "Giám Đốc Mua Hàng & Cung Ứng",
        "heat_score": 92.0,
        "status": "HOT",
        "ball_owner": "US",
        "went_silent_days": 0,
        "autonomy_level": 3,
        "engagement_score": 95.0,
        "churn_risk": 5.0,
        "score_explanation": "Điểm rất cao (92/100) vì: Tần suất trao đổi 14 tin nhắn/tuần, tỷ lệ phản hồi lại trong 5 phút đạt 98%, đang có 2 yêu cầu báo giá vật tư đang mở, lịch sử thanh toán luôn đúng hạn 100%.",
        "ai_summary": """Chị Mai Phương là Giám đốc Mua hàng cấp cao tại VinaSupply Corp, đối tác cung ứng chiến lược hơn 2 năm qua.
Phong cách làm việc: Cực kỳ chuyên nghiệp, chuộng văn bản báo giá rõ ràng, quyết định nhanh nếu có chiết khấu theo khối lượng.
Kênh tương tác chính: Zalo vào ban ngày và email xác nhận hợp đồng.
Nhu cầu trọng tâm: Đang tìm giải pháp tự động xuất báo giá và kiểm tra tồn kho tức thì qua API.
Mức tự trị khuyến nghị: Cấp 3 (Tự động trả lời whitelist và lên lịch hẹn trao đổi trực tiếp)."""
    },
    {
        "id": "CNT-002",
        "full_name": "Anh Hoàng Bách",
        "phone": "0912345678",
        "zalo_id": "zalo-bach-99",
        "whatsapp_id": "wa-bach-99",
        "email": "bach.hoang@logitechvn.io",
        "company": "LogiTech Global",
        "role": "Head of Tech Procurement",
        "heat_score": 88.0,
        "status": "HOT",
        "ball_owner": "THEM",
        "went_silent_days": 1,
        "autonomy_level": 2,
        "engagement_score": 88.0,
        "churn_risk": 10.0,
        "score_explanation": "Điểm cao (88/100) do: Đang theo đuổi deal 185 triệu VND gói AI điều phối kho bãi; đã tích hợp thử nghiệm qua WhatsApp; phản hồi nhiệt tình trong vòng 15 phút.",
        "ai_summary": """Anh Hoàng Bách phụ trách mua sắm công nghệ cho LogiTech Global tại khu vực Đông Nam Á.
Tính cách: Am hiểu sâu kỹ thuật, quan tâm lớn đến khả năng chạy on-premise, bảo mật token 0đ và tính sẵn sàng của hệ thống.
Tiến độ thương vụ: Đã nhận bản demo sơ bộ, đang lấy ý kiến thẩm định từ đội ngũ kỹ sư nội bộ trước khi chốt hợp đồng.
Kênh tương tác ưu tiên: WhatsApp đa thiết bị."""
    },
    {
        "id": "CNT-003",
        "full_name": "Trần Thu Hà",
        "phone": "0987654321",
        "zalo_id": "zalo-thuha",
        "whatsapp_id": "wa-thuha",
        "email": "thuha.tran@fashionviet.vn",
        "company": "Thời Trang Hà My",
        "role": "Founder & CEO",
        "heat_score": 70.0,
        "status": "WARM",
        "ball_owner": "US",
        "went_silent_days": 2,
        "autonomy_level": 2,
        "engagement_score": 75.0,
        "churn_risk": 20.0,
        "score_explanation": "Điểm ấm (70/100): Quy mô thương vụ rất lớn (1.2 tỷ VND gia công ERP), tuy nhiên chu kỳ ra quyết định kéo dài do phụ thuộc kế hoạch xuất khẩu sang Nhật Bản.",
        "ai_summary": """Chị Trần Thu Hà là nhà sáng lập kiêm điều hành thương hiệu Thời Trang Hà My với 4 xưởng may tại miền Bắc.
Nhu cầu then chốt: Tìm đối tác công nghệ tích hợp toàn bộ luồng đơn hàng từ Zalo vào hệ thống ERP quản trị xưởng.
Cơ hội: Hợp đồng giá trị lớn, cần cử nhân sự kỹ thuật đồng hành tư vấn trực tiếp 1-1."""
    },
    {
        "id": "CNT-004",
        "full_name": "Nguyễn Đức Trí",
        "phone": "0933445566",
        "zalo_id": "zalo-tri-tri",
        "whatsapp_id": "",
        "email": "tri.nguyen@vietfintech.net",
        "company": "Fintech Solutions",
        "role": "Chief Operating Officer (COO)",
        "heat_score": 35.0,
        "status": "COLD",
        "ball_owner": "THEM",
        "went_silent_days": 8,
        "autonomy_level": 1,
        "engagement_score": 40.0,
        "churn_risk": 75.0,
        "score_explanation": "Cảnh báo lạnh (35/100): Đã im lặng 8 ngày sau khi nhận tài liệu báo giá; rủi ro rơi vào tay đối thủ cạnh tranh cao (75%); cần chiến dịch hâm nóng quan hệ khẩn.",
        "ai_summary": """Anh Nguyễn Đức Trí là COO tại Fintech Solutions, từng rất hào hứng với giải pháp xác thực bảo mật đa tầng.
Thực trạng quan hệ: Đã 'Went Silent' hơn 1 tuần qua sau khi nhận demo.
Hành động đề xuất: Gửi thông điệp cập nhật tính năng mới kèm lời mời cà phê kết nối cùng Sếp Ryan."""
    },
    {
        "id": "CNT-005",
        "full_name": "Chị Thảo (Viễn Thông)",
        "phone": "0911223344",
        "zalo_id": "zalo-thao-tel",
        "whatsapp_id": "",
        "email": "thao.nt@viettelcom.vn",
        "company": "Đối Tác Hạ Tầng Số",
        "role": "Phó Giám Đốc Trung Tâm CSKH",
        "heat_score": 95.0,
        "status": "HOT",
        "ball_owner": "US",
        "went_silent_days": 0,
        "autonomy_level": 3,
        "engagement_score": 96.0,
        "churn_risk": 4.0,
        "score_explanation": "Điểm xuất sắc (95/100): Đang đàm phán hợp đồng độc quyền 85 triệu đồng giọng đọc AI Audio; liên lạc hàng ngày qua Zalo; phản hồi ngay lập tức.",
        "ai_summary": """Chị Thảo là đầu mối quan trọng phụ trách đổi mới trải nghiệm khách hàng tại trung tâm viễn thông số.
Ưu tiên hiện tại: Triển khai 3 giọng đọc AI Audio cho tổng đài và hệ thống nhắc nợ tự động.
Mối quan hệ: Cực kỳ thân thiết và tin tưởng năng lực kỹ thuật của Sếp Cơ La."""
    }
]

for c in contacts_data:
    conn.execute("""
    INSERT OR REPLACE INTO contacts (
        id, full_name, phone, zalo_id, whatsapp_id, email, company, role,
        heat_score, status, ball_owner, went_silent_days, tags, ai_summary,
        autonomy_level, engagement_score, churn_risk, score_explanation,
        interaction_count, first_seen, last_seen
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '[\"VIP\", \"Client\"]', ?, ?, ?, ?, ?, 5, '2026-09-20', '2026-09-21')
    """, (
        c["id"], c["full_name"], c["phone"], c["zalo_id"], c["whatsapp_id"],
        c["email"], c["company"], c["role"], c["heat_score"], c["status"],
        c["ball_owner"], c["went_silent_days"], c["ai_summary"],
        c["autonomy_level"], c["engagement_score"], c["churn_risk"],
        c["score_explanation"]
    ))

conn.commit()
conn.close()

# Copy to workplace
wp_db = "/home/ryan/Documents/Ryan-Workplace/Heo-Harness/data/heo.db"
if os.path.exists(os.path.dirname(wp_db)):
    import shutil
    shutil.copy2(db_path, wp_db)

print("Milestone 4 database schema & rich contacts patched successfully!")
