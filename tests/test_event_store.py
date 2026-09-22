"""
Unit Tests for SPEC-30: Kiến Trúc Sự Kiện Nguyên Tử (Event-Driven Persistence)
và SPEC-41: Phase 1 — Nhìn thấy được (Listen & Meaning Inbox).
Tuân thủ Mục G3 Spec LOCKED v2.2.
"""

import unittest
import tempfile
import shutil
import os
import time

from heo_harness.core.event_store import EventStore, CANONICAL_EVENT_TYPES
from heo_harness.core.bus import EventBus
from heo_harness.core.store import HeoDataStore


class TestEventStore(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.db_file = os.path.join(self.tmp_dir, "test_events.db")
        self.event_store = EventStore(db_path=self.db_file)
        self.store = HeoDataStore(data_dir=self.tmp_dir)

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_01_canonical_event_types(self):
        expected_types = [
            "AskedPrice", "RequestedPartnership", "Complained",
            "PromisedDelivery", "ScheduledMeeting", "SentQuotation",
            "MentionsCompetitor", "WentSilent"
        ]
        for t in expected_types:
            self.assertIn(t, CANONICAL_EVENT_TYPES)

    def test_02_detect_intent_and_extract_entities(self):
        # Test AskedPrice
        msg = "Em ơi cho anh xin báo giá 50 triệu lô áo thun nhé"
        evt = self.event_store.persist_inbound_message(
            content=msg, channel="zalo", sender_id="user-01", sender_name="Anh Nam"
        )
        self.assertEqual(evt["event_type"], "AskedPrice")
        self.assertTrue(any("50" in str(p) for p in evt["entities"].get("prices", [])))
        self.assertEqual(evt["priority"], "P1")

        self.assertGreater(evt["heat_score"], 70)

        # Test PromisedDelivery
        msg_promise = "Dạ anh yên tâm, chiều nay em gửi hợp đồng và mai giao hàng cho anh ạ"
        evt_p = self.event_store.persist_inbound_message(
            content=msg_promise, channel="whatsapp", sender_id="user-02", sender_name="Bé Heo"
        )
        self.assertEqual(evt_p["event_type"], "PromisedDelivery")

    def test_03_query_events_and_archive(self):
        self.event_store.persist_inbound_message("Bên khác chào giá rẻ hơn bên em nhiều", sender_name="Khách A")
        self.event_store.persist_inbound_message("Sao lâu quá không thấy ai trả lời vậy?", sender_name="Khách B")

        evts = self.event_store.get_events(limit=10, status="ACTIVE")
        self.assertGreaterEqual(len(evts), 2)

        # Test archive event
        first_id = evts[0]["id"]
        archived = self.event_store.archive_event(first_id)
        self.assertTrue(archived)

        evt_after = self.event_store.get_event_by_id(first_id)
        self.assertEqual(evt_after["status"], "ARCHIVED")

    def test_04_convert_event_to_task(self):
        evt = self.event_store.persist_inbound_message("Khiếu nại về hàng bị hỏng khi giao", sender_name="Khách VIP")
        res = self.event_store.convert_event_to_task(evt["id"], store=self.store)
        self.assertTrue(res["ok"])
        self.assertIsNotNone(res["work_item"])

        evt_after = self.event_store.get_event_by_id(evt["id"])
        self.assertEqual(evt_after["status"], "CONVERTED_TASK")

    def test_05_convert_event_to_opportunity(self):
        evt = self.event_store.persist_inbound_message("Cần tìm nguồn vải số lượng lớn cho xưởng may", sender_name="Xưởng Tân Bình")
        res = self.event_store.convert_event_to_opportunity(evt["id"], estimated_value=250000000)
        self.assertTrue(res["ok"])
        self.assertIn("OPP-", res["opportunity_id"])

        evt_after = self.event_store.get_event_by_id(evt["id"])
        self.assertEqual(evt_after["status"], "CONVERTED_OPPORTUNITY")

    def test_06_event_bus_listener_pipeline(self):
        bus = EventBus()
        self.event_store.register_event_bus_listeners(bus)

        emitted_events = []
        bus.on("data_factory:event:created", lambda data: emitted_events.append(data))

        # Giả lập tin nhắn Zalo đến qua EventBus
        bus.emit("channel:message:inbound", {
            "channel": "zalo",
            "content": "Anh muốn hỏi chi phí triển khai hệ thống AI này khoảng bao nhiêu?",
            "sender_id": "zalo-test-99",
            "sender_name": "Sếp Hoàng",
            "group_id": "grp-tech",
            "group_name": "Công Nghệ & Tự Động Hóa"
        })

        self.assertEqual(len(emitted_events), 1)
        created_evt = emitted_events[0]
        self.assertEqual(created_evt["event_type"], "AskedPrice")

        # Kiểm tra sự kiện đã được lưu vào SQLite
        db_evts = self.event_store.get_events(limit=5, search="Sếp Hoàng")
        self.assertEqual(len(db_evts), 1)
        self.assertEqual(db_evts[0]["sender_name"], "Sếp Hoàng")


if __name__ == "__main__":
    unittest.main()
