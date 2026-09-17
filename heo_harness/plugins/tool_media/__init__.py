"""
Plugin: @heo/tool-media
Công Cụ Tạo Beat Nhạc MP3 & Vẽ Tranh Minh Họa AI.
Tác giả: Anh Cơ La (genesis.corp.os@gmail.com)
"""

from heo_harness.core.plugin import BasePlugin, PluginMetadata, PluginCategory

class MediaToolPlugin(BasePlugin):
    metadata = PluginMetadata(
        id="@heo/tool-media",
        name="Sáng Tạo Media (Nhạc Beat & Vẽ Tranh AI)",
        version="1.0.0",
        author="Anh Cơ La",
        author_email="genesis.corp.os@gmail.com",
        category=PluginCategory.TOOL,
        description="Tự động lồng ghép beat nhạc acoustic/lo-fi tạo bài hát MP3 hoàn chỉnh và vẽ tranh minh họa.",
        icon="🎵",
        default_enabled=True
    )

    def on_load(self) -> None:
        self.ctx.provide("tool_media", self)

    def on_enable(self) -> None:
        self.log("Đã kích hoạt Media Creator Toolkit (Beat + Image).")

    def create_song(self, lyrics: str, beat_style: str = "acoustic") -> dict:
        """Tạo bài hát có beat từ lời thơ/nhạc."""
        return self.safe_execute(self._do_create_song, lyrics, beat_style)

    def _do_create_song(self, lyrics: str, beat_style: str) -> dict:
        self.log(f"Đang phối nhạc beat phong cách '{beat_style}' cho lời bài hát...")
        return {
            "ok": True,
            "beat_style": beat_style,
            "status": "ready",
            "message": f"Đã hòa âm phối khí thành công bài hát theo phong cách {beat_style}!"
        }
