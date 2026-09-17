"""
Plugin: @heo/channel-zalo
Cầu Nối Zalo 2 Chiều & Bộ Lọc Nhận Diện @Tag Nhóm Thông Minh.
Tác giả: Anh Cơ La (genesis.corp.os@gmail.com)
"""

from heo_harness.core.plugin import BasePlugin, PluginMetadata, PluginCategory

class ZaloChannelPlugin(BasePlugin):
    metadata = PluginMetadata(
        id="@heo/channel-zalo",
        name="Cầu Nối Zalo 2 Chiều (@Tag Filtering)",
        version="1.0.0",
        author="Anh Cơ La",
        author_email="genesis.corp.os@gmail.com",
        category=PluginCategory.CHANNEL,
        description="Kết nối tương tác Zalo thời gian thực, đăng nhập QR Code, chỉ phản hồi khi được @tag tên trên nhóm.",
        icon="📱",
        default_enabled=True
    )

    def on_load(self) -> None:
        self.ctx.provide("channel_zalo", self)
        self.connected = False
        self.logged_in = False
        self.user_id = ""

    def on_enable(self) -> None:
        self.log("Đã kích hoạt Zalo Channel Adapter. Sẵn sàng kết nối Bridge.")
        # Lắng nghe sự kiện tin nhắn đến từ Bridge
        self.bus.on("zalo:message_received", self.handle_incoming_message, plugin_id=self.metadata.id)

    def handle_incoming_message(self, msg_data: dict) -> dict:
        """Xử lý tin nhắn đến với bộ lọc @tag thông minh."""
        return self.safe_execute(self._filter_and_dispatch, msg_data)

    def _filter_and_dispatch(self, msg_data: dict) -> dict:
        is_group = msg_data.get("is_group", False)
        content = msg_data.get("content", "")
        sender_name = msg_data.get("sender_name", "Khách")

        # Lấy tên bot hiện tại từ Persona Service
        persona_svc = self.ctx.inject("persona")
        bot_name = "Bé Heo"
        if persona_svc:
            bot_name = persona_svc.get_config().get("bot_name", "Bé Heo")

        # NGUYÊN TẮC: Trên nhóm chỉ trả lời khi được tag @tên_bot
        if is_group:
            mentioned = msg_data.get("is_mentioned", False) or f"@{bot_name}" in content
            if not mentioned:
                # Không tag thì tuyệt đối im lặng
                return {"handled": False, "reason": "Not mentioned in group"}

        self.log(f"Tin nhắn hợp lệ từ {sender_name} (Nhóm: {is_group}): '{content}'")

        # Đẩy sang LLM Provider xử lý
        llm_svc = self.ctx.inject("llm")
        if llm_svc:
            reply = llm_svc.generate(content, sender_name=sender_name)
            return {"handled": True, "reply": reply}

        return {"handled": False, "reason": "No LLM service available"}
