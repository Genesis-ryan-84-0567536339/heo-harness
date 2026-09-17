"""
Application Entry Point: Khởi Động Heo-Harness Chassis
Tác giả & Kiến trúc sư trưởng: Anh Cơ La (genesis.corp.os@gmail.com)
"""

import sys
import os
import time
import signal

from heo_harness.core.context import Context
from heo_harness.core.bus import EventBus
from heo_harness.core.manager import PluginManager

class HeoHarnessApp:
    def __init__(self, config_path: str = None):
        print("🐷 [Heo-Harness] Đang khởi tạo Khung Sườn AI Agent Runtime...")
        self.ctx = Context(config_path)
        self.bus = EventBus()
        self.manager = PluginManager(self.ctx, self.bus)

        # Cung cấp PluginManager cho context để các plugin UI có thể gọi
        self.ctx.provide("plugin_manager", self.manager)
        self.running = False

    def start(self) -> None:
        self.running = True
        print("🚀 [Heo-Harness] Bắt đầu quét và nạp các Official Built-in Plugins...")
        
        # 1. Quét và đăng ký toàn bộ 7 plugin mặc định
        self.manager.scan_and_register_builtin()

        # 2. Nạp và kích hoạt toàn bộ plugin
        self.manager.load_all_registered()

        # Phát sóng sự kiện hệ thống sẵn sàng
        self.bus.emit("harness:ready")
        print("\n✨ [Heo-Harness] Hệ thống đã sẵn sàng 100%! Bảng điều khiển Web Console & Kho Plugin đang chạy.")

    def stop(self) -> None:
        if not self.running:
            return
        print("\n🛑 [Heo-Harness] Đang đóng hệ thống an toàn (Graceful Shutdown)...")
        self.running = False
        self.bus.emit("harness:stopping")

        # Gỡ sạch các plugin theo thứ tự an toàn
        for pid in list(self.manager._plugins.keys()):
            self.manager.unload_plugin(pid)
        print("✔ [Heo-Harness] Đã dừng toàn bộ dịch vụ sạch sẽ.")

def main():
    app = HeoHarnessApp()

    def handle_signal(sig, frame):
        app.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    app.start()

    # Vòng lặp giữ process chạy
    try:
        while app.running:
            time.sleep(1)
    except KeyboardInterrupt:
        app.stop()

if __name__ == "__main__":
    main()
