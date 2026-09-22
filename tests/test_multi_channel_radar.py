# -*- coding: utf-8 -*-
"""
Kiểm thử tự động cho SPEC-04: Multi-Channel Radar & Universal Ingestion Engine.
Tác giả & Chủ nhân duy nhất: Anh Cơ La (genesis.corp.os@gmail.com)
"""

import unittest
import tempfile
import os
import shutil
import time
from heo_harness.core.channel_radar import ChannelRadarEngine

class TestMultiChannelRadar(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, "test_radar.db")
        self.radar = ChannelRadarEngine.get_instance(db_path=self.db_path)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_default_channels_seeded(self):
        channels = self.radar.get_channels_status()
        self.assertGreaterEqual(len(channels), 5)
        channel_keys = [c["channel"] for c in channels]
        self.assertIn("zalo", channel_keys)
        self.assertIn("whatsapp", channel_keys)
        self.assertIn("telegram", channel_keys)
        self.assertIn("facebook", channel_keys)
        self.assertIn("generic_webhook", channel_keys)

    def test_telegram_update_ingestion(self):
        telegram_payload = {
            "update_id": 987654,
            "message": {
                "message_id": 101,
                "from": {
                    "id": 12345678,
                    "first_name": "Minh",
                    "last_name": "Đỗ",
                    "username": "minh_do"
                },
                "chat": {
                    "id": -100998877,
                    "title": "Hiệp Hội Phần Mềm Sài Gòn",
                    "type": "supergroup"
                },
                "text": "@heo_bot Tôi cần báo giá triển khai 50 tài khoản Gen-Harness cho công ty",
                "date": time.time()
            }
        }
        res = self.radar.ingest_telegram_update(telegram_payload)
        self.assertTrue(res["ok"])
        self.assertEqual(res["channel"], "telegram")
        self.assertEqual(res["sender_name"], "Minh Đỗ")
        self.assertTrue(res["log_id"].startswith("RADAR-"))

        # Verify radar log recorded
        logs = self.radar.get_recent_logs(channel="telegram")
        self.assertGreaterEqual(len(logs), 1)
        self.assertEqual(logs[0]["id"], res["log_id"])
        self.assertTrue(logs[0]["is_mention"])

    def test_facebook_webhook_ingestion(self):
        fb_payload = {
            "object": "page",
            "entry": [
                {
                    "id": "PAGE_ID_12345",
                    "time": 1727000000,
                    "messaging": [
                        {
                            "sender": {"id": "USER_FB_999"},
                            "recipient": {"id": "PAGE_ID_12345"},
                            "timestamp": 1727000000000,
                            "message": {
                                "mid": "mid.1234567890",
                                "text": "Chào ad, giải pháp này có bảo hành 12 tháng không?"
                            }
                        }
                    ]
                }
            ]
        }
        res = self.radar.ingest_facebook_entry(fb_payload)
        self.assertTrue(res["ok"])
        self.assertEqual(res["channel"], "facebook")
        self.assertEqual(res["processed_count"], 1)

        logs = self.radar.get_recent_logs(channel="facebook")
        self.assertGreaterEqual(len(logs), 1)
        self.assertIn("USER_FB_999", logs[0]["sender_id"])

    def test_generic_webhook_and_simulation(self):
        # Generic webhook
        webhook_payload = {
            "channel": "discord",
            "sender_name": "Hoàng Nam",
            "text": "Đã chuyển tiền hợp đồng 20 triệu qua ngân hàng",
            "group_id": "vip_lounge"
        }
        res = self.radar.ingest_generic_webhook(webhook_payload)
        self.assertTrue(res["ok"])
        self.assertEqual(res["channel"], "discord")
        self.assertEqual(res["sender_name"], "Hoàng Nam")

        # Simulation ping
        sim_res = self.radar.simulate_inbound_ping(
            channel="linkedin",
            sender_name="John Doe",
            text="Interested in your AI Executive OS enterprise licensing",
            group_name="InMail"
        )
        self.assertTrue(sim_res["ok"])
        self.assertEqual(sim_res["channel"], "linkedin")

    def test_channel_configuration_and_fb_verification(self):
        # Update config
        ok = self.radar.configure_channel("telegram", {
            "token": "bot123456:new_secret_token",
            "listen_mode": "MENTION_ONLY"
        })
        self.assertTrue(ok)

        # Verify challenge
        chal = self.radar.verify_facebook_webhook("subscribe", "heo_fb_verify_token", "challenge_12345")
        self.assertEqual(chal, "challenge_12345")

        # Wrong token fails
        invalid = self.radar.verify_facebook_webhook("subscribe", "wrong_token", "challenge_12345")
        self.assertIsNone(invalid)

if __name__ == "__main__":
    unittest.main()
