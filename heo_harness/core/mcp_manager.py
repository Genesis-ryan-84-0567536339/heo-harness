"""
Module: McpManager
Trung tâm quản lý kết nối MCP (Model Context Protocol) và Kho Ứng Dụng 1-Click (App Connectors).
Đọc/ghi trực tiếp Single Source of Truth tại ~/.gemini/config/mcp_config.json
Tác quyền: Anh Cơ La (genesis.corp.os@gmail.com)
"""

import os
import json
import shutil
import time

CONFIG_PATH = os.path.expanduser("~/.gemini/config/mcp_config.json")
DISABLED_CONFIG_PATH = os.path.expanduser("~/.gemini/config/mcp_disabled.json")

# Kho Catalog Ứng Dụng Chuẩn Hóa (Pre-declared Turnkey App Connectors)
CONNECTOR_CATALOG = [
    {
        "id": "google_drive",
        "name": "Google Drive",
        "icon": "📁",
        "color": "#4285F4",
        "category": "Google Workspace",
        "provider": "Google Cloud",
        "description": "Tìm kiếm tài liệu, đọc file Word/PDF/Excel trên Drive, tạo thư mục và chia sẻ tài liệu đám mây.",
        "server_key": "genos-hub",
        "tools": [
            {"name": "drive_search", "desc": "Tìm kiếm file và thư mục theo từ khóa"},
            {"name": "drive_read_file", "desc": "Đọc nội dung tệp tin văn bản, PDF hoặc bảng tính"},
            {"name": "drive_create_file", "desc": "Tạo file mới lên thư mục Google Drive"},
            {"name": "drive_share_file", "desc": "Cấp quyền chia sẻ tài liệu cho đối tác"}
        ],
        "turnkey": True,
        "auth_type": "OAuth2 / Hub Key",
        "default_command": "node /home/ryan/mcp-genos-bridge.js"
    },
    {
        "id": "gmail",
        "name": "Gmail",
        "icon": "✉️",
        "color": "#EA4335",
        "category": "Google Workspace",
        "provider": "Google Cloud",
        "description": "Quét thư đến, tóm tắt email quan trọng của đối tác, tạo bản nháp thư (draft) và gửi email chỉ đạo.",
        "server_key": "genos-hub",
        "tools": [
            {"name": "gmail_search", "desc": "Tìm kiếm email theo tiêu đề hoặc người gửi"},
            {"name": "gmail_read_message", "desc": "Đọc toàn bộ nội dung email"},
            {"name": "gmail_create_draft", "desc": "Tạo bản nháp thư sẵn sàng cho Sếp duyệt"},
            {"name": "gmail_send", "desc": "Gửi email chính thức tới đối tác"}
        ],
        "turnkey": True,
        "auth_type": "OAuth2 / Hub Key",
        "default_command": "node /home/ryan/mcp-genos-bridge.js"
    },
    {
        "id": "google_calendar",
        "name": "Google Calendar",
        "icon": "📅",
        "color": "#34A853",
        "category": "Google Workspace",
        "provider": "Google Cloud",
        "description": "Tra cứu lịch họp của Sếp, tự động đặt lịch hẹn mới khi phát hiện lời hẹn trong hội thoại chat.",
        "server_key": "genos-hub",
        "tools": [
            {"name": "calendar_list_events", "desc": "Liệt kê lịch họp, sự kiện trong ngày/tuần"},
            {"name": "calendar_create_event", "desc": "Tạo sự kiện lịch hẹn mới trên Google Calendar"}
        ],
        "turnkey": True,
        "auth_type": "OAuth2 / Hub Key",
        "default_command": "node /home/ryan/mcp-genos-bridge.js"
    },
    {
        "id": "google_office",
        "name": "Google Docs & Sheets",
        "icon": "📊",
        "color": "#0F9D58",
        "category": "Google Workspace",
        "provider": "Google Cloud",
        "description": "Đọc bảng tính tài chính Google Sheets, cập nhật số liệu kinh doanh và soạn thảo văn bản Docs.",
        "server_key": "genos-hub",
        "tools": [
            {"name": "sheets_read", "desc": "Đọc dữ liệu theo dải ô (Range) trong Google Sheets"},
            {"name": "sheets_write", "desc": "Ghi số liệu hoặc cập nhật báo cáo bảng tính"},
            {"name": "docs_edit", "desc": "Soạn thảo hoặc chèn nội dung vào Google Docs"},
            {"name": "slides_add_slide", "desc": "Thêm slide thuyết trình Google Slides"}
        ],
        "turnkey": True,
        "auth_type": "OAuth2 / Hub Key",
        "default_command": "node /home/ryan/mcp-genos-bridge.js"
    },
    {
        "id": "github",
        "name": "GitHub",
        "icon": "🐙",
        "color": "#24292e",
        "category": "Phát Triển & Code",
        "provider": "GitHub, Inc.",
        "description": "Quản lý repository, tìm kiếm mã nguồn, duyệt Pull Request, tạo Issue và commit code.",
        "server_key": "genos-hub",
        "tools": [
            {"name": "search_code", "desc": "Tìm kiếm file, hàm hoặc logic code trên repo"},
            {"name": "create_pull_request", "desc": "Tạo PR mới để cập nhật code"},
            {"name": "github_issue_create", "desc": "Tạo task / bug issue trên GitHub"},
            {"name": "get_commit", "desc": "Xem chi tiết commit và lịch sử thay đổi"}
        ],
        "turnkey": True,
        "auth_type": "OAuth2 / Personal Token",
        "default_command": "node /home/ryan/mcp-genos-bridge.js"
    },
    {
        "id": "playwright",
        "name": "Web Browser (Playwright)",
        "icon": "🌐",
        "color": "#2EAD33",
        "category": "Tự Động Hóa Web",
        "provider": "Microsoft / Playwright",
        "description": "Điều khiển trình duyệt Chrome lướt web, cào tin tức thị trường, chụp ảnh bằng chứng và tương tác web.",
        "server_key": "playwright",
        "tools": [
            {"name": "browser_navigate", "desc": "Mở trang web bất kỳ theo đường dẫn URL"},
            {"name": "browser_click", "desc": "Bấm vào nút, link hoặc form trên trang web"},
            {"name": "browser_take_screenshot", "desc": "Chụp ảnh màn hình lưu bằng chứng"},
            {"name": "browser_snapshot", "desc": "Lấy cấu trúc và nội dung chi tiết của trang web"}
        ],
        "turnkey": True,
        "auth_type": "Zero-Config (Local Headless Chrome)",
        "default_command": "npx -y @playwright/mcp --browser chrome"
    },
    {
        "id": "phone_control",
        "name": "Mobile Phone Control",
        "icon": "📱",
        "color": "#8B5CF6",
        "category": "Thiết Bị Cầm Tay",
        "provider": "Heo Mobile Bridge",
        "description": "Chụp ảnh màn hình điện thoại, kiểm tra tin nhắn, chuyển file và chạy lệnh shell trên thiết bị.",
        "server_key": "genos-hub",
        "tools": [
            {"name": "phone_screenshot", "desc": "Chụp màn hình điện thoại theo thời gian thực"},
            {"name": "phone_control", "desc": "Gửi thao tác chạm / gõ phím đến smartphone"},
            {"name": "phone_shell", "desc": "Chạy lệnh chẩn đoán trên thiết bị di động"}
        ],
        "turnkey": True,
        "auth_type": "ADB / Device Bridge",
        "default_command": "node /home/ryan/mcp-genos-bridge.js"
    },
    {
        "id": "postgres",
        "name": "PostgreSQL Database",
        "icon": "🐘",
        "color": "#336791",
        "category": "Cơ Sở Dữ Liệu",
        "provider": "Model Context Protocol",
        "description": "Kết nối trực tiếp cơ sở dữ liệu Genesis Corp, tra cứu bảng, đọc dữ liệu kinh doanh an toàn.",
        "server_key": "postgres",
        "tools": [
            {"name": "query", "desc": "Thực thi câu lệnh SQL SELECT an toàn"},
            {"name": "list_tables", "desc": "Liệt kê danh sách bảng và schema"},
            {"name": "describe_table", "desc": "Xem cấu trúc chi tiết các cột của bảng"}
        ],
        "turnkey": False,
        "auth_type": "Connection String",
        "config_template": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-postgres", "${CONNECTION_STRING}"]
        },
        "fields": [
            {"key": "CONNECTION_STRING", "label": "Connection URL (PostgreSQL)", "placeholder": "postgresql://user:pass@localhost:5432/genesis_db", "required": True}
        ]
    },
    {
        "id": "mysql",
        "name": "MySQL / MariaDB",
        "icon": "🐬",
        "color": "#00758F",
        "category": "Cơ Sở Dữ Liệu",
        "provider": "Model Context Protocol",
        "description": "Truy vấn dữ liệu tài chính, bán hàng và nhân sự từ MySQL/MariaDB Server.",
        "server_key": "mysql",
        "tools": [
            {"name": "mysql_query", "desc": "Thực thi truy vấn SQL trên MySQL"},
            {"name": "mysql_tables", "desc": "Liệt kê danh sách các bảng"}
        ],
        "turnkey": False,
        "auth_type": "Connection String / Parameters",
        "config_template": {
            "command": "npx",
            "args": ["-y", "mysql-mcp-server", "--host", "${HOST}", "--user", "${USER}", "--password", "${PASSWORD}", "--database", "${DATABASE}"]
        },
        "fields": [
            {"key": "HOST", "label": "MySQL Host", "placeholder": "127.0.0.1", "required": True},
            {"key": "USER", "label": "User", "placeholder": "root", "required": True},
            {"key": "PASSWORD", "label": "Password", "placeholder": "••••••••", "required": True},
            {"key": "DATABASE", "label": "Database Name", "placeholder": "genesis_corp", "required": True}
        ]
    },
    {
        "id": "sqlite",
        "name": "SQLite Database",
        "icon": "🗄️",
        "color": "#003B57",
        "category": "Cơ Sở Dữ Liệu",
        "provider": "Model Context Protocol",
        "description": "Thao tác đọc/ghi trực tiếp vào các file cơ sở dữ liệu .db / .sqlite nội bộ trên máy chủ.",
        "server_key": "sqlite",
        "tools": [
            {"name": "read_query", "desc": "Truy vấn bảng trong file SQLite"},
            {"name": "write_query", "desc": "Cập nhật dữ liệu vào file SQLite"}
        ],
        "turnkey": False,
        "auth_type": "File Path",
        "config_template": {
            "command": "npx",
            "args": ["-y", "mcp-server-sqlite", "--file", "${DB_PATH}"]
        },
        "fields": [
            {"key": "DB_PATH", "label": "Đường dẫn file database (.db)", "placeholder": "/home/ryan/heo-harness/data/app.db", "required": True}
        ]
    },
    {
        "id": "brave_search",
        "name": "Brave Search Engine",
        "icon": "🔍",
        "color": "#FB542B",
        "category": "Tìm Kiếm Internet",
        "provider": "Brave Software",
        "description": "Tìm kiếm thông tin web, tin tức thị trường và đối thủ cạnh tranh theo thời gian thực.",
        "server_key": "brave-search",
        "tools": [
            {"name": "brave_web_search", "desc": "Tìm kiếm web trực tiếp trả về danh sách link & tóm tắt"},
            {"name": "brave_local_search", "desc": "Tìm kiếm địa điểm, doanh nghiệp địa phương"}
        ],
        "turnkey": False,
        "auth_type": "API Key",
        "config_template": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-brave-search"],
            "env": {"BRAVE_API_KEY": "${API_KEY}"}
        },
        "fields": [
            {"key": "API_KEY", "label": "Brave API Key", "placeholder": "BSA...", "required": True}
        ]
    },
    {
        "id": "fetch_scraper",
        "name": "Fetch & Web Scraper",
        "icon": "📑",
        "color": "#06B6D4",
        "category": "Dữ Liệu Web",
        "provider": "Model Context Protocol",
        "description": "Cào nội dung trang web bất kỳ và chuyển đổi thành định dạng Markdown chuẩn.",
        "server_key": "fetch",
        "tools": [
            {"name": "fetch", "desc": "Tải trang web và chuyển đổi HTML thành Markdown sạch"}
        ],
        "turnkey": True,
        "auth_type": "Zero-Config (0đ API)",
        "config_template": {
            "command": "uvx",
            "args": ["mcp-server-fetch"]
        }
    },
    {
        "id": "docker",
        "name": "Docker Engine DevOps",
        "icon": "🐳",
        "color": "#2496ED",
        "category": "Hạ Tầng & DevOps",
        "provider": "Docker Community",
        "description": "Giám sát container, xem logs, restart dịch vụ và kiểm tra trạng thái hạ tầng.",
        "server_key": "docker",
        "tools": [
            {"name": "list_containers", "desc": "Liệt kê danh sách các container đang chạy"},
            {"name": "get_logs", "desc": "Xem log lỗi của container chỉ định"},
            {"name": "restart_container", "desc": "Khởi động lại dịch vụ container"}
        ],
        "turnkey": True,
        "auth_type": "Local Socket",
        "config_template": {
            "command": "npx",
            "args": ["-y", "mcp-server-docker"]
        }
    },
    {
        "id": "memory_graph",
        "name": "Memory Knowledge Graph",
        "icon": "🧠",
        "color": "#EC4899",
        "category": "Trí Tuệ & Trợ Lý",
        "provider": "Model Context Protocol",
        "description": "Lưu trữ đồ thị tri thức dài hạn, liên kết thông tin giữa các thực thể và bối cảnh của Sếp.",
        "server_key": "memory",
        "tools": [
            {"name": "create_entities", "desc": "Tạo thực thể mới trong bộ nhớ tri thức"},
            {"name": "create_relations", "desc": "Tạo mối quan hệ liên kết giữa các thực thể"},
            {"name": "search_nodes", "desc": "Tra cứu mạng lưới thông tin theo từ khóa"}
        ],
        "turnkey": True,
        "auth_type": "Zero-Config",
        "config_template": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-memory"]
        }
    }
]


class McpManager:
    """Điều phối và quản lý toàn diện các kết nối MCP Server & App Connectors."""

    def __init__(self):
        self.config_path = CONFIG_PATH
        self.disabled_path = DISABLED_CONFIG_PATH
        self._ensure_config_file()

    def _ensure_config_file(self):
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        if not os.path.exists(self.config_path):
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump({"mcpServers": {}}, f, indent=2)

    def load_config(self) -> dict:
        """Đọc file cấu hình mcp_config.json chính thống."""
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"mcpServers": {}}

    def save_config(self, config: dict) -> bool:
        """Ghi an toàn file cấu hình mcp_config.json."""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False

    def load_disabled(self) -> dict:
        """Đọc danh sách các server tạm tắt."""
        if os.path.exists(self.disabled_path):
            try:
                with open(self.disabled_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def save_disabled(self, disabled_servers: dict) -> bool:
        """Lưu danh sách server tạm tắt."""
        try:
            with open(self.disabled_path, "w", encoding="utf-8") as f:
                json.dump(disabled_servers, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False

    def get_raw_servers(self) -> list:
        """Trả về danh sách tất cả các MCP Server đang cấu hình (cả active và disabled)."""
        active = self.load_config().get("mcpServers", {})
        disabled = self.load_disabled()

        result = []
        for name, srv in active.items():
            result.append({
                "name": name,
                "type": "sse" if "serverUrl" in srv else "stdio",
                "command": srv.get("command", ""),
                "args": srv.get("args", []),
                "serverUrl": srv.get("serverUrl", ""),
                "env": srv.get("env", {}),
                "enabled": True,
                "status": "ONLINE",
                "is_active": True
            })

        for name, srv in disabled.items():
            result.append({
                "name": name,
                "type": "sse" if "serverUrl" in srv else "stdio",
                "command": srv.get("command", ""),
                "args": srv.get("args", []),
                "serverUrl": srv.get("serverUrl", ""),
                "env": srv.get("env", {}),
                "enabled": False,
                "status": "MUTED",
                "is_active": False
            })

        return result

    def get_app_connectors(self) -> list:
        """Trả về danh sách 1-Click App Connectors với trạng thái trực chiến thời gian thực."""
        cfg = self.load_config()
        active_servers = cfg.get("mcpServers", {})
        disabled_servers = self.load_disabled()

        apps = []
        for item in CONNECTOR_CATALOG:
            s_key = item.get("server_key")
            is_active = s_key in active_servers
            is_disabled = s_key in disabled_servers

            if is_active:
                status = "CONNECTED"
                status_label = "🟢 ĐÃ KẾT NỐI (SẴN SÀNG)"
                enabled = True
            elif is_disabled:
                status = "MUTED"
                status_label = "🟡 TẠM TẮT (MUTED)"
                enabled = False
            else:
                status = "DISCONNECTED"
                status_label = "⚪ CHƯA LIÊN KẾT"
                enabled = False

            app_copy = dict(item)
            app_copy["status"] = status
            app_copy["status_label"] = status_label
            app_copy["enabled"] = enabled
            app_copy["tool_count"] = len(item.get("tools", []))
            apps.append(app_copy)

        return apps

    def connect_app(self, app_id: str, form_params: dict = None) -> dict:
        """1-Click Kết nối một App Connector từ Catalog vào mcp_config.json."""
        app = next((a for a in CONNECTOR_CATALOG if a["id"] == app_id), None)
        if not app:
            return {"ok": False, "error": f"Không tìm thấy ứng dụng ID: {app_id}"}

        server_key = app.get("server_key", app_id)
        cfg = self.load_config()
        mcp_servers = cfg.get("mcpServers", {})

        # Nếu là ứng dụng cấu hình qua template
        template = app.get("config_template")
        if template:
            cmd = template.get("command", "npx")
            raw_args = list(template.get("args", []))
            raw_env = dict(template.get("env", {}))

            # Thay thế các biến ${KEY} bằng giá trị user nhập
            params = form_params or {}
            resolved_args = []
            for arg in raw_args:
                val = arg
                for k, v in params.items():
                    val = val.replace(f"${{{k}}}", str(v))
                resolved_args.append(val)

            resolved_env = {}
            for env_k, env_v in raw_env.items():
                val = env_v
                for k, v in params.items():
                    val = val.replace(f"${{{k}}}", str(v))
                resolved_env[env_k] = val

            server_def = {
                "command": cmd,
                "args": resolved_args
            }
            if resolved_env:
                server_def["env"] = resolved_env

            mcp_servers[server_key] = server_def
        else:
            # Ứng dụng turnkey mặc định (như genos-hub hoặc playwright)
            if server_key == "playwright":
                mcp_servers["playwright"] = {
                    "command": "npx",
                    "args": ["-y", "@playwright/mcp", "--browser", "chrome"]
                }
            elif server_key == "genos-hub":
                mcp_servers["genos-hub"] = {
                    "command": "node",
                    "args": ["/home/ryan/mcp-genos-bridge.js"]
                }
            else:
                mcp_servers[server_key] = {
                    "command": "npx",
                    "args": ["-y", f"@modelcontextprotocol/server-{server_key}"]
                }

        # Bỏ khỏi danh sách disabled nếu có
        disabled = self.load_disabled()
        if server_key in disabled:
            del disabled[server_key]
            self.save_disabled(disabled)

        cfg["mcpServers"] = mcp_servers
        self.save_config(cfg)
        return {
            "ok": True,
            "message": f"🎉 Đã kết nối thành công ứng dụng {app['name']}!",
            "app": app,
            "server_key": server_key
        }

    def disconnect_app(self, app_id: str) -> dict:
        """Ngắt kết nối App Connector khỏi mcp_config.json."""
        app = next((a for a in CONNECTOR_CATALOG if a["id"] == app_id), None)
        server_key = app.get("server_key", app_id) if app else app_id

        cfg = self.load_config()
        mcp_servers = cfg.get("mcpServers", {})
        if server_key in mcp_servers:
            del mcp_servers[server_key]
            cfg["mcpServers"] = mcp_servers
            self.save_config(cfg)

        disabled = self.load_disabled()
        if server_key in disabled:
            del disabled[server_key]
            self.save_disabled(disabled)

        return {"ok": True, "message": f"Đã ngắt kết nối {app['name'] if app else server_key}!"}

    def toggle_server(self, server_name: str, enabled: bool) -> dict:
        """Bật/Tắt công tắc một MCP Server."""
        cfg = self.load_config()
        active = cfg.get("mcpServers", {})
        disabled = self.load_disabled()

        if enabled:
            # Chuyển từ disabled sang active
            srv = disabled.pop(server_name, None)
            if srv:
                active[server_name] = srv
            self.save_config(cfg)
            self.save_disabled(disabled)
            return {"ok": True, "message": f"Đã kích hoạt trực chiến máy chủ {server_name}!", "enabled": True}
        else:
            # Chuyển từ active sang disabled
            srv = active.pop(server_name, None)
            if srv:
                disabled[server_name] = srv
            self.save_config(cfg)
            self.save_disabled(disabled)
            return {"ok": True, "message": f"Đã tạm ngắt trực chiến máy chủ {server_name}!", "enabled": False}

    def add_custom_server(self, name: str, srv_type: str, command: str = "", args: list = None, env: dict = None, server_url: str = "") -> dict:
        """Thêm một MCP Server tùy chỉnh (Stdio hoặc Remote SSE)."""
        name = name.strip().replace(" ", "-").lower()
        if not name:
            return {"ok": False, "error": "Tên máy chủ MCP không được để trống!"}

        cfg = self.load_config()
        mcp_servers = cfg.get("mcpServers", {})

        if srv_type == "sse":
            if not server_url:
                return {"ok": False, "error": "Vui lòng nhập đường dẫn Endpoint SSE (serverUrl)!"}
            mcp_servers[name] = {"serverUrl": server_url}
        else:
            if not command:
                return {"ok": False, "error": "Vui lòng nhập lệnh thực thi (command)!"}
            srv = {"command": command}
            if args:
                srv["args"] = args
            if env:
                srv["env"] = env
            mcp_servers[name] = srv

        cfg["mcpServers"] = mcp_servers
        self.save_config(cfg)
        return {"ok": True, "message": f"Đã thêm thành công máy chủ MCP '{name}'!", "name": name}

    def delete_server(self, name: str) -> dict:
        """Xóa hoàn toàn một MCP Server."""
        cfg = self.load_config()
        active = cfg.get("mcpServers", {})
        if name in active:
            del active[name]
            cfg["mcpServers"] = active
            self.save_config(cfg)

        disabled = self.load_disabled()
        if name in disabled:
            del disabled[name]
            self.save_disabled(disabled)

        return {"ok": True, "message": f"Đã xóa máy chủ MCP '{name}' thành công!"}

    def get_summary(self) -> dict:
        """Lấy số liệu thống kê tổng quan của toàn bộ hệ sinh thái MCP."""
        connectors = self.get_app_connectors()
        raw_servers = self.get_raw_servers()

        connected_connectors = [c for c in connectors if c["status"] == "CONNECTED"]
        total_tools = sum(c["tool_count"] for c in connected_connectors)
        active_raw = [s for s in raw_servers if s["enabled"]]

        return {
            "total_connectors": len(connectors),
            "connected_connectors": len(connected_connectors),
            "total_servers": len(raw_servers),
            "active_servers": len(active_raw),
            "total_tools_ready": total_tools,
            "connectors": connectors,
            "servers": raw_servers
        }


# Singleton Instance
mcp_manager = McpManager()
