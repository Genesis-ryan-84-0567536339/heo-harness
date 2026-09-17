"""
CLI Command Line Interface cho Heo-Harness
Tác giả: Anh Cơ La (genesis.corp.os@gmail.com)
"""

import sys
import argparse
import requests
import json

def get_harness_url():
    return "http://localhost:5066"

def cmd_start(args):
    from heo_harness.app import main as run_app
    run_app()

def cmd_status(args):
    try:
        res = requests.get(f"{get_harness_url()}/api/status", timeout=2)
        if res.status_code == 200:
            d = res.json()
            sys_info = d.get("system", {})
            print("🐷 [Heo-Harness Status] ĐANG HOẠT ĐỘNG BÌNH THƯỜNG")
            print(f"  • Phiên bản: {sys_info.get('version')}")
            print(f"  • Tác giả: {sys_info.get('author')} ({sys_info.get('email')})")
            print(f"  • Tổng số Plugin đã nạp: {d.get('plugins_count')}")
            print(f"  • Web Console: {get_harness_url()}")
        else:
            print(f"⚠️ Không thể lấy trạng thái (Mã HTTP: {res.status_code})")
    except Exception:
        print("❌ Heo-Harness chưa được khởi động (Cổng 5066 không phản hồi). Dùng: heo-harness start")

def cmd_plugin_list(args):
    try:
        res = requests.get(f"{get_harness_url()}/api/plugins/list", timeout=3)
        if res.status_code == 200:
            plugins = res.json().get("plugins", [])
            print(f"\n🧩 DANH SÁCH PLUGIN ({len(plugins)} plugin đã nạp):")
            print(f"{'ID':<25} {'Tên':<30} {'Trạng thái':<12} {'Sức khỏe':<10}")
            print("-" * 80)
            for p in plugins:
                meta = p["metadata"]
                status = "BẬT [ON]" if p["enabled"] else "TẮT [OFF]"
                print(f"{meta['id']:<25} {meta['name']:<30} {status:<12} {p['health']:<10}")
            print("")
        else:
            print("⚠️ Không thể tải danh sách plugin từ máy chủ.")
    except Exception as e:
        print(f"❌ Lỗi kết nối tới máy chủ Heo-Harness: {e}")

def cmd_plugin_toggle(args, enable: bool):
    try:
        res = requests.post(f"{get_harness_url()}/api/plugins/toggle", json={"id": args.id, "enable": enable}, timeout=3)
        if res.status_code == 200 and res.json().get("ok"):
            print(f"✔ Đã {'bật' if enable else 'tắt'} plugin '{args.id}' thành công!")
        else:
            print(f"❌ Lỗi khi thao tác với plugin: {res.text}")
    except Exception as e:
        print(f"❌ Không thể kết nối tới máy chủ: {e}")

def main():
    parser = argparse.ArgumentParser(description="Heo-Harness CLI: Trình điều khiển Khung Sườn AI Agent & Kho Plugin")
    subparsers = parser.add_subparsers(dest="command", help="Lệnh thực thi")

    # Start
    start_p = subparsers.add_parser("start", help="Khởi chạy Heo-Harness Chassis & Web Console")
    start_p.set_defaults(func=cmd_start)

    # Status
    status_p = subparsers.add_parser("status", help="Kiểm tra trạng thái máy chủ và plugin")
    status_p.set_defaults(func=cmd_status)

    # Plugin subcommands
    plugin_p = subparsers.add_parser("plugin", help="Quản trị Plugin")
    plugin_sub = plugin_p.add_subparsers(dest="subcommand")

    p_list = plugin_sub.add_parser("list", help="Xem danh sách plugin")
    p_list.set_defaults(func=cmd_plugin_list)

    p_enable = plugin_sub.add_parser("enable", help="Bật plugin")
    p_enable.add_argument("id", help="ID của plugin (ví dụ: @heo/tool-media)")
    p_enable.set_defaults(func=lambda a: cmd_plugin_toggle(a, True))

    p_disable = plugin_sub.add_parser("disable", help="Tắt plugin")
    p_disable.add_argument("id", help="ID của plugin (ví dụ: @heo/tool-media)")
    p_disable.set_defaults(func=lambda a: cmd_plugin_toggle(a, False))

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
