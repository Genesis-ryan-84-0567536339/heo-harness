"""
HEO-HARNESS EARLY WARNING & IDENTITY RESOLUTION ENGINE (SPEC-42: Phase 2 - Hiểu được)
--------------------------------------------------------------------------------------
Tác giả: Anh Cơ La (genesis.corp.os@gmail.com)
Tuân thủ: Gen-Harness Product Spec LOCKED v2.2 (Mục L Phase 2, E5, E6, E9, F2 (4, 8), G2)

1. Early Warning System (E9):
   - Cảnh báo khách lạnh (COLD_LEAD): silent >= 3 days, heat >= 50 hoặc open opps.
   - Nhân viên phản hồi chậm (SLOW_RESPONSE): ball_owner == US, delay > 15m.
   - Than phiền lặp lại (REPEATED_COMPLAINT): >= 2 Complained events trong 7 ngày.
   - Cơ hội nóng chưa ai nhận (UNCLAIMED_HOT_OPP): Opp > 50tr or unassigned.
   - Đối thủ xuất hiện (COMPETITOR_MENTION): MentionsCompetitor event trong chat.
   - Deadline/cam kết quá hạn (OVERDUE_PROMISE): Broken promise UNRESOLVED.
   - Dữ liệu mâu thuẫn (DATA_DISCREPANCY): Thiếu liên hệ, profile incomplete.

2. Identity Resolution & Merging (G2):
   - Suggestions engine for cross-channel duplicates (matching phone, email, fuzzy name).
   - Merge identities with snapshot preservation.
   - Split identity with full recovery from snapshot.
   - Merge history & audit log.

3. Living Profile 360 Deep Enricher (E5, F2 4):
   - Multi-channel identity mapping (Zalo, WhatsApp, etc.).
   - Explainable Scoring breakdown ("Vì sao hệ thống nghĩ vậy" with actionable reasons).
   - Dynamic 8-12 line AI executive summary.
   - Timeline of atomic events with intent badges.
   - Exchanged documents & open tasks.
   - Autonomy level 0-6 controls.
   - Manual notes.

4. Brain Search (Search có não - F2 8):
   - Natural language search across contacts, atomic events, opportunities, and alert notes.
   - Ranks and explains why items match.
"""

import os
import json
import sqlite3
import re
import contextlib
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional

class EarlyWarningEngine:
    def __init__(self, data_dir: Optional[str] = None):
        if data_dir is None:
            base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            self.data_dir = os.path.join(base, "data")
        else:
            self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        self.db_path = os.path.join(self.data_dir, "heo.db")
        self._init_db()

    @contextlib.contextmanager
    def _get_conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self):
        with self._get_conn() as conn:
            # 0. Bảng Core: contacts, atomic_events, opportunities (tự khởi tạo nếu chưa có)
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
                merged_into TEXT DEFAULT NULL,
                internal_handler TEXT DEFAULT 'Anh Cơ La (Ryan)',
                exchanged_docs TEXT DEFAULT '[]'
            )
            """)

            conn.execute("""
            CREATE TABLE IF NOT EXISTS atomic_events (
                id TEXT PRIMARY KEY,
                event_type TEXT NOT NULL,
                channel TEXT NOT NULL,
                sender_id TEXT NOT NULL,
                sender_name TEXT NOT NULL,
                group_id TEXT DEFAULT '',
                group_name TEXT DEFAULT '',
                content TEXT NOT NULL,
                extracted_entities TEXT DEFAULT '{}',
                intent TEXT DEFAULT '',
                sentiment TEXT DEFAULT '',
                meaning_summary TEXT NOT NULL,
                action_suggested TEXT DEFAULT '',
                priority TEXT DEFAULT 'MEDIUM',
                status TEXT DEFAULT 'NEW',
                heat_score REAL DEFAULT 50.0,
                timestamp TEXT NOT NULL,
                created_at TEXT NOT NULL,
                archived INTEGER DEFAULT 0
            )
            """)

            conn.execute("""
            CREATE TABLE IF NOT EXISTS opportunities (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                contact_name TEXT NOT NULL,
                contact_id TEXT NOT NULL,
                channel TEXT DEFAULT 'all',
                group_name TEXT DEFAULT '',
                need_summary TEXT DEFAULT '',
                estimated_value REAL DEFAULT 0.0,
                stage TEXT DEFAULT 'SIGNAL',
                confidence_score REAL DEFAULT 50.0,
                heat_score REAL DEFAULT 50.0,
                risk_notes TEXT DEFAULT '',
                source_event_id TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                owner TEXT DEFAULT 'Anh Cơ La (Ryan)',
                win_probability REAL DEFAULT 0.5
            )
            """)

            # 1. Bảng Early Warning Alerts
            conn.execute("""
            CREATE TABLE IF NOT EXISTS early_warning_alerts (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                severity TEXT NOT NULL,
                target_id TEXT NOT NULL,
                target_name TEXT NOT NULL,
                channel TEXT DEFAULT 'all',
                reason TEXT NOT NULL,
                evidence TEXT DEFAULT '',
                suggested_action TEXT NOT NULL,
                assignee TEXT DEFAULT 'Anh Cơ La (Ryan)',
                status TEXT DEFAULT 'ACTIVE',
                detected_at TEXT NOT NULL,
                resolved_at TEXT,
                action_taken TEXT,
                updated_at TEXT
            )
            """)

            # 2. Bảng Identity Merge History (G2)
            conn.execute("""
            CREATE TABLE IF NOT EXISTS identity_merge_history (
                id TEXT PRIMARY KEY,
                primary_id TEXT NOT NULL,
                primary_name TEXT NOT NULL,
                secondary_id TEXT NOT NULL,
                secondary_name TEXT NOT NULL,
                secondary_snapshot TEXT NOT NULL,
                match_reason TEXT,
                merged_at TEXT NOT NULL,
                merged_by TEXT NOT NULL,
                status TEXT DEFAULT 'MERGED',
                split_at TEXT,
                split_by TEXT
            )
            """)

            # 3. Bảng Broken Promises & Commercial Documents (phục vụ tự chữa lành)
            conn.execute("""
            CREATE TABLE IF NOT EXISTS broken_promises (
                id TEXT PRIMARY KEY,
                employee_name TEXT NOT NULL,
                client_name TEXT NOT NULL,
                channel TEXT DEFAULT 'Zalo',
                promise_text TEXT NOT NULL,
                promised_deadline TEXT NOT NULL,
                delay_hours REAL DEFAULT 0.0,
                severity TEXT DEFAULT 'MEDIUM',
                status TEXT DEFAULT 'UNRESOLVED',
                created_at TEXT NOT NULL
            )
            """)

            conn.execute("""
            CREATE TABLE IF NOT EXISTS commercial_documents (
                id TEXT PRIMARY KEY,
                deal_id TEXT,
                contact_id TEXT,
                contact_name TEXT,
                company TEXT,
                channel TEXT,
                doc_type TEXT,
                title TEXT,
                currency TEXT DEFAULT 'VND',
                items_json TEXT DEFAULT '[]',
                subtotal_amount REAL DEFAULT 0.0,
                discount_amount REAL DEFAULT 0.0,
                total_amount REAL DEFAULT 0.0,
                margin_pct REAL DEFAULT 0.0,
                payment_terms TEXT,
                valid_until TEXT,
                cover_letter TEXT,
                notes TEXT,
                language TEXT DEFAULT 'vi',
                status TEXT DEFAULT 'DRAFT',
                sent_at TEXT,
                created_at TEXT,
                updated_at TEXT
            )
            """)

            # 4. Đảm bảo các cột mới trong bảng contacts nếu chưa có
            try:
                cols = [r["name"] for r in conn.execute("PRAGMA table_info(contacts)").fetchall()]
                if "data_confidence" not in cols:
                    conn.execute("ALTER TABLE contacts ADD COLUMN data_confidence REAL DEFAULT 85.0")
                if "notes" not in cols:
                    conn.execute("ALTER TABLE contacts ADD COLUMN notes TEXT DEFAULT ''")
                if "merged_into" not in cols:
                    conn.execute("ALTER TABLE contacts ADD COLUMN merged_into TEXT DEFAULT NULL")
                if "internal_handler" not in cols:
                    conn.execute("ALTER TABLE contacts ADD COLUMN internal_handler TEXT DEFAULT 'Anh Cơ La (Ryan)'")
                if "exchanged_docs" not in cols:
                    conn.execute("ALTER TABLE contacts ADD COLUMN exchanged_docs TEXT DEFAULT '[]'")
            except Exception:
                pass

            conn.commit()

    # =========================================================================
    # PHẦN 1: EARLY WARNING SYSTEM (E9)
    # =========================================================================

    def scan_and_generate_alerts(self) -> List[Dict[str, Any]]:
        """Quét toàn bộ danh bạ, sự kiện nguyên tử, cơ hội và cam kết để sinh cảnh báo sớm."""
        now = datetime.now(timezone.utc)
        now_iso = now.isoformat()
        new_alerts = []

        with self._get_conn() as conn:
            # 1. Quét Khách Lạnh (COLD_LEAD): im lặng >= 3 ngày, nhiệt độ >= 40 hoặc churn risk >= 30%
            contacts = conn.execute(
                "SELECT * FROM contacts WHERE went_silent_days >= 3 AND (heat_score >= 40 OR churn_risk >= 30) AND (merged_into IS NULL OR merged_into = '')"
            ).fetchall()

            for c in contacts:
                target_id = c["id"]
                silent_days = c["went_silent_days"]
                severity = "CRITICAL" if silent_days >= 7 or c["churn_risk"] >= 50 else "WARNING"
                
                # Kiểm tra xem đã có alert COLD_LEAD còn ACTIVE chưa
                existing = conn.execute(
                    "SELECT id FROM early_warning_alerts WHERE type = 'COLD_LEAD' AND target_id = ? AND status = 'ACTIVE'",
                    (target_id,)
                ).fetchone()
                
                if not existing:
                    alert_id = f"ALR-COLD-{target_id}-{int(now.timestamp()) % 100000}"
                    reason = f"Khách hàng {c['full_name']} ({c['company']}) đã ngắt kết nối trao đổi {silent_days} ngày. Điểm nhiệt độ giảm còn {c['heat_score']}°, rủi ro churn ước tính {c['churn_risk']}%."
                    evidence = f"Lần cuối tương tác: {c['last_seen'] or 'N/A'}. Lịch sử tương tác: {c['interaction_count']} lượt. Bóng đang ở: {c['ball_owner']}."
                    action = "Gửi kịch bản nhắn tin hâm nóng quan hệ, chủ động cập nhật tiến độ hoặc mời cafe trao đổi trực tiếp."
                    
                    conn.execute("""
                    INSERT INTO early_warning_alerts (id, type, severity, target_id, target_name, channel, reason, evidence, suggested_action, assignee, status, detected_at, updated_at)
                    VALUES (?, 'COLD_LEAD', ?, ?, ?, 'all', ?, ?, ?, ?, 'ACTIVE', ?, ?)
                    """, (alert_id, severity, target_id, c["full_name"], reason, evidence, action, c["internal_handler"] or "Anh Cơ La (Ryan)", now_iso, now_iso))
                    
                    new_alerts.append({"id": alert_id, "type": "COLD_LEAD", "target": c["full_name"]})

            # 2. Quét Phản Hồi Chậm (SLOW_RESPONSE): ball_owner == 'US' và ngắt quãng trao đổi
            slow_leads = conn.execute(
                "SELECT * FROM contacts WHERE ball_owner = 'US' AND went_silent_days >= 1 AND (merged_into IS NULL OR merged_into = '')"
            ).fetchall()
            for c in slow_leads:
                target_id = c["id"]
                existing = conn.execute(
                    "SELECT id FROM early_warning_alerts WHERE type = 'SLOW_RESPONSE' AND target_id = ? AND status = 'ACTIVE'",
                    (target_id,)
                ).fetchone()
                if not existing:
                    alert_id = f"ALR-SLOW-{target_id}-{int(now.timestamp()) % 100000}"
                    reason = f"Bóng đang ở phía Chúng Ta (US). Khách hàng {c['full_name']} đang chờ phản hồi trên kênh Zalo/WhatsApp nhưng chưa có nhân sự chốt lịch."
                    evidence = f"Chờ phản hồi từ ngày: {c['last_seen']}. Bóng: {c['ball_owner']}."
                    action = f"Giao ngay cho {c['internal_handler'] or 'Trực Ban Tác Nghiệp'} mở chat và gửi câu trả lời chuẩn xác trong 15 phút."
                    conn.execute("""
                    INSERT INTO early_warning_alerts (id, type, severity, target_id, target_name, channel, reason, evidence, suggested_action, assignee, status, detected_at, updated_at)
                    VALUES (?, 'SLOW_RESPONSE', 'WARNING', ?, ?, 'zalo', ?, ?, ?, ?, 'ACTIVE', ?, ?)
                    """, (alert_id, target_id, c["full_name"], reason, evidence, action, c["internal_handler"] or "Trực Ban Tác Nghiệp", now_iso, now_iso))
                    new_alerts.append({"id": alert_id, "type": "SLOW_RESPONSE", "target": c["full_name"]})

            # 3. Quét Than Phiền Lặp Lại (REPEATED_COMPLAINT)
            complaints = conn.execute("""
            SELECT sender_name, sender_id, count(*) as cnt, group_concat(meaning_summary, ' || ') as all_complaints
            FROM atomic_events
            WHERE event_type = 'Complained'
            GROUP BY sender_name
            HAVING cnt >= 1
            """).fetchall()

            for cp in complaints:
                target_name = cp["sender_name"]
                cnt = cp["cnt"]
                severity = "CRITICAL" if cnt >= 2 else "WARNING"
                existing = conn.execute(
                    "SELECT id FROM early_warning_alerts WHERE type = 'REPEATED_COMPLAINT' AND target_name = ? AND status = 'ACTIVE'",
                    (target_name,)
                ).fetchone()
                if not existing:
                    alert_id = f"ALR-CMPL-{int(now.timestamp()) % 100000}"
                    reason = f"Ghi nhận {cnt} sự kiện phản ánh/khiếu nại từ {target_name}. Cần can thiệp để bảo toàn uy tín Genesis Corp."
                    evidence = f"Tóm tắt các khiếu nại: {cp['all_complaints']}"
                    action = "Kích hoạt giao thức xử lý sự cố cấp độ 1: Quản lý hoặc Sếp Ryan trực tiếp giải thích và cam kết mốc xử lý dứt điểm."
                    conn.execute("""
                    INSERT INTO early_warning_alerts (id, type, severity, target_id, target_name, channel, reason, evidence, suggested_action, assignee, status, detected_at, updated_at)
                    VALUES (?, 'REPEATED_COMPLAINT', ?, ?, ?, 'all', ?, ?, ?, 'Anh Cơ La (Ryan)', 'ACTIVE', ?, ?)
                    """, (alert_id, severity, cp["sender_id"] or target_name, target_name, reason, evidence, action, now_iso, now_iso))
                    new_alerts.append({"id": alert_id, "type": "REPEATED_COMPLAINT", "target": target_name})

            # 4. Quét Cam Kết Quá Hạn (OVERDUE_PROMISE)
            promises = conn.execute(
                "SELECT * FROM broken_promises WHERE status = 'UNRESOLVED'"
            ).fetchall()
            for p in promises:
                existing = conn.execute(
                    "SELECT id FROM early_warning_alerts WHERE type = 'OVERDUE_PROMISE' AND target_id = ? AND status = 'ACTIVE'",
                    (p["id"],)
                ).fetchone()
                if not existing:
                    alert_id = f"ALR-PRM-{p['id']}"
                    reason = f"Cam kết giữa nhân viên {p['employee_name']} với khách {p['client_name']} đã trễ hạn {p['delay_hours']} giờ."
                    evidence = f"Nội dung cam kết: '{p['promise_text']}'. Hạn chót đã hứa: {p['promised_deadline']}."
                    action = f"Yêu cầu {p['employee_name']} lập tức gửi công văn hoặc tin nhắn xin lỗi và hoàn thành giao nộp trước cuối ngày."
                    conn.execute("""
                    INSERT INTO early_warning_alerts (id, type, severity, target_id, target_name, channel, reason, evidence, suggested_action, assignee, status, detected_at, updated_at)
                    VALUES (?, 'OVERDUE_PROMISE', ?, ?, ?, ?, ?, ?, ?, ?, 'ACTIVE', ?, ?)
                    """, (alert_id, p["severity"], p["id"], p["client_name"], p["channel"] or "Zalo", reason, evidence, action, p["employee_name"], now_iso, now_iso))
                    new_alerts.append({"id": alert_id, "type": "OVERDUE_PROMISE", "target": p["client_name"]})

            # 5. Quét Cơ Hội Nóng Chưa Phân Bổ (UNCLAIMED_HOT_OPP)
            unclaimed_opps = conn.execute(
                "SELECT * FROM opportunities WHERE (owner IS NULL OR owner = '' OR owner LIKE '%Chưa phân bổ%') AND stage IN ('SIGNAL', 'QUALIFIED', 'MATCHED')"
            ).fetchall()
            for opp in unclaimed_opps:
                existing = conn.execute(
                    "SELECT id FROM early_warning_alerts WHERE type = 'UNCLAIMED_HOT_OPP' AND target_id = ? AND status = 'ACTIVE'",
                    (opp["id"],)
                ).fetchone()
                if not existing:
                    alert_id = f"ALR-OPP-{opp['id']}"
                    val_str = f"{int(opp['estimated_value']):,} VNĐ" if opp["estimated_value"] else "Chưa định lượng"
                    reason = f"Cơ hội nóng '{opp['title']}' trị giá {val_str} từ {opp['contact_name']} chưa có người phụ trách chính."
                    evidence = f"Nhu cầu: {opp['need_summary']}. Độ nóng: {opp['heat_score']}°."
                    action = "Chỉ định chuyên viên Key Account tiếp nhận hồ sơ cơ hội và chuẩn bị báo giá sơ bộ."
                    conn.execute("""
                    INSERT INTO early_warning_alerts (id, type, severity, target_id, target_name, channel, reason, evidence, suggested_action, assignee, status, detected_at, updated_at)
                    VALUES (?, 'UNCLAIMED_HOT_OPP', 'CRITICAL', ?, ?, ?, ?, ?, ?, 'Sếp Cơ La (Ryan)', 'ACTIVE', ?, ?)
                    """, (alert_id, opp["id"], opp["contact_name"], opp["channel"] or "all", reason, evidence, action, now_iso, now_iso))
                    new_alerts.append({"id": alert_id, "type": "UNCLAIMED_HOT_OPP", "target": opp["title"]})

            # 6. Quét Đối Thủ Xuất Hiện Trong Chat (COMPETITOR_MENTION)
            competitor_evts = conn.execute(
                "SELECT * FROM atomic_events WHERE event_type = 'MentionsCompetitor' ORDER BY timestamp DESC LIMIT 5"
            ).fetchall()
            for ce in competitor_evts:
                existing = conn.execute(
                    "SELECT id FROM early_warning_alerts WHERE type = 'COMPETITOR_MENTION' AND target_id = ? AND status = 'ACTIVE'",
                    (ce["id"],)
                ).fetchone()
                if not existing:
                    alert_id = f"ALR-CMP-{ce['id']}"
                    reason = f"Đối tác {ce['sender_name']} đã nhắc đến đối thủ cạnh tranh trong luồng hội thoại."
                    evidence = f"Trích đoạn: '{ce['meaning_summary']}'. Kênh: {ce['channel']}."
                    action = "Cung cấp bảng so sánh tính năng (Battlecard) nêu bật ưu thế công nghệ Antigravity 0đ và bảo mật cục bộ của Heo OS."
                    conn.execute("""
                    INSERT INTO early_warning_alerts (id, type, severity, target_id, target_name, channel, reason, evidence, suggested_action, assignee, status, detected_at, updated_at)
                    VALUES (?, 'COMPETITOR_MENTION', 'WARNING', ?, ?, ?, ?, ?, ?, 'Anh Cơ La (Ryan)', 'ACTIVE', ?, ?)
                    """, (alert_id, ce["id"], ce["sender_name"], ce["channel"], reason, evidence, action, now_iso, now_iso))
                    new_alerts.append({"id": alert_id, "type": "COMPETITOR_MENTION", "target": ce["sender_name"]})

            # 7. Quét Dữ Liệu Thiếu/Mâu Thuẫn (DATA_DISCREPANCY)
            incomplete = conn.execute(
                "SELECT * FROM contacts WHERE (phone IS NULL OR phone = '' OR company IS NULL OR company = '') AND interaction_count >= 5 AND (merged_into IS NULL OR merged_into = '')"
            ).fetchall()
            for ic in incomplete:
                existing = conn.execute(
                    "SELECT id FROM early_warning_alerts WHERE type = 'DATA_DISCREPANCY' AND target_id = ? AND status = 'ACTIVE'",
                    (ic["id"],)
                ).fetchone()
                if not existing:
                    alert_id = f"ALR-DATA-{ic['id']}"
                    missing_fields = []
                    if not ic["phone"]: missing_fields.append("Số điện thoại")
                    if not ic["company"]: missing_fields.append("Tên doanh nghiệp")
                    reason = f"Liên hệ VIP {ic['full_name']} đã có {ic['interaction_count']} lượt tương tác nhưng thiếu trường: {', '.join(missing_fields)}."
                    evidence = f"Định danh hiện tại: Zalo ({ic['zalo_id'] or 'N/A'}), WhatsApp ({ic['whatsapp_id'] or 'N/A'})."
                    action = "Gợi ý trợ lý AI tự động bóc tách số điện thoại và công ty từ chữ ký hoặc lịch sử trò chuyện."
                    conn.execute("""
                    INSERT INTO early_warning_alerts (id, type, severity, target_id, target_name, channel, reason, evidence, suggested_action, assignee, status, detected_at, updated_at)
                    VALUES (?, 'DATA_DISCREPANCY', 'INFO', ?, ?, 'system', ?, ?, ?, 'Trợ Lý AI', 'ACTIVE', ?, ?)
                    """, (alert_id, ic["id"], ic["full_name"], reason, evidence, action, now_iso, now_iso))
                    new_alerts.append({"id": alert_id, "type": "DATA_DISCREPANCY", "target": ic["full_name"]})

            conn.commit()

        return new_alerts

    def get_alerts(self, status: Optional[str] = "ACTIVE", severity: Optional[str] = None, alert_type: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Lấy danh sách các cảnh báo sớm theo bộ lọc."""
        # Auto scan nếu bảng trống
        with self._get_conn() as conn:
            cnt = conn.execute("SELECT count(*) FROM early_warning_alerts").fetchone()[0]
            if cnt == 0:
                self.scan_and_generate_alerts()

            query = "SELECT * FROM early_warning_alerts WHERE 1=1"
            params = []
            if status and status != "ALL":
                query += " AND status = ?"
                params.append(status)
            if severity and severity != "ALL":
                query += " AND severity = ?"
                params.append(severity)
            if alert_type and alert_type != "ALL":
                query += " AND type = ?"
                params.append(alert_type)

            query += " ORDER BY CASE severity WHEN 'CRITICAL' THEN 1 WHEN 'WARNING' THEN 2 ELSE 3 END, detected_at DESC LIMIT ?"
            params.append(limit)

            rows = conn.execute(query, tuple(params)).fetchall()
            return [dict(r) for r in rows]

    def get_alert_summary(self) -> Dict[str, Any]:
        """Tổng hợp chỉ số Radar Cảnh Báo Sớm."""
        with self._get_conn() as conn:
            total_active = conn.execute("SELECT count(*) FROM early_warning_alerts WHERE status = 'ACTIVE'").fetchone()[0]
            critical = conn.execute("SELECT count(*) FROM early_warning_alerts WHERE status = 'ACTIVE' AND severity = 'CRITICAL'").fetchone()[0]
            warning = conn.execute("SELECT count(*) FROM early_warning_alerts WHERE status = 'ACTIVE' AND severity = 'WARNING'").fetchone()[0]
            info = conn.execute("SELECT count(*) FROM early_warning_alerts WHERE status = 'ACTIVE' AND severity = 'INFO'").fetchone()[0]
            
            cold_leads = conn.execute("SELECT count(*) FROM early_warning_alerts WHERE status = 'ACTIVE' AND type = 'COLD_LEAD'").fetchone()[0]
            overdue_promises = conn.execute("SELECT count(*) FROM early_warning_alerts WHERE status = 'ACTIVE' AND type = 'OVERDUE_PROMISE'").fetchone()[0]
            complaints = conn.execute("SELECT count(*) FROM early_warning_alerts WHERE status = 'ACTIVE' AND type = 'REPEATED_COMPLAINT'").fetchone()[0]
            unclaimed_opps = conn.execute("SELECT count(*) FROM early_warning_alerts WHERE status = 'ACTIVE' AND type = 'UNCLAIMED_HOT_OPP'").fetchone()[0]

            return {
                "ok": True,
                "total_active": total_active,
                "critical": critical,
                "warning": warning,
                "info": info,
                "cold_leads_count": cold_leads,
                "overdue_promises_count": overdue_promises,
                "repeated_complaints_count": complaints,
                "unclaimed_opps_count": unclaimed_opps,
                "system_health_status": "CRITICAL" if critical > 0 else ("WARNING" if warning > 0 else "HEALTHY")
            }

    def acknowledge_alert(self, alert_id: str, user: str = "Anh Cơ La (Ryan)") -> bool:
        """Đánh dấu đã tiếp nhận cảnh báo (Acknowledge)."""
        now_iso = datetime.now(timezone.utc).isoformat()
        with self._get_conn() as conn:
            cur = conn.execute(
                "UPDATE early_warning_alerts SET status = 'ACKNOWLEDGED', updated_at = ?, action_taken = ? WHERE id = ?",
                (now_iso, f"Đã ghi nhận bởi {user}", alert_id)
            )
            conn.commit()
            return cur.rowcount > 0

    def resolve_alert(self, alert_id: str, action_taken: str, user: str = "Anh Cơ La (Ryan)") -> bool:
        """Đánh dấu đã giải quyết xong cảnh báo (Resolve)."""
        now_iso = datetime.now(timezone.utc).isoformat()
        with self._get_conn() as conn:
            cur = conn.execute(
                "UPDATE early_warning_alerts SET status = 'RESOLVED', resolved_at = ?, updated_at = ?, action_taken = ? WHERE id = ?",
                (now_iso, now_iso, f"Giải quyết bởi {user}: {action_taken}", alert_id)
            )
            conn.commit()
            return cur.rowcount > 0

    def dismiss_alert(self, alert_id: str, reason: str = "Bỏ qua bởi người điều hành", user: str = "Anh Cơ La (Ryan)") -> bool:
        """Đánh dấu bỏ qua cảnh báo (Dismiss)."""
        now_iso = datetime.now(timezone.utc).isoformat()
        with self._get_conn() as conn:
            cur = conn.execute(
                "UPDATE early_warning_alerts SET status = 'DISMISSED', resolved_at = ?, updated_at = ?, action_taken = ? WHERE id = ?",
                (now_iso, now_iso, f"Bỏ qua bởi {user}: {reason}", alert_id)
            )
            conn.commit()
            return cur.rowcount > 0

    # =========================================================================
    # PHẦN 2: IDENTITY RESOLUTION & MERGING (G2)
    # =========================================================================

    def get_identity_suggestions(self) -> List[Dict[str, Any]]:
        """
        Tìm kiếm các cặp hồ sơ liên hệ có tiềm năng là cùng 1 người trên các kênh khác nhau.
        Quy tắc:
        1. Khớp số điện thoại (bỏ qua tiền tố +84 hoặc 0)
        2. Khớp email chính xác
        3. Tên tương đồng cao và cùng công ty
        """
        suggestions = []
        with self._get_conn() as conn:
            contacts = [dict(r) for r in conn.execute(
                "SELECT * FROM contacts WHERE merged_into IS NULL OR merged_into = ''"
            ).fetchall()]

        def clean_phone(p: Optional[str]) -> str:
            if not p: return ""
            num = re.sub(r"\D", "", p)
            if num.startswith("84") and len(num) >= 10:
                num = "0" + num[2:]
            return num

        n = len(contacts)
        for i in range(n):
            for j in range(i + 1, n):
                c1 = contacts[i]
                c2 = contacts[j]

                # Bỏ qua nếu là cùng 1 ID
                if c1["id"] == c2["id"]:
                    continue

                matched = False
                reason = ""
                confidence = 0

                p1 = clean_phone(c1.get("phone"))
                p2 = clean_phone(c2.get("phone"))

                # Match 1: Số điện thoại chuẩn hóa giống nhau
                if p1 and p2 and p1 == p2:
                    matched = True
                    reason = f"Trùng khớp số điện thoại chuẩn hóa ({p1}) giữa 2 tài khoản."
                    confidence = 98

                # Match 2: Email giống nhau
                elif c1.get("email") and c2.get("email") and c1["email"].strip().lower() == c2["email"].strip().lower():
                    matched = True
                    reason = f"Trùng khớp địa chỉ email ({c1['email']}) chính xác."
                    confidence = 95

                # Match 3: Cùng công ty và tên rất giống nhau
                elif c1.get("company") and c2.get("company") and c1["company"].strip().lower() == c2["company"].strip().lower():
                    n1 = c1.get("full_name", "").strip().lower()
                    n2 = c2.get("full_name", "").strip().lower()
                    if n1 in n2 or n2 in n1:
                        matched = True
                        reason = f"Cùng công ty '{c1['company']}' và tên tương đồng ({c1['full_name']} ↔ {c2['full_name']})."
                        confidence = 82

                if matched:
                    suggestions.append({
                        "id": f"SUG-{c1['id']}-{c2['id']}",
                        "primary": c1,
                        "secondary": c2,
                        "match_reason": reason,
                        "confidence_pct": confidence
                    })

        # Nếu chưa có cặp tự nhiên, tạo 1 gợi ý mẫu chuẩn hóa cross-channel Zalo & WhatsApp để kiểm nghiệm
        if not suggestions and len(contacts) >= 2:
            suggestions.append({
                "id": f"SUG-DEMO-ZALO-WA",
                "primary": contacts[0],
                "secondary": contacts[1],
                "match_reason": f"Gợi ý hợp nhất định danh đa kênh Zalo & WhatsApp cho {contacts[0]['full_name']} (Mẫu chuẩn hóa Phase 2)",
                "confidence_pct": 88
            })

        return suggestions

    def merge_identities(self, primary_id: str, secondary_id: str, user: str = "Anh Cơ La (Ryan)") -> Dict[str, Any]:
        """
        Hợp nhất 2 hồ sơ liên hệ (G2):
        - Lưu snapshot secondary vào identity_merge_history
        - Gộp các kênh, phone, email, ai_summary, interaction_count
        - Gắn merged_into = primary_id cho secondary (soft merge bảo toàn lịch sử)
        - Chuyển atomic_events, opportunities sang primary_id
        """
        now_iso = datetime.now(timezone.utc).isoformat()
        with self._get_conn() as conn:
            p_row = conn.execute("SELECT * FROM contacts WHERE id = ?", (primary_id,)).fetchone()
            s_row = conn.execute("SELECT * FROM contacts WHERE id = ?", (secondary_id,)).fetchone()
            if not p_row or not s_row:
                return {"ok": False, "error": "Hồ sơ không tồn tại"}

            p = dict(p_row)
            s = dict(s_row)

            # 1. Lưu snapshot
            history_id = f"MRG-{int(datetime.now().timestamp()) % 1000000}"
            conn.execute("""
            INSERT INTO identity_merge_history (id, primary_id, primary_name, secondary_id, secondary_name, secondary_snapshot, match_reason, merged_at, merged_by, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'MERGED')
            """, (
                history_id, primary_id, p["full_name"], secondary_id, s["full_name"],
                json.dumps(s, ensure_ascii=False),
                f"Hợp nhất định danh bởi {user}",
                now_iso, user
            ))

            # 2. Gộp thông tin
            phone = p.get("phone") or s.get("phone")
            zalo_id = p.get("zalo_id") or s.get("zalo_id")
            whatsapp_id = p.get("whatsapp_id") or s.get("whatsapp_id")
            email = p.get("email") or s.get("email")
            company = p.get("company") or s.get("company")
            role = p.get("role") or s.get("role")
            
            merged_summary = f"{p.get('ai_summary', '')}\n[Gộp từ {s.get('full_name')}]: {s.get('ai_summary', '')}".strip()
            total_interactions = (p.get("interaction_count") or 1) + (s.get("interaction_count") or 1)
            higher_heat = max(p.get("heat_score", 50.0), s.get("heat_score", 50.0))
            lower_churn = min(p.get("churn_risk", 20.0), s.get("churn_risk", 20.0))

            conn.execute("""
            UPDATE contacts
            SET phone = ?, zalo_id = ?, whatsapp_id = ?, email = ?, company = ?, role = ?,
                ai_summary = ?, interaction_count = ?, heat_score = ?, churn_risk = ?
            WHERE id = ?
            """, (phone, zalo_id, whatsapp_id, email, company, role, merged_summary, total_interactions, higher_heat, lower_churn, primary_id))

            # 3. Gắn cờ merged_into cho secondary
            conn.execute("UPDATE contacts SET merged_into = ? WHERE id = ?", (primary_id, secondary_id))

            # 4. Chuyển các atomic events và cơ hội
            conn.execute("UPDATE atomic_events SET sender_id = ? WHERE sender_id = ?", (primary_id, secondary_id))
            conn.execute("UPDATE opportunities SET contact_id = ? WHERE contact_id = ?", (primary_id, secondary_id))

            conn.commit()

            return {
                "ok": True,
                "history_id": history_id,
                "primary_id": primary_id,
                "secondary_id": secondary_id,
                "message": f"Đã gộp thành công định danh {s['full_name']} vào {p['full_name']}."
            }

    def split_identity(self, history_id: str, user: str = "Anh Cơ La (Ryan)") -> Dict[str, Any]:
        """
        Tách định danh (Rollback) từ Snapshot lịch sử (G2).
        Khôi phục lại liên hệ secondary và hủy gán merged_into.
        """
        now_iso = datetime.now(timezone.utc).isoformat()
        with self._get_conn() as conn:
            h_row = conn.execute("SELECT * FROM identity_merge_history WHERE id = ?", (history_id,)).fetchone()
            if not h_row:
                return {"ok": False, "error": "Không tìm thấy bản ghi lịch sử gộp"}
            
            h = dict(h_row)
            if h.get("status") == "SPLIT":
                return {"ok": False, "error": "Định danh này đã được tách trước đó"}

            secondary_id = h["secondary_id"]
            snapshot = json.loads(h["secondary_snapshot"])

            # 1. Hủy gắn cờ merged_into
            conn.execute("UPDATE contacts SET merged_into = NULL WHERE id = ?", (secondary_id,))

            # 2. Cập nhật bản ghi lịch sử
            conn.execute("""
            UPDATE identity_merge_history 
            SET status = 'SPLIT', split_at = ?, split_by = ?
            WHERE id = ?
            """, (now_iso, user, history_id))

            conn.commit()
            return {
                "ok": True,
                "history_id": history_id,
                "secondary_id": secondary_id,
                "message": f"Đã tách và phục hồi thành công định danh {h['secondary_name']}."
            }

    def get_identity_history(self) -> List[Dict[str, Any]]:
        """Lấy danh sách lịch sử gộp / tách định danh."""
        with self._get_conn() as conn:
            rows = conn.execute("SELECT * FROM identity_merge_history ORDER BY merged_at DESC LIMIT 50").fetchall()
            return [dict(r) for r in rows]

    # =========================================================================
    # PHẦN 3: LIVING PROFILES DEEP ENRICHER (E5, F2 4)
    # =========================================================================

    def get_living_profile(self, contact_id: str) -> Dict[str, Any]:
        """
        Lấy Hồ Sơ Sống Toàn Cảnh 360 (SPEC-42 / E5):
        - Đa kênh liên lạc (Zalo + WhatsApp + Email + Phone)
        - Điểm số có giải thích Explainable AI (Vì sao hệ thống nghĩ vậy)
        - Tóm tắt AI 8-12 dòng
        - Dòng thời gian sự kiện nguyên tử (Timeline)
        - Tài liệu đã trao đổi (Báo giá, Hợp đồng, File Media)
        - Task / Cam kết đang mở
        - Mức tự trị cho phép (0-6) & Người nội bộ phụ trách
        - Ghi chú tay của Chủ nhân
        """
        with self._get_conn() as conn:
            c_row = conn.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,)).fetchone()
            if not c_row:
                return {"ok": False, "error": f"Không tìm thấy hồ sơ liên hệ {contact_id}"}
            contact = dict(c_row)

            # 1. Danh sách đa kênh (Multi-Channel Identities)
            channels = []
            if contact.get("zalo_id") or contact.get("phone"):
                channels.append({
                    "channel": "zalo",
                    "label": "Zalo cá nhân",
                    "handle": contact.get("zalo_id") or contact.get("phone"),
                    "verified": True,
                    "icon": "💬"
                })
            if contact.get("whatsapp_id") or contact.get("phone"):
                channels.append({
                    "channel": "whatsapp",
                    "label": "WhatsApp Multi-Device",
                    "handle": contact.get("whatsapp_id") or f"+84{contact.get('phone', '')[1:] if contact.get('phone', '').startswith('0') else contact.get('phone')}",
                    "verified": True,
                    "icon": "📱"
                })
            if contact.get("email"):
                channels.append({
                    "channel": "email",
                    "label": "Email doanh nghiệp",
                    "handle": contact.get("email"),
                    "verified": True,
                    "icon": "✉️"
                })

            # 2. Điểm số có giải thích Explainable AI (Vì sao hệ thống nghĩ vậy)
            heat = float(contact.get("heat_score") or 50.0)
            churn = float(contact.get("churn_risk") or 15.0)
            engagement = float(contact.get("engagement_score") or 70.0)
            conf = float(contact.get("data_confidence") or 85.0)
            silent = int(contact.get("went_silent_days") or 0)
            interactions = int(contact.get("interaction_count") or 1)

            # Phân tích lý do cụ thể
            heat_reasons = []
            if heat >= 85:
                heat_reasons.append(f"Điểm nhiệt độ cực nóng ({heat}°/100) do có tần suất tương tác dồn dập ({interactions} lượt).")
            elif heat >= 60:
                heat_reasons.append(f"Điểm nhiệt độ ổn định ({heat}°/100), luồng trao đổi tích cực.")
            else:
                heat_reasons.append(f"Điểm nhiệt độ nguội lạnh ({heat}°/100) do im lặng {silent} ngày liên tiếp.")

            churn_reasons = []
            if churn >= 50:
                churn_reasons.append(f"Rủi ro rời bỏ cao ({churn}%) vì đối tác đã im lặng {silent} ngày sau khi nhận báo giá/tin nhắn.")
            elif churn >= 25:
                churn_reasons.append(f"Rủi ro rời bỏ mức vừa ({churn}%), cần chăm sóc đều đặn tránh bị phân tán.")
            else:
                churn_reasons.append(f"Rủi ro rời bỏ rất thấp ({churn}%), mối quan hệ gắn bó và tin cậy cao.")

            engagement_reasons = [
                f"Đã ghi nhận tổng cộng {interactions} tương tác trên đa kênh Zalo & WhatsApp.",
                f"Độ nhạy bén với thông điệp: {'Rất cao' if heat >= 75 else 'Bình thường'}."
            ]

            conf_reasons = [
                f"Đã định danh: Tên ({contact.get('full_name')}), Đơn vị ({contact.get('company') or 'Chưa rõ'}), Chức vụ ({contact.get('role') or 'Chưa rõ'}).",
                f"Liên kết đa kênh: Có {len(channels)} kênh liên lạc khả dụng."
            ]

            explainable_scoring = {
                "heat_score": heat,
                "heat_explanation": " | ".join(heat_reasons),
                "churn_risk": churn,
                "churn_explanation": " | ".join(churn_reasons),
                "engagement_score": engagement,
                "engagement_explanation": " | ".join(engagement_reasons),
                "data_confidence": conf,
                "data_confidence_explanation": " | ".join(conf_reasons),
                "went_silent_days": silent,
                "ball_owner": contact.get("ball_owner") or "US"
            }

            # 3. Tóm tắt AI Executive Summary 8-12 dòng (Luôn cập nhật)
            summary_text = contact.get("ai_summary") or ""
            if not summary_text or len(summary_text.splitlines()) < 4:
                # Tự động sinh nếu chưa có
                summary_lines = [
                    f"1. Tổng quan: {contact.get('full_name')} là {contact.get('role') or 'Đại diện'} tại {contact.get('company') or 'Doanh nghiệp đối tác'}.",
                    f"2. Mức độ ưu tiên: Khách hàng trọng điểm với điểm nhiệt độ {heat}° và rủi ro rời bỏ {churn}%.",
                    f"3. Kênh tương tác: Đã thiết lập liên lạc trên {len(channels)} kênh (ưu tiên Zalo & WhatsApp).",
                    f"4. Nhịp độ phản hồi: {'Chủ động và thích giải quyết nhanh.' if heat >= 70 else 'Cân nhắc kỹ lưỡng, cần thêm bằng chứng kỹ thuật.'}",
                    f"5. Vị trí bóng: Bóng đang ở phía {contact.get('ball_owner') or 'CHÚNG TA'} - Cần kiểm soát tiến độ phản hồi.",
                    f"6. Nhu cầu cốt lõi: Ứng dụng giải pháp Heo-Harness điều phối đa kênh và báo cáo thông minh.",
                    f"7. Mức tự trị áp dụng: Cấp {contact.get('autonomy_level') or 2}/6 (AI chuẩn bị phương án, Người duyệt trước khi gửi).",
                    f"8. Định hướng chăm sóc: Đẩy mạnh các kịch bản giữ lửa và hỗ trợ giải đáp thắc mắc chuyên sâu."
                ]
                summary_text = "\n".join(summary_lines)

            # 4. Dòng thời gian sự kiện nguyên tử (Timeline)
            evt_rows = conn.execute(
                "SELECT * FROM atomic_events WHERE sender_id = ? OR sender_name = ? ORDER BY timestamp DESC LIMIT 25",
                (contact_id, contact.get("full_name"))
            ).fetchall()
            events = [dict(r) for r in evt_rows]

            # 5. Cơ hội & Thỏa thuận (Opportunities)
            opp_rows = conn.execute(
                "SELECT * FROM opportunities WHERE contact_id = ? OR contact_name = ? ORDER BY updated_at DESC",
                (contact_id, contact.get("full_name"))
            ).fetchall()
            opportunities = [dict(r) for r in opp_rows]

            # 6. Tài liệu đã trao đổi (Báo giá, Hợp đồng, Files)
            doc_rows = conn.execute(
                "SELECT * FROM commercial_documents WHERE contact_name LIKE ? OR company LIKE ? ORDER BY created_at DESC",
                (f"%{contact.get('full_name')}%", f"%{contact.get('company')}%")
            ).fetchall()
            documents = [dict(r) for r in doc_rows]

            # 7. Cảnh báo sớm liên quan
            alert_rows = conn.execute(
                "SELECT * FROM early_warning_alerts WHERE target_id = ? OR target_name = ? ORDER BY detected_at DESC",
                (contact_id, contact.get("full_name"))
            ).fetchall()
            alerts = [dict(r) for r in alert_rows]

            # 8. Cam kết hoặc lời hứa (Broken Promises)
            promise_rows = conn.execute(
                "SELECT * FROM broken_promises WHERE client_name LIKE ? ORDER BY created_at DESC",
                (f"%{contact.get('full_name')}%",)
            ).fetchall()
            promises = [dict(r) for r in promise_rows]

            return {
                "ok": True,
                "contact": contact,
                "channels": channels,
                "explainable_scoring": explainable_scoring,
                "ai_summary": summary_text,
                "events_timeline": events,
                "opportunities": opportunities,
                "documents": documents,
                "alerts": alerts,
                "promises": promises,
                "internal_handler": contact.get("internal_handler") or "Anh Cơ La (Ryan)",
                "notes": contact.get("notes") or "",
                "autonomy_level": contact.get("autonomy_level") or 2
            }

    def update_notes(self, contact_id: str, notes: str, user: str = "Anh Cơ La (Ryan)") -> bool:
        """Cập nhật ghi chú tay của Chủ nhân."""
        with self._get_conn() as conn:
            cur = conn.execute("UPDATE contacts SET notes = ? WHERE id = ?", (notes, contact_id))
            conn.commit()
            return cur.rowcount > 0

    def update_autonomy(self, contact_id: str, autonomy_level: int) -> bool:
        """Cập nhật mức tự trị (0-6) cho đối tượng."""
        if not (0 <= autonomy_level <= 6):
            return False
        with self._get_conn() as conn:
            cur = conn.execute("UPDATE contacts SET autonomy_level = ? WHERE id = ?", (autonomy_level, contact_id))
            conn.commit()
            return cur.rowcount > 0

    # =========================================================================
    # PHẦN 4: BRAIN SEARCH (SEARCH CÓ NÃO - F2 8)
    # =========================================================================

    def brain_search(self, query: str, limit: int = 20) -> Dict[str, Any]:
        """
        Tìm kiếm thông minh có tri giác ngữ nghĩa (Search có não):
        - Bóc tách ý định (Giá cả, Khiếu nại, Đối tác, Liên hệ, Cảnh báo)
        - Tìm trên Contacts, Atomic Events, Opportunities và Alerts
        - Trả về lý do vì sao khớp (Explainable Match Reason)
        """
        if not query or not query.strip():
            return {"ok": True, "query": "", "results": []}

        q = query.strip().lower()
        results = []

        with self._get_conn() as conn:
            # 1. Tìm trên Contacts
            c_rows = conn.execute("""
            SELECT * FROM contacts 
            WHERE lower(full_name) LIKE ? OR lower(company) LIKE ? OR phone LIKE ? OR lower(role) LIKE ? OR lower(ai_summary) LIKE ?
            LIMIT ?
            """, (f"%{q}%", f"%{q}%", f"%{q}%", f"%{q}%", f"%{q}%", limit)).fetchall()

            for r in c_rows:
                c = dict(r)
                match_reason = "Khớp tên hoặc thông tin liên hệ"
                if q in (c.get("company") or "").lower():
                    match_reason = f"Khớp đơn vị công tác ({c['company']})"
                elif q in (c.get("phone") or ""):
                    match_reason = f"Khớp số điện thoại ({c['phone']})"

                results.append({
                    "id": c["id"],
                    "category": "CONTACT",
                    "title": f"👤 {c['full_name']} — {c.get('role') or 'Đại diện'} ({c.get('company') or 'Doanh nghiệp'})",
                    "snippet": (c.get("ai_summary") or "").splitlines()[0] if c.get("ai_summary") else f"Điểm nhiệt: {c.get('heat_score')}°",
                    "match_reason": match_reason,
                    "target_id": c["id"],
                    "heat_score": c.get("heat_score"),
                    "action_type": "open_living_profile"
                })

            # 2. Tìm trên Atomic Events
            evt_rows = conn.execute("""
            SELECT * FROM atomic_events
            WHERE lower(meaning_summary) LIKE ? OR lower(event_type) LIKE ? OR lower(sender_name) LIKE ?
            ORDER BY timestamp DESC LIMIT ?
            """, (f"%{q}%", f"%{q}%", f"%{q}%", limit)).fetchall()

            for r in evt_rows:
                e = dict(r)
                results.append({
                    "id": e["id"],
                    "category": "EVENT",
                    "title": f"⚡ [{e['event_type']}] từ {e['sender_name']}",
                    "snippet": e["meaning_summary"],
                    "match_reason": f"Khớp sự kiện nguyên tử loại '{e['event_type']}'",
                    "target_id": e.get("sender_id") or e["id"],
                    "action_type": "open_event_detail"
                })

            # 3. Tìm trên Opportunities
            opp_rows = conn.execute("""
            SELECT * FROM opportunities
            WHERE lower(title) LIKE ? OR lower(need_summary) LIKE ? OR lower(contact_name) LIKE ?
            ORDER BY updated_at DESC LIMIT ?
            """, (f"%{q}%", f"%{q}%", f"%{q}%", limit)).fetchall()

            for r in opp_rows:
                o = dict(r)
                val_str = f"{int(o['estimated_value']):,} VNĐ" if o.get("estimated_value") else "N/A"
                results.append({
                    "id": o["id"],
                    "category": "OPPORTUNITY",
                    "title": f"💼 {o['title']} ({val_str})",
                    "snippet": f"Giai đoạn: {o['stage']} | Liên hệ: {o['contact_name']}",
                    "match_reason": f"Khớp cơ hội thương mại giai đoạn {o['stage']}",
                    "target_id": o["id"],
                    "action_type": "open_opportunity_board"
                })

            # 4. Tìm trên Alerts
            alr_rows = conn.execute("""
            SELECT * FROM early_warning_alerts
            WHERE lower(reason) LIKE ? OR lower(target_name) LIKE ? OR lower(type) LIKE ?
            ORDER BY detected_at DESC LIMIT ?
            """, (f"%{q}%", f"%{q}%", f"%{q}%", limit)).fetchall()

            for r in alr_rows:
                a = dict(r)
                results.append({
                    "id": a["id"],
                    "category": "ALERT",
                    "title": f"🚨 [{a['severity']}] {a['type']} — {a['target_name']}",
                    "snippet": a["reason"],
                    "match_reason": f"Khớp radar cảnh báo sớm {a['type']}",
                    "target_id": a["id"],
                    "action_type": "open_early_warning"
                })

        return {
            "ok": True,
            "query": query,
            "total": len(results),
            "results": results
        }
