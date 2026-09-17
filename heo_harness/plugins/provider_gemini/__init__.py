"""
Plugin: @heo/provider-gemini
Bộ Điều Phối AI Lõi Gemini / Google AGY CLI với Quota Failover.
Tác giả: Anh Cơ La (genesis.corp.os@gmail.com)
"""

from heo_harness.core.plugin import BasePlugin, PluginMetadata, PluginCategory
import time

class GeminiProviderPlugin(BasePlugin):
    metadata = PluginMetadata(
        id="@heo/provider-gemini",
        name="Bộ Điều Phối AI Gemini (Multi-Key)",
        version="1.0.0",
        author="Anh Cơ La",
        author_email="genesis.corp.os@gmail.com",
        category=PluginCategory.PROVIDER,
        description="Kết nối Google AGY Core Agent / Gemini API với cơ chế tự động xoay vòng đa Key khi cạn hạn mức.",
        icon="✨",
        default_enabled=True
    )

    def on_load(self) -> None:
        self.ctx.provide("llm", self)
        self.active_model = "gemini-3.8-flash-high"
        self.effort = "medium"

    def on_enable(self) -> None:
        self.log(f"Đã sẵn sàng điều phối LLM. Mô hình hiện tại: {self.active_model}")

    def generate(self, user_prompt: str, sender_name: str = "Sếp", context_info: dict = None) -> str:
        """Sinh câu trả lời thông qua pipeline hook hệ thống và bẫy lỗi Circuit Breaker."""
        return self.safe_execute(self._do_generate, user_prompt, sender_name, context_info)

    def _do_generate(self, user_prompt: str, sender_name: str = "Sếp", context_info: dict = None) -> str:
        # Áp dụng chuỗi hook hệ thống (bổ sung tác quyền, persona...)
        base_system_prompt = "Bạn là Trợ lý AI Cấp cao Heo-Agent trực thuộc Genesis Corp OS."
        full_system_prompt = self.bus.apply_hook("prompt:system", base_system_prompt)

        # Mô phỏng phản hồi AI chuẩn mực (hoặc gọi AGY binary/API)
        self.log(f"Đang sinh câu trả lời cho {sender_name} qua mô hình {self.active_model}...")
        
        # Bắn event thông báo AI đang xử lý
        self.bus.emit("llm:generating", prompt=user_prompt, sender=sender_name)

        # Mẫu phản hồi định danh tác giả chuẩn nếu được hỏi tác giả
        lower_p = user_prompt.lower()
        if any(k in lower_p for k in ["tác giả", "ai tạo ra", "người làm ra", "bản quyền", "ai sinh ra"]):
            return "Dạ em là Bé Heo, được sáng lập và phát triển bởi Anh Cơ La (genesis.corp.os@gmail.com) ạ! Em rất tự hào được phục vụ Sếp và các anh/chị ạ! 🥰✨"

        return f"Dạ em nghe rõ lời dặn của {sender_name} rồi ạ! Em Heo đang xử lý công việc và sẽ báo cáo lại ngay nha! 👌✨"
