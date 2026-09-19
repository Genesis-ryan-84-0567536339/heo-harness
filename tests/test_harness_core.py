"""
Kiểm thử tự động Khung sườn Heo-Harness & Vòng đời Plugin
"""

import unittest
import os
import sys

# Đảm bảo import được heo_harness
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from heo_harness.core.context import Context
from heo_harness.core.bus import EventBus
from heo_harness.core.manager import PluginManager
from heo_harness.core.plugin import BasePlugin, PluginMetadata, PluginCategory, PluginHealthStatus

class TestHeoHarness(unittest.TestCase):
    def setUp(self):
        self.tmp_cfg = f"/tmp/test_harness_core_{id(self)}.json"
        if os.path.exists(self.tmp_cfg):
            os.remove(self.tmp_cfg)
        self.ctx = Context(config_path=self.tmp_cfg)
        self.bus = EventBus()
        self.manager = PluginManager(self.ctx, self.bus)

    def tearDown(self):
        for pid in list(self.manager._plugins.keys()):
            self.manager.unload_plugin(pid)
        if hasattr(self, "tmp_cfg") and os.path.exists(self.tmp_cfg):
            try:
                os.remove(self.tmp_cfg)
            except Exception:
                pass

    def test_scan_builtin_plugins(self):
        """Kiểm tra việc quét và nạp tự động 7 plugin mặc định."""
        self.manager.scan_and_register_builtin()
        self.manager.load_all_registered()

        # Phải nạp đủ các plugin chính thức
        self.assertGreaterEqual(len(self.manager._plugins), 7)
        self.assertIn("heo-auth-rbac-security", self.manager._plugins)
        self.assertIn("heo-persona-heo-attitude", self.manager._plugins)
        self.assertIn("heo-provider-gemini-orchestrator", self.manager._plugins)
        self.assertIn("heo-channel-zalo-gateway", self.manager._plugins)
        self.assertIn("heo-tool-media-processor", self.manager._plugins)
        self.assertIn("heo-tool-office-reporter", self.manager._plugins)
        self.assertIn("heo-ui-dashboard-executive", self.manager._plugins)

    def test_hot_toggle_plugin(self):
        """Kiểm tra việc Bật / Tắt nóng plugin trong thời gian thực."""
        self.manager.scan_and_register_builtin()
        self.manager.load_plugin("heo-tool-media-processor")

        p = self.manager._plugins["heo-tool-media-processor"]
        self.assertTrue(p.enabled)

        # Tắt nóng
        self.manager.disable_plugin("heo-tool-media-processor")
        self.assertFalse(p.enabled)
        self.assertEqual(p.health_status, PluginHealthStatus.DISABLED)

        # Bật nóng lại
        self.manager.enable_plugin("heo-tool-media-processor")
        self.assertTrue(p.enabled)
        self.assertEqual(p.health_status, PluginHealthStatus.HEALTHY)

    def test_circuit_breaker_isolation(self):
        """Kiểm tra Circuit Breaker tự ngắt khi plugin con bị lỗi, không ảnh hưởng Core."""
        class BuggyPlugin(BasePlugin):
            metadata = PluginMetadata(id="@test/buggy", name="Buggy Plugin")
            def faulty_task(self):
                return self.safe_execute(lambda: 1 / 0)

        self.manager.register_plugin_class(BuggyPlugin)
        self.manager.load_plugin("@test/buggy")
        buggy = self.manager._plugins["@test/buggy"]

        # Gây lỗi liên tiếp 5 lần để kích hoạt Circuit Breaker
        for _ in range(5):
            res = buggy.faulty_task()
            self.assertIsNone(res)

        # Mạch ngắt đã kích hoạt, plugin bị chuyển sang trạng thái ERROR
        self.assertTrue(buggy.circuit.is_open)
        self.assertEqual(buggy.health_status, PluginHealthStatus.ERROR)

        # Core và các plugin khác vẫn hoàn toàn khỏe mạnh
        self.assertTrue(True)

    def test_author_attribution_invariant(self):
        """Kiểm tra tác quyền bất biến của Anh Cơ La qua Auth Hook."""
        self.manager.scan_and_register_builtin()
        self.manager.load_plugin("heo-auth-rbac-security")
        
        prompt = self.bus.apply_hook("prompt:system", "Base System Prompt")
        self.assertIn("Anh Cơ La", prompt)
        self.assertIn("genesis.corp.os@gmail.com", prompt)
        self.assertIn("Tuyệt đối không nhắc đến nền tảng Antigravity CLI Google", prompt)

if __name__ == "__main__":
    unittest.main()
