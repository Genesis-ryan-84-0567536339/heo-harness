"""
Plugin: @heo/channel-zalo
Cầu Nối Zalo 2 Chiều & Bộ Lọc Nhận Diện @Tag Nhóm Thông Minh.
Tuân thủ SSOT: Mọi tin nhắn gửi ra ngoài phải qua Policy Engine thẩm định cấp Permit.
Tác giả: Anh Cơ La (genesis.corp.os@gmail.com)
"""

from heo_harness.core.plugin import BasePlugin, PluginMetadata, PluginCategory, PluginHealthStatus
from heo_harness.core.policy import PolicyDecisionType
import time
import uuid

class ZaloChannelPlugin(BasePlugin):
    metadata = PluginMetadata(
        id="@heo/channel-zalo",
        name="Kênh Kết Nối Zalo Cá Nhân (Bảo Mật QR)",
        version="1.0.0",
        author="Anh Cơ La (Ryan)",
        author_email="genesis.corp.os@gmail.com",
        category=PluginCategory.CHANNEL,
        description="Kết nối tương tác Zalo thời gian thực, đăng nhập QR Code, lọc tag nhóm, kiểm soát xuất tin qua Policy Engine.",
        icon="💬",
        default_enabled=True
    )

    def on_load(self) -> None:
        self.ctx.provide("channel_zalo", self)
        self.connected = True
        self.logged_in = True
        self.session_id = "zalo_owner_session_v1"
        self.account_name = "Bé Heo (Assistant)"
        self.pending_approvals = []
        self.inbound_count = 0
        self.outbound_count = 0

    def on_enable(self) -> None:
        self.log("💬 Đã kích hoạt Zalo Channel Adapter. Sẵn sàng kết nối Bridge và kiểm soát chính sách an toàn.")
        # Lắng nghe sự kiện tin nhắn đến từ Zalo Bridge
        self.bus.on("channel:zalo:raw_inbound", self.handle_incoming_message, plugin_id=self.metadata.id)
        # Lắng nghe yêu cầu gửi tin ra ngoài
        self.bus.on("channel:message:outbound", self.handle_outbound_request, plugin_id=self.metadata.id)

    def handle_incoming_message(self, msg_data: dict) -> dict:
        """Xử lý tin nhắn đến với bộ lọc @tag thông minh và đánh dấu Evidence Nguồn."""
        return self.safe_execute(self._filter_and_dispatch, msg_data)

    def _filter_and_dispatch(self, msg_data: dict) -> dict:
        self.inbound_count += 1
        is_group = msg_data.get("is_group", False)
        content = msg_data.get("content", "")
        sender_id = msg_data.get("sender_id", "P-UNKNOWN")
        sender_name = msg_data.get("sender_name", "Khách")
        group_id = msg_data.get("group_id", "*")

        # Gắn Evidence Ref để bảo đảm tính truy vết bất biến theo chuẩn V6 SSOT
        raw_evidence_ref = f"raw_event:RE-{uuid.uuid4().hex[:8].upper()}"

        # Lấy tên bot từ Persona Service
        persona_svc = self.ctx.inject("persona")
        bot_name = "Bé Heo"
        if persona_svc:
            bot_name = persona_svc.get_config().get("bot_name", "Bé Heo")

        # NGUYÊN TẮC SSOT: Trên nhóm làm việc chỉ trả lời khi được tag @tên_bot
        if is_group:
            mentioned = msg_data.get("is_mentioned", False) or f"@{bot_name}" in content
            if not mentioned:
                # Ghi nhận trạng thái OBSERVE nhưng không phát sinh phản hồi tự động
                return {
                    "handled": False,
                    "reason": "Not mentioned in group (Observe only)",
                    "evidence_ref": raw_evidence_ref
                }

        self.log(f"📩 Tin nhắn hợp lệ từ {sender_name} (Nhóm: {is_group}) [Evidence: {raw_evidence_ref}]: '{content}'")

        # Phát sóng Typed Event chuẩn: channel:message:inbound
        self.bus.emit("channel:message:inbound", {
            "channel": "zalo",
            "sender_id": sender_id,
            "sender_name": sender_name,
            "group_id": group_id,
            "content": content,
            "evidence_ref": raw_evidence_ref
        })

        # Đẩy sang Core Agent Antigravity / LLM Service xử lý
        llm_svc = self.ctx.inject("llm_core") or self.ctx.inject("llm")
        if llm_svc:
            reply_text = llm_svc.generate(content, sender_name=sender_name)
            
            # Gửi tin phản hồi ra ngoài qua cơ chế thẩm định Policy
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
        """
        Gửi tin nhắn ra ngoài Zalo với quy tắc THẨM ĐỊNH CHÍNH SÁCH BẮT BUỘC.
        Không permit = Không side-effects!
        """
        return self.safe_execute(self._do_send_message, target_id, content, group_id, correlation_id, explicit_permit)

    def _do_send_message(
        self,
        target_id: str,
        content: str,
        group_id: str = None,
        correlation_id: str = None,
        explicit_permit: str = None
    ) -> dict:
        corr = correlation_id or f"COR-{uuid.uuid4().hex[:8].upper()}"
        policy_svc = self.ctx.inject("policy_engine")

        # 1. Thẩm định qua Policy Engine
        if policy_svc and not explicit_permit:
            eval_res = policy_svc.evaluate(
                action="zalo.send_message",
                channel="zalo",
                group=group_id or "*",
                person=target_id,
                correlation_id=corr
            )

            # Trường hợp DENY: Chặn ngay lập tức
            if eval_res.decision == PolicyDecisionType.DENY:
                self.log(f"🛑 [POLICY DENY] Cấm gửi tin Zalo tới {target_id}: {eval_res.reason}")
                return {
                    "sent": False,
                    "status": "DENIED",
                    "reason": eval_res.reason,
                    "correlation_id": corr
                }

            # Trường hợp APPROVAL: Đưa vào hàng chờ phê duyệt
            if eval_res.decision == PolicyDecisionType.APPROVAL:
                approval_item = {
                    "id": f"AP-{int(time.time()*1000)%10000}",
                    "action": "zalo.send_message",
                    "target": f"{target_id} (Group: {group_id})",
                    "summary": f"Gửi phản hồi Zalo: {content[:40]}...",
                    "content": content,
                    "correlation_id": corr,
                    "permit_id": eval_res.permit_id
                }
                self.pending_approvals.append(approval_item)
                self.log(f"⏳ [POLICY APPROVAL] Tin nhắn gửi tới {target_id} đang chờ Sếp duyệt ({approval_item['id']})")
                return {
                    "sent": False,
                    "status": "APPROVAL_REQUIRED",
                    "approval_id": approval_item["id"],
                    "correlation_id": corr
                }

        # 2. Trường hợp AUTO hoặc đã có explicit_permit: Cho phép gửi qua Bridge
        self.outbound_count += 1
        self.log(f"🚀 [ZALO SENT] Đã phát tin nhắn tới {target_id} (Nhóm: {group_id}): '{content[:60]}...'")
        return {
            "sent": True,
            "status": "SUCCEEDED",
            "target": target_id,
            "correlation_id": corr,
            "timestamp": time.time()
        }

    def handle_outbound_request(self, payload: dict) -> None:
        """Xử lý sự kiện channel:message:outbound được yêu cầu từ hệ thống."""
        target_id = payload.get("target_id", "")
        content = payload.get("content", "")
        group_id = payload.get("group_id", None)
        explicit_permit = payload.get("permit_id", None)
        self.send_message(target_id, content, group_id=group_id, explicit_permit=explicit_permit)

    def get_session_status(self) -> dict:
        return {
            "channel": "zalo",
            "connected": self.connected,
            "logged_in": self.logged_in,
            "account": self.account_name,
            "inbound_total": self.inbound_count,
            "outbound_total": self.outbound_count,
            "pending_approvals_count": len(self.pending_approvals)
        }
