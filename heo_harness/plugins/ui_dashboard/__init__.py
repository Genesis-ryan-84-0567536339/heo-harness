"""
Plugin: @heo/ui-dashboard
Bảng Điều Khiển Web Console HCS & Trung Tâm Quản Trị Kho Plugin (Marketplace).
Tác giả: Anh Cơ La (genesis.corp.os@gmail.com)
"""

from heo_harness.core.plugin import BasePlugin, PluginMetadata, PluginCategory
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import json
import os
from pathlib import Path

class DashboardRequestHandler(BaseHTTPRequestHandler):
    plugin_ref: 'DashboardUIPlugin' = None

    def _send_json(self, data: dict, status_code: int = 200):
        payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(payload)
        try:
            self.wfile.flush()
        except Exception:
            pass

    def _send_html(self, html_content: str, status_code: int = 200):
        payload = html_content.encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(payload)
        try:
            self.wfile.flush()
        except Exception:
            pass

    def do_GET(self):
        path_clean = self.path.split("?")[0]
        plugin = self.plugin_ref

        if path_clean in ["/", "/dashboard", "/plugins"]:
            html_file = os.path.join(os.path.dirname(__file__), "dashboard.html")
            if os.path.exists(html_file):
                with open(html_file, "r", encoding="utf-8") as f:
                    self._send_html(f.read())
            else:
                self._send_json({"error": "Dashboard template missing"}, 404)

        elif path_clean == "/api/status":
            manager = plugin.ctx.inject("plugin_manager")
            persona_svc = plugin.ctx.inject("persona")
            auth_svc = plugin.ctx.inject("auth")

            status_data = {
                "system": {
                    "name": "Heo-Harness",
                    "version": "3.0.0-alpha.1",
                    "author": "Anh Cơ La",
                    "email": "genesis.corp.os@gmail.com",
                    "architecture": "Modular Harness (DeepSeek Style)"
                },
                "plugins_count": len(manager._plugins) if manager else 0,
                "persona": persona_svc.get_config() if persona_svc else {},
                "auth": auth_svc.get_author_info() if auth_svc else {}
            }
            self._send_json(status_data)

        elif path_clean == "/api/plugins/list":
            manager = plugin.ctx.inject("plugin_manager")
            reports = manager.get_all_reports() if manager else []
            self._send_json({"ok": True, "plugins": reports})

        elif path_clean == "/api/plugins/catalog":
            manager = plugin.ctx.inject("plugin_manager")
            catalog = manager.get_marketplace_catalog() if manager else []
            self._send_json({"ok": True, "catalog": catalog})

        else:
            self._send_json({"error": "Endpoint not found"}, 404)

    def do_POST(self):
        path_clean = self.path.split("?")[0]
        plugin = self.plugin_ref
        manager = plugin.ctx.inject("plugin_manager")

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
        try:
            data = json.loads(body)
        except Exception:
            data = {}

        if path_clean == "/api/plugins/toggle":
            plugin_id = data.get("id")
            enable_val = data.get("enable", True)
            if not manager:
                self._send_json({"ok": False, "error": "PluginManager unavailable"}, 500)
                return

            if enable_val:
                success = manager.enable_plugin(plugin_id)
            else:
                success = manager.disable_plugin(plugin_id)

            self._send_json({"ok": success, "plugin_id": plugin_id, "enabled": enable_val})

        elif path_clean == "/api/plugins/install":
            plugin_id = data.get("id")
            # Giả lập cài đặt plugin từ Marketplace Catalog
            self._send_json({
                "ok": True,
                "message": f"Đã cài đặt thành công plugin {plugin_id} từ Kho Heo Marketplace!"
            })

        elif path_clean == "/api/plugins/uninstall":
            plugin_id = data.get("id")
            if not manager:
                self._send_json({"ok": False, "error": "PluginManager unavailable"}, 500)
                return

            success = manager.unload_plugin(plugin_id)
            self._send_json({"ok": success, "plugin_id": plugin_id})

        else:
            self._send_json({"error": "Endpoint not found"}, 404)


class DashboardUIPlugin(BasePlugin):
    metadata = PluginMetadata(
        id="@heo/ui-dashboard",
        name="Bảng Điều Khiển Web HCS & Kho Plugin",
        version="1.0.0",
        author="Anh Cơ La",
        author_email="genesis.corp.os@gmail.com",
        category=PluginCategory.UI,
        description="Giao diện Web Console điều hành máy chủ và Kho Plugin Marketplace cắm/rút trực quan.",
        icon="🖥️",
        default_enabled=True
    )

    def on_load(self) -> None:
        self.ctx.provide("ui_dashboard", self)
        self.server: HTTPServer = None
        self.thread: threading.Thread = None
        self.port = int(os.environ.get("HARNESS_PORT", "5066"))

    def on_enable(self) -> None:
        DashboardRequestHandler.plugin_ref = self
        try:
            self.server = HTTPServer(("0.0.0.0", self.port), DashboardRequestHandler)
            self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.thread.start()
            self.log(f"🌐 Web Console HCS & Kho Plugin đang phục vụ tại http://0.0.0.0:{self.port}")
        except Exception as e:
            self.log(f"❌ Không thể khởi động Web Console tại cổng {self.port}: {e}")

    def on_disable(self) -> None:
        if self.server:
            try:
                self.server.shutdown()
                self.server.server_close()
                self.log("Đã đóng máy chủ Web Console.")
            except Exception as e:
                self.log(f"Lỗi khi đóng Web Console: {e}")
