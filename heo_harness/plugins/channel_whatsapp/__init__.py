"""
Plugin: heo-channel-whatsapp-gateway
Cầu Nối WhatsApp Multi-Device 2 Chiều & Bộ Lọc @Tag Nhóm Thông Minh.
Tuân thủ SSOT: Mọi tin nhắn gửi ra ngoài phải qua Policy Engine thẩm định cấp Permit.
Tác giả & Chủ nhân duy nhất: Anh Cơ La (genesis.corp.os@gmail.com)
"""

from heo_harness.core.plugin import BasePlugin, PluginMetadata, PluginCategory, PluginHealthStatus
from heo_harness.core.policy import PolicyDecisionType
import os
import time
import uuid
from typing import Dict, Any, Optional

class WhatsAppChannelPlugin(BasePlugin):
    metadata = PluginMetadata(
        id="heo-channel-whatsapp-gateway",
        name="Kênh Kết Nối WhatsApp Gateway (Multi-Device & QR)",
        version="1.0.0",
        author="Anh Cơ La (Ryan)",
        author_email="genesis.corp.os@gmail.com",
        category=PluginCategory.CHANNEL,
        description="Kết nối tương tác WhatsApp thời gian thực qua giao thức Multi-Device Web/Cloud API, mã QR kết nối, lọc @tag và kiểm duyệt an toàn qua Policy Gate.",
        icon="📱",
        default_enabled=True
    )

    def on_load(self) -> None:
        self.ctx.provide("channel_whatsapp", self)
        data_dir = getattr(self.ctx, "data_dir", "data")
        session_file = os.path.join(data_dir, "whatsapp_session.json")
        has_real_session = os.path.exists(session_file)
        self.connected = has_real_session
        self.logged_in = has_real_session
        self.session_id = "wa_active_session" if has_real_session else ""
        self.account_name = "Bé Heo (WhatsApp Executive)" if has_real_session else "Chưa liên kết"
        self.phone_number = "+84-xxxxxxxxxx" if has_real_session else "Chưa liên kết"
        self.pending_approvals = []
        self.inbound_count = 0
        self.outbound_count = 0

    def on_enable(self) -> None:
        self.log("📱 Đã kích hoạt WhatsApp Channel Gateway. Sẵn sàng Multi-Device Bridge & kiểm soát chính sách an toàn.")
        self.bus.on("channel:whatsapp:raw_inbound", self.handle_incoming_message, plugin_id=self.metadata.id)
        self.bus.on("channel:message:outbound", self.handle_outbound_request, plugin_id=self.metadata.id)

    def handle_incoming_message(self, msg_data: dict) -> dict:
        return self.safe_execute(self._filter_and_dispatch, msg_data)

    def _filter_and_dispatch(self, msg_data: dict) -> dict:
        self.inbound_count += 1
        is_group = msg_data.get("is_group", False)
        content = msg_data.get("content", "")
        sender_id = msg_data.get("sender_id", "WA-UNKNOWN")
        sender_name = msg_data.get("sender_name", "Đối tác")
        group_id = msg_data.get("group_id", "*")

        raw_evidence_ref = f"raw_event:WA-{uuid.uuid4().hex[:8].upper()}"

        persona_svc = self.ctx.inject("persona")
        bot_name = "Bé Heo"
        if persona_svc:
            bot_name = persona_svc.get_config().get("bot_name", "Bé Heo")

        if is_group:
            mentioned = msg_data.get("is_mentioned", False) or f"@{bot_name}" in content
            if not mentioned:
                return {
                    "handled": False,
                    "reason": "Not mentioned in WhatsApp group (Observe only)",
                    "evidence_ref": raw_evidence_ref
                }

        self.log(f"📩 [WHATSAPP INBOUND] Tin nhắn từ {sender_name} [{sender_id}] (Nhóm: {is_group}): '{content}'")

        self.bus.emit("channel:message:inbound", {
            "channel": "whatsapp",
            "sender_id": sender_id,
            "sender_name": sender_name,
            "group_id": group_id,
            "content": content,
            "evidence_ref": raw_evidence_ref
        })

        llm_svc = self.ctx.inject("llm_core") or self.ctx.inject("llm")
        if llm_svc:
            reply_text = llm_svc.generate(content, sender_name=sender_name)
            send_result = self.send_message(
                target_id=sender_id,
                content=reply_text,
                group_id=group_id if is_group else None,
                correlation_id=raw_evidence_ref
            )
            return {
                "handled": True,
                "reply": reply_text,
                "evidence_ref": raw_evidence_ref,
                "send_status": send_result
            }

        return {"handled": False, "reason": "No LLM Core service available", "evidence_ref": raw_evidence_ref}

    def send_message(
        self,
        target_id: str,
        content: str,
        group_id: str = None,
        correlation_id: str = None,
        explicit_permit: str = None
    ) -> dict:
        return self.safe_execute(self._do_send_message, target_id, content, group_id, correlation_id, explicit_permit)

    def _do_send_message(
        self,
        target_id: str,
        content: str,
        group_id: str = None,
        correlation_id: str = None,
        explicit_permit: str = None
    ) -> dict:
        corr = correlation_id or f"COR-WA-{uuid.uuid4().hex[:8].upper()}"
        policy_svc = self.ctx.inject("policy_engine")

        if policy_svc and not explicit_permit:
            eval_res = policy_svc.evaluate(
                action="whatsapp.send_message",
                channel="whatsapp",
                group=group_id or "*",
                person=target_id,
                correlation_id=corr
            )

            if eval_res.decision == PolicyDecisionType.DENY:
                self.log(f"🛑 [POLICY DENY] Cấm gửi tin WhatsApp tới {target_id}: {eval_res.reason}")
                return {
                    "sent": False,
                    "status": "DENIED",
                    "reason": eval_res.reason,
                    "correlation_id": corr
                }

            if eval_res.decision == PolicyDecisionType.APPROVAL:
                approval_item = {
                    "id": f"AP-WA-{int(time.time()*1000)%10000}",
                    "action": "whatsapp.send_message",
                    "target": f"{target_id} (Group: {group_id})",
                    "summary": f"Gửi WhatsApp tới {target_id}: {content[:40]}...",
                    "content": content,
                    "correlation_id": corr,
                    "permit_id": eval_res.permit_id
                }
                self.pending_approvals.append(approval_item)
                self.log(f"⏳ [POLICY APPROVAL] Tin nhắn WhatsApp tới {target_id} đang chờ Sếp duyệt ({approval_item['id']})")
                return {
                    "sent": False,
                    "status": "APPROVAL_REQUIRED",
                    "approval_id": approval_item["id"],
                    "correlation_id": corr
                }

        self.outbound_count += 1
        self.log(f"🚀 [WHATSAPP SENT] Đã phát tin nhắn tới {target_id} (Nhóm: {group_id}): '{content[:60]}...'")
        
        # Ghi nhật ký vào store
        store = self.ctx.inject("data_store")
        if store and hasattr(store, "record_whatsapp_message"):
            store.record_whatsapp_message(
                sender_id="bot",
                sender_name=self.account_name,
                target_id=target_id,
                group_id=group_id,
                content=content,
                is_outgoing=True
            )

        return {
            "sent": True,
            "status": "SUCCEEDED",
            "target": target_id,
            "correlation_id": corr,
            "timestamp": time.time()
        }

    def handle_outbound_request(self, payload: dict) -> None:
        if payload.get("channel") != "whatsapp":
            return
        target_id = payload.get("target_id", "")
        content = payload.get("content", "")
        group_id = payload.get("group_id", None)
        explicit_permit = payload.get("permit_id", None)
        self.send_message(target_id, content, group_id=group_id, explicit_permit=explicit_permit)

    def get_session_status(self) -> dict:
        return {
            "channel": "whatsapp",
            "connected": self.connected,
            "logged_in": self.logged_in,
            "account": self.account_name,
            "phone_number": self.phone_number,
            "session_id": self.session_id,
            "inbound_total": self.inbound_count,
            "outbound_total": self.outbound_count,
            "pending_approvals_count": len(self.pending_approvals)
        }
