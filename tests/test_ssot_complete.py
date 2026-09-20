"""
Kiểm thử Tích Hợp Toàn Diện (End-to-End SSOT Verification)
Xác thực hoàn chỉnh 4 tầng kiến trúc: Chassis Core, Core Agent Antigravity, Policy Engine, Kênh Zalo và V6 UI.
Tác giả: Anh Cơ La (genesis.corp.os@gmail.com)
"""

import unittest
import os
import time

from heo_harness.core.context import Context
from heo_harness.core.bus import EventBus
from heo_harness.core.manager import PluginManager
from heo_harness.core.policy import PolicyEngine, PolicyDecisionType

class TestSSOTCompleteArchitecture(unittest.TestCase):
    def setUp(self):
        self.test_cfg = f"/tmp/test_ssot_{id(self)}.json"
        if os.path.exists(self.test_cfg):
            os.remove(self.test_cfg)

        self.ctx = Context(config_path=self.test_cfg)
        self.bus = EventBus()
        self.policy_engine = PolicyEngine()
        self.manager = PluginManager(self.ctx, self.bus)

        self.ctx.provide("plugin_manager", self.manager)
        self.ctx.provide("policy_engine", self.policy_engine)
        self.ctx.provide("event_bus", self.bus)

        # Quét và nạp toàn bộ official plugins
        self.manager.scan_and_register_builtin()
        self.manager.load_all_registered()

    def tearDown(self):
        for pid in list(self.manager._plugins.keys()):
            self.manager.unload_plugin(pid)
        if os.path.exists(self.test_cfg):
            os.remove(self.test_cfg)

    def test_01_all_official_plugins_registered(self):
        """Kiểm tra có đầy đủ cả các official plugins chuẩn SSOT."""
        self.assertIn("heo-auth-rbac-security", self.manager._plugins)
        self.assertIn("heo-persona-heo-attitude", self.manager._plugins)
        self.assertIn("heo-provider-antigravity-brain", self.manager._plugins)
        self.assertIn("heo-provider-deepseek-reasoning", self.manager._plugins)
        self.assertIn("heo-channel-zalo-gateway", self.manager._plugins)
        self.assertIn("heo-tool-media-processor", self.manager._plugins)
        self.assertIn("heo-tool-office-reporter", self.manager._plugins)
        self.assertIn("heo-ui-dashboard-executive", self.manager._plugins)

        # DeepSeek mặc định tắt theo SSOT
        deepseek = self.manager._plugins["heo-provider-deepseek-reasoning"]
        self.assertFalse(deepseek.enabled)

        # Antigravity Core mặc định bật
        antigravity = self.manager._plugins["heo-provider-antigravity-brain"]
        self.assertTrue(antigravity.enabled)

    def test_02_antigravity_core_provider(self):
        """Kiểm tra Core Agent Antigravity CLI gói tháng."""
        agy = self.manager._plugins["heo-provider-antigravity-brain"]
        probe = agy.probe_health()
        self.assertEqual(probe["status"], "PASS")
        self.assertEqual(probe["circuit_breaker"], "CLOSED (HEALTHY)")

        # Kiểm tra tác quyền bất biến của Anh Cơ La
        reply_author = agy.generate("Tác giả tạo ra em là ai?")
        self.assertIn("Anh Cơ La (Ryan)", reply_author)
        self.assertEqual(agy.metadata.author_email, "genesis.corp.os@gmail.com")

        # Kiểm tra câu trả lời thông thường
        reply_work = agy.generate("Chuẩn bị báo cáo tài chính giúp anh", sender_name="Sếp Cơ La")
        self.assertIn("Sếp Cơ La", reply_work)
        self.assertIn("Lõi AGY CLI gói tháng", reply_work)

    def test_03_policy_precedence_engine(self):
        """Kiểm tra trọng tài quyền lực Policy Engine theo độ sâu ưu tiên."""
        # 1. PERSON DENY thắng mọi scope: Gửi tin tới P-018
        res_deny = self.policy_engine.evaluate(
            action="zalo.send_message",
            person="P-018",
            channel="zalo"
        )
        self.assertEqual(res_deny.decision, PolicyDecisionType.DENY)
        self.assertIsNone(res_deny.permit_id)
        self.assertEqual(res_deny.depth, 3)

        # 2. GROUP APPROVAL: Gửi tin tới nhóm Sales Ops (G-002)
        res_group = self.policy_engine.evaluate(
            action="zalo.send_message",
            group="G-002",
            person="P-022"
        )
        self.assertEqual(res_group.decision, PolicyDecisionType.APPROVAL)
        self.assertIsNotNone(res_group.permit_id)
        self.assertEqual(res_group.depth, 2)

        # 3. ACTION AUTO: Tạo reminder nội bộ
        res_auto = self.policy_engine.evaluate(
            action="scheduler.create"
        )
        self.assertEqual(res_auto.decision, PolicyDecisionType.AUTO)
        self.assertIsNotNone(res_auto.permit_id)

    def test_04_channel_zalo_policy_gate(self):
        """Kiểm tra Kênh Zalo từ chối gửi tin nếu bị Policy DENY."""
        zalo = self.manager._plugins["heo-channel-zalo-gateway"]
        
        # Thử gửi tin tới P-018 (đối tượng rủi ro bị cấm)
        res = zalo.send_message(target_id="P-018", content="Xin chào bạn!")
        self.assertFalse(res["sent"])
        self.assertEqual(res["status"], "DENIED")
        self.assertIn("PR-PERSON-DENY-018", res["reason"])

    def test_05_channel_zalo_group_tag_filtering(self):
        """Kiểm tra bộ lọc @tag thông minh của Zalo trên nhóm làm việc."""
        zalo = self.manager._plugins["heo-channel-zalo-gateway"]

        # 1. Tin nhắn trong nhóm không tag bot -> Im lặng hoàn toàn (Observe only)
        res_untagged = zalo.handle_incoming_message({
            "is_group": True,
            "sender_name": "Nhân viên A",
            "content": "Mọi người nhớ nộp báo cáo lúc 5h chiều nhé",
            "is_mentioned": False
        })
        self.assertFalse(res_untagged["handled"])
        self.assertIn("Observe only", res_untagged["reason"])

        # 2. Tin nhắn trong nhóm CÓ tag @Bé Heo -> Core Agent xử lý ngay
        res_tagged = zalo.handle_incoming_message({
            "is_group": True,
            "sender_name": "Sếp Cơ La",
            "content": "@Bé Heo hôm nay tình hình dự án thế nào em?",
            "is_mentioned": True
        })
        self.assertTrue(res_tagged["handled"])
        self.assertIn("Sếp Cơ La", res_tagged["reply"])
        self.assertTrue(res_tagged["evidence_ref"].startswith("raw_event:RE-"))

    def test_06_optional_deepseek_toggle(self):
        """Kiểm tra bật/tắt Provider dự phòng DeepSeek mà không ảnh hưởng Core."""
        dsh_id = "heo-provider-deepseek-reasoning"
        
        # Bật DeepSeek
        self.assertTrue(self.manager.enable_plugin(dsh_id))
        dsh_plugin = self.manager._plugins[dsh_id]
        self.assertTrue(dsh_plugin.enabled)
        reply = dsh_plugin.generate("Phân tích đoạn mã này")
        self.assertIn("[DeepSeek V3 Fallback]", reply)

        # Tắt DeepSeek
        self.assertTrue(self.manager.disable_plugin(dsh_id))
        self.assertFalse(dsh_plugin.enabled)

        # Core Agent Antigravity vẫn hoạt động 100%
        agy = self.manager._plugins["heo-provider-antigravity-brain"]
        self.assertTrue(agy.enabled)

if __name__ == "__main__":
    unittest.main()
