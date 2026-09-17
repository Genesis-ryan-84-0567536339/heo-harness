"""
Context: Service Container & Shared State Manager
Cung cấp Dependency Injection và Chia sẻ Trạng thái cho mọi Plugin.
"""

from typing import Any, Dict, Optional, Callable
import threading
import json
import os

class Context:
    """
    Context lưu trữ các dịch vụ (Services), cấu hình (Config) và trạng thái (State)
    được chia sẻ giữa Chassis và toàn bộ các Plugins.
    """

    def __init__(self, config_path: Optional[str] = None):
        self._lock = threading.RLock()
        self._services: Dict[str, Any] = {}
        self._state: Dict[str, Any] = {}
        self.config_path = config_path or os.environ.get("HARNESS_CONFIG", "config/harness.json")
        self.config: Dict[str, Any] = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        with self._lock:
            if os.path.exists(self.config_path):
                try:
                    with open(self.config_path, "r", encoding="utf-8") as f:
                        return json.load(f)
                except Exception as e:
                    print(f"⚠️ [Context] Lỗi nạp cấu hình {self.config_path}: {e}")
            return {
                "system": {
                    "author": "Anh Cơ La",
                    "author_email": "genesis.corp.os@gmail.com",
                    "version": "3.0.0-alpha.1",
                    "log_dir": "logs"
                },
                "plugins": {}
            }

    def save_config(self) -> bool:
        with self._lock:
            try:
                os.makedirs(os.path.dirname(os.path.abspath(self.config_path)), exist_ok=True)
                with open(self.config_path, "w", encoding="utf-8") as f:
                    json.dump(self.config, f, ensure_ascii=False, indent=2)
                return True
            except Exception as e:
                print(f"❌ [Context] Không thể lưu cấu hình: {e}")
                return False

    def provide(self, name: str, service_instance: Any) -> None:
        """Đăng ký một dịch vụ để các plugin khác có thể gọi dùng."""
        with self._lock:
            self._services[name] = service_instance

    def inject(self, name: str, default: Any = None) -> Any:
        """Lấy một dịch vụ đã đăng ký."""
        with self._lock:
            return self._services.get(name, default)

    def has_service(self, name: str) -> bool:
        with self._lock:
            return name in self._services

    def set_state(self, key: str, value: Any) -> None:
        with self._lock:
            self._state[key] = value

    def get_state(self, key: str, default: Any = None) -> Any:
        with self._lock:
            return self._state.get(key, default)

    def get_plugin_config(self, plugin_id: str) -> Dict[str, Any]:
        with self._lock:
            plugins_cfg = self.config.setdefault("plugins", {})
            return plugins_cfg.setdefault(plugin_id, {})

    def set_plugin_config(self, plugin_id: str, new_cfg: Dict[str, Any]) -> None:
        with self._lock:
            plugins_cfg = self.config.setdefault("plugins", {})
            plugins_cfg[plugin_id] = new_cfg
            self.save_config()
