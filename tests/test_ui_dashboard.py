"""
Unit Tests cho Plugin @heo/ui-dashboard (Giao diện V6 & API Add-in Hub)
Tác giả: Anh Cơ La (genesis.corp.os@gmail.com)
"""

import unittest
import urllib.request
import json
import os
import time

from heo_harness.core.context import Context
from heo_harness.core.bus import EventBus
from heo_harness.core.manager import PluginManager

class TestUIDashboardPlugin(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Thiết lập port test riêng biệt để tránh xung đột
        cls.test_port = 5099
        os.environ["HARNESS_PORT"] = str(cls.test_port)

        test_config = "/tmp/test_harness_ui.json"
        if os.path.exists(test_config):
            os.remove(test_config)

        cls.ctx = Context(config_path=test_config)
        cls.bus = EventBus()
        cls.manager = PluginManager(cls.ctx, cls.bus)
        cls.ctx.provide("plugin_manager", cls.manager)

        cls.manager.scan_and_register_builtin()
        cls.manager.load_all_registered()
        cls.manager.enable_plugin("heo-ui-dashboard-executive")
        time.sleep(0.1) # Chờ HTTP server sẵn sàng

    @classmethod
    def tearDownClass(cls):
        ui_plugin = cls.manager._plugins.get("heo-ui-dashboard-executive")
        if ui_plugin:
            cls.manager.unload_plugin("heo-ui-dashboard-executive")

    def _get_url(self, path: str):
        return f"http://127.0.0.1:{self.test_port}{path}"

    def test_01_index_html_rendered(self):
        """Kiểm tra máy chủ trả về giao diện HTML V6 Executive UI."""
        req = urllib.request.Request(self._get_url("/"))
        with urllib.request.urlopen(req, timeout=3) as res:
            self.assertEqual(res.status, 200)
            content = res.read().decode("utf-8")
            self.assertIn("HEO OS / EXECUTIVE", content)
            self.assertIn("Tools & Add-ins Hub", content)
            self.assertIn("Anh Cơ La (Ryan)", content)

    def test_02_system_status_api(self):
        """Kiểm tra API /api/system/status trả về dữ liệu chuẩn V6."""
        req = urllib.request.Request(self._get_url("/api/system/status"))
        with urllib.request.urlopen(req, timeout=3) as res:
            self.assertEqual(res.status, 200)
            data = json.loads(res.read().decode("utf-8"))
            self.assertIn("system", data)
            self.assertEqual(data["system"]["readiness"], "READY_END_TO_END")
            self.assertEqual(data["system"]["author"], "Anh Cơ La (Ryan)")

    def test_03_plugins_list_api(self):
        """Kiểm tra API /api/plugins/list trả về danh sách plugin và Circuit Breaker."""
        req = urllib.request.Request(self._get_url("/api/plugins/list"))
        with urllib.request.urlopen(req, timeout=3) as res:
            self.assertEqual(res.status, 200)
            data = json.loads(res.read().decode("utf-8"))
            self.assertTrue(data.get("ok"))
            plugins = data.get("plugins", [])
            self.assertGreaterEqual(len(plugins), 5)
            # Kiểm tra một plugin có cấu trúc circuit_breaker chuẩn
            first = plugins[0]
            self.assertIn("circuit_breaker", first)
            self.assertIn("status", first["circuit_breaker"])

    def test_04_plugins_catalog_api(self):
        """Kiểm tra API /api/plugins/catalog trả về danh mục Marketplace."""
        req = urllib.request.Request(self._get_url("/api/plugins/catalog"))
        with urllib.request.urlopen(req, timeout=3) as res:
            self.assertEqual(res.status, 200)
            data = json.loads(res.read().decode("utf-8"))
            self.assertTrue(data.get("ok"))
            catalog = data.get("catalog", [])
            self.assertGreaterEqual(len(catalog), 3)

    def test_05_plugins_toggle_api(self):
        """Kiểm tra toggle Bật / Tắt plugin qua API POST."""
        target_id = "heo-tool-media-processor"
        
        # 1. Tắt plugin
        payload = json.dumps({"id": target_id, "enable": False}).encode("utf-8")
        req = urllib.request.Request(self._get_url("/api/plugins/toggle"), data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=3) as res:
            data = json.loads(res.read().decode("utf-8"))
            self.assertTrue(data.get("ok"))
            self.assertFalse(data.get("enabled"))
            self.assertFalse(self.manager._plugins[target_id].enabled)

        # 2. Bật lại plugin
        payload = json.dumps({"id": target_id, "enable": True}).encode("utf-8")
        req = urllib.request.Request(self._get_url("/api/plugins/toggle"), data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=3) as res:
            data = json.loads(res.read().decode("utf-8"))
            self.assertTrue(data.get("ok"))
            self.assertTrue(data.get("enabled"))
            self.assertTrue(self.manager._plugins[target_id].enabled)

    def test_06_policy_simulator_api(self):
        """Kiểm tra Policy Precedence Simulator trả về kết quả thẩm định quyền."""
        # Trường hợp DENY: Person P-018 gửi tin nhắn
        payload = json.dumps({"group": "G-001", "person": "P-018", "action": "zalo.send_message"}).encode("utf-8")
        req = urllib.request.Request(self._get_url("/api/policy/simulate"), data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=3) as res:
            data = json.loads(res.read().decode("utf-8"))
            self.assertEqual(data.get("decision"), "DENY")
            self.assertIsNone(data.get("permit_id"))

        # Trường hợp AUTO: Scheduler create nội bộ
        payload = json.dumps({"group": "G-001", "person": "P-022", "action": "scheduler.create"}).encode("utf-8")
        req = urllib.request.Request(self._get_url("/api/policy/simulate"), data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=3) as res:
            data = json.loads(res.read().decode("utf-8"))
            self.assertEqual(data.get("decision"), "AUTO")
            self.assertIsNotNone(data.get("permit_id"))

if __name__ == "__main__":
    unittest.main()
