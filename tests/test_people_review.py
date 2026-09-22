"""
Unit Tests for People Review & Care Quality Engine (SPEC-22 & SPEC-23)
Author: Anh Cơ La (genesis.corp.os@gmail.com)
"""

import unittest
import sqlite3
import time
from heo_harness.core.people_review import get_people_review_engine

class TestPeopleReviewEngine(unittest.TestCase):
    def setUp(self):
        self.engine = get_people_review_engine()

    def test_summary_metrics(self):
        summary = self.engine.get_summary()
        self.assertTrue(summary.get("ok"))
        self.assertIn("people_counts", summary)
        self.assertIn("care_quality", summary)

        counts = summary["people_counts"]
        for ptype in ["EMPLOYEE", "CUSTOMER", "CANDIDATE", "TRAINEE"]:
            self.assertIn(ptype, counts)
            self.assertGreater(counts[ptype]["count"], 0)

    def test_reviews_filtering(self):
        all_revs = self.engine.get_people_reviews()
        self.assertGreaterEqual(len(all_revs), 9)

        emp_revs = self.engine.get_people_reviews("EMPLOYEE")
        self.assertEqual(len(emp_revs), 3)

        cus_revs = self.engine.get_people_reviews("CUSTOMER")
        self.assertEqual(len(cus_revs), 3)

    def test_care_quality_records(self):
        records = self.engine.get_care_quality_records()
        self.assertGreaterEqual(len(records), 3)
        for r in records:
            self.assertIn("care_health_score", r)
            self.assertIn("winning_notes", r)

    def test_broken_promises_and_remind(self):
        promises = self.engine.get_broken_promises("ALL")
        self.assertGreaterEqual(len(promises), 3)

        first_id = promises[0]["id"]
        res = self.engine.remind_broken_promise(first_id, "Test reminder")
        self.assertTrue(res.get("ok"))
        self.assertEqual(res.get("status"), "REMINDED")

    def test_coaching_note_and_atomic_event(self):
        res = self.engine.submit_coaching_note("PR-EMP-01", "Chỉ thị kiểm tra kỹ hợp đồng trước khi ký")
        self.assertTrue(res.get("ok"))
        self.assertIn("Chỉ thị kiểm tra", res.get("coaching_note"))

        # Verify atomic_events has recorded the directive
        with self.engine._get_conn() as conn:
            evt = conn.execute("SELECT * FROM atomic_events WHERE event_type = 'ExecutiveCoachingDirective' ORDER BY timestamp DESC LIMIT 1").fetchone()
            self.assertIsNotNone(evt)
            self.assertIn("Lê Thùy Linh", evt["content"])
            self.assertIn("PR-EMP-01", evt["extracted_entities"])

if __name__ == "__main__":
    unittest.main()
