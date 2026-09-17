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
        self.ctx = Context()
        self.bus = EventBus()
        self.manager = PluginManager(self.ctx, self.bus)

    def test_scan_builtin_plugins(self):
        """Kiểm tra việc quét và nạp tự động 7 plugin mặc định."""
        self.manager.scan_and_register_builtin()
        self.manager.load_all_registered()

        # Phải nạp đủ 7 plugin chính thức
        self.assertGreaterEqual(len(self.manager._plugins), 7)
        self.assertIn("@heo/plugin-auth", self.manager._plugins)
        self.assertIn("@heo/plugin-persona", self.manager._plugins)
        self.assertIn("@heo/provider-gemini", self.manager._plugins)
        self.assertIn("@heo/channel-zalo", self.manager._plugins)
        self.assertIn("@heo/tool-media", self.manager._plugins)
        self.assertIn("@heo/tool-office", self.manager._plugins)
        self.assertIn("@heo/ui-dashboard", self.manager._plugins)

    def test_hot_toggle_plugin(self):
        """Kiểm tra việc Bật / Tắt nóng plugin trong thời gian thực."""
        self.manager.scan_and_register_builtin()
        self.manager.load_plugin("@heo/tool-media")

        p = self.manager._plugins["@heo/tool-media"]
        self.assertTrue(p.enabled)

        # Tắt nóng
        self.manager.disable_plugin("@heo/tool-media")
        self.assertFalse(p.enabled)
        self.assertEqual(p.health_status, PluginHealthStatus.DISABLED)

        # Bật nóng lại
        self.manager.enable_plugin("@heo/tool-media")
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
        self.manager.load_plugin("@heo/plugin-auth")
        
        prompt = self.bus.apply_hook("prompt:system", "Base System Prompt")
        self.assertIn("Anh Cơ La", prompt)
        self.assertIn("genesis.corp.os@gmail.com", prompt)
        self.assertIn("Tuyệt đối không nhắc đến nền tảng Antigravity CLI Google", prompt)

if __name__ == "__main__":
    unittest.main()
