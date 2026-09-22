# -*- coding: utf-8 -*-
"""
Module: heo_harness.core.data_factory
Conversation Data Factory & Atomic Events Pipeline (Spec E2, G1, G3).
Chuyển hóa tin nhắn hội thoại thô thành các Thực Thể (Entities), Ý Định (Intents)
và Sự Kiện Nguyên Tử (Atomic Events: AskedPrice, Complained, SentQuotation...).
Tác giả: Anh Cơ La (genesis.corp.os@gmail.com)
"""

import sqlite3
import json
import time
import os
import re
import uuid

class ConversationDataFactory:
    def __init__(self, db_path: str = None):
        if not db_path:
            db_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "heo.db")
        self.db_path = os.path.abspath(db_path)
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()
        self.seed_sample_data_if_empty()

    def _get_conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Khởi tạo cấu trúc các bảng Canonical Schema theo chuẩn Spec G1 & G3."""
        with self._get_conn() as conn:
            conn.execute("""
            CREATE TABLE IF NOT EXISTS atomic_events (
                id TEXT PRIMARY KEY,
                event_type TEXT NOT NULL,
                channel TEXT NOT NULL,
                sender_id TEXT,
                sender_name TEXT,
                group_id TEXT,
                group_name TEXT,
                content TEXT NOT NULL,
                extracted_entities TEXT,
                intent TEXT,
                sentiment TEXT,
                meaning_summary TEXT,
                action_suggested TEXT,
                priority TEXT DEFAULT 'P2',
                status TEXT DEFAULT 'NEW',
                archived INTEGER DEFAULT 0,
                heat_score REAL DEFAULT 50.0,
                timestamp INTEGER,
                created_at TEXT
            );
            """)

            conn.execute("""
            CREATE TABLE IF NOT EXISTS entities (
                id TEXT PRIMARY KEY,
                entity_type TEXT NOT NULL,
                value TEXT NOT NULL,
                normalized_value TEXT,
                source_event_id TEXT,
                frequency INTEGER DEFAULT 1,
                first_seen TEXT,
                last_seen TEXT
            );
            """)

            conn.execute("""
            CREATE TABLE IF NOT EXISTS opportunities (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                contact_name TEXT,
                contact_id TEXT,
                channel TEXT,
                group_name TEXT,
                need_summary TEXT,
                estimated_value REAL DEFAULT 0.0,
                stage TEXT DEFAULT 'SIGNAL',
                owner TEXT DEFAULT 'Anh Cơ La (Ryan)',
                win_probability REAL DEFAULT 50.0,
                confidence_score REAL DEFAULT 70.0,
                heat_score REAL DEFAULT 60.0,
                risk_notes TEXT,
                source_event_id TEXT,
                created_at TEXT,
                updated_at TEXT
            );
            """)

            conn.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                id TEXT PRIMARY KEY,
                full_name TEXT NOT NULL,
                phone TEXT,
                zalo_id TEXT,
                whatsapp_id TEXT,
                email TEXT,
                company TEXT,
                role TEXT,
                heat_score REAL DEFAULT 50.0,
                status TEXT DEFAULT 'WARM',
                ball_owner TEXT DEFAULT 'THEM',
                went_silent_days INTEGER DEFAULT 0,
                tags TEXT DEFAULT '[]',
                ai_summary TEXT,
                interaction_count INTEGER DEFAULT 1,
                autonomy_level INTEGER DEFAULT 1,
                engagement_score REAL DEFAULT 80.0,
                churn_risk REAL DEFAULT 15.0,
                score_explanation TEXT,
                first_seen TEXT,
                last_seen TEXT
            );
            """)

            # Tự động di trú các cột mới cho contacts nếu db cũ đã có sẵn
            for col_name, col_def in [
                ("autonomy_level", "INTEGER DEFAULT 1"),
                ("engagement_score", "REAL DEFAULT 80.0"),
                ("churn_risk", "REAL DEFAULT 15.0"),
                ("score_explanation", "TEXT")
            ]:
                try:
                    conn.execute(f"ALTER TABLE contacts ADD COLUMN {col_name} {col_def};")
                except Exception:
                    pass

            conn.execute("""
            CREATE TABLE IF NOT EXISTS matches (
                id TEXT PRIMARY KEY,
                opp_id TEXT NOT NULL,
                contact_id TEXT,
                title TEXT NOT NULL,
                match_score REAL DEFAULT 80.0,
                match_reason TEXT,
                status TEXT DEFAULT 'PENDING',
                created_at TEXT
            );
            """)
            conn.commit()

    def extract_entities_from_text(self, text: str) -> dict:
        """Trích xuất thực thể: Giá tiền, Hàng hóa/Dịch vụ, Thời gian, Số lượng."""
        entities = {
            "prices": [],
            "products": [],
            "contacts": [],
            "dates": []
        }

        # 1. Trích xuất giá / số tiền
        price_patterns = [
            r'(\d+[\.,]?\d*)\s*(tr|triệu|k|nghìn|ngàn|đ|vnd|usd|\$)',
            r'giá\s*[:=]?\s*(\d+[\.,]?\d*)',
            r'(\d+)\s*(tỷ|ty)'
        ]
        for pat in price_patterns:
            matches = re.findall(pat, text, re.IGNORECASE)
            for m in matches:
                if isinstance(m, tuple):
                    entities["prices"].append("".join(m).strip())
                else:
                    entities["prices"].append(str(m).strip())

        # 2. Trích xuất hàng hóa/dịch vụ từ khóa
        product_keywords = [
            "hợp đồng", "báo giá", "đơn hàng", "sản phẩm", "dịch vụ", 
            "phần mềm", "tài liệu", "hồ sơ", "chứng từ", "linh kiện", 
            "nguồn hàng", "xưởng may", "in ấn", "vải", "bao bì", "thiết kế"
        ]
        for kw in product_keywords:
            if kw in text.lower():
                entities["products"].append(kw)

        # 3. Trích xuất thời gian/hạn
        date_patterns = [
            r'(ngày\s*\d{1,2}[\/\-]\d{1,2})',
            r'(thứ\s*[2-7]|chủ nhật)',
            r'(hôm nay|ngày mai|tuần sau|tháng sau|chiều nay|sáng mai)'
        ]
        for pat in date_patterns:
            matches = re.findall(pat, text, re.IGNORECASE)
            for m in matches:
                entities["dates"].append(str(m).strip())

        return entities

    def detect_intent(self, text: str) -> tuple[str, str, str, str]:
        """
        Nhận diện Ý định (Intent) và phân loại Sự Kiện Nguyên Tử (Event Type).
        Trả về: (event_type, intent_label, meaning_summary, suggested_action, priority, heat_score)
        """
        t_lower = text.lower()

        # AskedPrice - Hỏi giá / Chi phí
        if any(k in t_lower for k in ["giá bao nhiêu", "xin giá", "báo giá", "chi phí", "bao nhiêu tiền", "hỏi giá", "rate", "cost"]):
            return (
                "AskedPrice",
                "Hỏi Giá / Chi Phí",
                "Đối tác/khách hàng đang hỏi báo giá dịch vụ hoặc sản phẩm.",
                "Soạn bảng báo giá gửi khách và kiểm tra tồn kho/đơn giá hiện hành.",
                "P1",
                85.0
            )

        # Complained - Than phiền / Khiếu nại
        elif any(k in t_lower for k in ["chậm quá", "lỗi", "không được", "kém", "chưa giao", "hỏng", "thất vọng", "bất mãn", "khiếu nại"]):
            return (
                "Complained",
                "Khiếu Nại / Than Phiền",
                "Tín hiệu không hài lòng về tiến độ hoặc chất lượng phục vụ.",
                "Ưu tiên phản hồi xoa dịu trong vòng 5 phút và kiểm tra sự vụ với team phụ trách.",
                "P0",
                95.0
            )

        # PromisedDelivery - Hứa giao hàng / Hẹn cam kết (Mục G3 & SPEC-22)
        elif any(k in t_lower for k in ["hứa gửi", "mai giao", "giao hàng", "hẹn thứ", "sẽ chuyển", "cam kết xong", "chiều nay gửi", "mai xong", "sẽ gửi lại", "hứa làm"]):
            return (
                "PromisedDelivery",
                "Hứa Giao Hàng & Hẹn Cam Kết",
                "Phát hiện lời hứa hẹn hoặc cam kết về thời gian giao hàng/tài liệu.",
                "Tự động ghi nhận cam kết vào Care Quality Engine để giám sát rủi ro Hứa Rồi Quên.",
                "P1",
                88.0
            )

        # ScheduledMeeting - Hẹn lịch / Gặp mặt
        elif any(k in t_lower for k in ["hẹn gặp", "lịch họp", "họp lúc", "họp zoom", "meet", "gặp nhau", "đặt lịch"]):
            return (
                "ScheduledMeeting",
                "Hẹn Họp / Giao Thương",
                "Đề xuất lịch gặp mặt trao đổi công việc hoặc đàm phán.",
                "Xác nhận lịch rảnh của Sếp và tạo lịch hẹn trên hệ thống Calendar.",
                "P1",
                75.0
            )


        # RequestedPartnership - Tìm đối tác / Cung cầu
        elif any(k in t_lower for k in ["cần tìm", "cần mua", "hợp tác", "tìm xưởng", "nhận làm", "đối tác", "tìm nguồn", "cung cấp"]):
            return (
                "RequestedPartnership",
                "Cung Cầu / Tìm Đối Tác",
                "Tín hiệu cơ hội thương mại xuất hiện: bên thứ ba cần nguồn cung hoặc dịch vụ.",
                "Tạo cơ hội vào Bảng Cơ Hội (Opportunity Board) và kết nối với danh mục năng lực nội bộ.",
                "P1",
                90.0
            )

        # SentQuotation - Gửi báo giá / Chốt deal
        elif any(k in t_lower for k in ["đã gửi báo giá", "gửi hợp đồng", "chốt đơn", "xác nhận đặt", "chuyển khoản", "đã thanh toán"]):
            return (
                "SentQuotation",
                "Báo Giá & Chốt Đơn",
                "Diễn biến thương mại tiến triển đến giai đoạn xác nhận thanh toán/chốt đơn.",
                "Ghi nhận giao dịch vào pipeline, chuẩn bị hợp đồng và thủ tục hậu cần.",
                "P1",
                80.0
            )


        # MentionsCompetitor - Nhắc đối thủ
        elif any(k in t_lower for k in ["bên kia", "công ty khác", "đối thủ", "chỗ khác rẻ hơn"]):
            return (
                "MentionsCompetitor",
                "Đối Thủ Cạnh Tranh",
                "Khách hàng so sánh với các đơn vị đối thủ trên thị trường.",
                "Tập trung tư vấn giá trị khác biệt và chính sách hậu mãi độc quyền.",
                "P2",
                65.0
            )

        # WentSilent - Tín hiệu im lặng / mất liên lạc
        elif any(k in t_lower for k in ["sao không trả lời", "mất hút", "im lặng", "chưa thấy phản hồi", "lâu quá chưa thấy"]):
            return (
                "WentSilent",
                "Cảnh Báo Im Lặng / Mất Hút",
                "Đối tác phản ánh trạng thái im lặng hoặc thiếu tương tác trong thời gian dài.",
                "Kích hoạt cảnh báo nguy cơ rớt khách (Churn Risk) và phân bổ nhân sự phụ trách tiếp cận ngay.",
                "P0",
                92.0
            )

        else:

            return (
                "GeneralConversation",
                "Trao Đổi Thông Thường",
                "Tin nhắn trao đổi nghiệp vụ hoặc chào hỏi thông thường.",
                "Ghi nhận nhật ký và theo dõi ngữ cảnh tiếp theo.",
                "P2",
                40.0
            )

    def process_incoming_message(
        self,
        content: str,
        channel: str = "zalo",
        sender_id: str = "unknown",
        sender_name: str = "Khách",
        group_id: str = None,
        group_name: str = "1-1"
    ) -> dict:
        """
        Bóc tách tin nhắn hội thoại thành Sự kiện nguyên tử (Atomic Event),
        lưu vào SQLite và tự động trích xuất Thực thể + Cơ hội.
        """
        if not content or not content.strip():
            return None

        event_type, intent_label, meaning_summary, suggested_action, priority, heat_score = self.detect_intent(content)
        entities = self.extract_entities_from_text(content)

        event_id = f"EVT-{int(time.time()*1000)%10000000:07d}-{uuid.uuid4().hex[:4]}"
        now_ts = int(time.time())
        now_str = time.strftime("%Y-%m-%d %H:%M:%S")

        # Lưu Atomic Event vào SQLite
        with self._get_conn() as conn:
            conn.execute("""
            INSERT INTO atomic_events (
                id, event_type, channel, sender_id, sender_name,
                group_id, group_name, content, extracted_entities,
                intent, sentiment, meaning_summary, action_suggested,
                priority, status, heat_score, timestamp, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event_id, event_type, channel, sender_id, sender_name,
                group_id, group_name, content, json.dumps(entities, ensure_ascii=False),
                intent_label, "neutral", meaning_summary, suggested_action,
                priority, "NEW", heat_score, now_ts, now_str
            ))

            # Lưu các thực thể đơn lẻ vào bảng entities
            for p in entities.get("prices", []):
                ent_id = f"ENT-PRICE-{uuid.uuid4().hex[:6]}"
                conn.execute("""
                INSERT OR REPLACE INTO entities (id, entity_type, value, normalized_value, source_event_id, frequency, first_seen, last_seen)
                VALUES (?, 'PRICE', ?, ?, ?, 1, ?, ?)
                """, (ent_id, p, p, event_id, now_str, now_str))

            for prod in entities.get("products", []):
                ent_id = f"ENT-PROD-{uuid.uuid4().hex[:6]}"
                conn.execute("""
                INSERT OR REPLACE INTO entities (id, entity_type, value, normalized_value, source_event_id, frequency, first_seen, last_seen)
                VALUES (?, 'PRODUCT', ?, ?, ?, 1, ?, ?)
                """, (ent_id, prod, prod, event_id, now_str, now_str))

            # Nếu là RequestedPartnership hoặc AskedPrice có giá trị -> Tự động kích hoạt Opportunity Signal
            if event_type in ["RequestedPartnership", "AskedPrice"]:
                opp_id = f"OPP-{int(time.time()*1000)%1000000:06d}-{uuid.uuid4().hex[:4]}"
                est_val = 0.0
                if entities.get("prices"):
                    # Thử trích xuất số
                    num_m = re.search(r'\d+', entities["prices"][0])
                    if num_m:
                        est_val = float(num_m.group(0)) * (1000000 if 'tr' in entities["prices"][0].lower() else 1000)

                conn.execute("""
                INSERT INTO opportunities (
                    id, title, contact_name, contact_id, channel,
                    group_name, need_summary, estimated_value,
                    stage, confidence_score, heat_score, risk_notes,
                    source_event_id, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'SIGNAL', 75.0, ?, ?, ?, ?, ?)
                """, (
                    opp_id,
                    f"Nhu cầu: {(entities.get('products') or ['Sản phẩm / Dịch vụ'])[0]} từ {sender_name}",
                    sender_name, sender_id, channel, group_name,
                    content[:200], est_val, heat_score,
                    "Cần tiếp cận trong vòng 24h để tránh nguội cơ hội.",
                    event_id, now_str, now_str
                ))

            conn.commit()

        return {
            "id": event_id,
            "event_type": event_type,
            "intent": intent_label,
            "entities": entities,
            "meaning_summary": meaning_summary,
            "action_suggested": suggested_action,
            "priority": priority,
            "heat_score": heat_score
        }

    def get_atomic_events(self, limit: int = 50, filter_type: str = None) -> list:
        with self._get_conn() as conn:
            if filter_type and filter_type != "ALL":
                cursor = conn.execute(
                    "SELECT * FROM atomic_events WHERE event_type = ? ORDER BY timestamp DESC LIMIT ?",
                    (filter_type, limit)
                )
            else:
                cursor = conn.execute(
                    "SELECT * FROM atomic_events ORDER BY timestamp DESC LIMIT ?",
                    (limit,)
                )
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def get_opportunities(self, limit: int = 50) -> list:
        with self._get_conn() as conn:
            cursor = conn.execute("SELECT * FROM opportunities ORDER BY heat_score DESC LIMIT ?", (limit,))
            return [dict(r) for r in cursor.fetchall()]

    def get_entities(self, limit: int = 100) -> list:
        with self._get_conn() as conn:
            cursor = conn.execute("SELECT * FROM entities ORDER BY last_seen DESC LIMIT ?", (limit,))
            return [dict(r) for r in cursor.fetchall()]

    def get_stats(self) -> dict:
        with self._get_conn() as conn:
            total_evts = conn.execute("SELECT COUNT(*) FROM atomic_events").fetchone()[0]
            total_opps = conn.execute("SELECT COUNT(*) FROM opportunities").fetchone()[0]
            total_ents = conn.execute("SELECT COUNT(*) FROM entities").fetchone()[0]
            
            # Group by event_type
            type_counts = dict(conn.execute("SELECT event_type, COUNT(*) FROM atomic_events GROUP BY event_type").fetchall())
            total_contacts = conn.execute("SELECT COUNT(*) FROM contacts").fetchone()[0]

        return {
            "total_events": total_evts,
            "total_opportunities": total_opps,
            "total_entities": total_ents,
            "total_contacts": total_contacts,
            "event_type_distribution": type_counts
        }

    def update_opportunity_stage(self, opp_id: str, new_stage: str) -> bool:
        """Cập nhật trạng thái cơ hội theo 7 cột Kanban chuẩn Spec LOCKED v2.2."""
        valid_stages = [
            "RAW_SIGNAL", "SIGNAL",
            "QUALIFIED", "VERIFIED",
            "MATCHED",
            "OUTREACH", "APPROACHING",
            "NEGOTIATING",
            "INTERNAL_REVIEW",
            "WON", "CLOSED_WON",
            "LOST", "CLOSED_LOST"
        ]
        if new_stage not in valid_stages:
            return False
        with self._get_conn() as conn:
            now_str = time.strftime("%Y-%m-%d %H:%M:%S")
            conn.execute(
                "UPDATE opportunities SET stage = ?, updated_at = ? WHERE id = ?",
                (new_stage, now_str, opp_id)
            )
            conn.commit()
            return True

    def create_opportunity(self, title: str, contact_name: str, need_summary: str, estimated_value: float = 0.0, channel: str = "manual", stage: str = "SIGNAL") -> dict:
        """Tạo thủ công hoặc từ API một cơ hội mới."""
        opp_id = f"OPP-{int(time.time()*1000)%1000000:06d}-{uuid.uuid4().hex[:4]}"
        now_str = time.strftime("%Y-%m-%d %H:%M:%S")
        with self._get_conn() as conn:
            conn.execute("""
            INSERT INTO opportunities (
                id, title, contact_name, contact_id, channel, group_name,
                need_summary, estimated_value, stage, confidence_score,
                heat_score, risk_notes, source_event_id, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, 'Direct', ?, ?, ?, 80.0, 75.0, 'Được tạo bởi Sếp hoặc AI Agent', 'MANUAL', ?, ?)
            """, (opp_id, title, contact_name, f"user-{uuid.uuid4().hex[:6]}", channel, need_summary, estimated_value, stage, now_str, now_str))
            conn.commit()
        return {"id": opp_id, "title": title, "stage": stage}


    def update_opportunity(self, opp_id: str, updates: dict) -> bool:
        """Cập nhật chi tiết cơ hội (giá trị, tỷ lệ thắng, người phụ trách, ghi chú...)."""
        allowed_fields = ["title", "estimated_value", "stage", "owner", "win_probability", "heat_score", "need_summary", "risk_notes"]
        set_clauses = []
        vals = []
        for k, v in updates.items():
            if k in allowed_fields:
                set_clauses.append(f"{k} = ?")
                vals.append(v)
        if not set_clauses:
            return False
        now_str = time.strftime("%Y-%m-%d %H:%M:%S")
        set_clauses.append("updated_at = ?")
        vals.append(now_str)
        vals.append(opp_id)

        query = f"UPDATE opportunities SET {', '.join(set_clauses)} WHERE id = ?"
        with self._get_conn() as conn:
            conn.execute(query, tuple(vals))
            conn.commit()
            return True

    def delete_opportunity(self, opp_id: str) -> bool:
        """Xóa hoặc lưu trữ một cơ hội khỏi Pipeline."""
        with self._get_conn() as conn:
            conn.execute("DELETE FROM opportunities WHERE id = ?", (opp_id,))
            conn.commit()
            return True

    def archive_atomic_event(self, event_id: str) -> bool:
        """Lưu trữ một sự kiện nguyên tử (Inbox Zero cho Meaning Cards)."""
        with self._get_conn() as conn:
            conn.execute("UPDATE atomic_events SET archived = 1, status = 'ARCHIVED' WHERE id = ?", (event_id,))
            conn.commit()
            return True

    def match_opportunity_supply_demand(self, opp_id: str) -> dict:
        """(SPEC-12) Ráp cung với cầu & Hàng đợi cơ hội tự động."""
        with self._get_conn() as conn:
            opp = conn.execute("SELECT * FROM opportunities WHERE id = ?", (opp_id,)).fetchone()
            if not opp:
                return {"matched": False, "reason": "Không tìm thấy cơ hội"}
            opp_dict = dict(opp)
            summary = (opp_dict.get("need_summary") or "").lower()
            title = (opp_dict.get("title") or "").lower()
            text = f"{title} {summary}"

            # Catalog dịch vụ nội bộ Gen-Harness
            catalog = [
                {"code": "SRV-AI", "name": "Giải pháp AI Agent Điều Phối & Chatbot Đa Kênh", "keywords": ["ai", "bot", "điều phối", "zalo", "whatsapp", "tin nhắn"], "base_price": 150000000.0, "default_owner": "Sếp Cơ La (Ryan)"},
                {"code": "SRV-ERP", "name": "Tích hợp MCP Connectors & Dữ liệu ERP/CRM", "keywords": ["erp", "crm", "kết nối", "tích hợp", "phần mềm", "dữ liệu"], "base_price": 300000000.0, "default_owner": "Phòng Kỹ Thuật & Sếp Ryan"},
                {"code": "SRV-DOC", "name": "Dịch vụ Báo Cáo Tự Động Word & Excel Reporter", "keywords": ["báo cáo", "tài chính", "word", "excel", "phân tích", "mẫu"], "base_price": 50000000.0, "default_owner": "Trợ Lý Thương Mại"},
                {"code": "SRV-AUDIO", "name": "Sản xuất Giọng Nói AI Độc Quyền & Audio TTS", "keywords": ["giọng đọc", "audio", "tts", "nhạc", "beat", "truyền thông"], "base_price": 80000000.0, "default_owner": "Bộ phận Media"}
            ]

            best_match = None
            best_score = 0
            for item in catalog:
                matched_kw = [kw for kw in item["keywords"] if kw in text]
                score = len(matched_kw) * 25
                if score > best_score:
                    best_score = score
                    best_match = item

            if best_match and best_score >= 25:
                # Update opportunity to MATCHED stage and assign owner
                new_val = opp_dict.get("estimated_value") or best_match["base_price"]
                conn.execute(
                    "UPDATE opportunities SET stage = 'MATCHED', estimated_value = ?, owner = ?, confidence_score = 85.0, updated_at = ? WHERE id = ?",
                    (new_val, best_match["default_owner"], time.strftime("%Y-%m-%d %H:%M:%S"), opp_id)
                )
                conn.commit()
                return {
                    "matched": True,
                    "service_code": best_match["code"],
                    "service_name": best_match["name"],
                    "confidence": best_score,
                    "recommended_price": best_match["base_price"],
                    "recommended_owner": best_match["default_owner"]
                }
            return {"matched": False, "reason": "Chưa đủ dữ kiện để ráp khớp tự động"}

    def get_contacts(self, limit: int = 50) -> list:
        """Lấy danh sách các liên hệ (Person / Living Contacts) kèm chỉ số tương tác."""
        with self._get_conn() as conn:
            cursor = conn.execute("SELECT * FROM contacts ORDER BY heat_score DESC, last_seen DESC LIMIT ?", (limit,))
            return [dict(r) for r in cursor.fetchall()]

    def merge_contacts(self, primary_id: str, secondary_id: str) -> bool:
        """Identity Resolution: Gộp định danh liên hệ thứ cấp vào liên hệ chính."""
        with self._get_conn() as conn:
            p_row = conn.execute("SELECT * FROM contacts WHERE id = ?", (primary_id,)).fetchone()
            s_row = conn.execute("SELECT * FROM contacts WHERE id = ?", (secondary_id,)).fetchone()
            if not p_row or not s_row:
                return False
            p = dict(p_row)
            s = dict(s_row)
            
            # Gộp thông tin
            phone = p.get("phone") or s.get("phone")
            zalo_id = p.get("zalo_id") or s.get("zalo_id")
            whatsapp_id = p.get("whatsapp_id") or s.get("whatsapp_id")
            email = p.get("email") or s.get("email")
            company = p.get("company") or s.get("company")
            role = p.get("role") or s.get("role")
            ai_summary = f"{p.get('ai_summary', '')}\n[Đã hợp nhất với {s.get('full_name')}]: {s.get('ai_summary', '')}".strip()
            total_interactions = (p.get("interaction_count") or 1) + (s.get("interaction_count") or 1)

            conn.execute("""
            UPDATE contacts 
            SET phone = ?, zalo_id = ?, whatsapp_id = ?, email = ?, company = ?, role = ?,
                ai_summary = ?, interaction_count = ?
            WHERE id = ?
            """, (phone, zalo_id, whatsapp_id, email, company, role, ai_summary, total_interactions, primary_id))

            # Chuyển các event và opp sang primary_id
            conn.execute("UPDATE atomic_events SET sender_id = ? WHERE sender_id = ?", (primary_id, secondary_id))
            conn.execute("UPDATE opportunities SET contact_id = ? WHERE contact_id = ?", (primary_id, secondary_id))
            conn.execute("DELETE FROM contacts WHERE id = ?", (secondary_id,))
            conn.commit()
            return True

    def get_contact_detail(self, contact_id: str) -> dict:
        """Lấy thông tin chi tiết một liên hệ, bao gồm hồ sơ 360, các sự kiện nguyên tử và deals liên quan."""
        with self._get_conn() as conn:
            c_row = conn.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,)).fetchone()
            if not c_row:
                return {"ok": False, "error": "Contact not found"}
            contact = dict(c_row)
            
            # Lấy danh sách atomic events của người này
            evt_rows = conn.execute(
                "SELECT * FROM atomic_events WHERE sender_id = ? OR sender_name = ? ORDER BY timestamp DESC LIMIT 20",
                (contact_id, contact.get("full_name"))
            ).fetchall()
            events = [dict(r) for r in evt_rows]
            
            # Lấy danh sách cơ hội deals liên quan
            opp_rows = conn.execute(
                "SELECT * FROM opportunities WHERE contact_id = ? OR contact_name = ? ORDER BY updated_at DESC",
                (contact_id, contact.get("full_name"))
            ).fetchall()
            opportunities = [dict(r) for r in opp_rows]
            
            return {
                "ok": True,
                "contact": contact,
                "events": events,
                "opportunities": opportunities
            }

    def update_contact_autonomy(self, contact_id: str, autonomy_level: int) -> bool:
        """(SPEC-20) Cập nhật mức tự trị (Autonomy Level 0-6) cho một liên hệ."""
        if not (0 <= autonomy_level <= 6):
            return False
        with self._get_conn() as conn:
            conn.execute("UPDATE contacts SET autonomy_level = ? WHERE id = ?", (autonomy_level, contact_id))
            conn.commit()
            return True

    def generate_contact_summary(self, contact_id: str) -> dict:
        """(SPEC-20, SPEC-10) Phân tích hành vi tương tác để sinh tóm tắt AI Executive Summary 8-12 dòng và giải thích điểm Explainable AI."""
        with self._get_conn() as conn:
            c_row = conn.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,)).fetchone()
            if not c_row:
                return {"ok": False, "error": "Contact not found"}
            c = dict(c_row)
            
            # Lấy các sự kiện tương tác
            evts = conn.execute(
                "SELECT * FROM atomic_events WHERE sender_id = ? OR sender_name = ? ORDER BY timestamp DESC LIMIT 10",
                (contact_id, c.get("full_name"))
            ).fetchall()
            
            name = c.get("full_name", "Đối tác")
            company = c.get("company", "Doanh nghiệp")
            role = c.get("role", "Đại diện")
            heat = c.get("heat_score", 50.0)
            went_silent = c.get("went_silent_days", 0)
            
            # Tính toán Explainable AI Logic
            reasons = []
            if heat >= 80:
                reasons.append(f"Điểm nhiệt huyết cao ({heat}°/100) nhờ tần suất trao đổi tích cực và phản hồi nhanh.")
            elif heat >= 50:
                reasons.append(f"Điểm nhiệt độ ổn định ({heat}°/100), đang duy trì đà quan hệ tích cực.")
            else:
                reasons.append(f"Điểm quan hệ thấp ({heat}°/100) do thời gian ngắt quãng trao đổi kéo dài.")
                
            if went_silent > 3:
                reasons.append(f"Cảnh báo: Đối tác đã im lặng {went_silent} ngày sau khi nhận tín hiệu.")
            else:
                reasons.append("Tương tác liên tục trong 48 giờ qua, không bị gián đoạn thông tin.")
                
            reasons.append(f"Đã ghi nhận {len(evts)} sự kiện hội thoại nguyên tử được bóc tách tự động.")
            score_expl = " | ".join(reasons)
            
            # Tạo Executive Summary 8-12 dòng chuẩn SSOT
            summary_lines = [
                f"1. Tổng quan: {name} hiện giữ vai trò {role} tại {company}, là mắt xích liên hệ quan trọng trong mạng lưới đối tác.",
                f"2. Kênh tương tác ưu tiên: Chủ yếu trao đổi qua Zalo ({c.get('zalo_id') or 'chính'}) và WhatsApp ({c.get('whatsapp_id') or 'phụ'}).",
                f"3. Nhịp độ phản hồi: {'Cực kỳ khẩn trương và thích hành động nhanh.' if heat >= 80 else 'Đều đặn, cân nhắc kỹ lưỡng các đề xuất giá trị.'}",
                f"4. Trạng thái bóng: Hiện bóng đang ở phía {'CHÚNG TA (US) - Cần chủ động phản hồi giải quyết nhu cầu.' if c.get('ball_owner') == 'US' else 'ĐỐI TÁC (THEM) - Đang chờ họ xem xét và hồi âm.'}",
                f"5. Xu hướng nhu cầu: Quan tâm đến các gói giải pháp AI điều phối, tự động hóa quy trình nghiệp vụ và báo cáo thông minh.",
                f"6. Rủi ro Churn: {c.get('churn_risk', 15.0)}% - {'Cần theo dõi sát để tránh bị phân tâm bởi đối thủ.' if c.get('churn_risk', 15) > 30 else 'Mối quan hệ tin cậy, mức gắn kết cao.'}",
                f"7. Mức tự trị đề xuất: Cấp {c.get('autonomy_level', 2)}/6 (Hệ thống có thể tự động trả lời theo kịch bản chuẩn và chuẩn bị bản nháp cho Sếp duyệt).",
                f"8. Đề xuất hành động tiếp theo: Duy trì liên lạc định kỳ, gửi các tài liệu cập nhật năng lực mới nhất của Heo-Harness."
            ]
            full_summary = "\n".join(summary_lines)
            
            conn.execute(
                "UPDATE contacts SET ai_summary = ?, score_explanation = ? WHERE id = ?",
                (full_summary, score_expl, contact_id)
            )
            conn.commit()
            
            return {
                "ok": True,
                "ai_summary": full_summary,
                "score_explanation": score_expl
            }

    def get_relationship_graph(self) -> dict:
        """(SPEC-19: [UI-03] Relationship Map - Obsidian Style) Dựng cấu trúc Node & Edge phân nhóm chuẩn xác."""
        with self._get_conn() as conn:
            contacts = [dict(r) for r in conn.execute("SELECT * FROM contacts").fetchall()]
            opportunities = [dict(r) for r in conn.execute("SELECT * FROM opportunities").fetchall()]
            events = [dict(r) for r in conn.execute("SELECT * FROM atomic_events ORDER BY timestamp DESC LIMIT 100").fetchall()]
            
        nodes = []
        edges = []
        
        # 1. Central HQ Node (Sếp Ryan)
        nodes.append({
            "id": "node-hq",
            "label": "Anh Cơ La (Ryan) / HQ",
            "type": "hq",
            "category": "hq",
            "role": "Tổng Chỉ Huy Tối Cao",
            "heat": 100,
            "size": 32,
            "color": "#818cf8"
        })
        
        # 2. Canonical Business Groups (Lọc bỏ các group tạm web_console)
        canonical_groups = [
            {"id": "grp-zalo-crm", "name": "Dự Án CRM (Zalo)", "channel": "zalo", "desc": "Cung ứng & Triển khai phần mềm"},
            {"id": "grp-wa-logitech", "name": "LogiTech Global (WhatsApp)", "channel": "whatsapp", "desc": "Đối tác công nghệ AI điều phối"},
            {"id": "grp-wa-fashion", "name": "Thời Trang Hà My (WhatsApp)", "channel": "whatsapp", "desc": "Gia công & ERP xưởng may"},
            {"id": "grp-zalo-telecom", "name": "Trung Tâm Viễn Thông (Zalo)", "channel": "zalo", "desc": "Đối tác hạ tầng AI Audio"}
        ]
        
        for g in canonical_groups:
            nodes.append({
                "id": g["id"],
                "label": g["name"],
                "type": "group",
                "category": "channel",
                "channel": g["channel"],
                "size": 22,
                "color": "#0ea5e9" if g["channel"] == "zalo" else "#10b981"
            })
            edges.append({
                "from": "node-hq",
                "to": g["id"],
                "label": "Kênh Kết Nối",
                "category": "channel_link",
                "color": "rgba(99, 102, 241, 0.35)"
            })
                
        # 3. Contact Nodes (Phân loại rõ ràng thành 3 cụm: Hot, Warm, Cold)
        for c in contacts:
            cid = f"cnt-{c['id']}"
            heat = c.get("heat_score", 50.0)
            went_silent = c.get("went_silent_days", 0)
            
            if heat >= 80:
                cat = "hot"
                color = "#f43f5e" # Rose / Hot Red
            elif heat >= 50 and went_silent <= 3:
                cat = "warm"
                color = "#f59e0b" # Amber / Warm
            else:
                cat = "cold"
                color = "#64748b" # Slate / Cold Silent

            nodes.append({
                "id": cid,
                "raw_id": c["id"],
                "label": c["full_name"],
                "company": c.get("company", ""),
                "role": c.get("role", ""),
                "type": "contact",
                "category": cat,
                "heat": heat,
                "autonomy_level": c.get("autonomy_level", 1),
                "ball_owner": c.get("ball_owner", "THEM"),
                "went_silent_days": went_silent,
                "size": 18,
                "color": color
            })
            
            # Phân bổ kết nối nhóm thông minh
            if "Mai Phương" in c["full_name"] or "Minh" in c["full_name"]:
                edges.append({"from": "grp-zalo-crm", "to": cid, "label": "Thành viên", "category": "group_link", "color": "rgba(14, 165, 233, 0.35)"})
            elif "Hoàng Bách" in c["full_name"] or "Tân Á" in c["full_name"]:
                edges.append({"from": "grp-wa-logitech", "to": cid, "label": "Thành viên", "category": "group_link", "color": "rgba(16, 185, 129, 0.35)"})
            elif "Thu Hà" in c["full_name"]:
                edges.append({"from": "grp-wa-fashion", "to": cid, "label": "Thành viên", "category": "group_link", "color": "rgba(16, 185, 129, 0.35)"})
            elif "Thảo" in c["full_name"] or "Viettel" in c["full_name"]:
                edges.append({"from": "grp-zalo-telecom", "to": cid, "label": "Thành viên", "category": "group_link", "color": "rgba(14, 165, 233, 0.35)"})
            elif "Long" in c["full_name"]:
                edges.append({"from": "grp-wa-logitech", "to": cid, "label": "Thành viên", "category": "group_link", "color": "rgba(16, 185, 129, 0.35)"})
            else:
                edges.append({"from": "node-hq", "to": cid, "label": "1-1", "category": "direct_link", "color": "rgba(148, 163, 184, 0.3)"})
                
        # 4. Opportunity Nodes (Deals vệ tinh xung quanh từng contact)
        def _compact_deal_title(raw_title: str, val: float) -> str:
            t = raw_title.replace("Nhu cầu: ", "").replace("Hợp đồng ", "").replace("Tín hiệu ", "").strip()
            # Rút gọn các mẫu câu thông dụng
            if "ERP/CRM" in t:
                name = "ERP/CRM Hub"
            elif "AI Điều Phối" in t:
                name = "AI Điều Phối Đa Kênh"
            elif "Báo Cáo Tài Chính" in t or "báo giá từ Anh Minh" in t:
                name = "Báo Cáo Phân Tích Kafi"
            elif "Nhận Diện AI" in t:
                name = "Bộ Nhận Diện AI"
            elif "Server Cục Bộ" in t or "Hạ Tầng" in t:
                name = "Hạ Tầng AI Server Viettel"
            elif "Bản Quyền Gen-Harness" in t:
                name = "Bản Quyền Doanh Nghiệp"
            elif "Cloud Server" in t:
                name = "Gói Cloud Server"
            elif "báo giá từ Chị Mai Phương" in t or "báo giá" in t.lower():
                name = "Báo Giá VinaSupply"
            else:
                name = (t[:22] + "...") if len(t) > 24 else t
            val_str = f" ({val/1e9:.1f}B)" if val >= 1e9 else (f" ({val/1e6:.0f}tr)" if val > 0 else "")
            return f"{name}{val_str}"

        for opp in opportunities:
            oid = f"opp-{opp['id']}"
            est_val = opp.get("estimated_value", 0.0)
            stage = opp.get("stage", "SIGNAL")
            full_title = opp.get("title", "Cơ hội")
            compact_label = _compact_deal_title(full_title, est_val)

            nodes.append({
                "id": oid,
                "raw_id": opp["id"],
                "label": compact_label,
                "full_title": full_title,
                "value": est_val,
                "stage": stage,
                "type": "opportunity",
                "category": "deal",
                "size": 14,
                "color": "#c084fc" # Purple Lavender
            })
            
            # Nối với Contact tương ứng
            c_match_id = None
            for c in contacts:
                if opp.get("contact_id") == c["id"] or opp.get("contact_name") == c["full_name"]:
                    c_match_id = f"cnt-{c['id']}"
                    break
            
            if c_match_id:
                edges.append({
                    "from": c_match_id,
                    "to": oid,
                    "label": f"{est_val/1000000:.0f}tr" if est_val > 0 else "Deal",
                    "category": "deal_link",
                    "color": "rgba(192, 132, 252, 0.45)"
                })
            else:
                # Nếu không xác định được contact, liên kết vào nhóm CRM thay vì kéo về HQ
                edges.append({
                    "from": "grp-zalo-crm",
                    "to": oid,
                    "label": "Deal",
                    "category": "deal_link",
                    "color": "rgba(192, 132, 252, 0.45)"
                })
                
        categories = [
            {"key": "hq", "label": "👑 HQ Trung Tâm", "color": "#818cf8"},
            {"key": "channel", "label": "💬 Kênh Zalo & WhatsApp", "color": "#0ea5e9"},
            {"key": "hot", "label": "🔥 Khách Hàng Nóng (>=80°)", "color": "#f43f5e"},
            {"key": "warm", "label": "🟡 Đối Tác Ấm Áp (50-79°)", "color": "#f59e0b"},
            {"key": "cold", "label": "⚪ Đang Lạnh / Went Silent", "color": "#64748b"},
            {"key": "deal", "label": "💼 Cơ Hội Deals (VND)", "color": "#c084fc"}
        ]

        return {
            "ok": True,
            "nodes": nodes,
            "edges": edges,
            "categories": categories,
            "stats": {
                "total_nodes": len(nodes),
                "total_edges": len(edges),
                "contacts_count": len(contacts),
                "opportunities_count": len(opportunities),
                "groups_count": len(canonical_groups)
            }
        }

    def seed_sample_data_if_empty(self):
        """Khởi tạo dữ liệu mẫu chuẩn theo Spec LOCKED nếu hệ thống chưa có dữ liệu."""
        with self._get_conn() as conn:
            cnt_count = conn.execute("SELECT COUNT(*) FROM contacts").fetchone()[0]
            evt_count = conn.execute("SELECT COUNT(*) FROM atomic_events").fetchone()[0]

        now_str = time.strftime("%Y-%m-%d %H:%M:%S")

        # 1. Thêm Contacts mẫu nếu chưa có
        if cnt_count == 0:
            sample_contacts = [
                ("CNT-001", "Chị Mai Phương", "0908123456", "zalo-mp-88", "", "maiphuong@vinasupply.com", "VinaSupply Corp", "Giám Đốc Mua Hàng", 92.0, "HOT", "US", 0, "Chị Mai Phương là đối tác cung ứng vật tư chiến lược, luôn cần báo giá nhanh trong 2 giờ. Thích làm việc rõ ràng bằng văn bản."),
                ("CNT-002", "Anh Hoàng Bách", "0912345678", "zalo-bach-99", "wa-bach-99", "bach.hoang@logitechvn.io", "LogiTech Global", "Head of Tech Procurement", 85.0, "HOT", "THEM", 1, "Cần triển khai hệ thống AI Agent điều phối kho bãi và tin nhắn CSKH Zalo cho 5 chi nhánh."),
                ("CNT-003", "Trần Thu Hà", "0987654321", "", "wa-thuha", "thuha.tran@fashionviet.vn", "Thời Trang Hà My", "Founder & CEO", 68.0, "WARM", "US", 2, "Đang tìm xưởng gia công 10,000 áo thun xuất khẩu đi Nhật Bản, ngân sách 1.2 tỷ VND."),
                ("CNT-004", "Nguyễn Đức Trí", "0933445566", "zalo-tri-tri", "", "tri.nguyen@vietfintech.net", "Fintech Solutions", "COO", 35.0, "COLD", "THEM", 8, "Đã trao đổi thử nghiệm demo API 8 ngày trước nhưng chưa phản hồi chốt lịch ký HĐ.")
            ]
            with self._get_conn() as conn:
                for c in sample_contacts:
                    conn.execute("""
                    INSERT OR IGNORE INTO contacts (
                        id, full_name, phone, zalo_id, whatsapp_id, email, company, role,
                        heat_score, status, ball_owner, went_silent_days, ai_summary, first_seen, last_seen
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (c[0], c[1], c[2], c[3], c[4], c[5], c[6], c[7], c[8], c[9], c[10], c[11], c[12], now_str, now_str))

        # 2. Xử lý các tin nhắn mẫu sinh Atomic Events & Opportunities nếu ít hơn 3 sự kiện
        if evt_count < 3:
            sample_messages = [
                ("Em cần bên mình gửi báo giá gấp 50 triệu cho gói triển khai phần mềm CRM trong chiều nay nhé!", "zalo", "CNT-001", "Chị Mai Phương", "GRP-01", "Dự Án CRM"),
                ("Chào Sếp, bên em chuẩn bị mở rộng 3 chi nhánh mới và cần hợp tác tìm đối tác công nghệ AI điều phối tin nhắn khách hàng.", "whatsapp", "CNT-002", "Anh Hoàng Bách", "GRP-02", "LogiTech Executive"),
                ("Hôm trước báo giao hồ sơ bản cứng mà hôm nay vẫn chưa thấy bên vận chuyển liên hệ, trễ hẹn quá em ơi!", "zalo", "CNT-001", "Chị Mai Phương", "GRP-01", "Dự Án CRM"),
                ("Anh muốn đặt lịch hẹn gặp trực tiếp tại văn phòng thứ 4 tuần này lúc 14h để bàn về điều khoản hợp đồng.", "zalo", "CNT-002", "Anh Hoàng Bách", "GRP-02", "LogiTech Executive"),
                ("Bên em đang cần tìm xưởng gia công gấp lô hàng may mặc xuất khẩu 1.2 tỷ hoàn thành trước tháng sau.", "whatsapp", "CNT-003", "Trần Thu Hà", "GRP-03", "Hợp Tác Cung Ứng")
            ]
            for msg in sample_messages:
                self.process_incoming_message(
                    content=msg[0],
                    channel=msg[1],
                    sender_id=msg[2],
                    sender_name=msg[3],
                    group_id=msg[4],
                    group_name=msg[5]
                )

# Global singleton
_data_factory_instance = None
def get_data_factory() -> ConversationDataFactory:
    global _data_factory_instance
    if _data_factory_instance is None:
        _data_factory_instance = ConversationDataFactory()
    return _data_factory_instance
