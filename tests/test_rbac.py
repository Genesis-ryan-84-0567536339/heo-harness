"""
Tests for SPEC-36: Phân quyền RBAC Console phân tầng (5 cấp độ)
Tuân thủ chuẩn SSOT Mục H2 Spec LOCKED v2.2:
- Owner: thấy toàn cảnh
- Manager: thấy team
- Operator: thấy hàng đợi việc
- Agent nhân viên: chỉ thấy khách mình được phân
- Auditor: xem log, không hành động
"""

import unittest
import tempfile
import shutil
import json
import urllib.request
import urllib.error
import os
import time

from heo_harness.core.rbac import (
    ROLE_OWNER, ROLE_MANAGER, ROLE_OPERATOR, ROLE_AGENT, ROLE_AUDITOR,
    ALL_ROLES, normalize_role, has_permission, can_role_act,
    get_role_view_policy, get_canonical_profiles
)
from heo_harness.core.store import HeoDataStore
from heo_harness.core.context import Context
from heo_harness.core.bus import EventBus
from heo_harness.core.manager import PluginManager


class TestRBACCore(unittest.TestCase):
    def test_canonical_roles_defined(self):
        self.assertEqual(len(ALL_ROLES), 5)
        self.assertEqual(set(ALL_ROLES), {"owner", "manager", "operator", "agent", "auditor"})

    def test_normalize_role(self):
        self.assertEqual(normalize_role("Chủ Nhân Tối Cao (Owner)"), ROLE_OWNER)
        self.assertEqual(normalize_role("full_root_rbac"), ROLE_OWNER)
        self.assertEqual(normalize_role("Phó Ban Điều Hành (Co-Executive)"), ROLE_MANAGER)
        self.assertEqual(normalize_role("Trưởng Phòng"), ROLE_MANAGER)
        self.assertEqual(normalize_role("Điều Phối Tác Nghiệp (Operator)"), ROLE_OPERATOR)
        self.assertEqual(normalize_role("Nhân Viên Kinh Doanh"), ROLE_AGENT)
        self.assertEqual(normalize_role("Kiểm Toán & Thanh Tra (Auditor)"), ROLE_AUDITOR)
        self.assertEqual(normalize_role("read_only"), ROLE_AUDITOR)

    def test_permissions_matrix_owner(self):
        # Owner có toàn quyền
        self.assertTrue(has_permission(ROLE_OWNER, "system.config.write"))
        self.assertTrue(has_permission(ROLE_OWNER, "system.terminal.execute"))
        self.assertTrue(has_permission(ROLE_OWNER, "people_review.view"))
        self.assertTrue(has_permission(ROLE_OWNER, "people_review.coaching"))
        self.assertTrue(has_permission(ROLE_OWNER, "commercial.action"))
        self.assertTrue(can_role_act(ROLE_OWNER))

    def test_permissions_matrix_manager(self):
        # Manager: Thấy team, coaching, nhưng không có quyền Terminal / System PIN
        self.assertTrue(has_permission(ROLE_MANAGER, "people_review.view"))
        self.assertTrue(has_permission(ROLE_MANAGER, "people_review.coaching"))
        self.assertTrue(has_permission(ROLE_MANAGER, "commercial.action"))
        self.assertFalse(has_permission(ROLE_MANAGER, "system.config.write"))
        self.assertFalse(has_permission(ROLE_MANAGER, "system.terminal.execute"))
        self.assertTrue(can_role_act(ROLE_MANAGER))

    def test_permissions_matrix_operator(self):
        # Operator: Thấy hàng đợi việc, khoá chặt đánh giá nhân sự (Mục H2)
        self.assertTrue(has_permission(ROLE_OPERATOR, "commercial.view"))
        self.assertTrue(has_permission(ROLE_OPERATOR, "commercial.action"))
        self.assertTrue(has_permission(ROLE_OPERATOR, "inbox.view_all"))
        self.assertFalse(has_permission(ROLE_OPERATOR, "people_review.view"))
        self.assertFalse(has_permission(ROLE_OPERATOR, "people_review.coaching"))
        self.assertFalse(has_permission(ROLE_OPERATOR, "system.config.write"))
        self.assertTrue(can_role_act(ROLE_OPERATOR))

    def test_permissions_matrix_agent(self):
        # Agent: Chỉ thấy khách phân công, khoá đánh giá nhân sự & cấu hình
        self.assertTrue(has_permission(ROLE_AGENT, "inbox.view_assigned"))
        self.assertFalse(has_permission(ROLE_AGENT, "inbox.view_all"))
        self.assertFalse(has_permission(ROLE_AGENT, "people_review.view"))
        self.assertFalse(has_permission(ROLE_AGENT, "commercial.view"))
        self.assertFalse(has_permission(ROLE_AGENT, "system.config.write"))
        self.assertTrue(can_role_act(ROLE_AGENT))

    def test_permissions_matrix_auditor(self):
        # Auditor: Xem log, không hành động (Mục H2)
        self.assertFalse(can_role_act(ROLE_AUDITOR))
        self.assertTrue(has_permission(ROLE_AUDITOR, "logs.view"))
        self.assertFalse(has_permission(ROLE_AUDITOR, "logs.clear"))
        self.assertFalse(has_permission(ROLE_AUDITOR, "system.config.write"))
        self.assertFalse(has_permission(ROLE_AUDITOR, "people_review.coaching"))


class TestRBACDataStore(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.store = HeoDataStore(data_dir=self.tmp_dir)

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_datastore_initializes_5_canonical_profiles(self):
        accs = self.store.get_accounts()
        boss_profiles = accs.get("boss_profiles", [])
        self.assertGreaterEqual(len(boss_profiles), 5)
        tiers = {p.get("role_tier") for p in boss_profiles}
        self.assertTrue({"owner", "manager", "operator", "agent", "auditor"}.issubset(tiers))

    def test_switch_rbac_role(self):
        # Chuyển sang auditor
        ok, msg, accs = self.store.switch_rbac_role("auditor")
        self.assertTrue(ok)
        active_prof = self.store.get_active_boss_profile()
        self.assertEqual(active_prof.get("role_tier"), "auditor")
        self.assertEqual(accs.get("active_role_tier"), "auditor")
        self.assertFalse(accs.get("active_rbac_policy", {}).get("can_act"))

        # Chuyển sang operator
        ok, msg, accs = self.store.switch_rbac_role("operator")
        self.assertTrue(ok)
        active_prof = self.store.get_active_boss_profile()
        self.assertEqual(active_prof.get("role_tier"), "operator")
        self.assertFalse(accs.get("active_rbac_policy", {}).get("can_view_people_review"))

        # Chuyển lại owner
        ok, msg, accs = self.store.switch_rbac_role("owner")
        self.assertTrue(ok)
        active_prof = self.store.get_active_boss_profile()
        self.assertEqual(active_prof.get("role_tier"), "owner")
        self.assertTrue(accs.get("active_rbac_policy", {}).get("can_act"))


class TestAuthPluginRBAC(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        cfg_file = os.path.join(self.tmp_dir, "config.json")
        self.ctx = Context(config_path=cfg_file)
        self.bus = EventBus()
        self.store = HeoDataStore(data_dir=self.tmp_dir)
        self.ctx.provide("data_store", self.store)
        self.ctx.store = self.store

        from heo_harness.plugins.auth import AuthPlugin
        self.auth = AuthPlugin(self.ctx, self.bus)
        self.auth.on_load()

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_auth_plugin_rbac_helpers(self):
        # Mặc định là owner
        self.assertEqual(self.auth.get_active_role(), "owner")
        self.assertTrue(self.auth.can_act())
        self.assertTrue(self.auth.has_permission("system.config.write"))

        # Đổi sang auditor trong store
        self.store.switch_rbac_role("auditor")
        self.assertEqual(self.auth.get_active_role(), "auditor")
        self.assertFalse(self.auth.can_act())
        self.assertFalse(self.auth.has_permission("system.config.write"))

        # Kiểm tra danh sách 5 roles
        all_roles = self.auth.get_all_roles()
        self.assertEqual(len(all_roles), 5)


class TestRBACHttpEndpoints(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_port = 5097
        os.environ["HARNESS_PORT"] = str(cls.test_port)

        cls.tmp_dir = tempfile.mkdtemp()
        cfg_file = os.path.join(cls.tmp_dir, "config.json")

        cls.ctx = Context(config_path=cfg_file)
        cls.bus = EventBus()
        cls.manager = PluginManager(cls.ctx, cls.bus)
        cls.store = HeoDataStore(data_dir=cls.tmp_dir)
        cls.ctx.provide("plugin_manager", cls.manager)
        cls.ctx.provide("data_store", cls.store)
        cls.ctx.store = cls.store

        cls.manager.scan_and_register_builtin()
        cls.manager.load_all_registered()
        cls.manager.enable_plugin("heo-auth-rbac-security")
        cls.manager.enable_plugin("heo-ui-dashboard-executive")
        time.sleep(0.15)

    @classmethod
    def tearDownClass(cls):
        ui = cls.manager._plugins.get("heo-ui-dashboard-executive")
        if ui:
            cls.manager.unload_plugin("heo-ui-dashboard-executive")
        shutil.rmtree(cls.tmp_dir, ignore_errors=True)

    def _req(self, path: str, method: str = "GET", data: dict = None):
        url = f"http://127.0.0.1:{self.test_port}{path}"
        headers = {"Content-Type": "application/json"} if data else {}
        body = json.dumps(data).encode("utf-8") if data else None
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=3) as res:
                return res.status, json.loads(res.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read().decode("utf-8"))

    def test_01_get_rbac_profile_and_roles(self):
        status, data = self._req("/api/rbac/profile")
        self.assertEqual(status, 200)
        self.assertTrue(data.get("ok"))
        self.assertIn("role_tier", data)

        status, data = self._req("/api/rbac/roles")
        self.assertEqual(status, 200)
        self.assertTrue(data.get("ok"))
        self.assertEqual(len(data.get("roles", [])), 5)

    def test_02_switch_to_auditor_blocks_actions(self):
        # 1. Switch to auditor
        status, data = self._req("/api/rbac/switch", method="POST", data={"role": "auditor"})
        self.assertEqual(status, 200)
        self.assertEqual(data.get("active_role_tier"), "auditor")

        # 2. Auditor attempting write action must receive 403 Forbidden
        status, data = self._req("/api/people_review/coaching", method="POST", data={"person_id": "PR-01", "coaching_note": "Test"})
        self.assertEqual(status, 403)
        self.assertFalse(data.get("ok"))
        self.assertIn("Kiểm Toán (Auditor)", data.get("error", ""))

    def test_03_switch_to_operator_restricts_people_review(self):
        # 1. Switch to operator
        status, data = self._req("/api/rbac/switch", method="POST", data={"role": "operator"})
        self.assertEqual(status, 200)
        self.assertEqual(data.get("active_role_tier"), "operator")

        # 2. Operator accessing people review should have data restricted
        status, data = self._req("/api/people_review/summary")
        self.assertEqual(status, 200)
        self.assertTrue(data.get("restricted"))

        # 3. Operator attempting coaching action should receive 403 Forbidden
        status, data = self._req("/api/people_review/coaching", method="POST", data={"person_id": "PR-01", "coaching_note": "Test"})
        self.assertEqual(status, 403)

    def test_04_switch_back_to_owner(self):
        # Switch back to owner
        status, data = self._req("/api/rbac/switch", method="POST", data={"role": "owner"})
        self.assertEqual(status, 200)
        self.assertEqual(data.get("active_role_tier"), "owner")

        # Owner has full access to people review summary
        status, data = self._req("/api/people_review/summary")
        self.assertEqual(status, 200)
        self.assertFalse(data.get("restricted", False))


if __name__ == "__main__":
    unittest.main()
