# -*- coding: utf-8 -*-
"""
Unit Test: Data Factory & Milestones 2-4 SSOT Verification
Kiểm thử trích xuất sự kiện nguyên tử, thực thể, cơ hội và hợp nhất định danh liên hệ.
Tác giả: Anh Cơ La (genesis.corp.os@gmail.com)
"""

import unittest
import os
import tempfile
import json
from heo_harness.core.data_factory import ConversationDataFactory

class TestDataFactoryMilestones(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test_heo.db")
        self.df = ConversationDataFactory(db_path=self.db_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_01_atomic_events_classification(self):
        """Kiểm tra phân loại chính xác các loại sự kiện nguyên tử."""
        # 1. AskedPrice
        res = self.df.process_incoming_message("Cho em xin báo giá dịch vụ CRM là bao nhiêu tiền?")
        self.assertEqual(res["event_type"], "AskedPrice")
        self.assertEqual(res["priority"], "P1")
        self.assertGreaterEqual(res["heat_score"], 80.0)

        # 2. Complained
        res = self.df.process_incoming_message("Hàng hóa giao chậm quá, hệ thống bị lỗi không chạy được!")
        self.assertEqual(res["event_type"], "Complained")
        self.assertEqual(res["priority"], "P0")
        self.assertGreaterEqual(res["heat_score"], 90.0)

        # 3. ScheduledMeeting
        res = self.df.process_incoming_message("Mình hẹn gặp nhau trao đổi lúc 14h chiều nay qua Zoom nhé!")
        self.assertEqual(res["event_type"], "ScheduledMeeting")

        # 4. RequestedPartnership
        res = self.df.process_incoming_message("Công ty mình đang cần tìm nguồn vải may mặc xuất khẩu số lượng lớn.")
        self.assertEqual(res["event_type"], "RequestedPartnership")

        # 5. SentQuotation
        res = self.df.process_incoming_message("Em đã chuyển khoản thanh toán cọc hợp đồng rồi anh nhé.")
        self.assertEqual(res["event_type"], "SentQuotation")

    def test_02_entity_extraction(self):
        """Kiểm tra trích xuất thực thể: Giá tiền, hàng hóa, thời gian."""
        entities = self.df.extract_entities_from_text("Báo giá hợp đồng phần mềm trị giá 50 triệu giao ngày 25/10")
        self.assertTrue(len(entities["prices"]) > 0)
        self.assertTrue(any("50" in p for p in entities["prices"]))
        self.assertIn("hợp đồng", entities["products"])
        self.assertIn("phần mềm", entities["products"])
        self.assertTrue(len(entities["dates"]) > 0)

    def test_03_opportunities_lifecycle(self):
        """Kiểm tra vòng đời Cơ Hội (Opportunities) qua 7 cột Kanban."""
        # Tự động sinh cơ hội từ RequestedPartnership
        msg_res = self.df.process_incoming_message(
            content="Bên mình cần tìm xưởng may gia công 5,000 áo thun ngân sách 100 triệu",
            channel="zalo",
            sender_id="cnt-partner-1",
            sender_name="Anh Tuấn"
        )
        opps = self.df.get_opportunities()
        self.assertGreater(len(opps), 0)
        opp = opps[0]
        self.assertEqual(opp["stage"], "SIGNAL")

        # Cập nhật chuyển stage Kanban
        ok = self.df.update_opportunity_stage(opp["id"], "VERIFIED")
        self.assertTrue(ok)

        ok2 = self.df.update_opportunity_stage(opp["id"], "NEGOTIATING")
        self.assertTrue(ok2)

        # Stage không hợp lệ
        ok_fail = self.df.update_opportunity_stage(opp["id"], "INVALID_STAGE")
        self.assertFalse(ok_fail)

    def test_04_identity_resolution_merge_contacts(self):
        """Kiểm tra hợp nhất định danh liên hệ (Identity Resolution)."""
        c1 = ("C-01", "Nguyễn Văn A", "0901111111", "zalo-a", "", "a@corp.vn", "A Corp", "CEO", 80.0, "HOT", "US", 0, "Ghi chú A", "2026-09-21", "2026-09-21")
        c2 = ("C-02", "Văn A (Zalo)", "", "zalo-a-extra", "wa-a", "", "", "", 60.0, "WARM", "THEM", 1, "Ghi chú B", "2026-09-21", "2026-09-21")

        with self.df._get_conn() as conn:
            for c in [c1, c2]:
                conn.execute("""
                INSERT INTO contacts (id, full_name, phone, zalo_id, whatsapp_id, email, company, role, heat_score, status, ball_owner, went_silent_days, ai_summary, first_seen, last_seen)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, c)
            conn.commit()

        # Thực hiện Merge C-02 vào C-01
        res = self.df.merge_contacts("C-01", "C-02")
        self.assertTrue(res)

        contacts = self.df.get_contacts()
        contact_ids = [c["id"] for c in contacts]
        self.assertIn("C-01", contact_ids)
        self.assertNotIn("C-02", contact_ids)

        merged = [c for c in contacts if c["id"] == "C-01"][0]
        self.assertEqual(merged["phone"], "0901111111")
        self.assertEqual(merged["whatsapp_id"], "wa-a")
        self.assertIn("Ghi chú A", merged["ai_summary"])
        self.assertIn("Ghi chú B", merged["ai_summary"])

    def test_05_opportunity_advanced_update_and_delete(self):
        """Kiểm tra cập nhật nâng cao và xóa cơ hội khỏi pipeline."""
        res = self.df.create_opportunity(
            title="Cung cấp phần mềm ERP",
            contact_name="Nguyễn Văn B",
            need_summary="Cần phần mềm ERP cho công ty sản xuất",
            estimated_value=250000000.0,
            channel="zalo",
            stage="RAW_SIGNAL"
        )
        opp_id = res["id"]

        # Cập nhật chi tiết
        ok = self.df.update_opportunity(opp_id, {
            "estimated_value": 300000000.0,
            "stage": "NEGOTIATING",
            "owner": "Sếp Cơ La (Ryan)",
            "win_probability": 80.0
        })
        self.assertTrue(ok)

        opps = self.df.get_opportunities()
        target = [o for o in opps if o["id"] == opp_id][0]
        self.assertEqual(target["estimated_value"], 300000000.0)
        self.assertEqual(target["stage"], "NEGOTIATING")
        self.assertEqual(target["owner"], "Sếp Cơ La (Ryan)")
        self.assertEqual(target["win_probability"], 80.0)

        # Xóa cơ hội
        ok_del = self.df.delete_opportunity(opp_id)
        self.assertTrue(ok_del)
        opps_after = self.df.get_opportunities()
        self.assertNotIn(opp_id, [o["id"] for o in opps_after])

    def test_06_supply_demand_matching(self):
        """(SPEC-12) Kiểm tra thuật toán ráp khớp cung-cầu tự động."""
        res = self.df.create_opportunity(
            title="Cần mua hệ thống chatbot AI điều phối Zalo",
            contact_name="Giám Đốc Bán Lẻ",
            need_summary="Cần giải pháp AI agent trả lời tin nhắn Zalo tự động cho chuỗi cửa hàng",
            estimated_value=0.0
        )
        opp_id = res["id"]
        match_result = self.df.match_opportunity_supply_demand(opp_id)
        self.assertTrue(match_result["matched"])
        self.assertEqual(match_result["service_code"], "SRV-AI")
        self.assertGreaterEqual(match_result["confidence"], 50)
        self.assertGreaterEqual(match_result["recommended_price"], 100000000.0)

        # Kiểm tra stage đã được cập nhật thành MATCHED
        opps = self.df.get_opportunities()
        target = [o for o in opps if o["id"] == opp_id][0]
        self.assertEqual(target["stage"], "MATCHED")

    def test_07_archive_atomic_event_inbox_zero(self):
        """Kiểm tra lưu trữ sự kiện đạt trạng thái Inbox Zero cho Hộp Thư Ý Nghĩa."""
        evt = self.df.process_incoming_message("Báo giá này tốt quá em ơi!")
        evt_id = evt["id"]
        ok = self.df.archive_atomic_event(evt_id)
        self.assertTrue(ok)

        with self.df._get_conn() as conn:
            row = conn.execute("SELECT archived, status FROM atomic_events WHERE id = ?", (evt_id,)).fetchone()
            self.assertEqual(row["archived"], 1)
            self.assertEqual(row["status"], "ARCHIVED")

    def test_08_relationship_graph_generation(self):
        """(SPEC-19) Kiểm tra tạo mạng lưới quan hệ đồ thị Node/Edge."""
        self.df.seed_sample_data_if_empty()
        graph = self.df.get_relationship_graph()
        self.assertTrue(graph["ok"])
        nodes = graph["nodes"]
        edges = graph["edges"]
        self.assertGreater(len(nodes), 3)
        self.assertGreater(len(edges), 2)

        # Kiểm tra node HQ trung tâm
        hq = [n for n in nodes if n["id"] == "node-hq"][0]
        self.assertEqual(hq["type"], "hq")
        self.assertEqual(hq["heat"], 100)

        # Kiểm tra node Contacts và Opportunities
        contact_nodes = [n for n in nodes if n["type"] == "contact"]
        self.assertGreaterEqual(len(contact_nodes), 1)

    def test_09_contact_detail_and_autonomy_update(self):
        """(SPEC-20) Kiểm tra hồ sơ sống 360 và thang đo tự trị (Autonomy Level 0-6)."""
        self.df.seed_sample_data_if_empty()
        contacts = self.df.get_contacts()
        c_id = contacts[0]["id"]

        # Cập nhật mức tự trị lên Cấp 4
        ok = self.df.update_contact_autonomy(c_id, 4)
        self.assertTrue(ok)

        # Không cho phép mức ngoài 0-6
        self.assertFalse(self.df.update_contact_autonomy(c_id, 7))
        self.assertFalse(self.df.update_contact_autonomy(c_id, -1))

        # Kiểm tra chi tiết hồ sơ
        detail = self.df.get_contact_detail(c_id)
        self.assertTrue(detail["ok"])
        self.assertEqual(detail["contact"]["autonomy_level"], 4)
        self.assertIn("events", detail)
        self.assertIn("opportunities", detail)

    def test_10_explainable_ai_and_summary_generation(self):
        """(SPEC-20, SPEC-10) Kiểm tra sinh tóm tắt AI 8-12 dòng và Explainable AI."""
        self.df.seed_sample_data_if_empty()
        contacts = self.df.get_contacts()
        c_id = contacts[0]["id"]

        res = self.df.generate_contact_summary(c_id)
        self.assertTrue(res["ok"])
        self.assertIn("ai_summary", res)
        self.assertIn("score_explanation", res)
        # Kiểm tra tóm tắt có nhiều dòng (8-12 dòng)
        lines = [l for l in res["ai_summary"].split("\n") if l.strip()]
        self.assertGreaterEqual(len(lines), 7)
        self.assertIn("Tổng quan", res["ai_summary"])
        self.assertIn("Điểm", res["score_explanation"])

if __name__ == "__main__":
    unittest.main()
