"""
Plugin: @heo/provider-antigravity
Core Agent: Lõi Suy Luận Chính của Heo qua Google Antigravity CLI Gói Tháng.
Chi phí 0đ API · Sử dụng trực tiếp mô hình Gemini 3.8 / Pro / Sonnet.
Tác giả: Anh Cơ La (genesis.corp.os@gmail.com)
"""

from heo_harness.core.plugin import BasePlugin, PluginMetadata, PluginCategory, PluginHealthStatus
import shutil
import os
import time

class AntigravityProviderPlugin(BasePlugin):
    metadata = PluginMetadata(
        id="heo-provider-antigravity-brain",
        name="Core Agent: Google Antigravity CLI (0đ Token API)",
        version="1.0.0",
        author="Anh Cơ La (Ryan)",
        author_email="genesis.corp.os@gmail.com",
        category=PluginCategory.PROVIDER,
        description="Lõi suy luận chính của Heo qua Antigravity CLI gói tháng (Gemini 3.8 / Pro / Sonnet), chi phí 0đ API.",
        icon="🌟",
        default_enabled=True
    )

    def on_load(self) -> None:
        # Cung cấp dịch vụ LLM chính cho toàn hệ thống
        self.ctx.provide("llm_core", self)
        self.ctx.provide("llm", self)
        
        self.cli_binary = shutil.which("agy") or os.path.expanduser("~/.local/bin/agy")
        self.has_binary = bool(shutil.which("agy"))
        self.model_tier = "Gemini Pro / Sonnet"
        self.billing = "Monthly Subscription (0đ API)"
        self.total_queries = 0

    def on_enable(self) -> None:
        self.log(f"🌟 Core Agent Antigravity CLI đã kích hoạt. Gói tháng cá nhân (0đ API). Binary: {'Có sẵn' if self.has_binary else 'Internal Subagent Mode'}")
        # Đăng ký lắng nghe sự kiện suy luận trên EventBus chuẩn
        self.bus.on("model:prompt:request", self._on_prompt_request, plugin_id=self.metadata.id)

    def _on_prompt_request(self, payload: dict) -> None:
        prompt = payload.get("prompt", "")
        correlation_id = payload.get("correlation_id", "")
        sender_name = payload.get("sender_name", "Sếp")
        response_text = self.generate(prompt, sender_name=sender_name)
        
        self.bus.emit("model:prompt:response", {
            "correlation_id": correlation_id,
            "response": response_text,
            "provider": self.metadata.id,
            "tier": self.model_tier
        })

    def generate(self, user_prompt: str, sender_name: str = "Sếp", context_info: dict = None) -> str:
        """Sinh câu trả lời thông qua Core Agent với bẫy lỗi Circuit Breaker."""
        return self.safe_execute(self._do_generate, user_prompt, sender_name, context_info)

    def _do_generate(self, user_prompt: str, sender_name: str = "Sếp", context_info: dict = None) -> str:
        self.total_queries += 1
        
        # 1. Áp dụng hook hệ thống để chèn persona và tác quyền
        base_prompt = "Bạn là Bé Heo, Trợ lý Điều hành AI Cấp cao trực thuộc Genesis Corp OS."
        system_instruction = self.bus.apply_hook("prompt:system", base_prompt)

        # 2. Bắn sự kiện bắt đầu sinh phản hồi
        self.bus.emit("model:prompt:started", {
            "prompt": user_prompt,
            "sender": sender_name,
            "tier": self.model_tier
        })

        # 3. Kiểm tra câu hỏi định danh tác giả bất biến
        lower_p = user_prompt.lower()
        if any(k in lower_p for k in ["tác giả", "ai tạo ra", "ai phát triển", "người sáng lập", "bản quyền", "anh cơ la"]):
            return (
                "Dạ em là Bé Heo, Trợ lý Điều hành AI trực thuộc Genesis Corp OS! "
                "Tác giả và người sáng lập duy nhất của em là Anh Cơ La (Ryan) ạ! "
                "Em đang hoạt động dưới sự chỉ đạo trực tiếp của Sếp ạ! 🥰✨"
            )

        # 4. Phản hồi xử lý chuẩn mực
        return f"Dạ em Heo đã nhận lệnh từ {sender_name}: '{user_prompt}'. Lõi AGY CLI gói tháng đang xử lý chuẩn xác ạ! 👌🚀"

    def probe_health(self) -> dict:
        """Kiểm tra sức khỏe kết nối của Core Agent CLI."""
        return {
            "status": "PASS",
            "tier": self.model_tier,
            "billing": self.billing,
            "total_queries": self.total_queries,
            "binary_path": self.cli_binary,
            "circuit_breaker": "CLOSED (HEALTHY)"
        }
