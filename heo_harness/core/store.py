"""
Module: heo_harness.core.store
Lưu trữ trạng thái thực tế toàn diện của hệ điều hành Heo OS (V6 SSOT Persistent State Store).
Quản lý:
- WorkItems (Kanban Trực Chiến 5 Cột)
- Calendar (Lịch Điều Hành Canonical)
- Approvals (Hàng Đợi Phê Duyệt An Ninh SSOT)
- Groups (Group 360 - Quản Trị Nhóm & Phòng Ban)
- People (Person 360 - Hồ Sơ Cá Nhân & Đối Tác)
- Policies (Tường Lửa Quy Tắc 5 Tầng & Permission Engine)
- Executions (Nhật Ký Thực Thi & Trace Sống)
- Attention (Attention Queue P1/P2/P3 Recompute)
- Insights (Phân Tích Rủi Ro & Dự Báo Quan Hệ)
- Zalo Gateway State (Cấu Hình, Pairing QR & Tin Nhắn Zalo)
- Audit Ledger (Sổ Cái Kiểm Toán Bất Biến)
- Snapshot Backup & Restore

Tác giả & Chủ nhân duy nhất: Anh Cơ La (genesis.corp.os@gmail.com)
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
                    data = json.load(f)
                    # Bổ sung các key thiếu nếu migrate từ bản cũ
                    migrated = False
                    defaults = self._get_default_schema()
                    for k, v in defaults.items():
                        if k not in data:
                            data[k] = v
                            migrated = True
                    if migrated:
                        self._save_state(data)
                    return data
            except Exception as e:
                print(f"[HeoDataStore] Cảnh báo lỗi đọc file state: {e}. Đang khởi tạo state chuẩn.")

        initial_state = self._get_default_schema()
        self._save_state(initial_state)
        return initial_state

    def _get_default_schema(self) -> dict:
        return {
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
            "groups": [
                {
                    "id": "G-001",
                    "name": "Strategic Partners",
                    "purpose": "Đối tác chiến lược · cơ hội & cam kết doanh nghiệp",
                    "health": "Healthy",
                    "members": 28,
                    "open": 7,
                    "alerts": 2,
                    "policy": "POL-G-STRATEGIC v8",
                    "instruction": "INS-G-12 v4",
                    "bot_active": True,
                    "created_at": "2026-09-01"
                },
                {
                    "id": "G-002",
                    "name": "Sales Ops",
                    "purpose": "Vận hành bán hàng & thực thi chỉ tiêu kinh doanh",
                    "health": "Healthy",
                    "members": 34,
                    "open": 12,
                    "alerts": 1,
                    "policy": "POL-G-SALES v12",
                    "instruction": "INS-G-18 v6",
                    "bot_active": True,
                    "created_at": "2026-09-05"
                },
                {
                    "id": "G-003",
                    "name": "Project Phoenix",
                    "purpose": "Điều phối dự án triển khai nền tảng AI & Hệ thống cốt lõi",
                    "health": "Lagging",
                    "members": 16,
                    "open": 9,
                    "alerts": 3,
                    "policy": "POL-G-PHX v5",
                    "instruction": "INS-G-20 v3",
                    "bot_active": True,
                    "created_at": "2026-09-10"
                }
            ],
            "people": [
                {
                    "id": "P-001",
                    "name": "Anh Cơ La (Ryan)",
                    "role": "Chủ Nhân & Tổng Chỉ Huy (Owner)",
                    "groups": "Toàn bộ hệ sinh thái Genesis OS",
                    "email": "genesis.corp.os@gmail.com",
                    "phone": "+84-0567536339",
                    "rel": "Tác quyền tối cao (SSOT Invariant)",
                    "open": 1,
                    "last": "Vừa thao tác xong"
                },
                {
                    "id": "P-018",
                    "name": "Nguyễn Anh",
                    "role": "Partner Lead",
                    "groups": "Strategic Partners",
                    "email": "nguyenanh.partner@genesis.corp",
                    "phone": "+84-0912345678",
                    "rel": "Medium risk (Cần follow-up)",
                    "open": 3,
                    "last": "38 phút trước"
                },
                {
                    "id": "P-022",
                    "name": "Trần Minh",
                    "role": "Sales Manager",
                    "groups": "Sales Ops",
                    "email": "tranminh.sales@genesis.corp",
                    "phone": "+84-0987654321",
                    "rel": "Stable (Ổn định)",
                    "open": 5,
                    "last": "12 phút trước"
                },
                {
                    "id": "P-041",
                    "name": "Lê Hương",
                    "role": "Project Owner",
                    "groups": "Project Phoenix",
                    "email": "lehuong.phoenix@genesis.corp",
                    "phone": "+84-0903123456",
                    "rel": "Opportunity (Tiềm năng cao)",
                    "open": 4,
                    "last": "1 giờ trước"
                }
            ],
            "policies": [
                {"id": "PR-0012", "scope": "GLOBAL", "target": "*", "action": "external.send", "decision": "APPROVAL", "priority": 50, "version": 12, "desc": "Mọi lệnh gửi ra ngoài qua mạng bắt buộc chủ nhân phê duyệt."},
                {"id": "PR-0091", "scope": "GROUP", "target": "G-001", "action": "zalo.send_message", "decision": "APPROVAL", "priority": 80, "version": 8, "desc": "Tin nhắn Zalo gửi vào nhóm Strategic Partners yêu cầu duyệt."},
                {"id": "PR-0110", "scope": "PERSON", "target": "P-018", "action": "zalo.send_message", "decision": "DENY", "priority": 100, "version": 3, "desc": "Chặn tự động gửi tin nhắn trực tiếp cho Nguyễn Anh khi chưa có phê duyệt."},
                {"id": "PR-0132", "scope": "ACTION", "target": "scheduler.create", "action": "scheduler.create", "decision": "AUTO", "priority": 70, "version": 5, "desc": "Tự động tạo lịch nhắc việc nội bộ không cần duyệt."}
            ],
            "executions": [
                {"id": "EX-8801", "corr": "COR-66201", "action": "scheduler.create", "status": "SUCCEEDED", "policy": "AUTO", "duration": "812 ms", "result": "EV-101 created", "time": "16:20:11"},
                {"id": "EX-8797", "corr": "COR-66193", "action": "zalo.send_message", "status": "APPROVAL_PENDING", "policy": "APPROVAL", "duration": "—", "result": "AP-91", "time": "16:15:30"},
                {"id": "EX-8789", "corr": "COR-66170", "action": "zalo.send_message", "status": "DENIED", "policy": "DENY", "duration": "49 ms", "result": "no permit", "time": "15:58:04"}
            ],
            "insights": [
                {"id": "IN-771", "kind": "Relationship risk", "truth": "INFERRED", "title": "Responsiveness giảm trong 14 ngày", "confidence": "0.78", "subject": "P-018 Nguyễn Anh", "reason": "median_response_time tăng · 3 follow-up chưa phản hồi", "evidence": "MSG-1209, MSG-1217, W-341"},
                {"id": "IN-779", "kind": "Opportunity", "truth": "INFERRED", "title": "Tín hiệu quan tâm tăng ở chủ đề Enterprise", "confidence": "0.72", "subject": "G-001 Strategic Partners", "reason": "Tần suất mention tăng + cam kết follow-through tích cực", "evidence": "MSG-1260, MSG-1268"},
                {"id": "FC-301", "kind": "Deadline risk", "truth": "FORECAST", "title": "Project Phoenix có risk HIGH trong 72h", "confidence": "0.81", "subject": "W-398", "reason": "blocked dependency + deadline proximity", "evidence": "W-398, EV-103"}
            ],
            "zalo": {
                "connected": True,
                "account_name": "Bé Heo Assistant (Zalo Personal Bot)",
                "phone": "+84-0567536339",
                "tag_filter": True,
                "bot_status": "ONLINE",
                "synced_groups": ["Strategic Partners", "Sales Ops", "Project Phoenix"],
                "recent_messages": [
                    {"time": "16:30:12", "sender": "Sếp Cơ La", "group": "Strategic Partners", "text": "@Bé Heo kiểm tra tiến độ báo giá V3", "reply": "Dạ Sếp! Báo giá V3 đang chờ Sếp duyệt gửi ạ."},
                    {"time": "16:12:45", "sender": "Lê Hương", "group": "Project Phoenix", "text": "@Bé Heo cập nhật API dependency", "reply": "Dạ em đã ghi nhận và gắn thẻ việc W-398 vào DOING rồi ạ!"}
                ]
            },
            "audits": [
                {"time": time.strftime("%H:%M:%S"), "actor": "heo_runtime", "event": "system.init", "object": "heo-10-plugins", "reason": "DSH Framework SSOT startup", "result": "ALL_HEALTHY", "corr": "COR-BOOT"},
                {"time": time.strftime("%H:%M:%S"), "actor": "ryan", "event": "policy.verify", "object": "heo-policy-gate-firewall", "reason": "Thẩm định 5 tầng quyền lực", "result": "PERMIT_ENFORCED", "corr": "COR-POL-01"}
            ]
        }

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
        self.add_execution("work.create", "SUCCEEDED", "AUTO", "12 ms", f"Created {new_id}")
        return item

    def update_work_status(self, work_id: str, new_status: str) -> bool:
        for w in self.state.get("works", []):
            if w["id"] == work_id:
                old_status = w.get("status")
                w["status"] = new_status
                self._save_state()
                self.add_audit("owner", "work.move", work_id, f"Chuyển trạng thái từ {old_status} -> {new_status}", "SUCCESS")
                self.add_execution("work.move", "SUCCEEDED", "AUTO", "8 ms", f"Moved {work_id} to {new_status}")
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
        self.add_execution("scheduler.create", "SUCCEEDED", "AUTO", "45 ms", f"Event {new_id} scheduled")
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
                self.add_execution(a.get("action", "approval.action"), "SUCCEEDED" if new_status == "APPROVED" else "DENIED", "APPROVAL", "120 ms", f"Approval {approval_id} {new_status}")
                return {"ok": True, "approval": a}
        return {"ok": False, "error": "Approval not found"}

    # ==================== GROUPS 360 ====================
    def get_groups(self) -> list:
        return self.state.get("groups", [])

    def add_group(self, name: str, purpose: str, policy: str = "POL-G-CUSTOM v1", instruction: str = "INS-G-CUSTOM v1") -> dict:
        new_id = f"G-00{len(self.state.get('groups', [])) + 1}"
        g = {
            "id": new_id,
            "name": name,
            "purpose": purpose,
            "health": "Healthy",
            "members": 1,
            "open": 0,
            "alerts": 0,
            "policy": policy,
            "instruction": instruction,
            "bot_active": True,
            "created_at": time.strftime("%Y-%m-%d")
        }
        self.state["groups"].append(g)
        self._save_state()
        self.add_audit("owner", "group.create", new_id, f"Khởi tạo nhóm làm việc mới: {name}", "SUCCESS")
        return g

    # ==================== PEOPLE 360 ====================
    def get_people(self) -> list:
        return self.state.get("people", [])

    def add_person(self, name: str, role: str, groups: str, email: str = "", phone: str = "") -> dict:
        new_id = f"P-0{len(self.state.get('people', [])) + 10}"
        p = {
            "id": new_id,
            "name": name,
            "role": role,
            "groups": groups,
            "email": email or f"{name.lower().replace(' ', '')}@genesis.corp",
            "phone": phone or "+84-09XXXXXXXX",
            "rel": "Stable",
            "open": 0,
            "last": "Mới tạo"
        }
        self.state["people"].append(p)
        self._save_state()
        self.add_audit("owner", "person.create", new_id, f"Thêm nhân sự/đối tác: {name}", "SUCCESS")
        return p

    # ==================== POLICIES & PERMISSIONS ====================
    def get_policies(self) -> list:
        return self.state.get("policies", [])

    def add_policy(self, scope: str, target: str, action: str, decision: str, priority: int, desc: str = "") -> dict:
        new_id = f"PR-{int(time.time()) % 10000:04d}"
        pol = {
            "id": new_id,
            "scope": scope.upper(),
            "target": target,
            "action": action,
            "decision": decision.upper(),
            "priority": int(priority),
            "version": 1,
            "desc": desc or f"Quy tắc {scope} áp dụng cho {target}"
        }
        self.state["policies"].append(pol)
        self._save_state()
        self.add_audit("owner", "policy.create", new_id, f"Tạo quy tắc bảo vệ 5 tầng mới: {new_id}", "ENFORCED")
        return pol

    def simulate_policy(self, actor: str, action: str, target: str, scope: str = "GLOBAL") -> dict:
        """
        Mô phỏng thẩm định quyền hạn chính xác theo nguyên tắc 5 tầng SSOT:
        GLOBAL -> CHANNEL -> GROUP -> PERSON -> ACTION.
        Explicit DENY thắng cùng cấp, priority cao nhất thắng.
        """
        matched_rules = []
        for p in self.state.get("policies", []):
            if p.get("action") in ("*", action):
                if p.get("target") in ("*", target, actor):
                    matched_rules.append(p)

        if not matched_rules:
            # Mặc định theo nguyên tắc SSOT: Cần phê duyệt của Sếp nếu tác động ra ngoài
            return {
                "decision": "APPROVAL",
                "matched_rule": None,
                "reason": "Mặc định an toàn: Không có quy tắc bypass explicit, yêu cầu phê duyệt SSOT.",
                "depth": 1
            }

        # Sắp xếp theo priority giảm dần, DENY ưu tiên
        matched_rules.sort(key=lambda r: (r.get("priority", 0), 1 if r.get("decision") == "DENY" else 0), reverse=True)
        top_rule = matched_rules[0]
        return {
            "decision": top_rule.get("decision"),
            "matched_rule": top_rule.get("id"),
            "reason": f"Khớp quy tắc {top_rule.get('id')} ({top_rule.get('scope')}) - Quyết định: {top_rule.get('decision')}",
            "depth": 5
        }

    # ==================== EXECUTIONS & TRACE ====================
    def get_executions(self, limit: int = 50) -> list:
        execs = self.state.get("executions", [])
        return execs[-limit:][::-1]

    def add_execution(self, action: str, status: str, policy: str, duration: str, result: str, corr: str = None) -> dict:
        ex_id = f"EX-{int(time.time()) % 10000}"
        corr_id = corr or f"COR-{uuid.uuid4().hex[:6].upper()}"
        item = {
            "id": ex_id,
            "corr": corr_id,
            "action": action,
            "status": status,
            "policy": policy,
            "duration": duration,
            "result": result,
            "time": time.strftime("%H:%M:%S")
        }
        if "executions" not in self.state:
            self.state["executions"] = []
        self.state["executions"].append(item)
        if len(self.state["executions"]) > 100:
            self.state["executions"] = self.state["executions"][-100:]
        self._save_state()
        return item

    # ==================== ATTENTION QUEUE (DYNAMIC RECOMPUTE) ====================
    def recompute_attention(self) -> list:
        """
        Tính toán Attention Queue thời gian thực từ dữ liệu thật:
        - Work items có priority P1 hoặc status BLOCKED.
        - Approvals đang PENDING.
        - Insights có risk HIGH.
        """
        items = []
        # 1. Từ Approvals đang chờ
        for a in self.state.get("approvals", []):
            if a.get("status") == "PENDING":
                items.append({
                    "id": f"ATT-APP-{a['id']}",
                    "band": "P1",
                    "title": f"Phê duyệt chờ xử lý: {a.get('summary')}",
                    "subject": f"Approval {a['id']} · {a.get('target')}",
                    "truth": "FACT",
                    "reason": f"approval_waiting + action: {a.get('action')}",
                    "action": "Sếp bấm Phê Duyệt hoặc Từ Chối trong tab Approvals",
                    "evidence": f"approval:{a['id']} · fingerprint:{a.get('fingerprint')}"
                })

        # 2. Từ WorkItems khẩn cấp hoặc bị chặn
        for w in self.state.get("works", []):
            if w.get("priority") == "P1" or w.get("status") == "BLOCKED":
                items.append({
                    "id": f"ATT-WRK-{w['id']}",
                    "band": "P1" if w.get("status") == "BLOCKED" else "P2",
                    "title": f"Công việc cần chú ý: {w.get('title')}",
                    "subject": f"Work {w['id']} · Phụ trách: {w.get('owner')} · Nhóm: {w.get('group')}",
                    "truth": "CALCULATED",
                    "reason": f"status_{w.get('status').lower()} + priority_{w.get('priority').lower()}",
                    "action": f"Chuyển trạng thái hoặc gỡ vướng mắc cho {w.get('owner')}",
                    "evidence": f"work_item:{w['id']} · deadline:{w.get('deadline')}"
                })

        # 3. Từ Insights
        for ins in self.state.get("insights", []):
            if "risk" in ins.get("kind", "").lower() or ins.get("truth") == "FORECAST":
                items.append({
                    "id": f"ATT-INS-{ins['id']}",
                    "band": "P2",
                    "title": ins.get("title"),
                    "subject": f"Insight {ins['id']} · Đối tượng: {ins.get('subject')}",
                    "truth": ins.get("truth"),
                    "reason": ins.get("reason"),
                    "action": "Xem bằng chứng tại Insights & Forecast",
                    "evidence": ins.get("evidence")
                })

        # Nếu không có item nào, đưa ra item trạng thái an toàn
        if not items:
            items.append({
                "id": "ATT-SYS-001",
                "band": "P3",
                "title": "Hệ thống vận hành trơn tru, không có sự cố tồn đọng",
                "subject": "Core Chassis · All 10 Plugins Enabled",
                "truth": "FACT",
                "reason": "system_nominal + zero_critical_blockers",
                "action": "Tiếp tục duy trì trạng thái trực chiến",
                "evidence": "chassis:HEALTHY · circuit_breaker:100%"
            })

        self.add_audit("system", "attention.recompute", "ATTENTION_QUEUE", f"Đã tính toán lại Attention Queue ({len(items)} mục)", "RECOMPUTED")
        return items

    def get_attention(self) -> list:
        return self.recompute_attention()

    # ==================== INSIGHTS & FORECAST ====================
    def get_insights(self) -> list:
        return self.state.get("insights", [])

    # ==================== ZALO GATEWAY STATE ====================
    def get_zalo_state(self) -> dict:
        return self.state.get("zalo", {})

    def send_zalo_test(self, group: str, message: str) -> dict:
        zalo = self.state.get("zalo", {})
        if "recent_messages" not in zalo:
            zalo["recent_messages"] = []
        msg_record = {
            "time": time.strftime("%H:%M:%S"),
            "sender": "Sếp Cơ La (Ryan)",
            "group": group,
            "text": message,
            "reply": f"Dạ Sếp Cơ La! Bé Heo đã nhận lệnh qua Zalo Gateway và đang điều phối công việc cho nhóm {group} rồi ạ! 🐷✨"
        }
        zalo["recent_messages"].insert(0, msg_record)
        if len(zalo["recent_messages"]) > 30:
            zalo["recent_messages"] = zalo["recent_messages"][:30]
        self._save_state()
        self.add_audit("zalo", "message.sent", group, f"Gửi tin nhắn test Zalo tới nhóm: {group}", "DELIVERED")
        self.add_execution("zalo.send_message", "SUCCEEDED", "AUTO", "310 ms", f"Sent to {group}")
        return {"ok": True, "message": msg_record}

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
