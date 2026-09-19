"""
Module: heo_harness.core.store
Lưu trữ trạng thái thực tế của hệ điều hành Heo OS (State Store Persistence).
Quản lý WorkItems (Kanban), Calendar, Approvals, Audit Ledger và Artifacts.
Tự động duy trì trạng thái vĩnh cửu tại data/heo_state.json.
Tác giả: Anh Cơ La (genesis.corp.os@gmail.com)
"""

import json
import os
import time
import uuid
import shutil

class HeoDataStore:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = os.path.abspath(data_dir)
        os.makedirs(self.data_dir, exist_ok=True)
        self.state_file = os.path.join(self.data_dir, "heo_state.json")
        self.state = self._load_initial_state()

    def _load_initial_state(self) -> dict:
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"[HeoDataStore] Cảnh báo lỗi đọc file state: {e}. Đang khởi tạo state chuẩn.")

        # Dữ liệu khởi tạo chuẩn V6 SSOT
        initial_state = {
            "works": [
                {"id": "W-341", "title": "Gửi báo giá V3 cho Nguyễn Anh", "status": "BLOCKED", "owner": "Anh Cơ La", "deadline": "Hôm nay 09:00", "group": "Strategic Partners", "priority": "P1"},
                {"id": "W-398", "title": "Chốt dependency API đối tác", "status": "DOING", "owner": "Lê Hương", "deadline": "19/09 15:00", "group": "Project Phoenix", "priority": "P2"},
                {"id": "W-403", "title": "Xác nhận lịch review Sales Ops", "status": "TODO", "owner": "Trần Minh", "deadline": "18/09 14:00", "group": "Sales Ops", "priority": "P2"},
                {"id": "W-405", "title": "Tổng hợp meeting notes tự động", "status": "REVIEW", "owner": "Bé Heo", "deadline": "Hôm nay 17:00", "group": "Sales Ops", "priority": "P3"},
                {"id": "W-411", "title": "Theo dõi phản hồi đối tác qua Zalo", "status": "WAITING", "owner": "Bé Heo", "deadline": "20/09 10:00", "group": "Strategic Partners", "priority": "P3"}
            ],
            "calendar": [
                {"id": "EV-101", "title": "Follow-up báo giá", "type": "Reminder", "timezone": "Asia/Ho_Chi_Minh", "when": "T3 18 09:00", "delivery": "Internal owner", "status": "SCHEDULED"},
                {"id": "EV-102", "title": "Sales review định kỳ", "type": "Meeting", "timezone": "Asia/Ho_Chi_Minh", "when": "T3 18 14:00", "delivery": "Internal owner", "status": "CONFIRMED"},
                {"id": "EV-103", "title": "API dependency deadline", "type": "Deadline", "timezone": "Asia/Ho_Chi_Minh", "when": "T4 19 15:00", "delivery": "Internal owner", "status": "WARNING"},
                {"id": "EV-104", "title": "Review notes tổng hợp", "type": "Checkpoint", "timezone": "Asia/Ho_Chi_Minh", "when": "T2 17 17:00", "delivery": "Internal owner", "status": "SCHEDULED"}
            ],
            "approvals": [
                {
                    "id": "AP-91",
                    "ttl": "06:12",
                    "action": "zalo.send_message",
                    "target": "Nguyễn Anh · Strategic Partners",
                    "summary": "Gửi file Báo giá V3 cùng lời nhắn follow-up tự động",
                    "why": "Work W-341 quá hạn và chủ nhiệm yêu cầu chuẩn bị follow-up",
                    "data": "Tên người nhận, nội dung tin nhắn, artifact AF-22",
                    "resource": "Zalo Gateway · Outbound permit",
                    "fingerprint": "d18e…77ab",
                    "status": "PENDING"
                },
                {
                    "id": "AP-94",
                    "ttl": "14:48",
                    "action": "artifact.send",
                    "target": "Group Sales Ops",
                    "summary": "Gửi biên bản họp đã xác nhận cho nhóm bán hàng",
                    "why": "Event EV-88 chuyển HELD, artifact AF-31 đã sẵn sàng",
                    "data": "Group ID, file AF-31, caption",
                    "resource": "Zalo Gateway · Session receipt",
                    "fingerprint": "a2c4…9ef1",
                    "status": "PENDING"
                },
                {
                    "id": "AP-97",
                    "ttl": "21:05",
                    "action": "scheduler.create",
                    "target": "Internal owner reminder",
                    "summary": "Tạo lịch nhắc nhở 09:00 sáng mai cho Anh Cơ La",
                    "why": "Commitment C-155 chưa có hành động tiếp nối",
                    "data": "Work ref + schedule timestamp",
                    "resource": "Internal · Không gọi mạng ngoài",
                    "fingerprint": "30be…151a",
                    "status": "PENDING"
                }
            ],
            "audits": [
                {"time": time.strftime("%H:%M:%S"), "actor": "heo_runtime", "event": "system.init", "object": "heo-10-plugins", "reason": "DSH Framework SSOT startup", "result": "ALL_HEALTHY", "corr": "COR-BOOT"},
                {"time": time.strftime("%H:%M:%S"), "actor": "ryan", "event": "policy.verify", "object": "heo-policy-gate-firewall", "reason": "Thẩm định 5 tầng quyền lực", "result": "PERMIT_ENFORCED", "corr": "COR-POL-01"}
            ]
        }
        self._save_state(initial_state)
        return initial_state

    def _save_state(self, state_dict: dict = None):
        if state_dict is None:
            state_dict = self.state
        try:
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(state_dict, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[HeoDataStore] Lỗi lưu state_file: {e}")

    # ==================== WORK OS (KANBAN) ====================
    def get_works(self) -> list:
        return self.state.get("works", [])

    def add_work(self, title: str, owner: str = "Anh Cơ La", priority: str = "P2", deadline: str = "Hôm nay 18:00", group: str = "Strategic Partners", note: str = "") -> dict:
        new_id = f"W-{int(time.time()) % 10000}"
        item = {
            "id": new_id,
            "title": title,
            "status": "TODO",
            "owner": owner,
            "deadline": deadline,
            "group": group,
            "priority": priority,
            "note": note,
            "created_at": time.time()
        }
        self.state["works"].insert(0, item)
        self._save_state()
        self.add_audit("owner", "work.create", new_id, f"Tạo công việc mới: {title}", "SUCCESS")
        return item

    def update_work_status(self, work_id: str, new_status: str) -> bool:
        for w in self.state.get("works", []):
            if w["id"] == work_id:
                old_status = w.get("status")
                w["status"] = new_status
                self._save_state()
                self.add_audit("owner", "work.move", work_id, f"Chuyển trạng thái từ {old_status} -> {new_status}", "SUCCESS")
                return True
        return False

    # ==================== CALENDAR ====================
    def get_calendar(self) -> list:
        return self.state.get("calendar", [])

    def add_calendar_event(self, title: str, event_type: str = "Reminder", when: str = "Hôm nay 15:00", timezone: str = "Asia/Ho_Chi_Minh", delivery: str = "Internal owner") -> dict:
        new_id = f"EV-{int(time.time()) % 10000}"
        ev = {
            "id": new_id,
            "title": title,
            "type": event_type,
            "timezone": timezone,
            "when": when,
            "delivery": delivery,
            "status": "SCHEDULED",
            "created_at": time.time()
        }
        self.state["calendar"].append(ev)
        self._save_state()
        self.add_audit("owner", "calendar.create", new_id, f"Lên lịch sự kiện: {title}", "SCHEDULED")
        return ev

    # ==================== APPROVALS ====================
    def get_approvals(self, status: str = None) -> list:
        all_appr = self.state.get("approvals", [])
        if status:
            return [a for a in all_appr if a.get("status") == status]
        return all_appr

    def action_approval(self, approval_id: str, action_type: str) -> dict:
        for a in self.state.get("approvals", []):
            if a["id"] == approval_id:
                new_status = "APPROVED" if action_type == "approve" else "DENIED"
                a["status"] = new_status
                a["resolved_at"] = time.strftime("%H:%M:%S")
                self._save_state()
                self.add_audit("owner", f"approval.{action_type}", approval_id, f"Quyết định của Sếp: {new_status}", "EXECUTED")
                return {"ok": True, "approval": a}
        return {"ok": False, "error": "Approval not found"}

    # ==================== AUDIT LEDGER ====================
    def get_audits(self, limit: int = 50) -> list:
        audits = self.state.get("audits", [])
        return audits[-limit:][::-1]

    def add_audit(self, actor: str, event: str, object_id: str, reason: str, result: str, corr: str = None):
        corr_id = corr or f"COR-{uuid.uuid4().hex[:6].upper()}"
        entry = {
            "time": time.strftime("%H:%M:%S"),
            "actor": actor,
            "event": event,
            "object": object_id,
            "reason": reason,
            "result": result,
            "corr": corr_id
        }
        if "audits" not in self.state:
            self.state["audits"] = []
        self.state["audits"].append(entry)
        if len(self.state["audits"]) > 200:
            self.state["audits"] = self.state["audits"][-200:]
        self._save_state()

    # ==================== BACKUP & RESTORE ====================
    def create_backup(self) -> dict:
        backup_id = f"BK-{time.strftime('%Y%m%d-%H%M%S')}"
        backup_dir = os.path.join(self.data_dir, "backups")
        os.makedirs(backup_dir, exist_ok=True)
        backup_file = os.path.join(backup_dir, f"{backup_id}.json")
        try:
            with open(backup_file, "w", encoding="utf-8") as f:
                json.dump(self.state, f, ensure_ascii=False, indent=2)
            self.add_audit("system", "backup.created", backup_id, "Tạo snapshot dữ liệu an toàn", "SUCCESS")
            return {
                "ok": True,
                "backup_id": backup_id,
                "path": backup_file,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        except Exception as e:
            return {"ok": False, "error": str(e)}
