"""
Policy & Permission Engine: Trọng tài Quyền lực & Thẩm định Giấy phép Thực thi (Execution Permits)
Tuân thủ quy tắc SSOT bất biến:
Thứ tự ưu tiên tuyệt đối: GLOBAL -> CHANNEL -> GROUP -> PERSON -> ACTION
Max depth wins, explicit DENY wins tại cùng hoặc cao hơn depth.
Model không bao giờ có thẩm quyền tự cấp permit.
Tác giả: Anh Cơ La (genesis.corp.os@gmail.com)
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import time
import uuid

class PolicyDecisionType(str, Enum):
    AUTO = "AUTO"             # Tự động cho phép chạy ngầm
    APPROVAL = "APPROVAL"     # Cần Sếp (Owner) phê duyệt trước khi chạy
    DENY = "DENY"             # Cấm tuyệt đối, không cấp permit
    OBSERVE = "OBSERVE"       # Chỉ quan sát, không thực thi tác vụ ghi

@dataclass
class PolicyRule:
    id: str
    scope: str               # GLOBAL, CHANNEL, GROUP, PERSON, ACTION
    target: str              # ID của mục tiêu hoặc '*'
    action: str              # Tên action: 'zalo.send_message', 'scheduler.create', v.v.
    decision: PolicyDecisionType
    priority: int = 50       # 0 - 100, cao hơn ưu tiên hơn
    version: int = 1
    description: str = ""

@dataclass
class EvaluationResult:
    decision: PolicyDecisionType
    permit_id: Optional[str]
    rule_id: str
    reason: str
    depth: int
    correlation_id: str
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision": self.decision.value,
            "permit_id": self.permit_id,
            "rule_id": self.rule_id,
            "reason": self.reason,
            "depth": self.depth,
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp
        }

SCOPE_DEPTH = {
    "GLOBAL": 0,
    "CHANNEL": 1,
    "GROUP": 2,
    "PERSON": 3,
    "ACTION": 4
}

class PolicyEngine:
    """
    Hệ thống Quản trị Quyền lực và Cấp Giấy Phép Thực Thi (Execution Permit)
    """

    def __init__(self):
        self.rules: List[PolicyRule] = []
        self._init_default_rules()

    def _init_default_rules(self):
        """Khởi tạo các luật mặc định theo chuẩn SSOT."""
        self.rules = [
            # 1. Luật mặc định toàn cục: Mọi tác vụ gửi tin nhắn ra ngoài bắt buộc qua APPROVAL
            PolicyRule(
                id="PR-GLOBAL-01",
                scope="GLOBAL",
                target="*",
                action="external.send",
                decision=PolicyDecisionType.APPROVAL,
                priority=10,
                description="Mọi tương tác ngoại vi gửi tin cần phê duyệt"
            ),
            # 2. Tác vụ nội bộ (scheduler, read artifact, memory): AUTO
            PolicyRule(
                id="PR-ACTION-AUTO-01",
                scope="ACTION",
                target="scheduler.create",
                action="scheduler.create",
                decision=PolicyDecisionType.AUTO,
                priority=70,
                description="Tạo nhắc việc nội bộ được phép tự động"
            ),
            PolicyRule(
                id="PR-ACTION-AUTO-02",
                scope="ACTION",
                target="artifact.read",
                action="artifact.read",
                decision=PolicyDecisionType.AUTO,
                priority=70,
                description="Đọc tài liệu nội bộ được phép tự động"
            ),
            # 3. Luật riêng theo Person: Người có rủi ro P-018 bị DENY gửi tin nhắn tự động
            PolicyRule(
                id="PR-PERSON-DENY-018",
                scope="PERSON",
                target="P-018",
                action="zalo.send_message",
                decision=PolicyDecisionType.DENY,
                priority=100,
                description="Người P-018 có rủi ro cao, cấm gửi tin nhắn trực tiếp"
            ),
            PolicyRule(
                id="PR-PERSON-DENY-018-WA",
                scope="PERSON",
                target="P-018",
                action="whatsapp.send_message",
                decision=PolicyDecisionType.DENY,
                priority=100,
                description="Cấm WhatsApp tới P-018"
            ),
            # 4. Kênh chat Zalo nội bộ của nhóm Sales: APPROVAL
            PolicyRule(
                id="PR-GROUP-SALES",
                scope="GROUP",
                target="G-002",
                action="zalo.send_message",
                decision=PolicyDecisionType.APPROVAL,
                priority=80,
                description="Nhóm Sales Ops cần duyệt trước khi gửi tin"
            )
        ]

    def add_rule(self, rule: PolicyRule):
        self.rules.append(rule)

    def evaluate(
        self,
        action: str,
        channel: str = "*",
        group: str = "*",
        person: str = "*",
        correlation_id: Optional[str] = None
    ) -> EvaluationResult:
        """
        Thẩm định chính sách xác định (Deterministic Precedence Evaluation).
        Precedence: GLOBAL -> CHANNEL -> GROUP -> PERSON -> ACTION
        Max depth wins, explicit DENY wins at highest depth, priority DESC.
        """
        corr_id = correlation_id or f"COR-{uuid.uuid4().hex[:8].upper()}"

        applicable_rules: List[PolicyRule] = []

        for r in self.rules:
            # So khớp action
            if r.action != "*" and r.action != action and not (r.action == "external.send" and "send_message" in action):
                continue

            # So khớp target theo scope
            matched = False
            if r.scope == "GLOBAL":
                matched = True
            elif r.scope == "CHANNEL" and (r.target == "*" or r.target == channel):
                matched = True
            elif r.scope == "GROUP" and (r.target == "*" or r.target == group):
                matched = True
            elif r.scope == "PERSON" and (r.target == "*" or r.target == person):
                matched = True
            elif r.scope == "ACTION" and (r.target == "*" or r.target == action):
                matched = True

            if matched:
                applicable_rules.append(r)

        if not applicable_rules:
            # Fallback mặc định: Tác vụ ngoại vi cần APPROVAL, nội bộ AUTO
            is_outbound = "send" in action or "delete" in action or "update" in action
            dec = PolicyDecisionType.APPROVAL if is_outbound else PolicyDecisionType.AUTO
            permit = f"PERMIT-{uuid.uuid4().hex[:8].upper()}" if dec != PolicyDecisionType.DENY else None
            return EvaluationResult(
                decision=dec,
                permit_id=permit,
                rule_id="DEFAULT_FALLBACK",
                reason="Không có rule cụ thể, áp dụng fallback an toàn",
                depth=0,
                correlation_id=corr_id
            )

        # Sắp xếp theo:
        # 1. Scope Depth (DESC)
        # 2. Explicit DENY (ưu tiên DENY trước nếu cùng depth)
        # 3. Priority (DESC)
        def sort_key(rule: PolicyRule):
            depth = SCOPE_DEPTH.get(rule.scope, 0)
            is_deny = 1 if rule.decision == PolicyDecisionType.DENY else 0
            return (depth, is_deny, rule.priority)

        applicable_rules.sort(key=sort_key, reverse=True)
        winning_rule = applicable_rules[0]

        decision = winning_rule.decision
        permit_id = None
        if decision in [PolicyDecisionType.AUTO, PolicyDecisionType.APPROVAL]:
            permit_id = f"PERMIT-{uuid.uuid4().hex[:8].upper()}"

        reason = (
            f"Chiến thắng tại độ sâu {winning_rule.scope} (Depth={SCOPE_DEPTH.get(winning_rule.scope, 0)}) "
            f"qua luật {winning_rule.id}: {winning_rule.description or winning_rule.decision.value}"
        )

        return EvaluationResult(
            decision=decision,
            permit_id=permit_id,
            rule_id=winning_rule.id,
            reason=reason,
            depth=SCOPE_DEPTH.get(winning_rule.scope, 0),
            correlation_id=corr_id
        )
