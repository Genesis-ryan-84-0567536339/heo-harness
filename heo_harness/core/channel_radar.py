# -*- coding: utf-8 -*-
"""
Module: heo_harness.core.channel_radar
Multi-Channel Radar & Universal Ingestion Engine (SPEC-04 SSOT).
Lắng nghe và thu nạp tín hiệu đa kênh: Zalo, WhatsApp, Telegram, Facebook, LinkedIn, Generic Webhook.
Đồng bộ trực tiếp vào Conversation Data Factory & Atomic Event Ledger.
Tác giả & Chủ nhân duy nhất: Anh Cơ La (genesis.corp.os@gmail.com)
"""

import sqlite3
import json
import time
import os
import uuid
from typing import Dict, Any, List, Optional
from heo_harness.core.data_factory import ConversationDataFactory

class ChannelRadarEngine:
    _instance = None
    _active_db_path = None

    @classmethod
    def get_instance(cls, db_path: str = None):
        if cls._instance is None or (db_path and cls._active_db_path != db_path):
            cls._instance = cls(db_path=db_path)
            cls._active_db_path = db_path
        return cls._instance

    def __init__(self, db_path: str = None):
        if not db_path:
            db_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "heo.db")
        self.db_path = os.path.abspath(db_path)
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.data_factory = ConversationDataFactory(db_path=self.db_path)
        self._ensure_schema()
        self._seed_default_channels()

    def _get_conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_schema(self):
        """Khởi tạo schema tự phục hồi cho cấu hình kênh Radar và nhật ký thu nạp."""
        with self._get_conn() as conn:
            conn.execute("""
            CREATE TABLE IF NOT EXISTS channel_radar_config (
                channel TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                enabled INTEGER NOT NULL DEFAULT 1,
                status TEXT NOT NULL DEFAULT 'STANDBY',
                token TEXT DEFAULT '',
                verify_token TEXT DEFAULT '',
                webhook_path TEXT DEFAULT '',
                listen_mode TEXT NOT NULL DEFAULT 'PROACTIVE',
                total_inbound INTEGER NOT NULL DEFAULT 0,
                last_active REAL,
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL
            )
            """)
            conn.execute("""
            CREATE TABLE IF NOT EXISTS channel_radar_logs (
                id TEXT PRIMARY KEY,
                channel TEXT NOT NULL,
                sender_id TEXT,
                sender_name TEXT,
                group_id TEXT,
                message_text TEXT,
                intent TEXT,
                is_mention INTEGER DEFAULT 0,
                status TEXT NOT NULL DEFAULT 'INGESTED',
                raw_payload TEXT,
                created_at REAL NOT NULL
            )
            """)
            conn.commit()

    def _seed_default_channels(self):
        """Khởi tạo 5 kênh radar chuẩn SSOT nếu chưa tồn tại."""
        now = time.time()
        default_channels = [
            {
                "channel": "zalo",
                "name": "Zalo Gateway (Multi-Account QR)",
                "enabled": 1,
                "status": "ONLINE",
                "token": "local-bridge-5051",
                "verify_token": "",
                "webhook_path": "/api/zalo/webhook",
                "listen_mode": "MENTION_AND_KEYWORD"
            },
            {
                "channel": "whatsapp",
                "name": "WhatsApp Gateway (Multi-Device Baileys)",
                "enabled": 1,
                "status": "ONLINE",
                "token": "local-bridge-5052",
                "verify_token": "",
                "webhook_path": "/api/whatsapp/webhook",
                "listen_mode": "PROACTIVE"
            },
            {
                "channel": "telegram",
                "name": "Telegram Bot & Community Radar",
                "enabled": 1,
                "status": "CONNECTED",
                "token": "tg_bot_token_simulated",
                "verify_token": "heo_tg_secret_123",
                "webhook_path": "/api/radar/webhook/telegram",
                "listen_mode": "PROACTIVE"
            },
            {
                "channel": "facebook",
                "name": "Facebook Messenger & Page Radar",
                "enabled": 1,
                "status": "CONNECTED",
                "token": "meta_page_token_simulated",
                "verify_token": "heo_fb_verify_token",
                "webhook_path": "/api/radar/webhook/facebook",
                "listen_mode": "PROACTIVE"
            },
            {
                "channel": "generic_webhook",
                "name": "Generic Webhook (Discord / Email / CRM)",
                "enabled": 1,
                "status": "ONLINE",
                "token": "heo_secret_webhook_key",
                "verify_token": "",
                "webhook_path": "/api/radar/webhook/generic",
                "listen_mode": "PROACTIVE"
            }
        ]

        with self._get_conn() as conn:
            for ch in default_channels:
                row = conn.execute("SELECT channel FROM channel_radar_config WHERE channel = ?", (ch["channel"],)).fetchone()
                if not row:
                    conn.execute("""
                    INSERT INTO channel_radar_config 
                    (channel, name, enabled, status, token, verify_token, webhook_path, listen_mode, total_inbound, last_active, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?, ?)
                    """, (
                        ch["channel"], ch["name"], ch["enabled"], ch["status"],
                        ch["token"], ch["verify_token"], ch["webhook_path"], ch["listen_mode"],
                        now, now, now
                    ))
            conn.commit()

    def get_channels_status(self) -> List[Dict[str, Any]]:
        """Lấy danh sách kênh Radar kèm trạng thái và số liệu thu nạp."""
        with self._get_conn() as conn:
            rows = conn.execute("""
            SELECT channel, name, enabled, status, webhook_path, listen_mode, total_inbound, last_active, updated_at
            FROM channel_radar_config
            ORDER BY created_at ASC
            """).fetchall()

            result = []
            for r in rows:
                item = dict(r)
                item["enabled"] = bool(item["enabled"])
                # Lấy số tin nhắn trong 24h qua
                count_24h = conn.execute("""
                SELECT COUNT(*) as c FROM channel_radar_logs 
                WHERE channel = ? AND created_at >= ?
                """, (item["channel"], time.time() - 86400)).fetchone()["c"]
                item["inbound_24h"] = count_24h
                result.append(item)
            return result

    def configure_channel(self, channel: str, updates: Dict[str, Any]) -> bool:
        """Cập nhật cấu hình kênh Radar (Token, chế độ lắng nghe, bật/tắt)."""
        allowed = ["name", "enabled", "status", "token", "verify_token", "listen_mode"]
        sets = []
        vals = []
        for k in allowed:
            if k in updates:
                sets.append(f"{k} = ?")
                if k == "enabled":
                    vals.append(1 if updates[k] else 0)
                else:
                    vals.append(updates[k])

        if not sets:
            return False

        sets.append("updated_at = ?")
        vals.append(time.time())
        vals.append(channel)

        with self._get_conn() as conn:
            cur = conn.execute(f"UPDATE channel_radar_config SET {', '.join(sets)} WHERE channel = ?", vals)
            conn.commit()
            return cur.rowcount > 0

    def _increment_channel_stat(self, channel: str):
        with self._get_conn() as conn:
            conn.execute("""
            UPDATE channel_radar_config 
            SET total_inbound = total_inbound + 1, last_active = ?, updated_at = ?
            WHERE channel = ?
            """, (time.time(), time.time(), channel))
            conn.commit()

    def _record_radar_log(self, channel: str, sender_id: str, sender_name: str, group_id: str,
                           message_text: str, intent: str, is_mention: bool, raw_payload: Any) -> str:
        log_id = f"RADAR-{uuid.uuid4().hex[:8].upper()}"
        payload_str = json.dumps(raw_payload, ensure_ascii=False) if isinstance(raw_payload, (dict, list)) else str(raw_payload)
        with self._get_conn() as conn:
            conn.execute("""
            INSERT INTO channel_radar_logs 
            (id, channel, sender_id, sender_name, group_id, message_text, intent, is_mention, status, raw_payload, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'INGESTED', ?, ?)
            """, (
                log_id, channel, sender_id, sender_name, group_id, message_text,
                intent, 1 if is_mention else 0, payload_str, time.time()
            ))
            conn.commit()
        self._increment_channel_stat(channel)
        return log_id

    # --------------------------------------------------------------------------
    # INGESTION ENGINES THEO TỪNG GIAO THỨC CHUẨN
    # --------------------------------------------------------------------------

    def ingest_telegram_update(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Bóc tách Telegram Update payload chuẩn từ Telegram Bot API Webhook.
        Hỗ trợ message, edited_message, channel_post.
        """
        msg = payload.get("message") or payload.get("edited_message") or payload.get("channel_post") or {}
        if not msg:
            return {"ok": False, "error": "Không tìm thấy nội dung message trong Telegram Update"}

        chat = msg.get("chat", {})
        sender = msg.get("from", {})
        text = msg.get("text", "") or msg.get("caption", "")

        sender_id = f"tg_{sender.get('id', 'unknown')}"
        sender_name = f"{sender.get('first_name', '')} {sender.get('last_name', '')}".strip() or sender.get("username", "Telegram User")
        
        chat_type = chat.get("type", "private")
        group_id = f"tg_group_{chat.get('id')}" if chat_type in ["group", "supergroup", "channel"] else "direct"
        is_mention = ("@" in text) or (chat_type == "private")

        # Thu nạp vào Data Factory
        df_res = self.data_factory.process_incoming_message(
            content=text,
            channel="telegram",
            sender_id=sender_id,
            sender_name=sender_name,
            group_id=group_id,
            group_name=chat.get("title", group_id)
        )

        intent = (df_res or {}).get("intent_label") or (df_res or {}).get("event_type", "Chitchat")
        log_id = self._record_radar_log("telegram", sender_id, sender_name, group_id, text, intent, is_mention, payload)

        return {
            "ok": True,
            "channel": "telegram",
            "log_id": log_id,
            "sender_name": sender_name,
            "text": text,
            "data_factory": df_res
        }

    def ingest_facebook_entry(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Bóc tách Meta / Facebook Messenger Webhook payload chuẩn.
        """
        entries = payload.get("entry", [])
        results = []

        for entry in entries:
            for messaging_event in entry.get("messaging", []):
                sender = messaging_event.get("sender", {})
                recipient = messaging_event.get("recipient", {})
                msg = messaging_event.get("message", {})
                text = msg.get("text", "")

                if not text:
                    continue

                sender_id = f"fb_{sender.get('id', 'unknown')}"
                sender_name = f"FB User ({sender.get('id')})"
                group_id = f"fb_page_{recipient.get('id', 'main')}"
                is_mention = True  # Direct message tới Fanpage mặc định xem như tương tác trực tiếp

                df_res = self.data_factory.process_incoming_message(
                    content=text,
                    channel="facebook",
                    sender_id=sender_id,
                    sender_name=sender_name,
                    group_id=group_id,
                    group_name=group_id
                )

                intent = (df_res or {}).get("intent_label") or (df_res or {}).get("event_type", "Chitchat")
                log_id = self._record_radar_log("facebook", sender_id, sender_name, group_id, text, intent, is_mention, messaging_event)
                results.append({
                    "log_id": log_id,
                    "sender_id": sender_id,
                    "text": text,
                    "intent": intent,
                    "data_factory": df_res
                })

        return {
            "ok": True,
            "channel": "facebook",
            "processed_count": len(results),
            "events": results
        }

    def ingest_generic_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Thu nạp qua Webhook chuẩn hóa đa kênh (Discord, Webform, CRM, Email parser).
        Payload yêu cầu: channel, sender_name, text; group_id & sender_id tuỳ chọn.
        """
        channel = payload.get("channel", "generic_webhook").lower()
        text = payload.get("text") or payload.get("content") or payload.get("message") or ""
        sender_name = payload.get("sender_name") or payload.get("author") or "Webhook Partner"
        sender_id = payload.get("sender_id") or f"{channel}_{uuid.uuid4().hex[:6]}"
        group_id = payload.get("group_id", "direct")
        is_mention = bool(payload.get("is_mention", True))

        if not text:
            return {"ok": False, "error": "Thiếu nội dung tin nhắn (text / content / message)"}

        df_res = self.data_factory.process_incoming_message(
            content=text,
            channel=channel,
            sender_id=sender_id,
            sender_name=sender_name,
            group_id=group_id,
            group_name=group_id
        )

        intent = (df_res or {}).get("intent_label") or (df_res or {}).get("event_type", "Chitchat")
        log_id = self._record_radar_log(channel, sender_id, sender_name, group_id, text, intent, is_mention, payload)

        return {
            "ok": True,
            "channel": channel,
            "log_id": log_id,
            "sender_name": sender_name,
            "text": text,
            "intent": intent,
            "data_factory": df_res
        }

    def simulate_inbound_ping(self, channel: str, sender_name: str, text: str, group_name: str = "") -> Dict[str, Any]:
        """Mô phỏng tin nhắn đến qua Radar để kiểm thử nhanh và demo trực quan."""
        simulated_payload = {
            "channel": channel,
            "sender_id": f"{channel}_{uuid.uuid4().hex[:6]}",
            "sender_name": sender_name,
            "group_id": group_name or "demo_group",
            "text": text,
            "is_mention": True,
            "metadata": {"simulated": True, "ping_time": time.time()}
        }
        return self.ingest_generic_webhook(simulated_payload)

    def verify_facebook_webhook(self, mode: str, token: str, challenge: str) -> Optional[str]:
        """Xác thực Webhook Facebook (hub.mode, hub.verify_token, hub.challenge)."""
        with self._get_conn() as conn:
            row = conn.execute("SELECT verify_token FROM channel_radar_config WHERE channel = 'facebook'").fetchone()
            expected_token = row["verify_token"] if row else "heo_fb_verify_token"
            if mode == "subscribe" and token == expected_token:
                return challenge
        return None

    def get_recent_logs(self, limit: int = 50, channel: str = None) -> List[Dict[str, Any]]:
        """Lấy danh sách nhật ký radar gần đây nhất."""
        with self._get_conn() as conn:
            if channel and channel != "ALL":
                rows = conn.execute("""
                SELECT * FROM channel_radar_logs 
                WHERE channel = ? 
                ORDER BY created_at DESC LIMIT ?
                """, (channel, limit)).fetchall()
            else:
                rows = conn.execute("""
                SELECT * FROM channel_radar_logs 
                ORDER BY created_at DESC LIMIT ?
                """, (limit,)).fetchall()

            result = []
            for r in rows:
                item = dict(r)
                item["is_mention"] = bool(item["is_mention"])
                result.append(item)
            return result
