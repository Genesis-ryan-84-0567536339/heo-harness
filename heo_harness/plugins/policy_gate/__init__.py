"""
Plugin: heo-policy-gate-firewall
Tường Lửa 5 Tầng Phê Duyệt & Cấp Phép Thực Thi (SSOT Policy Engine)
Tuân thủ nguyên tắc DSH: Mọi hành động gửi tin, gọi công cụ, truy cập dữ liệu đều phải thẩm định qua Policy Gate.
Tác giả: Anh Cơ La (genesis.corp.os@gmail.com)
"""

from heo_harness.core.plugin import BasePlugin, PluginMetadata, PluginCategory, PluginHealthStatus
from heo_harness.core.policy import PolicyEngine, PolicyDecisionType

class PolicyGatePlugin(BasePlugin):
    metadata = PluginMetadata(
        id="heo-policy-gate-firewall",
        name="Tường Lửa 5 Tầng Phê Duyệt & Cấp Phép SSOT",
        version="1.0.0",
        author="Anh Cơ La (Ryan)",
        author_email="genesis.corp.os@gmail.com",
        category=PluginCategory.CORE,
        description="Kiểm soát toàn diện 5 tầng (Global, Channel, Group, Person, Action), cấp Execution Permit cho mọi hoạt động.",
        icon="🛡️",
        default_enabled=True
    )

    def on_load(self) -> None:
        self.engine = self.ctx.get("policy_engine")
        if not self.engine:
            self.engine = PolicyEngine()
            self.ctx.provide("policy_engine", self.engine)
        self.ctx.provide("policy_gate", self)

    def on_enable(self) -> None:
        self.log("🛡️ Tường lửa Policy Gate 5 tầng đã kích hoạt. Bảo vệ 100% tài chính, danh dự và quyền riêng tư của Sếp.")
        self.bus.on("policy:evaluate_request", self.handle_evaluate_request, plugin_id=self.metadata.id)

    def handle_evaluate_request(self, payload: dict) -> dict:
        channel = payload.get("channel", "zalo")
        group_id = payload.get("group_id")
        person_id = payload.get("person_id")
        action = payload.get("action", "unknown")
        context = payload.get("context", {})
        
        result = self.engine.evaluate(
            channel=channel,
            group_id=group_id,
            person_id=person_id,
            action=action,
            context=context
        )
        return result.to_dict()

    def on_disable(self) -> None:
        self.log("⚠️ Policy Gate đang tạm dừng. Hệ thống chuyển sang chế độ cảnh báo giới hạn.")
