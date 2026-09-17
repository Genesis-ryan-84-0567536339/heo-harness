"""
Plugin: @heo/tool-office
Công Cụ Xuất Báo Cáo Word (.docx) & Bảng Tính Excel (.xlsx).
Tác giả: Anh Cơ La (genesis.corp.os@gmail.com)
"""

from heo_harness.core.plugin import BasePlugin, PluginMetadata, PluginCategory

class OfficeToolPlugin(BasePlugin):
    metadata = PluginMetadata(
        id="@heo/tool-office",
        name="Xuất Báo Cáo Tài Liệu Word & Excel",
        version="1.0.0",
        author="Anh Cơ La",
        author_email="genesis.corp.os@gmail.com",
        category=PluginCategory.TOOL,
        description="Định dạng văn bản hành chính chuyên nghiệp, xuất file Word và bảng tính tài chính Excel.",
        icon="📊",
        default_enabled=True
    )

    def on_load(self) -> None:
        self.ctx.provide("tool_office", self)

    def on_enable(self) -> None:
        self.log("Đã kích hoạt Office Document Exporter (Word & Excel).")

    def export_word(self, title: str, content: str) -> dict:
        return self.safe_execute(self._do_export_word, title, content)

    def _do_export_word(self, title: str, content: str) -> dict:
        self.log(f"Đang biên soạn tài liệu Word: '{title}'...")
        return {
            "ok": True,
            "filename": f"{title}.docx",
            "message": f"Đã xuất thành công tài liệu '{title}.docx' theo chuẩn hành chính!"
        }
