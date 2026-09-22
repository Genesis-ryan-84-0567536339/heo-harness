"""
Unit tests for SPEC-43: Phase 3 — Quản được (Relationship Map & Opportunity Board)
Tuân thủ chuẩn SSOT Spec LOCKED v2.2 (Mục L Phase 3, E4, E8, F2.3, F2.5, F2.7, F4)
"""

import os
import tempfile
import shutil
import unittest
import json
import urllib.request
import urllib.error
import time

from heo_harness.core.context import Context
from heo_harness.core.bus import EventBus
from heo_harness.core.manager import PluginManager
from heo_harness.core.store import HeoDataStore
from heo_harness.core.relationship_map import RelationshipIntelligenceEngine, get_relationship_engine


class TestRelationshipIntelligenceEngine(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.engine = RelationshipIntelligenceEngine(data_dir=self.tmp_dir)

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_01_self_healing_schema_and_initial_seed(self):
        # Database và bảng phải được tự khởi tạo đầy đủ
        self.assertTrue(os.path.exists(self.engine.db_path))
        with self.engine._get_conn() as conn:
            tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
            self.assertIn("contacts", tables)
            self.assertIn("opportunities", tables)
            self.assertIn("relationship_edges", tables)
            self.assertIn("opportunity_stage_history", tables)
            self.assertIn("care_quality_records", tables)

    def test_02_relationship_graph_structure(self):
        graph = self.engine.get_relationship_graph()
        self.assertTrue(graph.get("ok"))
        self.assertIn("nodes", graph)
        self.assertIn("edges", graph)
        self.assertIn("categories", graph)
        self.assertIn("stats", graph)

        # Kiểm tra sự hiện diện của HQ node
        hq_nodes = [n for n in graph["nodes"] if n["id"] == "node-hq"]
        self.assertEqual(len(hq_nodes), 1)
        self.assertEqual(hq_nodes[0]["label"], "Anh Cơ La (Ryan) / HQ")

        # Kiểm tra nhóm kênh hội thoại
        groups = [n for n in graph["nodes"] if n["type"] == "group"]
        self.assertGreaterEqual(len(groups), 4)

        # Kiểm tra contacts & opportunities
        contacts = [n for n in graph["nodes"] if n["type"] == "contact"]
        opps = [n for n in graph["nodes"] if n["type"] == "opportunity"]
        self.assertGreaterEqual(len(contacts), 1)
        self.assertGreaterEqual(len(opps), 1)

    def test_03_relationship_analytics(self):
        analytics = self.engine.get_relationship_analytics()
        self.assertTrue(analytics.get("ok"))
        self.assertIn("top_connectors", analytics)
        self.assertIn("cold_leads", analytics)
        self.assertIn("overloaded_agents", analytics)
        self.assertIn("ball_in_court", analytics)
        self.assertIn("network_health_score", analytics)

        # Kiểm tra top connectors có degree
        self.assertGreaterEqual(len(analytics["top_connectors"]), 1)
        first_conn = analytics["top_connectors"][0]
        self.assertIn("degree_connections", first_conn)
        self.assertIn("full_name", first_conn)

        # Kiểm tra trọng tài bóng
        ball = analytics["ball_in_court"]
        self.assertIn("us_count", ball)
        self.assertIn("them_count", ball)
        self.assertIn("us_pct", ball)
        self.assertIn("them_pct", ball)

    def test_04_upsert_and_delete_edge(self):
        # Thêm edge
        res = self.engine.upsert_edge(
            from_node="cnt-1",
            to_node="cnt-3",
            edge_type="collaboration",
            weight=1.5,
            last_topic="Trao đổi kỹ thuật",
            relationship_stage="hot",
            ball_owner="US"
        )
        self.assertTrue(res.get("ok"))
        edge_id = res["edge_id"]

        # Kiểm tra edge đã lưu
        with self.engine._get_conn() as conn:
            row = conn.execute("SELECT * FROM relationship_edges WHERE id = ?", (edge_id,)).fetchone()
            self.assertIsNotNone(row)
            self.assertEqual(row["from_node"], "cnt-1")
            self.assertEqual(row["to_node"], "cnt-3")
            self.assertEqual(row["last_topic"], "Trao đổi kỹ thuật")

        # Xóa edge
        deleted = self.engine.delete_edge(edge_id)
        self.assertTrue(deleted)
        with self.engine._get_conn() as conn:
            row_after = conn.execute("SELECT * FROM relationship_edges WHERE id = ?", (edge_id,)).fetchone()
            self.assertIsNone(row_after)

    def test_05_opportunity_board_8_canonical_stages(self):
        board = self.engine.get_opportunity_board()
        self.assertTrue(board.get("ok"))
        stages = board.get("stages", [])
        self.assertEqual(len(stages), 8)
        expected_keys = [
            "RAW_SIGNAL", "VERIFIED", "MATCHED", "APPROACHING",
            "NEGOTIATING", "INTERNAL_TRANSFERRED", "WON", "LOST"
        ]
        actual_keys = [s["key"] for s in stages]
        self.assertEqual(actual_keys, expected_keys)

        # Kiểm tra columns có đủ 8 cột
        cols = board.get("columns", {})
        for k in expected_keys:
            self.assertIn(k, cols)

        # Kiểm tra metrics
        metrics = board.get("metrics", {})
        self.assertIn("total_deals", metrics)
        self.assertIn("active_pipeline_value", metrics)
        self.assertIn("won_value", metrics)

    def test_06_transition_opportunity_stage(self):
        # Chuyển stage sang WON
        res = self.engine.transition_opportunity_stage(
            opp_id="OPP-01",
            new_stage="WON",
            reason="Đã ký kết hợp đồng chính thức",
            changed_by="Anh Cơ La (Ryan)"
        )
        self.assertTrue(res.get("ok"))
        self.assertEqual(res.get("to_stage"), "WON")

        # Kiểm tra lịch sử đã ghi nhận
        with self.engine._get_conn() as conn:
            hist = conn.execute("SELECT * FROM opportunity_stage_history WHERE opp_id = 'OPP-01'").fetchall()
            self.assertGreaterEqual(len(hist), 1)
            self.assertEqual(hist[0]["to_stage"], "WON")
            self.assertIn("ký kết", hist[0]["reason"])

            # Kiểm tra contact liên quan được tăng nhiệt độ lên 95°
            cnt = conn.execute("SELECT * FROM contacts WHERE id = '3'").fetchone()
            self.assertIsNotNone(cnt)
            self.assertEqual(cnt["heat_score"], 95.0)

    def test_07_care_quality_analytics(self):
        care = self.engine.get_care_quality_analytics()
        self.assertTrue(care.get("ok"))
        self.assertIn("summary", care)
        self.assertIn("agents", care)
        self.assertIn("time_slot_averages", care)

        summary = care["summary"]
        self.assertIn("overall_care_score", summary)
        self.assertIn("median_response_min", summary)
        self.assertIn("avg_follow_up_rate_pct", summary)

        # Có ít nhất 3 nhân sự được đánh giá
        agents = care["agents"]
        self.assertGreaterEqual(len(agents), 3)
        self.assertEqual(agents[0]["agent_name"], "Lê Thùy Linh")


class TestRelationshipHttpEndpoints(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_port = 5098
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
        time.sleep(0.2)

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
            with urllib.request.urlopen(req, timeout=4) as res:
                return res.status, json.loads(res.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read().decode("utf-8"))

    def test_01_get_relationship_graph_http(self):
        status, data = self._req("/api/relationship/graph")
        self.assertEqual(status, 200)
        self.assertTrue(data.get("ok"))
        self.assertIn("nodes", data)
        self.assertIn("edges", data)

    def test_02_get_relationship_analytics_http(self):
        status, data = self._req("/api/relationship_graph/analytics")
        self.assertEqual(status, 200)
        self.assertTrue(data.get("ok"))
        self.assertIn("top_connectors", data)
        self.assertIn("cold_leads", data)
        self.assertIn("overloaded_agents", data)
        self.assertIn("ball_in_court", data)

    def test_03_get_opportunity_board_http(self):
        status, data = self._req("/api/opportunity_board/stages")
        self.assertEqual(status, 200)
        self.assertTrue(data.get("ok"))
        self.assertEqual(len(data.get("stages", [])), 8)
        self.assertIn("columns", data)

    def test_04_get_care_quality_http(self):
        status, data = self._req("/api/care_quality/analytics")
        self.assertEqual(status, 200)
        self.assertTrue(data.get("ok"))
        self.assertIn("summary", data)
        self.assertIn("agents", data)

    def test_05_post_edge_and_transition(self):
        # Tạo liên kết quan hệ mới
        status, data = self._req("/api/relationship_graph/edge", method="POST", data={
            "from_node": "cnt-1",
            "to_node": "cnt-2",
            "edge_type": "collaboration",
            "last_topic": "Báo cáo kiểm toán chung",
            "relationship_stage": "partner"
        })
        self.assertEqual(status, 200)
        self.assertTrue(data.get("ok"))

        # Chuyển stage cơ hội
        status, data = self._req("/api/opportunity_board/transition", method="POST", data={
            "opp_id": "OPP-02",
            "stage": "NEGOTIATING",
            "reason": "Khách hàng đồng ý đàm phán chi tiết"
        })
        self.assertEqual(status, 200)
        self.assertTrue(data.get("ok"))
        self.assertEqual(data.get("to_stage"), "NEGOTIATING")

    def test_06_rbac_auditor_blocked(self):
        # 1. Đổi sang vai trò Auditor
        status, data = self._req("/api/rbac/switch", method="POST", data={"role": "auditor"})
        self.assertEqual(status, 200)
        self.assertEqual(data.get("active_role_tier"), "auditor")

        # 2. Auditor cố ý thêm edge -> 403 Forbidden
        status, data = self._req("/api/relationship_graph/edge", method="POST", data={
            "from_node": "cnt-1",
            "to_node": "cnt-3"
        })
        self.assertEqual(status, 403)
        self.assertFalse(data.get("ok"))

        # 3. Auditor cố ý chuyển stage cơ hội -> 403 Forbidden
        status, data = self._req("/api/opportunity_board/transition", method="POST", data={
            "opp_id": "OPP-01",
            "stage": "WON"
        })
        self.assertEqual(status, 403)
        self.assertFalse(data.get("ok"))

        # 4. Trả về Owner
        status, data = self._req("/api/rbac/switch", method="POST", data={"role": "owner"})
        self.assertEqual(status, 200)


if __name__ == "__main__":
    unittest.main()
