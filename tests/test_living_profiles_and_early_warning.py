"""
Unit tests for SPEC-42: Phase 2 — Hiểu được (Living Profiles, Early Warning, Identity Resolution & Brain Search)
Tác giả: Anh Cơ La (genesis.corp.os@gmail.com)
"""

import unittest
import tempfile
import os
import shutil
import sqlite3
import json
from heo_harness.core.early_warning import EarlyWarningEngine
from heo_harness.core.data_factory import ConversationDataFactory

class TestLivingProfilesAndEarlyWarning(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.tmp_dir, "heo.db")
        # Initialize factory and early warning on this temp db
        self.df = ConversationDataFactory(db_path=self.db_path)
        self.ew = EarlyWarningEngine(data_dir=self.tmp_dir)

        # Seed sample test data
        with sqlite3.connect(self.db_path) as conn:
            # Seed 1 cold contact
            conn.execute("""
            INSERT OR REPLACE INTO contacts (id, full_name, phone, company, heat_score, went_silent_days, churn_risk, ball_owner, interaction_count, last_seen, autonomy_level)
            VALUES ('TEST-CNT-01', 'Đỗ Minh Tuấn', '0901234567', 'Tuấn Minh Log', 45.0, 5, 40.0, 'THEM', 8, '2026-09-17 10:00:00', 2)
            """)

            # Seed 1 slow response contact
            conn.execute("""
            INSERT OR REPLACE INTO contacts (id, full_name, phone, company, heat_score, went_silent_days, churn_risk, ball_owner, interaction_count, last_seen, autonomy_level)
            VALUES ('TEST-CNT-02', 'Bà Vũ Bích Ngọc', '0907654321', 'Bích Ngọc Vina', 75.0, 1, 15.0, 'US', 12, '2026-09-21 14:00:00', 3)
            """)

            # Seed 1 contact with duplicate phone for identity matching
            conn.execute("""
            INSERT OR REPLACE INTO contacts (id, full_name, phone, company, heat_score, went_silent_days, churn_risk, ball_owner, interaction_count, last_seen, autonomy_level)
            VALUES ('TEST-CNT-03', 'Tuấn Minh (WhatsApp)', '+84901234567', 'Tuấn Minh Log', 50.0, 2, 20.0, 'THEM', 4, '2026-09-20 09:00:00', 2)
            """)

            # Seed atomic events
            conn.execute("""
            INSERT OR REPLACE INTO atomic_events (id, event_type, channel, sender_id, sender_name, group_id, group_name, content, extracted_entities, intent, sentiment, meaning_summary, action_suggested, priority, status, heat_score, timestamp, created_at, archived)
            VALUES 
            ('EVT-TEST-1', 'Complained', 'zalo', 'TEST-CNT-01', 'Đỗ Minh Tuấn', 'grp-1', 'Nhóm Test', 'Giao hàng chậm quá', '{}', 'complain', 'negative', 'Khách hàng phản ánh giao hàng chậm', 'Gặp xin lỗi', 'HIGH', 'NEW', 40.0, '2026-09-20 10:00:00', '2026-09-20 10:00:00', 0),
            ('EVT-TEST-2', 'Complained', 'zalo', 'TEST-CNT-01', 'Đỗ Minh Tuấn', 'grp-1', 'Nhóm Test', 'Lại trễ hẹn báo giá rồi', '{}', 'complain', 'negative', 'Khách phàn nàn lại trễ hẹn báo giá', 'Gửi báo giá gấp', 'HIGH', 'NEW', 35.0, '2026-09-21 11:00:00', '2026-09-21 11:00:00', 0),
            ('EVT-TEST-3', 'MentionsCompetitor', 'whatsapp', 'TEST-CNT-02', 'Bà Vũ Bích Ngọc', 'grp-2', 'Nhóm VIP', 'Bên công ty ABC chào giá rẻ hơn 20%', '{}', 'competitor', 'neutral', 'Khách hàng nhắc tới đối thủ ABC chào rẻ hơn 20%', 'Dùng battlecard', 'HIGH', 'NEW', 80.0, '2026-09-22 09:00:00', '2026-09-22 09:00:00', 0)
            """)

            # Seed broken promise
            conn.execute("""
            INSERT OR REPLACE INTO broken_promises (id, employee_name, client_name, channel, promise_text, promised_deadline, delay_hours, severity, status, created_at)
            VALUES ('BP-TEST-01', 'Nguyễn Văn A', 'Đỗ Minh Tuấn (Tuấn Minh Log)', 'Zalo', 'Hứa gửi hợp đồng trước 12h', '2026-09-21 12:00:00', 28.5, 'HIGH', 'UNRESOLVED', '2026-09-21 12:00:00')
            """)

            # Seed opportunity
            conn.execute("""
            INSERT OR REPLACE INTO opportunities (id, title, contact_name, contact_id, channel, group_name, need_summary, estimated_value, stage, confidence_score, heat_score, risk_notes, source_event_id, created_at, updated_at, owner, win_probability)
            VALUES ('OPP-TEST-01', 'Gói Điều Phối Doanh Nghiệp', 'Bà Vũ Bích Ngọc', 'TEST-CNT-02', 'whatsapp', 'Nhóm VIP', 'Cần triển khai AI tự động hóa chăm sóc', 150000000.0, 'SIGNAL', 90.0, 85.0, '', 'EVT-TEST-3', '2026-09-22 08:00:00', '2026-09-22 08:00:00', 'Chưa phân bổ', 0.6)
            """)
            conn.commit()

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_01_scan_and_generate_alerts(self):
        """Kiểm tra radar cảnh báo phát hiện đúng các loại cảnh báo sớm."""
        alerts = self.ew.scan_and_generate_alerts()
        self.assertGreater(len(alerts), 0)

        active_alerts = self.ew.get_alerts(status="ACTIVE")
        types = [a["type"] for a in active_alerts]
        
        # Phải bắt được COLD_LEAD, SLOW_RESPONSE, REPEATED_COMPLAINT, OVERDUE_PROMISE, COMPETITOR_MENTION, UNCLAIMED_HOT_OPP
        self.assertIn("COLD_LEAD", types)
        self.assertIn("SLOW_RESPONSE", types)
        self.assertIn("REPEATED_COMPLAINT", types)
        self.assertIn("OVERDUE_PROMISE", types)
        self.assertIn("COMPETITOR_MENTION", types)
        self.assertIn("UNCLAIMED_HOT_OPP", types)

    def test_02_alert_lifecycle(self):
        """Kiểm tra vòng đời cảnh báo: Tiếp nhận (Acknowledge) -> Giải quyết (Resolve) -> Bỏ qua (Dismiss)."""
        self.ew.scan_and_generate_alerts()
        alerts = self.ew.get_alerts(status="ACTIVE")
        self.assertTrue(len(alerts) > 0)
        target = alerts[0]

        # 1. Acknowledge
        ack = self.ew.acknowledge_alert(target["id"], user="Sếp Ryan")
        self.assertTrue(ack)

        # 2. Resolve
        res = self.ew.resolve_alert(target["id"], action_taken="Đã xử lý xong", user="Sếp Ryan")
        self.assertTrue(res)

        # 3. Dismiss
        if len(alerts) > 1:
            target2 = alerts[1]
            dsm = self.ew.dismiss_alert(target2["id"], reason="Không cần thiết", user="Sếp Ryan")
            self.assertTrue(dsm)

        # Summary check
        summary = self.ew.get_alert_summary()
        self.assertTrue(summary["ok"])
        self.assertIn("total_active", summary)
        self.assertIn("critical", summary)

    def test_03_identity_suggestions_and_merge(self):
        """Kiểm tra nhận diện trùng số điện thoại đa kênh và hợp nhất định danh (G2)."""
        suggestions = self.ew.get_identity_suggestions()
        self.assertTrue(len(suggestions) > 0)
        
        # Tìm suggestion giữa TEST-CNT-01 và TEST-CNT-03 (cùng số 0901234567)
        phone_match = None
        for s in suggestions:
            ids = [s["primary"]["id"], s["secondary"]["id"]]
            if "TEST-CNT-01" in ids and "TEST-CNT-03" in ids:
                phone_match = s
                break
        self.assertIsNotNone(phone_match)
        self.assertIn("số điện thoại", phone_match["match_reason"].lower())

        # Tiến hành merge
        res = self.ew.merge_identities("TEST-CNT-01", "TEST-CNT-03", user="Anh Cơ La")
        self.assertTrue(res["ok"])
        history_id = res["history_id"]

        # Kiểm tra secondary đã được gắn merged_into
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            s_row = conn.execute("SELECT * FROM contacts WHERE id = 'TEST-CNT-03'").fetchone()
            self.assertEqual(s_row["merged_into"], "TEST-CNT-01")

            p_row = conn.execute("SELECT * FROM contacts WHERE id = 'TEST-CNT-01'").fetchone()
            self.assertIn("Tuấn Minh (WhatsApp)", p_row["ai_summary"])

        # Kiểm tra split rollback
        split_res = self.ew.split_identity(history_id, user="Anh Cơ La")
        self.assertTrue(split_res["ok"])

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            s_row_after = conn.execute("SELECT * FROM contacts WHERE id = 'TEST-CNT-03'").fetchone()
            self.assertIsNone(s_row_after["merged_into"])

    def test_04_living_profile_deep_enricher(self):
        """Kiểm tra Hồ sơ sống 360 với Explainable Scoring và Đa kênh."""
        profile = self.ew.get_living_profile("TEST-CNT-01")
        self.assertTrue(profile["ok"])
        
        # 1. Đa kênh
        channels = profile.get("channels", [])
        self.assertTrue(len(channels) >= 1)

        # 2. Explainable AI Scoring
        scoring = profile.get("explainable_scoring", {})
        self.assertIn("heat_score", scoring)
        self.assertIn("heat_explanation", scoring)
        self.assertIn("churn_risk", scoring)
        self.assertIn("churn_explanation", scoring)
        self.assertIn("went_silent_days", scoring)

        # 3. AI Summary 8-12 dòng
        summary = profile.get("ai_summary", "")
        self.assertGreaterEqual(len(summary.splitlines()), 6)

        # 4. Timeline
        timeline = profile.get("events_timeline", [])
        self.assertTrue(len(timeline) >= 2)

        # 5. Cập nhật notes và autonomy
        ok_notes = self.ew.update_notes("TEST-CNT-01", "Ghi chú đặc biệt từ Sếp Ryan")
        self.assertTrue(ok_notes)

        ok_auto = self.ew.update_autonomy("TEST-CNT-01", 4)
        self.assertTrue(ok_auto)

        prof_updated = self.ew.get_living_profile("TEST-CNT-01")
        self.assertEqual(prof_updated["notes"], "Ghi chú đặc biệt từ Sếp Ryan")
        self.assertEqual(prof_updated["autonomy_level"], 4)

    def test_05_brain_search(self):
        """Kiểm tra Tìm kiếm có não (Brain Search) bóc tách tri giác ngữ nghĩa."""
        # 1. Tìm theo khiếu nại
        res_cmpl = self.ew.brain_search("khiếu nại")
        self.assertTrue(res_cmpl["ok"])

        # 2. Tìm theo tên khách hàng
        res_name = self.ew.brain_search("Bích Ngọc")
        self.assertTrue(res_name["ok"])
        self.assertTrue(len(res_name["results"]) > 0)
        top = res_name["results"][0]
        self.assertIn("Bích Ngọc", top["title"])
        self.assertIn("match_reason", top)

        # 3. Tìm theo đối thủ cạnh tranh
        res_comp = self.ew.brain_search("đối thủ")
        self.assertTrue(res_comp["ok"])


class TestEarlyWarningHttpEndpoints(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import urllib.request
        cls.test_port = 5098
        os.environ["HARNESS_PORT"] = str(cls.test_port)

        cls.tmp_dir = tempfile.mkdtemp()
        cfg_file = os.path.join(cls.tmp_dir, "config.json")

        from heo_harness.core.context import Context
        from heo_harness.core.bus import EventBus
        from heo_harness.core.manager import PluginManager
        from heo_harness.core.store import HeoDataStore

        cls.ctx = Context(config_path=cfg_file)
        cls.bus = EventBus()
        cls.manager = PluginManager(cls.ctx, cls.bus)
        cls.store = HeoDataStore(data_dir=cls.tmp_dir)
        cls.ctx.provide("plugin_manager", cls.manager)
        cls.ctx.provide("data_store", cls.store)
        cls.ctx.store = cls.store

        # Init early warning engine on this tmp_dir
        cls.ew = EarlyWarningEngine(data_dir=cls.tmp_dir)
        cls.ew.scan_and_generate_alerts()

        cls.manager.scan_and_register_builtin()
        cls.manager.load_all_registered()
        cls.manager.enable_plugin("heo-auth-rbac-security")
        cls.manager.enable_plugin("heo-ui-dashboard-executive")
        import time
        time.sleep(0.2)

    @classmethod
    def tearDownClass(cls):
        ui = cls.manager._plugins.get("heo-ui-dashboard-executive")
        if ui:
            cls.manager.unload_plugin("heo-ui-dashboard-executive")
        shutil.rmtree(cls.tmp_dir, ignore_errors=True)

    def _req(self, path: str, method: str = "GET", data: dict = None):
        import urllib.request, urllib.error
        url = f"http://127.0.0.1:{self.test_port}{path}"
        headers = {"Content-Type": "application/json"} if data else {}
        body = json.dumps(data).encode("utf-8") if data else None
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=3) as res:
                return res.status, json.loads(res.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read().decode("utf-8"))

    def test_01_early_warning_apis(self):
        # 1. Summary
        status, data = self._req("/api/early_warning/summary")
        self.assertEqual(status, 200)
        self.assertTrue(data.get("ok"))
        self.assertIn("total_active", data)

        # 2. List alerts
        status, data = self._req("/api/early_warning/alerts")
        self.assertEqual(status, 200)
        self.assertTrue(data.get("ok"))
        alerts = data.get("alerts", [])
        if alerts:
            alr_id = alerts[0]["id"]
            # 3. Action acknowledge
            status, ack = self._req("/api/early_warning/action", method="POST", data={"id": alr_id, "action": "acknowledge"})
            self.assertEqual(status, 200)
            self.assertTrue(ack.get("ok"))

    def test_02_identity_and_living_profile_apis(self):
        # 1. Suggestions
        status, data = self._req("/api/identity/suggestions")
        self.assertEqual(status, 200)
        self.assertTrue(data.get("ok"))

        # 2. Living profile detail (seed CNT-001 if needed)
        with sqlite3.connect(os.path.join(self.tmp_dir, "heo.db")) as conn:
            conn.execute("""
            INSERT OR REPLACE INTO contacts (id, full_name, phone, company, heat_score, went_silent_days, churn_risk)
            VALUES ('CNT-TEST-HTTP', 'Khách VIP HTTP', '0911223344', 'Tập đoàn VIP', 80.0, 0, 10.0)
            """)
            conn.commit()

        status, prof = self._req("/api/living_profile/detail?id=CNT-TEST-HTTP")
        self.assertEqual(status, 200)
        self.assertTrue(prof.get("ok"))
        self.assertIn("explainable_scoring", prof)

        # 3. Save notes
        status, res_notes = self._req("/api/living_profile/save_notes", method="POST", data={"id": "CNT-TEST-HTTP", "notes": "Đã đàm phán giảm 5%"})
        self.assertEqual(status, 200)
        self.assertTrue(res_notes.get("ok"))

        # 4. Brain search
        status, search = self._req("/api/brain_search?q=VIP")
        self.assertEqual(status, 200)
        self.assertTrue(search.get("ok"))

    def test_03_auditor_rbac_protection(self):
        # Đổi sang vai trò Auditor
        self.store.switch_rbac_role("auditor")
        
        # Auditor gọi action -> Bị chặn 403 Forbidden!
        status, res = self._req("/api/early_warning/action", method="POST", data={"id": "ALR-TEST", "action": "resolve"})
        self.assertEqual(status, 403)
        self.assertTrue(res.get("restricted"))

        # Auditor gọi identity merge -> Bị chặn 403 Forbidden!
        status, res = self._req("/api/identity/merge", method="POST", data={"primary_id": "A", "secondary_id": "B"})
        self.assertEqual(status, 403)

        # Trả lại quyền Owner
        self.store.switch_rbac_role("owner")


if __name__ == "__main__":
    unittest.main()
