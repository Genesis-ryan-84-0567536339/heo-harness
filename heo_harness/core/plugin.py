"""
BasePlugin, PluginMetadata & Circuit Breaker
Khung gầm trừu tượng cho mọi Plugin trong Heo-Harness.
Tích hợp sẵn Error Boundary & Circuit Breaker cách ly lỗi 100%.
"""

from typing import Dict, Any, Optional, List
from enum import Enum
import traceback
import time

class PluginCategory(str, Enum):
    CORE = "core"
    PROVIDER = "provider"
    CHANNEL = "channel"
    TOOL = "tool"
    UI = "ui"
    AGENT = "agent"
    COMMUNITY = "community"


class PluginHealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    ERROR = "error"
    DISABLED = "disabled"


class PluginMetadata:
    def __init__(
        self,
        id: str,
        name: str,
        version: str = "1.0.0",
        description: str = "",
        author: str = "Anh Cơ La",
        author_email: str = "genesis.corp.os@gmail.com",
        category: PluginCategory = PluginCategory.TOOL,
        tags: Optional[List[str]] = None,
        default_enabled: bool = True,
        dependencies: Optional[List[str]] = None,
        icon: str = "🧩"
    ):
        self.id = id
        self.name = name
        self.version = version
        self.description = description
        self.author = author
        self.author_email = author_email
        self.category = category
        self.tags = tags or []
        self.default_enabled = default_enabled
        self.dependencies = dependencies or []
        self.icon = icon

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "author_email": self.author_email,
            "category": self.category.value if isinstance(self.category, PluginCategory) else str(self.category),
            "tags": self.tags,
            "default_enabled": self.default_enabled,
            "dependencies": self.dependencies,
            "icon": self.icon
        }


class CircuitBreaker:
    """Mạch ngắt bảo vệ: nếu một plugin gặp lỗi liên tiếp vượt ngưỡng, nó sẽ bị cô lập."""
    def __init__(self, failure_threshold: int = 5, cooldown_seconds: float = 60.0):
        self.failure_threshold = failure_threshold
        self.cooldown_seconds = cooldown_seconds
        self.consecutive_failures = 0
        self.total_errors = 0
        self.last_failure_time = 0.0
        self.is_open = False  # Mạch hở = Tạm ngắt

    def record_success(self) -> None:
        self.consecutive_failures = 0
        self.is_open = False

    def record_failure(self) -> bool:
        """Ghi nhận 1 lỗi. Trả về True nếu mạch vừa bị ngắt."""
        self.total_errors += 1
        self.consecutive_failures += 1
        self.last_failure_time = time.time()
        if self.consecutive_failures >= self.failure_threshold:
            self.is_open = True
            return True
        return False

    def can_execute(self) -> bool:
        if not self.is_open:
            return True
        # Thử hồi phục sau thời gian làm mát
        if time.time() - self.last_failure_time > self.cooldown_seconds:
            self.is_open = False
            self.consecutive_failures = 0
            return True
        return False


class BasePlugin:
    """
    Lớp cơ sở cho toàn bộ Plugin trong Heo-Harness.
    Tất cả các tính năng nghiệp vụ, cổng giao tiếp, AI provider và UI đều kế thừa lớp này.
    """

    metadata: PluginMetadata

    def __init__(self, ctx: Any, bus: Any):
        self.ctx = ctx
        self.bus = bus
        self.enabled = False
        self.loaded = False
        self.circuit = CircuitBreaker()
        self.logs: List[str] = []
        self.health_status = PluginHealthStatus.DISABLED

    def log(self, message: str) -> None:
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{ts}] [{self.metadata.id}] {message}"
        self.logs.append(entry)
        if len(self.logs) > 100:
            self.logs.pop(0)
        print(f"🧩 {entry}")

    def safe_execute(self, func, *args, **kwargs) -> Any:
        """Thực thi an toàn một hàm nghiệp vụ của plugin có bọc Circuit Breaker."""
        if not self.enabled:
            return None
        if not self.circuit.can_execute():
            self.health_status = PluginHealthStatus.DEGRADED
            self.log("⚠️ Circuit Breaker đang ngắt mạch để bảo vệ hệ thống.")
            return None

        try:
            res = func(*args, **kwargs)
            self.circuit.record_success()
            self.health_status = PluginHealthStatus.HEALTHY
            return res
        except Exception as e:
            tripped = self.circuit.record_failure()
            err_detail = traceback.format_exc()
            self.log(f"❌ Lỗi thực thi: {e}")
            if tripped:
                self.health_status = PluginHealthStatus.ERROR
                self.log(f"🛑 ĐÃ KÍCH HOẠT CIRCUIT BREAKER! Plugin bị tạm ngắt do {self.circuit.consecutive_failures} lỗi liên tiếp.")
            else:
                self.health_status = PluginHealthStatus.DEGRADED
            return None

    def on_load(self) -> None:
        """Được gọi khi plugin được nạp vào bộ nhớ."""
        pass

    def on_unload(self) -> None:
        """Được gọi khi plugin bị gỡ bỏ khỏi bộ nhớ."""
        pass

    def on_enable(self) -> None:
        """Được gọi khi plugin được bật hoạt động."""
        pass

    def on_disable(self) -> None:
        """Được gọi khi plugin bị tắt tạm thời."""
        pass

    def get_status_report(self) -> Dict[str, Any]:
        meta_dict = self.metadata.to_dict()
        category_str = self.metadata.category.value if hasattr(self.metadata.category, "value") else str(self.metadata.category)
        return {
            "id": self.metadata.id,
            "name": self.metadata.name,
            "version": self.metadata.version,
            "author": self.metadata.author,
            "author_email": self.metadata.author_email,
            "category": category_str,
            "description": self.metadata.description,
            "icon": self.metadata.icon,
            "metadata": meta_dict,
            "enabled": self.enabled,
            "loaded": self.loaded,
            "health": self.health_status.value,
            "circuit_breaker": {
                "status": "HEALTHY" if not self.circuit.is_open else "CIRCUIT_TRIPPED",
                "failure_count": self.circuit.consecutive_failures,
                "max_failures": self.circuit.failure_threshold,
                "circuit_open": self.circuit.is_open,
                "total_errors": self.circuit.total_errors
            },
            "total_errors": self.circuit.total_errors,
            "consecutive_failures": self.circuit.consecutive_failures,
            "circuit_tripped": self.circuit.is_open,
            "recent_logs": self.logs[-10:]
        }
