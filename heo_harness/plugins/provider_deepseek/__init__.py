"""
Plugin: @heo/provider-deepseek
Mô Hình AI Dự Phòng: DeepSeek V3 / R1 qua API.
Mặc định TẮT. Chỉ kích hoạt khi Sếp bật để chạy batch tác vụ phụ hoặc phân tích mã nguồn.
Tác giả: Anh Cơ La (genesis.corp.os@gmail.com)
"""

from heo_harness.core.plugin import BasePlugin, PluginMetadata, PluginCategory, PluginHealthStatus
import os

class DeepSeekProviderPlugin(BasePlugin):
    metadata = PluginMetadata(
        id="@heo/provider-deepseek",
        name="Secondary Provider: DeepSeek V3 / R1 (Optional)",
        version="1.0.0",
        author="Anh Cơ La (Ryan)",
        author_email="genesis.corp.os@gmail.com",
        category=PluginCategory.PROVIDER,
        description="Mô hình dự phòng giá rẻ qua API DeepSeek khi cần phân tích mã nguồn hoặc chạy batch tác vụ phụ.",
        icon="⚡",
        default_enabled=False  # Mặc định TẮT theo SSOT: Không ép buộc Sếp dùng DeepSeek!
    )

    def on_load(self) -> None:
        self.ctx.provide("llm_deepseek", self)
        self.api_key = os.environ.get("DEEPSEEK_API_KEY", "")
        self.model_name = "deepseek-chat" # V3 / R1
        self.total_queries = 0

    def on_enable(self) -> None:
        self.log(f"⚡ DeepSeek Provider đã được BẬT. API Key: {'Đã cấu hình' if self.api_key else 'Chưa có (Chế độ mô phỏng)'}")

    def on_disable(self) -> None:
        self.log("⚡ DeepSeek Provider đã được TẮT. Core Agent Antigravity CLI vẫn vận hành 100%.")

    def generate(self, user_prompt: str, sender_name: str = "Sếp", context_info: dict = None) -> str:
        return self.safe_execute(self._do_generate, user_prompt, sender_name, context_info)

    def _do_generate(self, user_prompt: str, sender_name: str = "Sếp", context_info: dict = None) -> str:
        self.total_queries += 1
        self.log(f"DeepSeek V3 đang xử lý prompt từ {sender_name}...")
        return f"[DeepSeek V3 Fallback] Phản hồi phân tích cho {sender_name}: '{user_prompt}'"
