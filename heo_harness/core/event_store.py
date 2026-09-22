"""
Module: heo_harness.core.event_store
Kiến Trúc Sự Kiện Nguyên Tử (SPEC-30 & SPEC-41 Event-Driven Persistence)
Tuân thủ chuẩn SSOT Mục G3 Spec LOCKED v2.2:
- Sự kiện là đơn vị nguyên tử (Atomic Unit): Không xây hệ thống quanh 'đoạn chat thô', mà xây quanh 'sự kiện có nghĩa'.
- Các loại sự kiện chuẩn:
  * AskedPrice (Hỏi giá / Báo giá)
  * RequestedPartnership (Đề nghị hợp tác / Cung cầu)
  * Complained (Khiếu nại / Than phiền)
  * PromisedDelivery (Hứa giao hàng / Hẹn cam kết)
  * ScheduledMeeting (Hẹn họp / Gặp gỡ)
  * SentQuotation (Gửi báo giá / Chốt deal)
  * MentionsCompetitor (Nhắc đối thủ)
  * WentSilent (Cảnh báo mất hút / Im lặng)
  * ExecutiveCoachingDirective (Chỉ thị đào tạo của Sếp)
  * CareQualityAnomaly (Bất thường chăm sóc)
- Tự động chuyển đổi sự kiện thành Task hoặc Opportunity Deal trên Console V6.
"""

import os
import json
import time
import uuid
import sqlite3
from typing import Dict, List, Any, Optional, Tuple
from heo_harness.core.bus import EventBus
from heo_harness.core.data_factory import get_data_factory, ConversationDataFactory

CANONICAL_EVENT_TYPES = [
    "AskedPrice",
    "RequestedPartnership",
    "Complained",
    "PromisedDelivery",
    "ScheduledMeeting",
    "SentQuotation",
    "MentionsCompetitor",
    "WentSilent",
    "GeneralConversation"
]

EVENT_TYPE_METADATA = {
    "AskedPrice": {"label": "Hỏi Giá / Chi Phí", "color": "#f59e0b", "icon": "💰", "default_priority": "P1"},
    "RequestedPartnership": {"label": "Cung Cầu / Đối Tác", "color": "#a855f7", "icon": "🤝", "default_priority": "P1"},
    "Complained": {"label": "Khiếu Nại / Than Phiền", "color": "#ef4444", "icon": "⚠️", "default_priority": "P0"},
    "PromisedDelivery": {"label": "Hứa Hẹn & Cam Kết", "color": "#10b981", "icon": "📦", "default_priority": "P1"},
    "ScheduledMeeting": {"label": "Hẹn Lịch / Giao Thương", "color": "#38bdf8", "icon": "📅", "default_priority": "P1"},
    "SentQuotation": {"label": "Báo Giá & Chốt Đơn", "color": "#06b6d4", "icon": "📄", "default_priority": "P1"},
    "MentionsCompetitor": {"label": "Đối Thủ Cạnh Tranh", "color": "#ec4899", "icon": "🥊", "default_priority": "P2"},
    "WentSilent": {"label": "Im Lặng / Mất Hút", "color": "#f43f5e", "icon": "⏳", "default_priority": "P0"},
    "GeneralConversation": {"label": "Trao Đổi Thông Thường", "color": "#94a3b8", "icon": "💬", "default_priority": "P2"}
}


class EventStore:
    def __init__(self, db_path: str = None):
        if db_path:
            self.data_factory = ConversationDataFactory(db_path=db_path)
        else:
            self.data_factory = get_data_factory()
        self.db_path = db_path or self.data_factory.db_path


    def _get_conn(self) -> sqlite3.Connection:
        return self.data_factory._get_conn()

    def persist_inbound_message(
        self,
        content: str,
        channel: str = "zalo",
        sender_id: str = "unknown",
        sender_name: str = "Khách",
        group_id: str = None,
        group_name: str = "1-1"
    ) -> dict:
        """Bóc tách tin nhắn thô và lưu bền vững vào Event Store SQLite (SPEC-30)"""
        return self.data_factory.process_incoming_message(
            content=content,
            channel=channel,
            sender_id=sender_id,
            sender_name=sender_name,
            group_id=group_id,
            group_name=group_name
        )

    def get_events(
        self,
        limit: int = 50,
        filter_type: str = None,
        channel: str = None,
        status: str = None,
        search: str = None
    ) -> List[Dict[str, Any]]:
        """Tra cứu danh sách sự kiện nguyên tử kèm metadata phong phú"""
        with self._get_conn() as conn:
            query = "SELECT * FROM atomic_events WHERE 1=1"
            params = []

            if status == "ACTIVE":
                query += " AND (archived = 0 OR archived IS NULL) AND status != 'ARCHIVED'"
            elif status == "ARCHIVED":
                query += " AND (archived = 1 OR status = 'ARCHIVED')"

            if filter_type and filter_type != "ALL":
                query += " AND event_type = ?"
                params.append(filter_type)

            if channel and channel != "ALL":
                query += " AND LOWER(channel) = LOWER(?)"
                params.append(channel)

            if search and search.strip():
                query += " AND (content LIKE ? OR sender_name LIKE ? OR meaning_summary LIKE ?)"
                kw = f"%{search.strip()}%"
                params.extend([kw, kw, kw])

            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)

            rows = conn.execute(query, params).fetchall()
            return [dict(r) for r in rows]

    def get_event_by_id(self, event_id: str) -> Optional[Dict[str, Any]]:
        with self._get_conn() as conn:
            row = conn.execute("SELECT * FROM atomic_events WHERE id = ?", (event_id,)).fetchone()
            return dict(row) if row else None

    def archive_event(self, event_id: str) -> bool:
        """Đưa sự kiện vào trạng thái đã xử lý (Inbox Zero cho Meaning Cards)"""
        with self._get_conn() as conn:
            conn.execute("UPDATE atomic_events SET archived = 1, status = 'ARCHIVED' WHERE id = ?", (event_id,))
            conn.commit()
            return True

    def convert_event_to_task(self, event_id: str, title: str = None, owner: str = None, priority: str = "P2", store = None) -> Dict[str, Any]:
        """(SPEC-30 & SPEC-41) Chuyển đổi sự kiện có nghĩa thành Task/WorkItem trong Work OS"""
        evt = self.get_event_by_id(event_id)
        if not evt:
            return {"ok": False, "error": f"Không tìm thấy sự kiện {event_id}"}

        task_title = title or f"Xử lý {evt.get('intent') or evt.get('event_type')}: {evt.get('meaning_summary') or evt.get('content')[:50]}"
        task_owner = owner or "Sếp Cơ La & Trợ Lý"
        task_note = f"Tạo tự động từ Sự Kiện Nguyên Tử {event_id} ({evt.get('channel')}) của {evt.get('sender_name')}: \"{evt.get('content')}\""

        work_item = None
        if store and hasattr(store, "add_work"):
            work_item = store.add_work(
                title=task_title,
                owner=task_owner,
                priority=priority,
                deadline="Hôm nay",
                group=evt.get("group_name", "1-1"),
                note=task_note,
                group_id=evt.get("group_id"),
                channel=evt.get("channel", "zalo"),
                source_msg_id=event_id
            )


        # Đánh dấu sự kiện đã chuyển thành task
        with self._get_conn() as conn:
            conn.execute("UPDATE atomic_events SET status = 'CONVERTED_TASK' WHERE id = ?", (event_id,))
            conn.commit()

        return {
            "ok": True,
            "event_id": event_id,
            "work_item": work_item,
            "message": f"Đã chuyển đổi thành công sự kiện {event_id} thành Công Việc!"
        }

    def convert_event_to_opportunity(self, event_id: str, custom_title: str = None, estimated_value: float = None) -> Dict[str, Any]:
        """(SPEC-30 & SPEC-41) Chuyển đổi sự kiện có nghĩa thành Deal trong Kanban 7 Cột"""
        evt = self.get_event_by_id(event_id)
        if not evt:
            return {"ok": False, "error": f"Không tìm thấy sự kiện {event_id}"}

        opp_id = f"OPP-{int(time.time()*1000)%1000000:06d}-{uuid.uuid4().hex[:4]}"
        now_str = time.strftime("%Y-%m-%d %H:%M:%S")

        title = custom_title or f"Nhu cầu {evt.get('event_type')} từ {evt.get('sender_name')}"
        est_val = estimated_value if estimated_value is not None else 0.0

        with self._get_conn() as conn:
            conn.execute("""
            INSERT INTO opportunities (
                id, title, contact_name, contact_id, channel,
                group_name, need_summary, estimated_value,
                stage, confidence_score, heat_score, risk_notes,
                source_event_id, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'SIGNAL', 80.0, ?, ?, ?, ?, ?)
            """, (
                opp_id, title, evt.get("sender_name", "Đối tác"), evt.get("sender_id"),
                evt.get("channel", "zalo"), evt.get("group_name", "1-1"),
                evt.get("content", "")[:200], est_val,
                evt.get("heat_score", 60.0),
                "Chuyển đổi trực tiếp từ Thẻ Ý Nghĩa (Meaning Card).",
                event_id, now_str, now_str
            ))

            conn.execute("UPDATE atomic_events SET status = 'CONVERTED_OPPORTUNITY' WHERE id = ?", (event_id,))
            conn.commit()

        return {
            "ok": True,
            "opportunity_id": opp_id,
            "title": title,
            "stage": "SIGNAL",
            "message": f"Đã chuyển đổi sự kiện thành Cơ Hội {opp_id} thành công!"
        }

    def get_event_stats(self) -> Dict[str, Any]:
        with self._get_conn() as conn:
            total = conn.execute("SELECT COUNT(*) FROM atomic_events").fetchone()[0]
            active = conn.execute("SELECT COUNT(*) FROM atomic_events WHERE (archived = 0 OR archived IS NULL) AND status != 'ARCHIVED'").fetchone()[0]
            by_type = dict(conn.execute("SELECT event_type, COUNT(*) FROM atomic_events GROUP BY event_type").fetchall())
            by_channel = dict(conn.execute("SELECT channel, COUNT(*) FROM atomic_events GROUP BY channel").fetchall())
            by_priority = dict(conn.execute("SELECT priority, COUNT(*) FROM atomic_events GROUP BY priority").fetchall())

        return {
            "ok": True,
            "total_events": total,
            "active_events": active,
            "by_type": by_type,
            "by_channel": by_channel,
            "by_priority": by_priority,
            "supported_types": CANONICAL_EVENT_TYPES
        }

    def register_event_bus_listeners(self, bus: EventBus) -> None:
        """Đăng ký hook tự động đón nhận tin nhắn thô từ mọi Channel Gateway (SPEC-30 & SPEC-04)"""
        def on_inbound_message(data: dict):
            try:
                content = data.get("content", "")
                channel = data.get("channel", "zalo")
                sender_id = data.get("sender_id", "unknown")
                sender_name = data.get("sender_name", "Khách")
                group_id = data.get("group_id")
                group_name = data.get("group_name", "1-1")

                if content and content.strip():
                    evt_result = self.persist_inbound_message(
                        content=content,
                        channel=channel,
                        sender_id=sender_id,
                        sender_name=sender_name,
                        group_id=group_id,
                        group_name=group_name
                    )
                    if evt_result:
                        bus.emit("data_factory:event:created", evt_result)
            except Exception as err:
                print(f"[EventStore] Lỗi tự động chuyển hoá tin nhắn thành Sự Kiện Nguyên Tử: {err}")

        bus.on("channel:message:inbound", on_inbound_message, priority=10, plugin_id="heo-core-event-store")


_EVENT_STORE_INSTANCE = None

def get_event_store() -> EventStore:
    global _EVENT_STORE_INSTANCE
    if _EVENT_STORE_INSTANCE is None:
        _EVENT_STORE_INSTANCE = EventStore()
    return _EVENT_STORE_INSTANCE
