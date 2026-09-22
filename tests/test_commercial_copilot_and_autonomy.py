"""
Unit tests for SPEC-44: Phase 4 — Làm được (Commercial Copilot, AI Quotation, Autonomy 4-5)
Tuân thủ chuẩn SSOT Spec LOCKED v2.2 (Mục L Phase 4, E10, E11, E12, F2.9, H1)
"""

import os
import tempfile
import shutil
import unittest
import json
import urllib.request
import urllib.error
import time
import sqlite3

from heo_harness.core.context import Context
from heo_harness.core.bus import EventBus
from heo_harness.core.manager import PluginManager
from heo_harness.core.store import HeoDataStore
from heo_harness.core.commercial_workbench import CommercialWorkbenchEngine, get_commercial_workbench


class TestCommercialWorkbenchCore(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.tmp_dir, "heo.db")
        
        # Khởi tạo db mẫu có contacts và opportunities
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE contacts (
                id TEXT PRIMARY KEY,
                full_name TEXT NOT NULL,
                company TEXT,
                phone TEXT,
                heat_score REAL DEFAULT 85.0
            )
        """)
        conn.execute("""
            INSERT INTO contacts (id, full_name, company, phone, heat_score)
            VALUES ('CNT-001', 'Chị Mai Phương', 'VinaSupply Corp', '0912345678', 88.0)
        """)
        conn.execute("""
            CREATE TABLE opportunities (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                contact_name TEXT,
                contact_id TEXT,
                channel TEXT DEFAULT 'zalo',
                need_summary TEXT,
                estimated_value REAL DEFAULT 150000000.0,
                stage TEXT DEFAULT 'NEGOTIATING'
            )
        """)
        conn.execute("""
            INSERT INTO opportunities (id, title, contact_name, contact_id, channel, need_summary, estimated_value, stage)
            VALUES ('OPP-101', 'Nhu cầu báo giá giải pháp AI Điều Phối', 'Chị Mai Phương', 'CNT-001', 'zalo', 'Cần triển khai AI điều phối hội thoại đa kênh Zalo & WhatsApp', 185000000.0, 'NEGOTIATING')
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS atomic_events (
                id TEXT PRIMARY KEY,
                event_type TEXT,
                channel TEXT,
                sender_id TEXT,
                sender_name TEXT,
                group_id TEXT,
                group_name TEXT,
                content TEXT,
                extracted_entities TEXT,
                intent TEXT,
                sentiment TEXT,
                meaning_summary TEXT,
                action_suggested TEXT,
                priority TEXT,
                status TEXT,
                heat_score REAL,
                timestamp REAL,
                created_at TEXT,
                archived INTEGER DEFAULT 0
            )
        """)
        conn.commit()
        conn.close()

        self.engine = CommercialWorkbenchEngine(db_path=self.db_path)

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_01_service_catalog(self):
        catalog = self.engine.get_service_catalog()
        self.assertGreaterEqual(len(catalog), 4)
        codes = [item["code"] for item in catalog]
        self.assertIn("SRV-AI-01", codes)
        self.assertIn("SRV-ERP-02", codes)

    def test_02_generate_ai_quotation(self):
        res = self.engine.generate_ai_quotation(deal_id="OPP-101", language="vi")
        self.assertTrue(res.get("ok"))
        doc = res.get("document", {})
        self.assertEqual(doc.get("deal_id"), "OPP-101")
        self.assertEqual(doc.get("contact_name"), "Chị Mai Phương")
        self.assertEqual(doc.get("company"), "VinaSupply Corp")
        self.assertGreater(doc.get("total_amount", 0), 0)
        self.assertGreater(len(doc.get("items", [])), 0)
        self.assertIn("margin_pct", doc)

    def test_03_save_document_and_autonomy_approval(self):
        res = self.engine.generate_ai_quotation(deal_id="OPP-101", language="vi")
        doc = res["document"]

        # Cấp tự trị 4: Lưu nháp chờ Sếp duyệt
        saved = self.engine.save_document(doc)
        self.assertTrue(saved)

        # Kiểm tra document trong db
        docs = self.engine.get_documents()
        self.assertGreaterEqual(len(docs), 1)
        doc_id = doc["id"]

        # Cấp tự trị 5: Duyệt và chuyển trạng thái gửi khách
        action_res = self.engine.send_or_approve_document(doc_id, action="approve_and_send")
        self.assertTrue(action_res.get("ok"))
        self.assertEqual(action_res.get("status"), "SENT")


class TestCommercialCopilotHttpEndpoints(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_port = 5096
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

        # Tạo sẵn cơ hội trong store db
        db_path = os.path.join(cls.tmp_dir, "heo.db")
        conn = sqlite3.connect(db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                id TEXT PRIMARY KEY,
                full_name TEXT NOT NULL,
                company TEXT,
                phone TEXT,
                heat_score REAL DEFAULT 85.0
            )
        """)
        conn.execute("""
            INSERT OR REPLACE INTO contacts (id, full_name, company, phone, heat_score)
            VALUES ('CNT-TEST', 'Anh Hoàng Bách', 'LogiTech Global', '0987654321', 90.0)
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS opportunities (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                contact_name TEXT,
                contact_id TEXT,
                channel TEXT DEFAULT 'whatsapp',
                need_summary TEXT,
                estimated_value REAL DEFAULT 120000000.0,
                stage TEXT DEFAULT 'APPROACHING'
            )
        """)
        conn.execute("""
            INSERT OR REPLACE INTO opportunities (id, title, contact_name, contact_id, channel, need_summary, estimated_value, stage)
            VALUES ('OPP-TEST', 'Báo giá bản quyền Gen-Harness', 'Anh Hoàng Bách', 'CNT-TEST', 'whatsapp', 'Bản quyền doanh nghiệp và hỗ trợ triển khai', 120000000.0, 'APPROACHING')
        """)
        conn.commit()
        conn.close()

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

    def test_01_get_commercial_catalog(self):
        status, data = self._req("/api/commercial/catalog")
        self.assertEqual(status, 200)
        self.assertTrue(data.get("ok"))
        self.assertGreaterEqual(len(data.get("catalog", [])), 4)

    def test_02_post_generate_copilot(self):
        status, data = self._req("/api/commercial/generate_copilot", method="POST", data={
            "deal_id": "OPP-TEST",
            "language": "vi"
        })
        self.assertEqual(status, 200)
        self.assertTrue(data.get("ok"))
        doc = data.get("document", {})
        self.assertEqual(doc.get("deal_id"), "OPP-TEST")
        self.assertEqual(doc.get("contact_name"), "Anh Hoàng Bách")

        # Lưu tài liệu (Autonomy 4)
        save_status, save_data = self._req("/api/commercial/save_document", method="POST", data={
            "document": doc
        })
        self.assertEqual(save_status, 200)
        self.assertTrue(save_data.get("ok"))

        # Phê duyệt & Gửi (Autonomy 5)
        appr_status, appr_data = self._req("/api/commercial/send_or_approve", method="POST", data={
            "id": doc["id"],
            "action": "approve_and_send"
        })
        self.assertEqual(appr_status, 200)
        self.assertTrue(appr_data.get("ok"))


if __name__ == "__main__":
    unittest.main()
