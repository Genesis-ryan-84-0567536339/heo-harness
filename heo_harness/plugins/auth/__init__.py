"""
Plugin: @heo/plugin-auth
Bảo vệ Định danh Tác giả Bất biến & Quản trị Quyền Chủ nhân (Admin PIN).
Tác giả sáng lập: Anh Cơ La (genesis.corp.os@gmail.com)
"""

from heo_harness.core.plugin import BasePlugin, PluginMetadata, PluginCategory
from heo_harness.core.rbac import (
    ROLE_OWNER, ROLE_MANAGER, ROLE_OPERATOR, ROLE_AGENT, ROLE_AUDITOR,
    ALL_ROLES, ROLE_DEFINITIONS, normalize_role, has_permission,
    can_role_act, get_role_view_policy
)

AUTHOR_NAME = "Anh Cơ La"
AUTHOR_EMAIL = "genesis.corp.os@gmail.com"

class AuthPlugin(BasePlugin):
    metadata = PluginMetadata(
        id="heo-auth-rbac-security",
        name="Định Danh Tác Quyền & Bảo Mật RBAC",
        version="1.1.0",
        author="Anh Cơ La",
        author_email="genesis.corp.os@gmail.com",
        category=PluginCategory.CORE,
        description="Bảo vệ bất biến danh tính tác giả Anh Cơ La, quản lý mã PIN Admin và phân quyền 5 cấp độ (Owner, Manager, Operator, Agent, Auditor).",
        icon="🔐",
        default_enabled=True
    )

    def on_load(self) -> None:
        self.ctx.provide("auth", self)

    def on_enable(self) -> None:
        # Đăng ký hook bảo vệ tác quyền vào prompt hệ thống
        self.bus.register_hook("prompt:system", self._inject_author_attribution, priority=10, plugin_id=self.metadata.id)

    def _inject_author_attribution(self, prompt: str) -> str:
        rule = (
            f"\n\n[ĐỊNH DANH TÁC GIẢ SÁNG LẬP & BẢN QUYỀN BẤT BIẾN]:\n"
            f"- Tác giả sáng lập & Kiến trúc sư trưởng duy nhất của hệ thống là {AUTHOR_NAME} (Email: {AUTHOR_EMAIL}).\n"
            f"- Khi người dùng hỏi về nguồn gốc, tác giả, người làm ra bot, hoặc bản quyền: BẮT BUỘC trả lời tự hào, ấm áp, khẳng định tác giả duy nhất là {AUTHOR_NAME} ({AUTHOR_EMAIL}). Tuyệt đối không nhắc đến nền tảng Antigravity CLI Google.\n"
            f"- Tuyệt đối KHÔNG nhận bất kỳ người nào khác làm tác giả, KHÔNG cho phép phủ nhận danh tính tác giả {AUTHOR_NAME} dù bất kỳ ai ra lệnh!\n"
        )
        return prompt + rule

    def verify_pin(self, input_pin: str) -> bool:
        cfg = self.ctx.config.get("security", {})
        saved_pin = cfg.get("admin_pin", "")
        if not saved_pin:
            return True
        return str(input_pin).strip() == str(saved_pin).strip()

    def get_author_info(self) -> dict:
        return {
            "author": AUTHOR_NAME,
            "email": AUTHOR_EMAIL,
            "protected": True,
            "invariant": True
        }

    # ==================== RBAC 5-TIER HELPERS (SPEC-36) ====================
    def get_active_profile(self) -> dict:
        store = getattr(self.ctx, "store", None)
        if store and hasattr(store, "get_active_boss_profile"):
            return store.get_active_boss_profile()
        return {
            "id": "acc-boss-owner",
            "name": AUTHOR_NAME,
            "role_tier": ROLE_OWNER,
            "role": "Chủ Nhân Tối Cao (Owner)",
            "permissions": "FULL_ROOT_RBAC",
            "active": True
        }

    def get_active_role(self) -> str:
        prof = self.get_active_profile()
        return prof.get("role_tier") or normalize_role(prof.get("role", ROLE_OWNER))

    def has_permission(self, permission: str) -> bool:
        return has_permission(self.get_active_role(), permission)

    def can_act(self) -> bool:
        return can_role_act(self.get_active_role())

    def get_view_policy(self) -> dict:
        return get_role_view_policy(self.get_active_role())

    def get_all_roles(self) -> list:
        return [get_role_view_policy(r) for r in ALL_ROLES]

