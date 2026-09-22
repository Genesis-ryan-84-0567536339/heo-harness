"""
Module: heo_harness.core.rbac
Hệ thống Phân Quyền RBAC Phân Tầng (SPEC-36)
Tuân thủ chuẩn SSOT Mục H2 Spec LOCKED v2.2:
- Owner: thấy toàn cảnh
- Manager: thấy team
- Operator: thấy hàng đợi việc
- Agent nhân viên: chỉ thấy khách mình được phân
- Auditor: xem log, không hành động

Nguyên tắc: Dữ liệu đánh giá nhân sự và ứng viên phải bị khoá chặt hơn dữ liệu cơ hội.
"""

from typing import Dict, List, Any, Optional

# 5 Canonical Roles theo Mục H2
ROLE_OWNER = "owner"
ROLE_MANAGER = "manager"
ROLE_OPERATOR = "operator"
ROLE_AGENT = "agent"
ROLE_AUDITOR = "auditor"

ALL_ROLES = [ROLE_OWNER, ROLE_MANAGER, ROLE_OPERATOR, ROLE_AGENT, ROLE_AUDITOR]

# Role Metadata & Policy Definitions
ROLE_DEFINITIONS: Dict[str, Dict[str, Any]] = {
    ROLE_OWNER: {
        "id": ROLE_OWNER,
        "name": "Chủ Nhân Tối Cao (Owner)",
        "badge": "Full Root RBAC",
        "description": "Thấy toàn cảnh, toàn quyền điều hành hệ thống, phê duyệt tối cao và bảo vệ tác quyền sáng lập.",
        "icon": "👑",
        "color": "#f59e0b",
        "can_act": True,
        "can_view_people_review": True,
        "can_view_commercial": True,
        "can_view_system_config": True,
        "can_execute_cli": True,
        "inbox_scope": "all",
    },
    ROLE_MANAGER: {
        "id": ROLE_MANAGER,
        "name": "Quản Lý Đội Ngũ (Manager)",
        "badge": "Quản Trị Nhóm",
        "description": "Thấy toàn bộ hoạt động của team, chất lượng chăm sóc, đôn đốc cam kết; không can thiệp PIN Admin tối cao.",
        "icon": "👔",
        "color": "#6366f1",
        "can_act": True,
        "can_view_people_review": True,
        "can_view_commercial": True,
        "can_view_system_config": False,
        "can_execute_cli": False,
        "inbox_scope": "team",
    },
    ROLE_OPERATOR: {
        "id": ROLE_OPERATOR,
        "name": "Điều Phối Tác Nghiệp (Operator)",
        "badge": "Hàng Đợi Việc",
        "description": "Thấy hàng đợi việc (Inbox tác nghiệp, cơ hội mậu dịch cần xử lý). Khoá chặt đánh giá nhân sự.",
        "icon": "🎯",
        "color": "#10b981",
        "can_act": True,
        "can_view_people_review": False,  # Khoá chặt theo Mục H2
        "can_view_commercial": True,
        "can_view_system_config": False,
        "can_execute_cli": False,
        "inbox_scope": "queue",
    },
    ROLE_AGENT: {
        "id": ROLE_AGENT,
        "name": "Nhân Viên Tác Chiến (Agent)",
        "badge": "Khách Phân Công",
        "description": "Chỉ thấy khách hàng và hội thoại mình được phân công. Khoá chặt đánh giá nhân sự & cấu hình.",
        "icon": "💼",
        "color": "#06b6d4",
        "can_act": True,
        "can_view_people_review": False,  # Khoá chặt theo Mục H2
        "can_view_commercial": False,
        "can_view_system_config": False,
        "can_execute_cli": False,
        "inbox_scope": "assigned",
    },
    ROLE_AUDITOR: {
        "id": ROLE_AUDITOR,
        "name": "Kiểm Toán & Thanh Tra (Auditor)",
        "badge": "Chỉ Đọc (Read-Only)",
        "description": "Xem logs, audit trail, báo cáo tuân thủ, nhưng tuyệt đối không được thực thi hành động.",
        "icon": "🛡️",
        "color": "#ef4444",
        "can_act": False,  # Chặn mọi hành động can thiệp dữ liệu theo Mục H2
        "can_view_people_review": True,  # Xem logs / audit trail
        "can_view_commercial": True,
        "can_view_system_config": False,
        "can_execute_cli": False,
        "inbox_scope": "audit",
    }
}

# Detailed Permission Matrix
PERMISSIONS: Dict[str, List[str]] = {
    # System & Auth
    "system.config.read": [ROLE_OWNER, ROLE_MANAGER, ROLE_AUDITOR],
    "system.config.write": [ROLE_OWNER],
    "system.terminal.execute": [ROLE_OWNER],
    "system.plugins.toggle": [ROLE_OWNER],
    
    # People Review / Care Quality (Khoá chặt theo H2)
    "people_review.view": [ROLE_OWNER, ROLE_MANAGER, ROLE_AUDITOR],
    "people_review.coaching": [ROLE_OWNER, ROLE_MANAGER],
    "people_review.resolve_promise": [ROLE_OWNER, ROLE_MANAGER],
    
    # Commercial & Opportunities
    "commercial.view": [ROLE_OWNER, ROLE_MANAGER, ROLE_OPERATOR, ROLE_AUDITOR],
    "commercial.action": [ROLE_OWNER, ROLE_MANAGER, ROLE_OPERATOR],
    
    # Inbox & Communication
    "inbox.view_all": [ROLE_OWNER, ROLE_MANAGER, ROLE_OPERATOR, ROLE_AUDITOR],
    "inbox.view_assigned": [ROLE_OWNER, ROLE_MANAGER, ROLE_OPERATOR, ROLE_AGENT, ROLE_AUDITOR],
    "inbox.send_message": [ROLE_OWNER, ROLE_MANAGER, ROLE_OPERATOR, ROLE_AGENT],
    
    # Logs & Audit
    "logs.view": [ROLE_OWNER, ROLE_MANAGER, ROLE_OPERATOR, ROLE_AGENT, ROLE_AUDITOR],
    "logs.clear": [ROLE_OWNER]
}

def normalize_role(role_raw: str) -> str:
    """Ánh xạ tên role bất kỳ, permissions string hoặc role_tier về 1 trong 5 Canonical Roles"""
    r = str(role_raw or "").lower()
    if "owner" in r or "chủ nhân" in r or "full_root" in r:
        return ROLE_OWNER
    if "manager" in r or "phó ban" in r or "co-executive" in r or "quản lý" in r or "trưởng phòng" in r:
        return ROLE_MANAGER
    if "operator" in r or "điều phối" in r or "trực ban" in r or "trực chiến" in r or "hàng đợi" in r:
        return ROLE_OPERATOR
    if "agent" in r or "nhân viên" in r or "assigned" in r or "kinh doanh" in r:
        return ROLE_AGENT
    if "auditor" in r or "kiểm toán" in r or "thanh tra" in r or "khách" in r or "guest" in r or "read_only" in r:
        return ROLE_AUDITOR
    return ROLE_OPERATOR

def has_permission(role: str, permission: str) -> bool:
    norm_role = normalize_role(role)
    if norm_role == ROLE_OWNER:
        return True  # Owner có toàn quyền
    allowed_roles = PERMISSIONS.get(permission, [])
    return norm_role in allowed_roles

def can_role_act(role: str) -> bool:
    """Auditor không được thực hiện hành động ghi/sửa/phê duyệt (Mục H2)"""
    norm_role = normalize_role(role)
    return ROLE_DEFINITIONS.get(norm_role, {}).get("can_act", True)

def get_role_view_policy(role: str) -> Dict[str, Any]:
    norm_role = normalize_role(role)
    meta = ROLE_DEFINITIONS.get(norm_role, ROLE_DEFINITIONS[ROLE_OPERATOR])
    return {
        "role": norm_role,
        "name": meta["name"],
        "badge": meta["badge"],
        "description": meta["description"],
        "icon": meta["icon"],
        "color": meta["color"],
        "can_act": meta["can_act"],
        "can_view_people_review": meta["can_view_people_review"],
        "can_view_commercial": meta["can_view_commercial"],
        "can_view_system_config": meta["can_view_system_config"],
        "can_execute_cli": meta["can_execute_cli"],
        "inbox_scope": meta["inbox_scope"],
        "allowed_permissions": [p for p, roles in PERMISSIONS.items() if norm_role in roles or norm_role == ROLE_OWNER]
    }

def get_canonical_profiles(boss_name: str = "Anh Cơ La (Ryan)") -> List[Dict[str, Any]]:
    """Trả về danh sách 5 profile mẫu đại diện chuẩn 5 tầng RBAC"""
    name_display = boss_name if ("Cơ La" in boss_name or "Ryan" in boss_name) else f"{boss_name} (Chính)"
    return [
        {
            "id": "acc-boss-owner",
            "name": name_display,
            "role_tier": ROLE_OWNER,
            "role": "Chủ Nhân Tối Cao (Owner)",
            "email": "genesis.corp.os@gmail.com",
            "badge": "Tác Quyền Duy Nhất",
            "avatar": "👑",
            "permissions": "FULL_ROOT_RBAC",
            "active": True
        },
        {
            "id": "acc-boss-manager",
            "name": "Ban Điều Hành & Trưởng Phòng",
            "role_tier": ROLE_MANAGER,
            "role": "Quản Lý Đội Ngũ (Manager)",
            "email": "manager@genesis.corp",
            "badge": "Quản Trị Nhóm",
            "avatar": "👔",
            "permissions": "TEAM_MANAGEMENT_APPROVAL",
            "active": False
        },
        {
            "id": "acc-boss-operator",
            "name": "Trực Ban Tác Nghiệp Hàng Đợi",
            "role_tier": ROLE_OPERATOR,
            "role": "Điều Phối Tác Nghiệp (Operator)",
            "email": "operator@genesis.corp",
            "badge": "Hàng Đợi Việc",
            "avatar": "🎯",
            "permissions": "QUEUE_DISPATCH_COMMERCIAL",
            "active": False
        },
        {
            "id": "acc-boss-agent",
            "name": "Chuyên Viên Kinh Doanh (Nguyễn Văn A)",
            "role_tier": ROLE_AGENT,
            "role": "Nhân Viên Tác Chiến (Agent)",
            "email": "agent.nguyen@genesis.corp",
            "badge": "Khách Phân Công",
            "avatar": "💼",
            "permissions": "ASSIGNED_ONLY",
            "active": False
        },
        {
            "id": "acc-boss-auditor",
            "name": "Thanh Tra & Kiểm Toán Độc Lập",
            "role_tier": ROLE_AUDITOR,
            "role": "Kiểm Toán & Thanh Tra (Auditor)",
            "email": "auditor@genesis.corp",
            "badge": "Chỉ Đọc (Read-Only)",
            "avatar": "🛡️",
            "permissions": "AUDIT_READONLY",
            "active": False
        }
    ]
