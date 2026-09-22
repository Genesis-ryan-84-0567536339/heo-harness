"""
HEO-HARNESS RELATIONSHIP MAP & OPPORTUNITY BOARD INTELLIGENCE ENGINE (SPEC-43: Phase 3 - Quản được)
----------------------------------------------------------------------------------------------------
Tác giả: Anh Cơ La (genesis.corp.os@gmail.com)
Tuân thủ: Gen-Harness Product Spec LOCKED v2.2 (Mục L Phase 3, E4, E8, F2.3, F2.5, F2.7, F4)

1. Relationship Graph (E4, F2.3):
   - Đồ thị sống: Node (Người / Tổ chức / Nhóm) & Edge (Tần suất, chiều tương tác, chủ đề, giai đoạn, ai nắm bóng).
   - Phân tích Top Cầu Nối (Top Connectors), Khách Đang Lạnh (Cold Leads), Nhân Viên Quá Tải (Overloaded Agents).
   - Trọng tài bóng (Ball-in-court breakdown): US vs THEM.
   - Hai chế độ: Danh sách lọc đa chiều + Đồ thị trực quan Canvas.
   - Click node mở Living Profile 360.

2. Opportunity Kanban Board (E3, F2.5):
   - 8 giai đoạn chuẩn:
     1. RAW_SIGNAL (Tín hiệu thô từ chat)
     2. VERIFIED (Đã xác thực nhu cầu & ngân sách)
     3. MATCHED (Đã ráp khớp catalog / nhân sự)
     4. APPROACHING (Đang tiếp cận / chào giá sơ bộ)
     5. NEGOTIATING (Đang đàm phán điều khoản)
     6. INTERNAL_TRANSFERRED (Đã chuyển giao nội bộ / ERP)
     7. WON (Thắng / Chốt thành công)
     8. LOST (Trượt / Ngủ đông)
   - Mỗi card có: Ai cần gì, Độ nóng & Độ tin, Ghép với ai/hàng gì, Giá trị deal, Rủi ro nếu không làm gì.
   - Lưu vết lịch sử chuyển stage (opportunity_stage_history).

3. Care Quality Intelligence (E8, F2.7):
   - Tốc độ phản hồi trung bình theo nhân viên và theo khung giờ (sáng, trưa, chiều, tối).
   - Tỷ lệ follow sau báo giá (Follow-up rate).
   - Tỷ lệ hứa rồi quên (Broken promise rate).
   - Khách bị bỏ rơi (Abandoned contacts).
   - Kịch bản thắng vs kịch bản mất khách (Winning & Churn patterns).
"""

import os
import json
import sqlite3
import time
import contextlib
from typing import Dict, List, Any, Optional


class RelationshipIntelligenceEngine:
    """
    Bộ não điều phối Bản Đồ Quan Hệ, Bảng Cơ Hội Kanban 8 Cột và Chất Lượng Chăm Sóc.
    Đạt chuẩn SSOT Chặng 3 (Phase 3 - Quản được) Spec LOCKED v2.2.
    """

    # 8 Canonical Opportunity Stages
    STAGE_RAW_SIGNAL = "RAW_SIGNAL"
    STAGE_VERIFIED = "VERIFIED"
    STAGE_MATCHED = "MATCHED"
    STAGE_APPROACHING = "APPROACHING"
    STAGE_NEGOTIATING = "NEGOTIATING"
    STAGE_INTERNAL_TRANSFERRED = "INTERNAL_TRANSFERRED"
    STAGE_WON = "WON"
    STAGE_LOST = "LOST"

    CANONICAL_STAGES = [
        {"key": STAGE_RAW_SIGNAL, "label": "📡 Tín Hiệu Thô", "color": "#94a3b8", "desc": "Tín hiệu vừa bóc tách từ chat"},
        {"key": STAGE_VERIFIED, "label": "🔍 Đã Xác Thực", "color": "#38bdf8", "desc": "Đã làm rõ nhu cầu & ngân sách"},
        {"key": STAGE_MATCHED, "label": "🤝 Đã Ráp Khớp", "color": "#a855f7", "desc": "Ghép catalog sản phẩm & người phụ trách"},
        {"key": STAGE_APPROACHING, "label": "📞 Đang Tiếp Cận", "color": "#f59e0b", "desc": "Đang kết nối & chào giá sơ bộ"},
        {"key": STAGE_NEGOTIATING, "label": "💼 Đang Đàm Phán", "color": "#ec4899", "desc": "Thương thảo điều khoản, chiết khấu"},
        {"key": STAGE_INTERNAL_TRANSFERRED, "label": "⚖️ Chuyển Nội Bộ", "color": "#6366f1", "desc": "Đã chuyển giao ERP / Hậu cần hợp đồng"},
        {"key": STAGE_WON, "label": "🏆 Thắng (Won)", "color": "#10b981", "desc": "Chốt hợp đồng thành công"},
        {"key": STAGE_LOST, "label": "❄️ Trượt / Ngủ Đông", "color": "#64748b", "desc": "Tạm dừng hoặc đối thủ lấy mất"}
    ]

    # Stage alias mapping for backwards compatibility
    STAGE_MAP = {
        "SIGNAL": STAGE_RAW_SIGNAL,
        "RAW_SIGNAL": STAGE_RAW_SIGNAL,
        "QUALIFIED": STAGE_VERIFIED,
        "VERIFIED": STAGE_VERIFIED,
        "MATCHED": STAGE_MATCHED,
        "OUTREACH": STAGE_APPROACHING,
        "APPROACHING": STAGE_APPROACHING,
        "NEGOTIATING": STAGE_NEGOTIATING,
        "INTERNAL_REVIEW": STAGE_INTERNAL_TRANSFERRED,
        "INTERNAL_TRANSFERRED": STAGE_INTERNAL_TRANSFERRED,
        "CLOSED_WON": STAGE_WON,
        "WON": STAGE_WON,
        "CLOSED_LOST": STAGE_LOST,
        "LOST": STAGE_LOST,
        "DORMANT": STAGE_LOST
    }

    def __init__(self, data_dir: str = None):
        if not data_dir:
            root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            self.data_dir = os.path.join(root_dir, "data")
        else:
            self.data_dir = data_dir
            
        os.makedirs(self.data_dir, exist_ok=True)
        self.db_path = os.path.join(self.data_dir, "heo.db")
        self._init_db()
        self._seed_initial_data_if_needed()

    @contextlib.contextmanager
    def _get_conn(self):
        conn = sqlite3.connect(self.db_path, timeout=15.0)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_db(self):
        """Khởi tạo cấu trúc bảng SSOT cho Relationship Map, Opportunity Board và Care Quality."""
        with self._get_conn() as conn:
            # 0. Core tables nếu đang chạy môi trường test cô lập
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
                    status TEXT DEFAULT 'ACTIVE',
                    ball_owner TEXT DEFAULT 'US',
                    went_silent_days INTEGER DEFAULT 0,
                    tags TEXT DEFAULT '[]',
                    ai_summary TEXT DEFAULT '',
                    interaction_count INTEGER DEFAULT 1,
                    first_seen TEXT,
                    last_seen TEXT,
                    autonomy_level INTEGER DEFAULT 2,
                    engagement_score REAL DEFAULT 50.0,
                    churn_risk REAL DEFAULT 20.0,
                    score_explanation TEXT DEFAULT '',
                    data_confidence REAL DEFAULT 85.0,
                    notes TEXT DEFAULT '',
                    merged_into TEXT,
                    internal_handler TEXT DEFAULT 'Anh Cơ La (Ryan)',
                    exchanged_docs TEXT DEFAULT '[]',
                    relationship_stage TEXT DEFAULT 'warm'
                )
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
                    stage TEXT DEFAULT 'RAW_SIGNAL',
                    confidence_score REAL DEFAULT 75.0,
                    heat_score REAL DEFAULT 60.0,
                    risk_notes TEXT DEFAULT '',
                    source_event_id TEXT,
                    created_at REAL,
                    updated_at REAL,
                    owner TEXT DEFAULT 'Anh Cơ La (Ryan)',
                    win_probability INTEGER DEFAULT 50,
                    matched_offer TEXT DEFAULT '',
                    risk_of_inaction TEXT DEFAULT '',
                    assigned_owner TEXT DEFAULT 'Anh Cơ La (Ryan)'
                )
            """)

            # 1. Bảng quan hệ mạng lưới đồ thị (Relationship Edges)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS relationship_edges (
                    id TEXT PRIMARY KEY,
                    from_node TEXT NOT NULL,
                    to_node TEXT NOT NULL,
                    edge_type TEXT NOT NULL, -- channel_link, deal_link, collaboration, referral, direct_1_1
                    weight REAL DEFAULT 1.0,
                    interaction_count INTEGER DEFAULT 1,
                    last_topic TEXT DEFAULT '',
                    relationship_stage TEXT DEFAULT 'warm', -- cold, warm, hot, partner, risk
                    ball_owner TEXT DEFAULT 'THEM', -- US, THEM
                    risk_factor TEXT DEFAULT 'LOW', -- LOW, MEDIUM, HIGH
                    last_interaction_ts REAL DEFAULT 0,
                    metadata TEXT DEFAULT '{}',
                    created_at REAL DEFAULT 0,
                    updated_at REAL DEFAULT 0
                )
            """)

            # 2. Bảng lịch sử chuyển stage cơ hội (Opportunity Stage History)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS opportunity_stage_history (
                    id TEXT PRIMARY KEY,
                    opp_id TEXT NOT NULL,
                    from_stage TEXT NOT NULL,
                    to_stage TEXT NOT NULL,
                    reason TEXT DEFAULT '',
                    changed_by TEXT DEFAULT 'Anh Cơ La (Ryan)',
                    created_at REAL DEFAULT 0
                )
            """)

            # 3. Bảng chất lượng chăm sóc (Care Quality Records)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS care_quality_records (
                    id TEXT PRIMARY KEY,
                    person_id TEXT,
                    full_name TEXT NOT NULL,
                    role TEXT NOT NULL,
                    avg_response_min REAL DEFAULT 5.0,
                    follow_up_rate REAL DEFAULT 85.0,
                    broken_promises_count INTEGER DEFAULT 0,
                    abandoned_clients_count INTEGER DEFAULT 0,
                    care_health_score INTEGER DEFAULT 80,
                    winning_notes TEXT DEFAULT '',
                    losing_notes TEXT DEFAULT '',
                    updated_at TEXT DEFAULT ''
                )
            """)

            # 4. Self-heal các cột bổ sung cho opportunities nếu thiếu
            opp_cols = [c[1] for c in conn.execute("PRAGMA table_info(opportunities)").fetchall()]
            if opp_cols:
                if "matched_offer" not in opp_cols:
                    conn.execute("ALTER TABLE opportunities ADD COLUMN matched_offer TEXT DEFAULT ''")
                if "risk_of_inaction" not in opp_cols:
                    conn.execute("ALTER TABLE opportunities ADD COLUMN risk_of_inaction TEXT DEFAULT ''")
                if "assigned_owner" not in opp_cols:
                    conn.execute("ALTER TABLE opportunities ADD COLUMN assigned_owner TEXT DEFAULT 'Anh Cơ La (Ryan)'")

            # 5. Self-heal cột relationship_stage cho contacts nếu thiếu
            cnt_cols = [c[1] for c in conn.execute("PRAGMA table_info(contacts)").fetchall()]
            if cnt_cols:
                if "relationship_stage" not in cnt_cols:
                    conn.execute("ALTER TABLE contacts ADD COLUMN relationship_stage TEXT DEFAULT 'warm'")

    def _seed_initial_data_if_needed(self):
        """Khởi tạo dữ liệu mẫu cho contacts, opportunities, relationship_edges và care_quality nếu trống."""
        now = time.time()
        with self._get_conn() as conn:
            # Seed contacts nếu trống (trong unit test cô lập)
            cnt_count = conn.execute("SELECT COUNT(*) as cnt FROM contacts").fetchone()["cnt"]
            if cnt_count == 0:
                conn.execute("""
                    INSERT INTO contacts (id, full_name, phone, company, role, heat_score, ball_owner, went_silent_days, relationship_stage, internal_handler)
                    VALUES 
                    ('1', 'Anh Minh (Kafi)', '0901234567', 'Kafi Securities', 'Giám Đốc Phân Tích', 90.0, 'US', 1, 'hot', 'Anh Cơ La (Ryan)'),
                    ('2', 'Chị Mai Phương', '0912345678', 'VinaSupply Co', 'Trưởng Phòng Mua Hàng', 85.0, 'THEM', 0, 'hot', 'Mai Phương'),
                    ('3', 'Hoàng Bách', '0987654321', 'LogiTech Global', 'Managing Director', 88.0, 'US', 2, 'partner', 'Hoàng Bách'),
                    ('4', 'Thu Hà', '0933445566', 'Thời Trang Hà My', 'Chủ Thương Hiệu', 65.0, 'THEM', 4, 'warm', 'Anh Cơ La (Ryan)'),
                    ('5', 'Thảo Viettel', '0988776655', 'Viettel Telecom', 'Chuyên Viên Kỹ Thuật', 40.0, 'THEM', 8, 'cold', 'Trần Quốc Tuấn')
                """)

            # Seed opportunities nếu trống
            opp_count = conn.execute("SELECT COUNT(*) as cnt FROM opportunities").fetchone()["cnt"]
            if opp_count == 0:
                conn.execute("""
                    INSERT INTO opportunities (id, title, contact_name, contact_id, channel, estimated_value, stage, heat_score, confidence_score, assigned_owner, matched_offer, risk_of_inaction)
                    VALUES
                    ('OPP-01', 'Hợp đồng ERP/CRM Hub Đa Kênh', 'Hoàng Bách', '3', 'whatsapp', 180000000.0, 'NEGOTIATING', 90.0, 85.0, 'Hoàng Bách', 'Gói Bản Quyền ERP/CRM Hub Đa Kênh', 'Đối tác cần chốt trước ngày 30 để kịp quý tới.'),
                    ('OPP-02', 'Báo Cáo Phân Tích Tài Chính Kafi', 'Anh Minh (Kafi)', '1', 'zalo', 65000000.0, 'APPROACHING', 85.0, 80.0, 'Anh Cơ La (Ryan)', 'Dịch Vụ Phân Tích Tài Chính Tự Động', 'Khách đang đợi bản xem trước báo cáo tuần.'),
                    ('OPP-03', 'Cung cấp phần mềm quản trị xưởng may Hà My', 'Thu Hà', '4', 'whatsapp', 45000000.0, 'VERIFIED', 65.0, 70.0, 'Anh Cơ La (Ryan)', 'Phần Mềm Quản Trị Đơn Hàng & Xưởng', 'Khách chưa phản hồi sau khi nhận demo.'),
                    ('OPP-04', 'Tín hiệu hỏi giá License Doanh Nghiệp', 'Thảo Viettel', '5', 'zalo', 120000000.0, 'RAW_SIGNAL', 40.0, 60.0, 'Trần Quốc Tuấn', 'License Doanh Nghiệp Cấp Lớn', 'Khách đã im lặng 8 ngày, có nguy cơ đóng deal.')
                """)

            edge_count = conn.execute("SELECT COUNT(*) as cnt FROM relationship_edges").fetchone()["cnt"]
            if edge_count == 0:
                seed_edges = [
                    # HQ -> Groups
                    ("edge-hq-zalo-crm", "node-hq", "grp-zalo-crm", "channel_link", 1.0, 45, "Cung ứng & Triển khai phần mềm", "partner", "THEM", "LOW", now - 3600),
                    ("edge-hq-wa-logitech", "node-hq", "grp-wa-logitech", "channel_link", 1.0, 38, "Đối tác công nghệ AI điều phối", "partner", "US", "LOW", now - 7200),
                    ("edge-hq-wa-fashion", "node-hq", "grp-wa-fashion", "channel_link", 0.9, 22, "Gia công & ERP xưởng may", "warm", "THEM", "LOW", now - 18000),
                    ("edge-hq-zalo-telecom", "node-hq", "grp-zalo-telecom", "channel_link", 0.95, 29, "Đối tác hạ tầng AI Audio", "partner", "US", "MEDIUM", now - 14400),
                    # Groups -> Contacts
                    ("edge-crm-minh", "grp-zalo-crm", "cnt-1", "group_link", 0.85, 24, "Phân tích tài chính & Kafi Deal", "hot", "US", "LOW", now - 3600),
                    ("edge-crm-phuong", "grp-zalo-crm", "cnt-2", "group_link", 0.95, 31, "Báo giá phần mềm VinaSupply", "hot", "THEM", "LOW", now - 1200),
                    ("edge-wa-bach", "grp-wa-logitech", "cnt-3", "group_link", 0.9, 19, "Triển khai điều phối LogiTech", "hot", "US", "LOW", now - 7200),
                    ("edge-wa-ha", "grp-wa-fashion", "cnt-4", "group_link", 0.7, 12, "Tư vấn phần mềm Hà My", "warm", "THEM", "LOW", now - 28000),
                    ("edge-zalo-thao", "grp-zalo-telecom", "cnt-5", "group_link", 0.6, 8, "Hỏi đáp đường truyền Viettel", "cold", "THEM", "HIGH", now - 600000),
                    # Direct Peer Connections
                    ("edge-minh-phuong", "cnt-1", "cnt-2", "collaboration", 0.8, 14, "Chia sẻ tài liệu kiểm toán", "partner", "US", "LOW", now - 86400),
                    ("edge-bach-minh", "cnt-3", "cnt-1", "referral", 0.75, 9, "Giới thiệu hợp đồng tích hợp hệ thống", "warm", "THEM", "LOW", now - 172800)
                ]
                for eid, fn, tn, et, w, ic, lt, rs, bo, rf, ts in seed_edges:
                    conn.execute("""
                        INSERT OR REPLACE INTO relationship_edges
                        (id, from_node, to_node, edge_type, weight, interaction_count, last_topic, relationship_stage, ball_owner, risk_factor, last_interaction_ts, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (eid, fn, tn, et, w, ic, lt, rs, bo, rf, ts, now, now))

            care_count = conn.execute("SELECT COUNT(*) as cnt FROM care_quality_records").fetchone()["cnt"]
            if care_count == 0:
                conn.execute("""
                    INSERT INTO care_quality_records (id, person_id, full_name, role, avg_response_min, follow_up_rate, broken_promises_count, abandoned_clients_count, care_health_score, winning_notes, losing_notes, updated_at)
                    VALUES
                    ('CQ-01', 'EMP-101', 'Lê Thùy Linh', 'Senior B2B Account Manager', 4.2, 94.0, 0, 0, 96, 'Kịch bản thắng: Phản hồi dưới 5 phút, gửi demo trực quan và chốt điều khoản ngay khi khách đang nóng.', 'Hạn chế: Cần phân bổ bớt các việc hành chính cho bot để tập trung deal lớn.', '2026-09-22 12:00:00'),
                    ('CQ-02', 'EMP-102', 'Trần Quốc Tuấn', 'Junior Key Account Executive', 18.5, 62.0, 2, 2, 64, 'Điểm mạnh: Lễ phép, chịu khó lắng nghe khách hàng.', 'Kịch bản mất khách: Hứa hẹn gửi tài liệu nhưng quá 24h không phản hồi, để khách phải giục 2 lần.', '2026-09-22 12:00:00'),
                    ('CQ-03', 'EMP-103', 'Nguyễn Hoàng Nam', 'Chuyên Viên Kỹ Thuật & Triển Khai', 8.0, 88.0, 0, 0, 88, 'Kịch bản thắng: Cung cấp giải pháp kỹ thuật chính xác, hỗ trợ ngoài giờ tận tâm.', 'Hạn chế: Giọng văn đôi khi còn nhiều thuật ngữ kỹ thuật, cần mềm hóa ngôn từ khi nói với khách.', '2026-09-22 12:00:00')
                """)

    # =========================================================================
    # 1. RELATIONSHIP GRAPH & ANALYTICS (Spec E4, F2.3)
    # =========================================================================

    def get_relationship_graph(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Dựng cấu trúc Node & Edge đa chiều, hỗ trợ bộ lọc và phân nhóm trực quan.
        Bổ sung trọng số sống, giai đoạn quan hệ, ball_owner và liên kết deal.
        """
        filters = filters or {}
        with self._get_conn() as conn:
            contacts = [dict(r) for r in conn.execute("SELECT * FROM contacts").fetchall()]
            opportunities = [dict(r) for r in conn.execute("SELECT * FROM opportunities").fetchall()]
            custom_edges = [dict(r) for r in conn.execute("SELECT * FROM relationship_edges").fetchall()]

        nodes = []
        edges = []

        # 1. HQ Node
        nodes.append({
            "id": "node-hq",
            "label": "Anh Cơ La (Ryan) / HQ",
            "type": "hq",
            "category": "hq",
            "role": "Tổng Chỉ Huy Tối Cao",
            "heat": 100,
            "size": 34,
            "color": "#818cf8"
        })

        # 2. Canonical Channel Groups
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
                "size": 24,
                "color": "#0ea5e9" if g["channel"] == "zalo" else "#10b981"
            })
            edges.append({
                "id": f"edge-hq-{g['id']}",
                "from": "node-hq",
                "to": g["id"],
                "label": "Kênh Kết Nối",
                "category": "channel_link",
                "color": "rgba(99, 102, 241, 0.45)",
                "weight": 1.0,
                "ball_owner": "US",
                "relationship_stage": "partner"
            })

        # 3. Contact Nodes
        for c in contacts:
            cid = f"cnt-{c['id']}"
            heat = float(c.get("heat_score", 50.0))
            went_silent = int(c.get("went_silent_days", 0))
            stage = c.get("relationship_stage")
            
            if not stage:
                if heat >= 80:
                    stage = "hot"
                elif heat >= 50 and went_silent <= 3:
                    stage = "warm"
                else:
                    stage = "cold"

            color_map = {
                "hot": "#f43f5e",
                "warm": "#f59e0b",
                "cold": "#64748b",
                "partner": "#10b981",
                "risk": "#ef4444"
            }
            node_color = color_map.get(stage, "#f59e0b")

            nodes.append({
                "id": cid,
                "raw_id": c["id"],
                "label": c["full_name"],
                "company": c.get("company", ""),
                "role": c.get("role", ""),
                "type": "contact",
                "category": stage,
                "relationship_stage": stage,
                "heat": heat,
                "autonomy_level": c.get("autonomy_level", 1),
                "ball_owner": c.get("ball_owner", "THEM"),
                "went_silent_days": went_silent,
                "size": 18,
                "color": node_color
            })

            # Phân bổ kết nối nhóm mặc định
            assigned_grp = "node-hq"
            name = c.get("full_name", "")
            if "Mai Phương" in name or "Minh" in name:
                assigned_grp = "grp-zalo-crm"
            elif "Hoàng Bách" in name or "Tân Á" in name:
                assigned_grp = "grp-wa-logitech"
            elif "Thu Hà" in name:
                assigned_grp = "grp-wa-fashion"
            elif "Thảo" in name or "Viettel" in name:
                assigned_grp = "grp-zalo-telecom"

            edges.append({
                "id": f"edge-auto-{cid}",
                "from": assigned_grp,
                "to": cid,
                "label": "Thành viên" if assigned_grp != "node-hq" else "1-1",
                "category": "group_link" if assigned_grp != "node-hq" else "direct_link",
                "color": "rgba(14, 165, 233, 0.4)" if "zalo" in assigned_grp else "rgba(16, 185, 129, 0.4)",
                "weight": 0.85,
                "ball_owner": c.get("ball_owner", "THEM"),
                "relationship_stage": stage
            })

        # 4. Opportunity Nodes
        for opp in opportunities:
            oid = f"opp-{opp['id']}"
            est_val = float(opp.get("estimated_value", 0.0))
            raw_stage = opp.get("stage", "RAW_SIGNAL")
            canonical_stage = self.STAGE_MAP.get(raw_stage, self.STAGE_RAW_SIGNAL)
            full_title = opp.get("title", "Cơ hội")

            nodes.append({
                "id": oid,
                "raw_id": opp["id"],
                "label": full_title[:24] + ("..." if len(full_title) > 24 else ""),
                "full_title": full_title,
                "value": est_val,
                "stage": canonical_stage,
                "type": "opportunity",
                "category": "deal",
                "size": 15,
                "color": "#c084fc"
            })

            # Nối opportunity với contact tương ứng
            c_match_id = None
            for c in contacts:
                if opp.get("contact_id") == c["id"] or opp.get("contact_name") == c["full_name"]:
                    c_match_id = f"cnt-{c['id']}"
                    break

            target_from = c_match_id or "grp-zalo-crm"
            edges.append({
                "id": f"edge-opp-{oid}",
                "from": target_from,
                "to": oid,
                "label": f"{est_val/1e6:.0f}tr" if est_val > 0 else "Deal",
                "category": "deal_link",
                "color": "rgba(192, 132, 252, 0.55)",
                "weight": 1.2,
                "ball_owner": "US",
                "relationship_stage": "hot"
            })

        # 5. Bổ sung custom edges
        for ce in custom_edges:
            edges.append({
                "id": ce["id"],
                "from": ce["from_node"],
                "to": ce["to_node"],
                "label": ce.get("last_topic") or ce.get("edge_type", "Liên kết"),
                "category": ce.get("edge_type", "custom_link"),
                "color": "rgba(245, 158, 11, 0.6)" if ce.get("edge_type") == "referral" else "rgba(99, 102, 241, 0.45)",
                "weight": ce.get("weight", 1.0),
                "ball_owner": ce.get("ball_owner", "THEM"),
                "relationship_stage": ce.get("relationship_stage", "warm")
            })

        categories = [
            {"key": "hq", "label": "👑 HQ Trung Tâm", "color": "#818cf8"},
            {"key": "channel", "label": "💬 Kênh Zalo & WhatsApp", "color": "#0ea5e9"},
            {"key": "hot", "label": "🔥 Quan Hệ Nóng (>=80°)", "color": "#f43f5e"},
            {"key": "warm", "label": "🟡 Đối Tác Ấm Áp (50-79°)", "color": "#f59e0b"},
            {"key": "cold", "label": "⚪ Đang Lạnh / Went Silent", "color": "#64748b"},
            {"key": "partner", "label": "🤝 Đối Tác Chiến Lược", "color": "#10b981"},
            {"key": "risk", "label": "⚠️ Nguy Cơ Churn / Đứt Gãy", "color": "#ef4444"},
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

    def get_relationship_analytics(self) -> Dict[str, Any]:
        """
        Bóc tách 4 chiều thông tin quản trị cốt lõi (Spec LOCKED v2.2 Mục E4, F2.3):
        1. Top Connectors (Ai là cầu nối quan trọng)
        2. Cold Leads (Khách nào đang lạnh)
        3. Overloaded Agents (Nhân viên nào đang ôm quá nhiều bóng)
        4. Ball In Court Summary (Tỷ lệ phân bổ bóng phía ta vs đối tác)
        """
        with self._get_conn() as conn:
            contacts = [dict(r) for r in conn.execute("SELECT * FROM contacts").fetchall()]
            opps = [dict(r) for r in conn.execute("SELECT * FROM opportunities").fetchall()]
            edges = [dict(r) for r in conn.execute("SELECT * FROM relationship_edges").fetchall()]

        # 1. Top Connectors: Tính bậc liên kết
        degrees: Dict[str, int] = {}
        for e in edges:
            degrees[e["from_node"]] = degrees.get(e["from_node"], 0) + 1
            degrees[e["to_node"]] = degrees.get(e["to_node"], 0) + 1

        connectors = []
        for c in contacts:
            cid = f"cnt-{c['id']}"
            deg = degrees.get(cid, 1)
            deal_cnt = sum(1 for o in opps if o.get("contact_id") == c["id"] or o.get("contact_name") == c["full_name"])
            total_strength = deg + (deal_cnt * 2)
            connectors.append({
                "id": c["id"],
                "full_name": c["full_name"],
                "company": c.get("company", "—"),
                "role": c.get("role", "—"),
                "degree_connections": deg,
                "deal_count": deal_cnt,
                "strength_score": total_strength,
                "is_bridge": total_strength >= 3
            })
        connectors.sort(key=lambda x: x["strength_score"], reverse=True)
        top_connectors = connectors[:5]

        # 2. Cold Leads: Khách hàng im lặng > 5 ngày hoặc heat < 50
        cold_leads = []
        for c in contacts:
            went_silent = int(c.get("went_silent_days", 0))
            heat = float(c.get("heat_score", 50.0))
            stage = c.get("relationship_stage", "warm")
            if went_silent >= 4 or heat < 50.0 or stage == "cold":
                cold_leads.append({
                    "id": c["id"],
                    "full_name": c["full_name"],
                    "company": c.get("company", "—"),
                    "went_silent_days": went_silent,
                    "heat_score": heat,
                    "risk_level": "CAO" if went_silent >= 7 else "TRUNG BÌNH",
                    "action_recommended": f"Chủ động gửi tin nhắn hỏi thăm hoặc gửi báo cáo chuyên môn sau {went_silent} ngày im lặng"
                })
        cold_leads.sort(key=lambda x: x["went_silent_days"], reverse=True)

        # 3. Overloaded Agents & Ball-In-Court Analysis
        us_ball_count = sum(1 for c in contacts if c.get("ball_owner") == "US")
        them_ball_count = sum(1 for c in contacts if c.get("ball_owner") != "US")
        total_balls = max(1, us_ball_count + them_ball_count)

        agent_ball_map: Dict[str, int] = {
            "Anh Cơ La (Ryan)": 0,
            "Trợ Lý AI Bé Heo": 0,
            "Hoàng Bách": 0,
            "Mai Phương": 0
        }
        for c in contacts:
            if c.get("ball_owner") == "US":
                handler = c.get("internal_handler") or "Anh Cơ La (Ryan)"
                agent_ball_map[handler] = agent_ball_map.get(handler, 0) + 1

        overloaded_agents = []
        for ag, cnt in agent_ball_map.items():
            overloaded_agents.append({
                "agent_name": ag,
                "holding_balls": cnt,
                "is_overloaded": cnt >= 3,
                "status": "QUÁ TẢI" if cnt >= 3 else ("BẬN" if cnt >= 2 else "ỔN ĐỊNH")
            })
        overloaded_agents.sort(key=lambda x: x["holding_balls"], reverse=True)

        # 4. Phân bổ giai đoạn quan hệ
        stage_dist = {"hot": 0, "warm": 0, "cold": 0, "partner": 0, "risk": 0}
        for c in contacts:
            s = c.get("relationship_stage") or ("hot" if float(c.get("heat_score", 50)) >= 80 else "warm")
            stage_dist[s] = stage_dist.get(s, 0) + 1

        return {
            "ok": True,
            "top_connectors": top_connectors,
            "cold_leads": cold_leads,
            "overloaded_agents": overloaded_agents,
            "ball_in_court": {
                "us_count": us_ball_count,
                "them_count": them_ball_count,
                "us_pct": round((us_ball_count / total_balls) * 100, 1),
                "them_pct": round((them_ball_count / total_balls) * 100, 1)
            },
            "relationship_stages": stage_dist,
            "total_contacts": len(contacts),
            "network_health_score": round(100 - (len(cold_leads) * 5) - (us_ball_count * 2), 1)
        }

    def upsert_edge(self, from_node: str, to_node: str, edge_type: str = "collaboration",
                    weight: float = 1.0, last_topic: str = "", relationship_stage: str = "warm",
                    ball_owner: str = "THEM") -> Dict[str, Any]:
        """Tạo hoặc cập nhật liên kết giữa 2 đối tượng trong mạng lưới quan hệ."""
        edge_id = f"edge-{from_node}-{to_node}".replace(" ", "_")
        now = time.time()
        with self._get_conn() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO relationship_edges
                (id, from_node, to_node, edge_type, weight, interaction_count, last_topic, relationship_stage, ball_owner, last_interaction_ts, updated_at)
                VALUES (?, ?, ?, ?, ?, COALESCE((SELECT interaction_count + 1 FROM relationship_edges WHERE id = ?), 1), ?, ?, ?, ?, ?)
            """, (edge_id, from_node, to_node, edge_type, weight, edge_id, last_topic, relationship_stage, ball_owner, now, now))

        return {"ok": True, "edge_id": edge_id, "message": "Đã cập nhật liên kết quan hệ"}

    def delete_edge(self, edge_id: str) -> bool:
        """Xoá một liên kết quan hệ khỏi mạng lưới."""
        with self._get_conn() as conn:
            cur = conn.execute("DELETE FROM relationship_edges WHERE id = ?", (edge_id,))
            return cur.rowcount > 0

    # =========================================================================
    # 2. OPPORTUNITY BOARD KANBAN 8 CỘT (Spec E3, F2.5)
    # =========================================================================

    def get_opportunity_board(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Lấy toàn bộ cơ hội thương mại theo 8 cột Kanban chuẩn của Spec LOCKED v2.2.
        Bổ sung đầy đủ chỉ số: Hotness, Confidence, Matched Offer, Risk of Inaction.
        """
        filters = filters or {}
        with self._get_conn() as conn:
            opps = [dict(r) for r in conn.execute("SELECT * FROM opportunities ORDER BY updated_at DESC").fetchall()]
            history = [dict(r) for r in conn.execute("SELECT * FROM opportunity_stage_history ORDER BY created_at DESC LIMIT 50").fetchall()]

        hist_by_opp: Dict[str, List[dict]] = {}
        for h in history:
            hist_by_opp.setdefault(h["opp_id"], []).append(h)

        columns: Dict[str, List[dict]] = {st["key"]: [] for st in self.CANONICAL_STAGES}

        total_pipeline_val = 0.0
        won_val = 0.0
        lost_val = 0.0

        for o in opps:
            raw_stage = o.get("stage", "RAW_SIGNAL")
            canonical_stage = self.STAGE_MAP.get(raw_stage, self.STAGE_RAW_SIGNAL)
            val = float(o.get("estimated_value", 0.0))

            if canonical_stage == self.STAGE_WON:
                won_val += val
            elif canonical_stage == self.STAGE_LOST:
                lost_val += val
            else:
                total_pipeline_val += val

            # Risk text
            risk_text = o.get("risk_of_inaction")
            if not risk_text:
                if val >= 100000000:
                    risk_text = "Hợp đồng giá trị cao. Đối thủ có thể can thiệp nếu không chốt phương án trong tuần."
                elif canonical_stage in [self.STAGE_APPROACHING, self.STAGE_NEGOTIATING]:
                    risk_text = "Khách đang chờ báo giá chi tiết, trễ sẽ giảm độ nóng giao dịch."
                else:
                    risk_text = "Cần tiếp tục theo dõi tiến độ."

            matched_offer = o.get("matched_offer")
            if not matched_offer:
                title_lower = (o.get("title") or "").lower()
                if "erp" in title_lower or "crm" in title_lower:
                    matched_offer = "Gói Bản Quyền ERP/CRM Hub Đa Kênh"
                elif "ai" in title_lower or "điều phối" in title_lower:
                    matched_offer = "Giải Pháp AI Điều Phối Giao Tiếp Doanh Nghiệp"
                elif "tài chính" in title_lower or "báo cáo" in title_lower:
                    matched_offer = "Dịch Vụ Phân Tích Tài Chính Tự Động"
                else:
                    matched_offer = "Dịch Vụ Tích Hợp Gen-Harness"

            enriched_card = {
                "id": o["id"],
                "title": o.get("title", "Cơ hội mới"),
                "contact_name": o.get("contact_name", "Đối tác"),
                "contact_id": o.get("contact_id", ""),
                "channel": o.get("channel", "zalo"),
                "group_name": o.get("group_name", "1-1"),
                "need_summary": o.get("need_summary", ""),
                "estimated_value": val,
                "stage": canonical_stage,
                "raw_stage": raw_stage,
                "heat_score": float(o.get("heat_score", 60.0)),
                "confidence_score": float(o.get("confidence_score", 75.0)),
                "assigned_owner": o.get("assigned_owner") or o.get("owner") or "Anh Cơ La (Ryan)",
                "matched_offer": matched_offer,
                "risk_of_inaction": risk_text,
                "win_probability": o.get("win_probability", 50),
                "created_at": o.get("created_at"),
                "updated_at": o.get("updated_at"),
                "stage_history": hist_by_opp.get(o["id"], [])
            }

            if canonical_stage in columns:
                columns[canonical_stage].append(enriched_card)
            else:
                columns[self.STAGE_RAW_SIGNAL].append(enriched_card)

        total_deals = len(opps)
        won_deals = len(columns[self.STAGE_WON])
        win_rate = round((won_deals / total_deals * 100), 1) if total_deals > 0 else 0.0

        return {
            "ok": True,
            "stages": self.CANONICAL_STAGES,
            "columns": columns,
            "metrics": {
                "total_deals": total_deals,
                "active_pipeline_value": total_pipeline_val,
                "won_value": won_val,
                "lost_value": lost_val,
                "win_rate_pct": win_rate,
                "avg_deal_size": round(total_pipeline_val / max(1, total_deals - won_deals - len(columns[self.STAGE_LOST])), 0)
            }
        }

    def transition_opportunity_stage(self, opp_id: str, new_stage: str, reason: str = "",
                                      changed_by: str = "Anh Cơ La (Ryan)") -> Dict[str, Any]:
        """
        Chuyển đổi stage của card cơ hội kèm ghi nhận lý do và cập nhật lịch sử SSOT.
        Nếu chốt WON: tăng nhiệt độ contact lên 95° và ghi nhận thành tích.
        """
        canonical_new_stage = self.STAGE_MAP.get(new_stage, new_stage)
        now = time.time()
        
        with self._get_conn() as conn:
            opp = conn.execute("SELECT * FROM opportunities WHERE id = ?", (opp_id,)).fetchone()
            if not opp:
                return {"ok": False, "error": f"Không tìm thấy cơ hội {opp_id}"}

            old_stage = opp["stage"]
            canonical_old_stage = self.STAGE_MAP.get(old_stage, self.STAGE_RAW_SIGNAL)

            # Cập nhật stage trong bảng opportunities
            conn.execute("""
                UPDATE opportunities
                SET stage = ?, updated_at = ?
                WHERE id = ?
            """, (canonical_new_stage, now, opp_id))

            # Ghi nhật ký vào bảng opportunity_stage_history
            hist_id = f"hist-{opp_id}-{int(now)}"
            conn.execute("""
                INSERT INTO opportunity_stage_history
                (id, opp_id, from_stage, to_stage, reason, changed_by, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (hist_id, opp_id, canonical_old_stage, canonical_new_stage, reason or "Cập nhật tiến độ trên Kanban Console", changed_by, now))

            # Xử lý hiệu ứng phụ khi WON hoặc LOST
            contact_id = opp["contact_id"]
            if canonical_new_stage == self.STAGE_WON and contact_id:
                conn.execute("""
                    UPDATE contacts
                    SET heat_score = 95.0, relationship_stage = 'hot', ball_owner = 'THEM'
                    WHERE id = ?
                """, (contact_id,))
            elif canonical_new_stage == self.STAGE_LOST and contact_id:
                conn.execute("""
                    UPDATE contacts
                    SET relationship_stage = 'cold'
                    WHERE id = ?
                """, (contact_id,))

        return {
            "ok": True,
            "opp_id": opp_id,
            "from_stage": canonical_old_stage,
            "to_stage": canonical_new_stage,
            "message": f"Đã chuyển giai đoạn {opp_id} sang {canonical_new_stage}"
        }

    # =========================================================================
    # 3. CARE QUALITY INTELLIGENCE (Spec E8, F2.7)
    # =========================================================================

    def get_care_quality_analytics(self) -> Dict[str, Any]:
        """
        Đo lường và phân tích chất lượng chăm sóc của nhân sự và tổ chức.
        Tuân thủ chặt chẽ Mục E8 & F2.7 Spec LOCKED v2.2.
        """
        with self._get_conn() as conn:
            records = [dict(r) for r in conn.execute("SELECT * FROM care_quality_records").fetchall()]
            contacts = [dict(r) for r in conn.execute("SELECT * FROM contacts").fetchall()]
            broken_promises = [dict(r) for r in conn.execute("SELECT * FROM broken_promises WHERE status = 'UNRESOLVED'").fetchall()] if self._table_exists(conn, "broken_promises") else []

        agent_reports = []
        for r in records:
            agent_reports.append({
                "id": r["id"],
                "person_id": r.get("person_id", ""),
                "agent_name": r["full_name"],
                "role": r["role"],
                "median_response_min": float(r.get("avg_response_min", 5.0)),
                "follow_up_rate_pct": float(r.get("follow_up_rate", 85.0)),
                "broken_promises_count": int(r.get("broken_promises_count", 0)),
                "abandoned_contacts_count": int(r.get("abandoned_clients_count", 0)),
                "care_score": float(r.get("care_health_score", 80)),
                "winning_notes": r.get("winning_notes", ""),
                "losing_notes": r.get("losing_notes", ""),
                "updated_at": r.get("updated_at", "")
            })

        # Danh sách khách hàng bị bỏ rơi
        abandoned_list = []
        for c in contacts:
            went_silent = int(c.get("went_silent_days", 0))
            if went_silent >= 5:
                abandoned_list.append({
                    "id": c["id"],
                    "full_name": c["full_name"],
                    "company": c.get("company", "—"),
                    "went_silent_days": went_silent,
                    "handler": c.get("internal_handler") or "Chưa phân bổ",
                    "reason": f"Không có liên hệ sau {went_silent} ngày"
                })

        avg_score = round(sum(m["care_score"] for m in agent_reports) / max(1, len(agent_reports)), 1)
        avg_response = round(sum(m["median_response_min"] for m in agent_reports) / max(1, len(agent_reports)), 1)
        avg_fu_rate = round(sum(m["follow_up_rate_pct"] for m in agent_reports) / max(1, len(agent_reports)), 1)

        return {
            "ok": True,
            "summary": {
                "overall_care_score": avg_score,
                "median_response_min": avg_response,
                "avg_follow_up_rate_pct": avg_fu_rate,
                "unresolved_broken_promises": len(broken_promises),
                "total_abandoned_contacts": len(abandoned_list)
            },
            "agents": agent_reports,
            "abandoned_contacts": abandoned_list,
            "time_slot_averages": {
                "morning": {"slot": "Sáng (08:00 - 12:00)", "median_min": 3.8, "rating": "Rất Nhanh"},
                "noon": {"slot": "Trưa (12:00 - 13:30)", "median_min": 11.5, "rating": "Chậm Do Nghỉ Trưa"},
                "afternoon": {"slot": "Chiều (13:30 - 18:00)", "median_min": 4.5, "rating": "Nhanh"},
                "evening": {"slot": "Tối (18:00 - 22:00)", "median_min": 8.2, "rating": "Trung Bình"}
            }
        }

    def _table_exists(self, conn: sqlite3.Connection, table_name: str) -> bool:
        res = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,)).fetchone()
        return bool(res)


# Global singleton helper
_rel_engine: Optional[RelationshipIntelligenceEngine] = None

def get_relationship_engine(data_dir: str = None) -> RelationshipIntelligenceEngine:
    global _rel_engine
    if _rel_engine is None or data_dir:
        _rel_engine = RelationshipIntelligenceEngine(data_dir=data_dir)
    return _rel_engine
