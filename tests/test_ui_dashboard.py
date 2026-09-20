"""
Unit Tests cho Plugin @heo/ui-dashboard (Giao diện V6 & API Add-in Hub)
Tác giả: Anh Cơ La (genesis.corp.os@gmail.com)
"""

import unittest
import urllib.request
import json
import os
import time
import shutil

from heo_harness.core.context import Context
from heo_harness.core.bus import EventBus
from heo_harness.core.manager import PluginManager
from heo_harness.core.store import HeoDataStore

class TestUIDashboardPlugin(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Thiết lập port test riêng biệt để tránh xung đột
        cls.test_port = 5099
        os.environ["HARNESS_PORT"] = str(cls.test_port)

        test_config = "/tmp/test_harness_ui.json"
        if os.path.exists(test_config):
            os.remove(test_config)

        test_data_dir = "/tmp/test_heo_data"
        if os.path.exists(test_data_dir):
            shutil.rmtree(test_data_dir, ignore_errors=True)

        cls.ctx = Context(config_path=test_config)
        cls.bus = EventBus()
        cls.manager = PluginManager(cls.ctx, cls.bus)
        cls.store = HeoDataStore(data_dir=test_data_dir)
        cls.ctx.provide("plugin_manager", cls.manager)
        cls.ctx.provide("data_store", cls.store)

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
            self.assertIn("HEO OS", content)
            self.assertIn("Executive Intelligence", content)
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

    def test_07_group_and_person_persona_and_notes_api(self):
        """Kiểm tra cập nhật persona và ghi chú riêng cho Nhóm và Nhân sự."""
        # Khởi tạo Group và Person mẫu
        g = self.store.add_group(name="Ban Điều Hành Phoenix", purpose="Điều hành chiến lược")
        p = self.store.add_person(name="Đối Tác Alpha", role="Tư vấn bên ngoài")

        # 1. Cập nhật Group
        grp_payload = json.dumps({
            "id": g["id"],
            "persona_style": "professional",
            "notes": "Nhóm cốt lõi điều hành, chỉ báo cáo số liệu chính xác."
        }).encode("utf-8")
        req = urllib.request.Request(self._get_url("/api/groups/update"), data=grp_payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=3) as res:
            data = json.loads(res.read().decode("utf-8"))
            self.assertTrue(data.get("ok"))
            self.assertEqual(data["group"]["persona_style"], "professional")
            self.assertEqual(data["group"]["notes"], "Nhóm cốt lõi điều hành, chỉ báo cáo số liệu chính xác.")

        # 2. Cập nhật Person
        person_payload = json.dumps({
            "id": p["id"],
            "persona_style": "cautious",
            "notes": "Đối tác cung cấp dịch vụ bên ngoài, cần cẩn trọng bảo mật."
        }).encode("utf-8")
        req = urllib.request.Request(self._get_url("/api/people/update"), data=person_payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=3) as res:
            data = json.loads(res.read().decode("utf-8"))
            self.assertTrue(data.get("ok"))
            self.assertEqual(data["person"]["persona_style"], "cautious")
            self.assertEqual(data["person"]["notes"], "Đối tác cung cấp dịch vụ bên ngoài, cần cẩn trọng bảo mật.")

        # 3. Cập nhật Global Notes
        cfg_payload = json.dumps({
            "bot_global_notes": "Tuyệt đối không tiết lộ tài chính công ty."
        }).encode("utf-8")
        req = urllib.request.Request(self._get_url("/api/config"), data=cfg_payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=3) as res:
            data = json.loads(res.read().decode("utf-8"))
            self.assertTrue(data.get("ok"))

    def test_08_chat_with_context_and_notes(self):
        """Kiểm tra Chat API nhận diện ngữ cảnh Group/Person và phản hồi đúng phong thái."""
        groups = self.store.get_groups()
        target_gid = groups[0]["id"] if groups else "G-001"

        chat_payload = json.dumps({
            "message": "Chào em Bé Heo",
            "group_id": target_gid,
            "person_id": "*"
        }).encode("utf-8")
        req = urllib.request.Request(self._get_url("/api/chat"), data=chat_payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=3) as res:
            data = json.loads(res.read().decode("utf-8"))
            self.assertTrue(data.get("ok"))
            self.assertIn("reply", data)
            self.assertEqual(data.get("persona"), "professional")
            self.assertEqual(data.get("target_group"), "Ban Điều Hành Phoenix")
            self.assertIn("Executive", data.get("reply"))

if __name__ == "__main__":
    unittest.main()
