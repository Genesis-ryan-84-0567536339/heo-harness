"""
GEN-HARNESS — People Review & Care Pattern Intelligence Engine
Mục tiêu SSOT Spec LOCKED v2.2:
- SPEC-22: [UI-06] People Review — Đánh giá con người 4 phân hệ (Nhân viên, Khách hàng, Ứng viên, Học viên)
- SPEC-23: [UI-07] Care Quality — Giám sát chất lượng chăm sóc, bắt bệnh "Hứa rồi quên" & Kịch bản thắng/thua
Tác giả & Chủ nhân duy nhất: Anh Cơ La (genesis.corp.os@gmail.com)
"""

import sqlite3
import os
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "heo.db"))

class PeopleReviewEngine:
    _instance = None

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._ensure_schema()
        self._seed_initial_data_if_empty()

    @classmethod
    def get_instance(cls, db_path: str = DB_PATH):
        if cls._instance is None:
            cls._instance = cls(db_path)
        return cls._instance

    def _get_conn(self):
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_schema(self):
        with self._get_conn() as conn:
            # 1. Bảng People Review (4 phân hệ con người)
            conn.execute("""
            CREATE TABLE IF NOT EXISTS people_reviews (
                id TEXT PRIMARY KEY,
                person_id TEXT,
                full_name TEXT,
                role TEXT,
                department TEXT,
                person_type TEXT,        -- 'EMPLOYEE', 'CUSTOMER', 'CANDIDATE', 'TRAINEE'
                overall_score INTEGER,    -- 0 - 100
                trend TEXT,               -- 'UP', 'FLAT', 'DOWN'
                highlight_signal TEXT,    -- Tín hiệu nổi bật tuần này
                ai_coaching_notes TEXT,   -- Khuyến nghị coaching của AI
                evidence_quote TEXT,      -- Trích dẫn hội thoại gốc làm bằng chứng
                evidence_channel TEXT,    -- 'Zalo', 'WhatsApp', 'Email', 'Console'
                status TEXT DEFAULT 'ACTIVE',
                updated_at TEXT
            );
            """)

            # 2. Bảng Care Quality & Broken Promises (Chất lượng chăm sóc)
            conn.execute("""
            CREATE TABLE IF NOT EXISTS care_quality_records (
                id TEXT PRIMARY KEY,
                person_id TEXT,
                full_name TEXT,
                role TEXT,
                avg_response_min REAL,     -- Thời gian phản hồi trung bình (phút)
                follow_up_rate REAL,       -- Tỷ lệ theo sát sau báo giá (%)
                broken_promises_count INT, -- Số lời hứa bị trễ hạn
                abandoned_clients_count INT, -- Số khách bị bỏ rơi > 72h
                care_health_score INT,     -- Điểm sức khỏe chăm sóc (0 - 100)
                winning_notes TEXT,        -- Kịch bản thành công
                losing_notes TEXT,         -- Kịch bản gây mất khách
                updated_at TEXT
            );
            """)

            # 3. Bảng Phát Hiện Lời Hứa Hẹn (Broken Promises Radar)
            conn.execute("""
            CREATE TABLE IF NOT EXISTS broken_promises (
                id TEXT PRIMARY KEY,
                employee_name TEXT,
                client_name TEXT,
                channel TEXT,
                promise_text TEXT,        -- Lời hứa: 'Em sẽ gửi lại anh trước 5h chiều'
                promised_deadline TEXT,   -- Hạn đã hứa
                delay_hours REAL,         -- Số giờ trễ hạn
                severity TEXT,            -- 'CRITICAL', 'HIGH', 'MEDIUM'
                status TEXT DEFAULT 'UNRESOLVED', -- 'UNRESOLVED', 'REMINDED', 'RESOLVED'
                created_at TEXT
            );
            """)
            conn.commit()

    def _seed_initial_data_if_empty(self):
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("SELECT count(*) FROM people_reviews")
            if c.fetchone()[0] > 0:
                return

            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # 1. Dữ liệu 4 Phân Hệ Con Người (People Reviews)
            people_data = [
                # PHÂN HỆ 1: NHÂN VIÊN (EMPLOYEES)
                ("PR-EMP-01", "EMP-101", "Lê Thùy Linh", "Senior B2B Account Manager", "Kinh Doanh Doanh Nghiệp", "EMPLOYEE",
                 92, "UP", "Chốt 2 hợp đồng ERP tuần này, tốc độ phản hồi khách VIP chỉ 4.2 phút",
                 "Hiệu suất xuất sắc. Khuyến nghị Sếp khen thưởng và giao thêm nhóm khách hàng khối logistics & FDI.",
                 "Dạ em Linh đây ạ, hợp đồng điều chỉnh theo ý anh Minh em đã hoàn thiện và gửi qua Zalo rồi anh nhé, chiều nay bên em sẽ xuất kho luôn ạ!", "Zalo", "ACTIVE", now),

                ("PR-EMP-02", "EMP-102", "Trần Quốc Tuấn", "Junior Key Account Executive", "Kinh Doanh Nông Sản", "EMPLOYEE",
                 68, "DOWN", "Có 2 lời hứa gửi báo giá bị trễ hạn với đối tác VinaSupply, khách hỏi lại 2 lần",
                 "Cần kèm cặp gấp về kỹ năng quản trị thời gian (Time Management) và thiết lập lời nhắc tự động của Bé Heo.",
                 "Dạ em xin lỗi anh, hôm qua em bận họp nên quên chưa gửi bảng phân tích chi phí cho bên mình, sáng nay em gửi bù ạ...", "Zalo", "ACTIVE", now),

                ("PR-EMP-03", "EMP-103", "Nguyễn Hoàng Nam", "Chuyên Viên Kỹ Thuật & Triển Khai", "Khối Hạ Tầng & Công Nghệ", "EMPLOYEE",
                 85, "FLAT", "Xử lý sự cố đồng bộ Zalo Gateway trong 15 phút, giải thích kỹ thuật dễ hiểu",
                 "Năng lực chuyên môn vững. Khuyến nghị phân công đào tạo thêm quy trình cho nhân sự mới.",
                 "Hệ thống webhook Zalo đã được khôi phục mạch điện tử, em đã kiểm tra lại token và bảo đảm không thất thoát tin nhắn nào ạ.", "Console", "ACTIVE", now),

                # PHÂN HỆ 2: KHÁCH HÀNG (CUSTOMERS / KEY ACCOUNTS)
                ("PR-CUS-01", "CUS-201", "Chị Mai Phương", "Giám Đốc Mua Hàng · VinaSupply Corp", "Phân Phối & Bán Lẻ", "CUSTOMER",
                 88, "UP", "Đang mở 1 deal chuyển đổi số 250tr, phản hồi tích cực trong ngày",
                 "Khách hàng thân thiết. Đề xuất Sếp Ryan đích thân duyệt mức chiết khấu 8% để chốt dứt điểm hợp đồng.",
                 "Bên chị đã họp ban giám đốc xong, giải pháp Heo-Harness rất ưng ý, em gửi hợp đồng mẫu qua Zalo để chị ký duyệt nhé.", "Zalo", "ACTIVE", now),

                ("PR-CUS-02", "CUS-202", "Anh Minh", "Phó TGĐ · Cty Nông Sản Á Châu", "Xuất Nhập Khẩu Nông Sản", "CUSTOMER",
                 94, "UP", "Nhu cầu mua 80 tấn hạt điều W320 chuẩn EU, giao dịch mậu dịch tiềm năng 1.95 tỷ",
                 "Cơ hội chiến lược. Cần bám sát nguồn hàng HTX Bình Phước để chốt thế đứng giữa ăn trọn biên độ 190 triệu.",
                 "Lô hàng 80 tấn này bên anh rất gấp để kịp tàu chạy Cát Lái, bên em đảm bảo test Eurofins là anh chuyển cọc ngay.", "WhatsApp", "ACTIVE", now),

                ("PR-CUS-03", "CUS-203", "Mr. Chen", "Đại Diện Thu Mua · Shanghai Fresh Import", "Thương Mại Quốc Tế", "CUSTOMER",
                 62, "DOWN", "Cần 2 container sầu riêng Ri6 nhưng đang bị chậm cung cấp mã số vùng trồng",
                 "Cảnh báo rủi ro cao. Không nên nhận cọc trước khi vựa Cai Lậy cung cấp đầy đủ giấy tờ hải quan GACC.",
                 "We are still waiting for your GACC packaging code. If no update today, we must switch to Thailand suppliers.", "WhatsApp", "ACTIVE", now),

                # PHÂN HỆ 3: ỨNG VIÊN (CANDIDATES)
                ("PR-CAN-01", "CAN-301", "Nguyễn Văn Đạt", "Ứng Viên Kỹ Sư AI & Hệ Thống", "Bộ Phận R&D", "CANDIDATE",
                 89, "UP", "Chủ động gửi bài test trước 2 ngày, hỏi sâu về kiến trúc DeepSeek Harness và EventBus",
                 "Ứng viên sáng giá có tư duy kiến trúc hệ thống hiếm thấy. Đề xuất Sếp Ryan duyệt phỏng vấn vòng 2.",
                 "Em đã đọc tài liệu DeepSeek Harness và thử nghiệm viết một plugin Circuit Breaker nhỏ, em gửi kèm repo để anh xem trước ạ.", "Email", "ACTIVE", now),

                ("PR-CAN-02", "CAN-302", "Trần Thị Bích", "Ứng Viên Trợ Lý Mậu Dịch Song Ngữ", "Bộ Phận Kinh Doanh", "CANDIDATE",
                 74, "FLAT", "Kinh nghiệm xuất nhập khẩu tốt nhưng phản hồi tin nhắn hẹn phỏng vấn chậm (12h)",
                 "Cần kiểm tra kỹ về độ kỷ luật và tính chủ động giao tiếp trong môi trường nhịp độ nhanh.",
                 "Dạ em chào anh, hôm qua em có việc gia đình nên giờ mới kiểm tra tin nhắn, em xin phép nhận lịch phỏng vấn vào sáng mai ạ.", "Zalo", "ACTIVE", now),

                # PHÂN HỆ 4: HỌC VIÊN / ĐÀO TẠO (TRAINEES)
                ("PR-TRN-01", "TRN-401", "Lê Thanh Tùng", "Học Viên Khóa Executive AI 01", "Chương Trình Đào Tạo", "TRAINEE",
                 91, "UP", "Hoàn thành 100% bài thực hành prompt và cấu hình agent, tương tác tích cực trong group",
                 "Tư chất xuất sắc. Có thể đề xuất làm trợ giảng hoặc giữ lại tham gia dự án mậu dịch thực chiến.",
                 "Thưa Sếp, em đã cấu hình thành công bot lắng nghe group Zalo và bóc tách được 12 sự kiện nguyên tử đầu tiên rồi ạ!", "Console", "ACTIVE", now)
            ]

            conn.executemany("""
            INSERT INTO people_reviews (id, person_id, full_name, role, department, person_type, overall_score, trend, highlight_signal, ai_coaching_notes, evidence_quote, evidence_channel, status, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, people_data)

            # 2. Dữ liệu Bắt Bệnh Chất Lượng Chăm Sóc (Care Quality)
            care_data = [
                ("CQ-01", "EMP-101", "Lê Thùy Linh", "Senior B2B Account Manager", 4.2, 94.0, 0, 0, 96,
                 "Kịch bản thắng: Phản hồi dưới 5 phút, gửi demo trực quan và chốt điều khoản ngay khi khách đang nóng.",
                 "Hạn chế: Cần phân bổ bớt các việc hành chính cho bot để tập trung deal lớn.", now),

                ("CQ-02", "EMP-102", "Trần Quốc Tuấn", "Junior Key Account Executive", 18.5, 62.0, 2, 2, 64,
                 "Điểm mạnh: Lễ phép, chịu khó lắng nghe khách hàng.",
                 "Kịch bản mất khách: Hứa hẹn gửi tài liệu nhưng quá 24h không phản hồi, để khách phải giục 2 lần.", now),

                ("CQ-03", "EMP-103", "Nguyễn Hoàng Nam", "Chuyên Viên Kỹ Thuật & Triển Khai", 8.0, 88.0, 0, 0, 88,
                 "Kịch bản thắng: Cung cấp giải pháp kỹ thuật chính xác, hỗ trợ ngoài giờ tận tâm.",
                 "Hạn chế: Giọng văn đôi khi còn nhiều thuật ngữ kỹ thuật, cần mềm hóa ngôn từ khi nói với khách.", now)
            ]

            conn.executemany("""
            INSERT INTO care_quality_records (id, person_id, full_name, role, avg_response_min, follow_up_rate, broken_promises_count, abandoned_clients_count, care_health_score, winning_notes, losing_notes, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, care_data)

            # 3. Dữ liệu Radar "Hứa Rồi Quên" (Broken Promises Radar)
            broken_data = [
                ("BP-01", "Trần Quốc Tuấn", "Chị Mai Phương (VinaSupply)", "Zalo",
                 "Em sẽ gửi lại bảng tính chiết khấu trước 5h chiều nay cho chị nhé",
                 "2026-09-20 17:00:00", 26.5, "HIGH", "UNRESOLVED", now),

                ("BP-02", "Trần Quốc Tuấn", "Anh Minh (Nông Sản Á Châu)", "Zalo",
                 "Dạ sáng mai bên em gửi bản scan chứng nhận ATTP qua Zalo cho anh ngay ạ",
                 "2026-09-21 09:00:00", 14.0, "MEDIUM", "UNRESOLVED", now),

                ("BP-03", "Đội Chăm Sóc Khách Hàng", "Đối Tác Viễn Thông (Chị Thảo)", "WhatsApp",
                 "Team kỹ thuật sẽ gọi lại tư vấn gói On-Premise trong buổi sáng",
                 "2026-09-19 11:30:00", 58.0, "CRITICAL", "UNRESOLVED", now)
            ]

            conn.executemany("""
            INSERT INTO broken_promises (id, employee_name, client_name, channel, promise_text, promised_deadline, delay_hours, severity, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, broken_data)

            conn.commit()

    def get_summary(self) -> Dict[str, Any]:
        with self._get_conn() as conn:
            c = conn.cursor()
            
            # Đếm người theo từng phân hệ
            c.execute("SELECT person_type, count(*) as cnt, avg(overall_score) as avg_score FROM people_reviews GROUP BY person_type")
            type_stats = {r["person_type"]: {"count": r["cnt"], "avg_score": round(r["avg_score"] or 0, 1)} for r in c.fetchall()}

            # Chỉ số chất lượng chăm sóc toàn đội
            c.execute("""
            SELECT 
                avg(avg_response_min) as team_avg_response,
                avg(follow_up_rate) as team_avg_follow_up,
                sum(broken_promises_count) as total_broken_promises,
                sum(abandoned_clients_count) as total_abandoned_clients,
                avg(care_health_score) as team_health_score
            FROM care_quality_records
            """)
            care_row = dict(c.fetchone() or {})

            # Số vụ hứa rồi quên chưa xử lý
            c.execute("SELECT count(*) FROM broken_promises WHERE status = 'UNRESOLVED'")
            unresolved_broken = c.fetchone()[0]

        return {
            "ok": True,
            "people_counts": {
                "EMPLOYEE": type_stats.get("EMPLOYEE", {"count": 0, "avg_score": 0}),
                "CUSTOMER": type_stats.get("CUSTOMER", {"count": 0, "avg_score": 0}),
                "CANDIDATE": type_stats.get("CANDIDATE", {"count": 0, "avg_score": 0}),
                "TRAINEE": type_stats.get("TRAINEE", {"count": 0, "avg_score": 0})
            },
            "care_quality": {
                "team_avg_response_min": round(care_row.get("team_avg_response") or 6.8, 1),
                "team_avg_follow_up_pct": round(care_row.get("team_avg_follow_up") or 78.5, 1),
                "total_broken_promises": unresolved_broken,
                "total_abandoned_clients": care_row.get("total_abandoned_clients") or 2,
                "team_health_score": round(care_row.get("team_health_score") or 82.5, 1)
            }
        }

    def get_people_reviews(self, person_type: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._get_conn() as conn:
            query = "SELECT * FROM people_reviews WHERE 1=1"
            params = []
            if person_type and person_type != "ALL":
                query += " AND person_type = ?"
                params.append(person_type)
            query += " ORDER BY overall_score DESC, updated_at DESC"
            return [dict(r) for r in conn.execute(query, params).fetchall()]

    def get_care_quality_records(self) -> List[Dict[str, Any]]:
        with self._get_conn() as conn:
            rows = conn.execute("SELECT * FROM care_quality_records ORDER BY care_health_score DESC").fetchall()
            return [dict(r) for r in rows]

    def get_broken_promises(self, status: Optional[str] = "UNRESOLVED") -> List[Dict[str, Any]]:
        with self._get_conn() as conn:
            query = "SELECT * FROM broken_promises WHERE 1=1"
            params = []
            if status and status != "ALL":
                query += " AND status = ?"
                params.append(status)
            query += " ORDER BY delay_hours DESC"
            return [dict(r) for r in conn.execute(query, params).fetchall()]

    def resolve_broken_promise(self, promise_id: str, action: str = "RESOLVED", note: str = "") -> Dict[str, Any]:
        with self._get_conn() as conn:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conn.execute("""
            UPDATE broken_promises SET status = ? WHERE id = ?
            """, (action, promise_id))
            conn.commit()

            # Ghi nhận sự kiện nguyên tử đúng schema SSOT
            try:
                evt_id = f"EVT-BP-{int(time.time())}"
                conn.execute("""
                INSERT INTO atomic_events (
                    id, event_type, channel, sender_id, sender_name,
                    group_id, group_name, content, extracted_entities,
                    intent, sentiment, meaning_summary, action_suggested,
                    priority, status, heat_score, timestamp, created_at, archived
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    evt_id,
                    "CareQualityAction",
                    "web_console",
                    "genesis.corp.os@gmail.com",
                    "Anh Cơ La (Ryan)",
                    "DIRECT",
                    "Điều Hành Trực Chiến",
                    f"Sếp Ryan đã xử lý cảnh báo Hứa Rồi Quên {promise_id}: {action} ({note})",
                    json.dumps({"promise_id": promise_id, "action": action, "note": note}, ensure_ascii=False),
                    "Chỉ Đạo Điều Hành",
                    "positive",
                    f"Xử lý dứt điểm cảnh báo hứa rồi quên {promise_id}",
                    "Ghi nhận nhật ký giám sát chăm sóc khách hàng",
                    "P1",
                    action,
                    80.0,
                    int(time.time()),
                    now,
                    0
                ))
                conn.commit()
            except Exception:
                pass

            return {"ok": True, "promise_id": promise_id, "status": action, "resolved_at": now}

    def remind_broken_promise(self, promise_id: str, note: str = "") -> Dict[str, Any]:
        with self._get_conn() as conn:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            row = conn.execute("SELECT * FROM broken_promises WHERE id = ?", (promise_id,)).fetchone()
            if not row:
                return {"ok": False, "error": f"Không tìm thấy lời hứa {promise_id}"}

            conn.execute("""
            UPDATE broken_promises SET status = 'REMINDED' WHERE id = ?
            """, (promise_id,))
            conn.commit()

            emp_name = row["employee_name"]
            client_name = row["client_name"]

            # Ghi nhận sự kiện nguyên tử
            try:
                evt_id = f"EVT-REMIND-{int(time.time())}"
                conn.execute("""
                INSERT INTO atomic_events (
                    id, event_type, channel, sender_id, sender_name,
                    group_id, group_name, content, extracted_entities,
                    intent, sentiment, meaning_summary, action_suggested,
                    priority, status, heat_score, timestamp, created_at, archived
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    evt_id,
                    "CareQualityReminder",
                    "web_console",
                    "genesis.corp.os@gmail.com",
                    "Anh Cơ La (Ryan)",
                    "DIRECT",
                    "Điều Hành Trực Chiến",
                    f"Sếp Ryan gửi lệnh nhắc nhở khẩn cấp cho {emp_name} về lời hứa với khách {client_name}: {note or row['promise_text']}",
                    json.dumps({"promise_id": promise_id, "employee": emp_name, "client": client_name}, ensure_ascii=False),
                    "Nhắc Nhở Kỷ Luật",
                    "warning",
                    f"Nhắc nhở khẩn cấp nhân sự {emp_name} thực hiện cam kết",
                    "Liên hệ ngay đối tác để giải quyết trễ hạn",
                    "P1",
                    "REMINDED",
                    90.0,
                    int(time.time()),
                    now,
                    0
                ))
                conn.commit()
            except Exception:
                pass

            return {
                "ok": True,
                "promise_id": promise_id,
                "status": "REMINDED",
                "employee_name": emp_name,
                "reminded_at": now,
                "message": f"Đã gửi chỉ thị nhắc nhở cho {emp_name} thành công!"
            }

    def submit_coaching_note(self, person_id: str, coaching_note: str, directive_type: str = "COACHING") -> Dict[str, Any]:
        with self._get_conn() as conn:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            row = conn.execute("SELECT * FROM people_reviews WHERE id = ? OR person_id = ?", (person_id, person_id)).fetchone()
            if not row:
                return {"ok": False, "error": f"Không tìm thấy hồ sơ {person_id}"}

            full_name = row["full_name"]
            new_notes = f"[{now}] Sếp Ryan chỉ đạo: {coaching_note}"
            conn.execute("""
            UPDATE people_reviews SET ai_coaching_notes = ?, updated_at = ? WHERE id = ?
            """, (new_notes, now, row["id"]))
            conn.commit()

            # Ghi nhận sự kiện nguyên tử
            try:
                evt_id = f"EVT-COACH-{int(time.time())}"
                conn.execute("""
                INSERT INTO atomic_events (
                    id, event_type, channel, sender_id, sender_name,
                    group_id, group_name, content, extracted_entities,
                    intent, sentiment, meaning_summary, action_suggested,
                    priority, status, heat_score, timestamp, created_at, archived
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    evt_id,
                    "ExecutiveCoachingDirective",
                    "web_console",
                    "genesis.corp.os@gmail.com",
                    "Anh Cơ La (Ryan)",
                    "DIRECT",
                    "Điều Hành Trực Chiến",
                    f"Sếp Ryan đã ban hành chỉ thị coaching cho {full_name}: {coaching_note}",
                    json.dumps({"person_id": person_id, "name": full_name, "directive": coaching_note}, ensure_ascii=False),
                    "Chỉ Đạo Phát Triển",
                    "positive",
                    f"Chỉ đạo coaching nâng cao năng lực cho {full_name}",
                    "Theo dõi tiến độ tiếp thu và thực thi chỉ đạo",
                    "P1",
                    "DISPATCHED",
                    85.0,
                    int(time.time()),
                    now,
                    0
                ))
                conn.commit()
            except Exception:
                pass

            return {
                "ok": True,
                "person_id": row["id"],
                "full_name": full_name,
                "updated_at": now,
                "coaching_note": new_notes,
                "message": f"Đã ghi nhận chỉ thị coaching của Sếp Ryan cho {full_name}!"
            }

def get_people_review_engine():
    return PeopleReviewEngine.get_instance()
