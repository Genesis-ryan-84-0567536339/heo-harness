"""
PluginManager: Trình Quản Lý & Điều Phối Plugin Toàn Diện
Cung cấp Dynamic Loading, Bật/Tắt nóng, Cô lập lỗi, Quét thư mục và Kho Marketplace.
"""

from typing import Dict, List, Any, Optional, Type
import os
import sys
import importlib
import inspect
import threading
import traceback

from heo_harness.core.context import Context
from heo_harness.core.bus import EventBus
from heo_harness.core.plugin import BasePlugin, PluginHealthStatus, PluginCategory

# Kho Catalog Marketplace có sẵn để người dùng có thể cài đặt thêm trên Web UI
MARKETPLACE_CATALOG: List[Dict[str, Any]] = [
    {
        "id": "heo-provider-antigravity-brain",
        "name": "Core Agent: Google Antigravity CLI (0đ Token API)",
        "version": "1.0.0",
        "author": "Anh Cơ La (Ryan)",
        "category": "provider",
        "description": "Lõi suy luận chính của Heo qua Antigravity CLI gói tháng (Gemini 3.8 / Pro / Sonnet), chi phí 0đ API.",
        "icon": "🌟",
        "installed": True,
        "is_default": True
    },
    {
        "id": "heo-provider-deepseek-reasoning",
        "name": "Secondary Provider: DeepSeek V3 / R1 (Reasoning)",
        "version": "1.0.0",
        "author": "Anh Cơ La (Ryan)",
        "category": "provider",
        "description": "Mô hình dự phòng giá rẻ qua API DeepSeek khi cần phân tích mã nguồn hoặc chạy batch tác vụ phụ.",
        "icon": "⚡",
        "installed": False,
        "is_default": False
    },
    {
        "id": "heo-channel-zalo-gateway",
        "name": "Kênh Kết Nối Zalo Cá Nhân (Bảo Mật QR)",
        "version": "1.0.0",
        "author": "Anh Cơ La (Ryan)",
        "category": "channel",
        "description": "Kết nối và đồng bộ tin nhắn cá nhân / nhóm Zalo, mã hóa phiên làm việc, tự động tương tác.",
        "icon": "💬",
        "installed": True,
        "is_default": True
    },
    {
        "id": "heo-policy-gate-firewall",
        "name": "Tường Lửa 5 Tầng Phê Duyệt & Cấp Phép SSOT",
        "version": "1.0.0",
        "author": "Anh Cơ La (Ryan)",
        "category": "core",
        "description": "Kiểm soát toàn diện 5 tầng (Global, Channel, Group, Person, Action), cấp Execution Permit cho mọi hoạt động.",
        "icon": "🛡️",
        "installed": True,
        "is_default": True
    },
    {
        "id": "heo-persona-heo-attitude",
        "name": "Danh Xưng & 7 Persona Thái Độ Bé Heo",
        "version": "1.0.0",
        "author": "Anh Cơ La (Ryan)",
        "category": "core",
        "description": "Quản lý danh xưng Sếp Cơ La, tên bot, văn hóa giới thiệu nhóm và 7 phong cách thái độ ứng xử.",
        "icon": "🎭",
        "installed": True,
        "is_default": True
    },
    {
        "id": "heo-auth-rbac-security",
        "name": "Định Danh Tác Quyền & Bảo Mật RBAC",
        "version": "1.0.0",
        "author": "Anh Cơ La (Ryan)",
        "category": "core",
        "description": "Bảo vệ bất biến danh tính tác giả Anh Cơ La, quản lý mã PIN Admin và phân quyền Chủ nhân.",
        "icon": "🔐",
        "installed": True,
        "is_default": True
    },
    {
        "id": "heo-tool-office-reporter",
        "name": "Bộ Công Cụ Văn Phòng (Word, Excel, PDF)",
        "version": "1.0.0",
        "author": "Anh Cơ La (Ryan)",
        "category": "tool",
        "description": "Đọc, tạo lập và xuất báo cáo tài liệu tự động dưới các định dạng DOCX, XLSX, PDF theo chuẩn doanh nghiệp.",
        "icon": "📊",
        "installed": True,
        "is_default": True
    },
    {
        "id": "heo-tool-media-processor",
        "name": "Bộ Xử Lý Đa Phương Tiện (Image, Voice, Video)",
        "version": "1.0.0",
        "author": "Anh Cơ La (Ryan)",
        "category": "tool",
        "description": "Nhận dạng giọng nói voice message, phân tích ảnh chụp màn hình và chuyển đổi định dạng tệp.",
        "icon": "🎨",
        "installed": True,
        "is_default": True
    },
    {
        "id": "heo-channel-whatsapp-gateway",
        "name": "Kênh Kết Nối WhatsApp Gateway (Multi-Device & QR)",
        "version": "1.0.0",
        "author": "Anh Cơ La (Ryan)",
        "category": "channel",
        "description": "Mở rộng khả năng tiếp cận đối tác quốc tế qua giao thức WhatsApp Multi-Device và mã QR bảo mật.",
        "icon": "📱",
        "installed": True,
        "is_default": True
    },
    {
        "id": "heo-tool-crm-pipeline",
        "name": "HubSpot & Customer Pipeline CRM",
        "version": "1.0.0",
        "author": "Anh Cơ La (Ryan)",
        "category": "tool",
        "description": "Tự động trích xuất thông tin khách hàng tiềm năng, đồng bộ deals và lịch sử liên hệ từ Zalo vào CRM.",
        "icon": "📇",
        "installed": False,
        "is_default": False
    },
    {
        "id": "heo-channel-telegram-bot",
        "name": "Kênh Kết Nối Telegram Bot",
        "version": "1.0.0",
        "author": "Genesis Corp OS",
        "category": "channel",
        "description": "Mở rộng khả năng trực chiến của Bé Heo sang mạng lưới Telegram song song với Zalo.",
        "icon": "✈️",
        "installed": False,
        "is_default": False
    }
]


class PluginManager:
    """
    Quản lý vòng đời nạp, dỡ, kích hoạt và giám sát toàn bộ các Plugin trong Heo-Harness.
    """

    def __init__(self, ctx: Context, bus: EventBus):
        self.ctx = ctx
        self.bus = bus
        self._lock = threading.RLock()
        self._plugins: Dict[str, BasePlugin] = {}
        self._plugin_classes: Dict[str, Type[BasePlugin]] = {}

    def register_plugin_class(self, plugin_cls: Type[BasePlugin]) -> None:
        """Đăng ký một lớp Plugin vào hệ thống."""
        with self._lock:
            meta = getattr(plugin_cls, "metadata", None)
            if not meta or not meta.id:
                raise ValueError(f"Plugin {plugin_cls} thiếu thuộc tính metadata.id")
            self._plugin_classes[meta.id] = plugin_cls

    def load_plugin(self, plugin_id: str) -> bool:
        """Khởi tạo và nạp một plugin vào bộ nhớ."""
        with self._lock:
            if plugin_id in self._plugins:
                return True
            cls = self._plugin_classes.get(plugin_id)
            if not cls:
                print(f"❌ [PluginManager] Không tìm thấy lớp cho plugin ID: {plugin_id}")
                return False

            try:
                instance = cls(self.ctx, self.bus)
                instance.on_load()
                instance.loaded = True
                self._plugins[plugin_id] = instance
                print(f"✔ [PluginManager] Đã nạp plugin: {instance.metadata.name} ({plugin_id})")

                # Kiểm tra trạng thái đã lưu trong config để tự động bật
                cfg = self.ctx.get_plugin_config(plugin_id)
                should_enable = cfg.get("enabled", instance.metadata.default_enabled)
                if should_enable:
                    self.enable_plugin(plugin_id, persist=False)
                else:
                    instance.health_status = PluginHealthStatus.DISABLED
                return True
            except Exception as e:
                print(f"❌ [PluginManager] Lỗi khi nạp plugin {plugin_id}: {e}")
                traceback.print_exc()
                return False

    def enable_plugin(self, plugin_id: str, persist: bool = True) -> bool:
        """Kích hoạt hoạt động của plugin."""
        with self._lock:
            instance = self._plugins.get(plugin_id)
            if not instance:
                if plugin_id in self._plugin_classes:
                    if not self.load_plugin(plugin_id):
                        return False
                    instance = self._plugins.get(plugin_id)
                else:
                    return False

            if instance.enabled:
                return True

            try:
                instance.on_enable()
                instance.enabled = True
                instance.health_status = PluginHealthStatus.HEALTHY
                if persist:
                    self.ctx.set_plugin_config(plugin_id, {"enabled": True})
                instance.log("Đã kích hoạt hoạt động thành công.")
                self.bus.emit("plugin:enabled", plugin_id=plugin_id)
                return True
            except Exception as e:
                instance.health_status = PluginHealthStatus.ERROR
                instance.log(f"Lỗi khi kích hoạt: {e}")
                return False

    def disable_plugin(self, plugin_id: str, persist: bool = True) -> bool:
        """Vô hiệu hóa hoạt động của plugin (Gạt công tắc OFF tức thì)."""
        with self._lock:
            instance = self._plugins.get(plugin_id)
            if not instance or not instance.enabled:
                return True

            try:
                # Gỡ bỏ toàn bộ event listeners của plugin này khỏi bus để tránh rò rỉ
                self.bus.unregister_all_for_plugin(plugin_id)
                instance.on_disable()
                instance.enabled = False
                instance.health_status = PluginHealthStatus.DISABLED
                if persist:
                    self.ctx.set_plugin_config(plugin_id, {"enabled": False})
                instance.log("Đã tạm dừng hoạt động.")
                self.bus.emit("plugin:disabled", plugin_id=plugin_id)
                return True
            except Exception as e:
                instance.log(f"Lỗi khi tạm dừng: {e}")
                return False

    def unload_plugin(self, plugin_id: str) -> bool:
        """Gỡ sạch một plugin ra khỏi bộ nhớ."""
        with self._lock:
            self.disable_plugin(plugin_id, persist=False)
            instance = self._plugins.pop(plugin_id, None)
            if instance:
                try:
                    instance.on_unload()
                    instance.loaded = False
                    print(f"✔ [PluginManager] Đã gỡ bỏ plugin: {plugin_id}")
                    return True
                except Exception as e:
                    print(f"⚠️ [PluginManager] Lỗi khi unload {plugin_id}: {e}")
            return False

    def load_all_registered(self) -> None:
        """Nạp tất cả các plugin đã đăng ký."""
        with self._lock:
            for pid in list(self._plugin_classes.keys()):
                self.load_plugin(pid)

    def scan_and_register_builtin(self) -> None:
        """Quét và đăng ký tự động toàn bộ 7 plugin chính thức trong heo_harness/plugins/."""
        import heo_harness.plugins as builtin_pkg
        pkg_dir = os.path.dirname(builtin_pkg.__file__)

        for item in os.listdir(pkg_dir):
            sub_path = os.path.join(pkg_dir, item)
            if os.path.isdir(sub_path) and not item.startswith("__"):
                mod_name = f"heo_harness.plugins.{item}"
                try:
                    mod = importlib.import_module(mod_name)
                    for _, obj in inspect.getmembers(mod, inspect.isclass):
                        if issubclass(obj, BasePlugin) and obj is not BasePlugin:
                            if hasattr(obj, "metadata"):
                                self.register_plugin_class(obj)
                except Exception as e:
                    print(f"⚠️ [PluginManager] Lỗi nạp plugin tích hợp sẵn '{item}': {e}")

    def get_all_reports(self) -> List[Dict[str, Any]]:
        """Trả về báo cáo trạng thái của toàn bộ plugin để Web UI hiển thị."""
        with self._lock:
            reports = []
            for pid, instance in self._plugins.items():
                reports.append(instance.get_status_report())
            return reports

    def get_marketplace_catalog(self) -> List[Dict[str, Any]]:
        """Trả về danh mục Kho Marketplace kết hợp trạng thái đã cài đặt hay chưa."""
        with self._lock:
            catalog = []
            installed_ids = set(self._plugins.keys())
            for item in MARKETPLACE_CATALOG:
                item_copy = dict(item)
                item_copy["installed"] = item["id"] in installed_ids
                catalog.append(item_copy)
            return catalog
