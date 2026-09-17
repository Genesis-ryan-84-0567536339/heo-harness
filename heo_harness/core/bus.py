"""
EventBus & Hook Pipeline
Trạm điều phối sự kiện theo thời gian thực giữa Chassis và Plugins.
Hỗ trợ bẫy lỗi cách ly (Fault Isolation) để một handler lỗi không làm sập các handler khác.
"""

from typing import Callable, Dict, List, Any, Optional
import threading
import traceback
import inspect

class EventHandler:
    def __init__(self, callback: Callable, priority: int = 100, plugin_id: str = "core"):
        self.callback = callback
        self.priority = priority
        self.plugin_id = plugin_id

    def __call__(self, *args, **kwargs):
        return self.callback(*args, **kwargs)


class EventBus:
    """
    EventBus quản lý việc đăng ký, lắng nghe và phát sóng sự kiện (Pub/Sub).
    Cung cấp pipeline biến đổi dữ liệu (Filter Hooks) và hành động (Action Hooks).
    """

    def __init__(self):
        self._lock = threading.RLock()
        self._listeners: Dict[str, List[EventHandler]] = {}
        self._hooks: Dict[str, List[EventHandler]] = {}

    def on(self, event_name: str, callback: Callable, priority: int = 100, plugin_id: str = "core") -> Callable:
        """Đăng ký lắng nghe một sự kiện."""
        with self._lock:
            handler = EventHandler(callback, priority, plugin_id)
            if event_name not in self._listeners:
                self._listeners[event_name] = []
            self._listeners[event_name].append(handler)
            self._listeners[event_name].sort(key=lambda h: h.priority)
            return callback

    def off(self, event_name: str, callback: Callable) -> None:
        """Hủy đăng ký lắng nghe sự kiện."""
        with self._lock:
            if event_name in self._listeners:
                self._listeners[event_name] = [h for h in self._listeners[event_name] if h.callback != callback]

    def emit(self, event_name: str, *args, **kwargs) -> List[Any]:
        """
        Phát sóng sự kiện tới toàn bộ listener.
        Mỗi handler được bảo vệ an toàn: lỗi ở handler này sẽ không chặn các handler khác!
        """
        with self._lock:
            handlers = list(self._listeners.get(event_name, []))

        results = []
        for handler in handlers:
            try:
                res = handler(*args, **kwargs)
                results.append(res)
            except Exception as e:
                print(f"⚠️ [EventBus] Lỗi khi xử lý sự kiện '{event_name}' bởi plugin '{handler.plugin_id}': {e}")
                traceback.print_exc()
        return results

    def register_hook(self, hook_name: str, callback: Callable, priority: int = 100, plugin_id: str = "core") -> None:
        """Đăng ký một pipeline hook biến đổi dữ liệu tuần tự."""
        with self._lock:
            handler = EventHandler(callback, priority, plugin_id)
            if hook_name not in self._hooks:
                self._hooks[hook_name] = []
            self._hooks[hook_name].append(handler)
            self._hooks[hook_name].sort(key=lambda h: h.priority)

    def apply_hook(self, hook_name: str, value: Any, *args, **kwargs) -> Any:
        """Chạy dữ liệu qua chuỗi pipeline hooks để lọc hoặc biến đổi."""
        with self._lock:
            handlers = list(self._hooks.get(hook_name, []))

        current_val = value
        for handler in handlers:
            try:
                current_val = handler(current_val, *args, **kwargs)
            except Exception as e:
                print(f"⚠️ [EventBus] Lỗi trong hook '{hook_name}' từ plugin '{handler.plugin_id}': {e}")
        return current_val

    def unregister_all_for_plugin(self, plugin_id: str) -> None:
        """Gỡ sạch toàn bộ listener và hook của một plugin khi bị unload/disable."""
        with self._lock:
            for event_name in list(self._listeners.keys()):
                self._listeners[event_name] = [h for h in self._listeners[event_name] if h.plugin_id != plugin_id]
            for hook_name in list(self._hooks.keys()):
                self._hooks[hook_name] = [h for h in self._hooks[hook_name] if h.plugin_id != plugin_id]
