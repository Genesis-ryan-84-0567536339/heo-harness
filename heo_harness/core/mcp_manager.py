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

    # ================= 1. GOOGLE WORKSPACE =================
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
            {"name": "calendar_list_events", "desc": "Xem danh sách lịch hẹn và cuộc họp sắp tới"},
            {"name": "calendar_create_event", "desc": "Tạo lịch hẹn mới đồng bộ lên Google Calendar"}
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
            {"name": "sheets_read", "desc": "Đọc dữ liệu từ Google Sheets theo dải ô (range)"},
            {"name": "sheets_write", "desc": "Ghi dòng dữ liệu mới vào bảng tính Sheets"},
            {"name": "docs_edit", "desc": "Chèn văn bản hoặc chỉnh sửa tài liệu Google Docs"}
        ],
        "turnkey": True,
        "auth_type": "OAuth2 / Hub Key",
        "default_command": "node /home/ryan/mcp-genos-bridge.js"
    },
    {
        "id": "google_slides",
        "name": "Google Slides",
        "icon": "📽️",
        "color": "#F4B400",
        "category": "Google Workspace",
        "provider": "Google Cloud",
        "description": "Tự động tạo bài thuyết trình, thêm slide báo cáo dự án và trình bày ý tưởng cho Ban Lãnh Đạo.",
        "server_key": "genos-hub",
        "tools": [
            {"name": "slides_add_slide", "desc": "Tạo slide mới trong bài thuyết trình"},
            {"name": "slides_update_text", "desc": "Cập nhật nội dung văn bản trên slide"}
        ],
        "turnkey": True,
        "auth_type": "OAuth2 / Hub Key",
        "default_command": "node /home/ryan/mcp-genos-bridge.js"
    },
    {
        "id": "google_tasks",
        "name": "Google Tasks & Contacts",
        "icon": "✅",
        "color": "#4285F4",
        "category": "Google Workspace",
        "provider": "Google Cloud",
        "description": "Đồng bộ danh sách việc cần làm cá nhân và tra cứu danh bạ đối tác kinh doanh trên tài khoản Google.",
        "server_key": "genos-hub",
        "tools": [
            {"name": "tasks_list", "desc": "Xem danh sách việc cần làm trên Google Tasks"},
            {"name": "tasks_create", "desc": "Tạo việc mới cần làm trên Google Tasks"},
            {"name": "contacts_search", "desc": "Tra cứu số điện thoại và email danh bạ đối tác"}
        ],
        "turnkey": True,
        "auth_type": "OAuth2 / Hub Key",
        "default_command": "node /home/ryan/mcp-genos-bridge.js"
    },

    # ================= 2. GIAO TIẾP & CHAT TEAM =================
    {
        "id": "slack",
        "name": "Slack Workspace",
        "icon": "💬",
        "color": "#4A154B",
        "category": "Giao Tiếp & Chat Team",
        "provider": "Slack Technologies",
        "description": "Gửi thông báo điều hành vào các channel Slack, đọc tin nhắn và tương tác trực tiếp với đội ngũ nhân sự.",
        "server_key": "slack",
        "tools": [
            {"name": "slack_post_message", "desc": "Gửi tin nhắn hoặc thông báo vào kênh Slack"},
            {"name": "slack_list_channels", "desc": "Liệt kê danh sách các kênh công việc"},
            {"name": "slack_get_history", "desc": "Đọc lịch sử tin nhắn trong kênh chỉ định"}
        ],
        "turnkey": False,
        "auth_type": "Bot Token",
        "config_template": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-slack"],
            "env": {"SLACK_BOT_TOKEN": "${SLACK_BOT_TOKEN}", "SLACK_TEAM_ID": "${SLACK_TEAM_ID}"}
        },
        "fields": [
            {"key": "SLACK_BOT_TOKEN", "label": "Slack Bot User OAuth Token (xoxb-...)", "placeholder": "xoxb-123456789...", "required": True},
            {"key": "SLACK_TEAM_ID", "label": "Slack Team ID (T...)", "placeholder": "T0123456789", "required": True}
        ]
    },
    {
        "id": "discord",
        "name": "Discord Community & Bot",
        "icon": "🎮",
        "color": "#5865F2",
        "category": "Giao Tiếp & Chat Team",
        "provider": "Discord Inc.",
        "description": "Điều phối máy chủ Discord, gửi thông báo cập nhật tình hình hệ thống và lắng nghe trao đổi cộng đồng.",
        "server_key": "discord",
        "tools": [
            {"name": "discord_send_message", "desc": "Gửi tin nhắn vào channel Discord"},
            {"name": "discord_read_messages", "desc": "Đọc tin nhắn gần nhất trong channel"}
        ],
        "turnkey": False,
        "auth_type": "Bot Token",
        "config_template": {
            "command": "npx",
            "args": ["-y", "discord-mcp"],
            "env": {"DISCORD_BOT_TOKEN": "${DISCORD_BOT_TOKEN}"}
        },
        "fields": [
            {"key": "DISCORD_BOT_TOKEN", "label": "Discord Bot Token", "placeholder": "MTE...", "required": True}
        ]
    },
    {
        "id": "telegram",
        "name": "Telegram Bot Gateway",
        "icon": "✈️",
        "color": "#229ED9",
        "category": "Giao Tiếp & Chat Team",
        "provider": "Telegram FZ-LLC",
        "description": "Nhận lệnh điều hành khẩn cấp từ Sếp qua Telegram bot và gửi báo cáo tiến độ tức thì.",
        "server_key": "telegram",
        "tools": [
            {"name": "telegram_send_message", "desc": "Gửi tin nhắn hoặc tài liệu tới người dùng / nhóm Telegram"},
            {"name": "telegram_get_updates", "desc": "Kiểm tra các tin nhắn mới gửi tới Bot"}
        ],
        "turnkey": False,
        "auth_type": "Bot Token",
        "config_template": {
            "command": "npx",
            "args": ["-y", "mcp-server-telegram"],
            "env": {"TELEGRAM_BOT_TOKEN": "${TELEGRAM_BOT_TOKEN}"}
        },
        "fields": [
            {"key": "TELEGRAM_BOT_TOKEN", "label": "Telegram Bot Token (từ @BotFather)", "placeholder": "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11", "required": True}
        ]
    },
    {
        "id": "zalo_gateway",
        "name": "Zalo Cá Nhân Gateway",
        "icon": "💬",
        "color": "#0068FF",
        "category": "Giao Tiếp & Chat Team",
        "provider": "Genesis Local Bridge",
        "description": "Cổng kết nối Zalo cá nhân 2 chiều, quét QR bảo mật, lọc tin nhắn @tag nhóm và chat 1:1 với Sếp.",
        "server_key": "heo-channel-zalo-gateway",
        "tools": [
            {"name": "zalo_send_msg", "desc": "Gửi tin nhắn phản hồi tới người dùng hoặc nhóm Zalo"},
            {"name": "zalo_get_status", "desc": "Kiểm tra trạng thái kết nối socket Zalo cổng 5051"}
        ],
        "turnkey": True,
        "auth_type": "Local Bridge (Cổng 5051)",
        "default_command": "node bot.js"
    },
    {
        "id": "whatsapp_gateway",
        "name": "WhatsApp Multi-Device",
        "icon": "📱",
        "color": "#25D366",
        "category": "Giao Tiếp & Chat Team",
        "provider": "Genesis Local Bridge",
        "description": "Cổng kết nối WhatsApp Multi-Device 2 chiều, quét mã QR chuẩn Baileys, lưu phiên an toàn cục bộ.",
        "server_key": "heo-channel-whatsapp-gateway",
        "tools": [
            {"name": "wa_send_msg", "desc": "Gửi tin nhắn WhatsApp tới số điện thoại đối tác"},
            {"name": "wa_get_status", "desc": "Kiểm tra trạng thái kết nối Baileys cổng 5052"}
        ],
        "turnkey": True,
        "auth_type": "Local Bridge (Cổng 5052)",
        "default_command": "node wa_bridge.js"
    },

    # ================= 3. GHI CHÚ & QUẢN TRỊ CÔNG VIỆC =================
    {
        "id": "notion",
        "name": "Notion Knowledge Base",
        "icon": "📝",
        "color": "#000000",
        "category": "Ghi Chú & Quản Trị Công Việc",
        "provider": "Notion Labs",
        "description": "Quản lý cơ sở tri thức công ty, tìm kiếm trang, đọc/ghi database dự án và tự động tạo trang ghi chú mới.",
        "server_key": "notion",
        "tools": [
            {"name": "notion_search", "desc": "Tìm kiếm tài liệu và trang trong không gian làm việc Notion"},
            {"name": "notion_read_page", "desc": "Đọc toàn bộ nội dung khối văn bản (blocks) của trang"},
            {"name": "notion_create_page", "desc": "Tạo trang ghi chú hoặc bản ghi mới trong Notion Database"}
        ],
        "turnkey": False,
        "auth_type": "Internal Integration Token",
        "config_template": {
            "command": "npx",
            "args": ["-y", "@notionhq/notion-mcp-server"],
            "env": {"NOTION_API_TOKEN": "${NOTION_API_TOKEN}"}
        },
        "fields": [
            {"key": "NOTION_API_TOKEN", "label": "Notion Internal Integration Secret (secret_...)", "placeholder": "secret_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx", "required": True}
        ]
    },
    {
        "id": "linear",
        "name": "Linear Issues & Projects",
        "icon": "🎯",
        "color": "#5E6AD2",
        "category": "Ghi Chú & Quản Trị Công Việc",
        "provider": "Linear Orbit",
        "description": "Quản lý issue, theo dõi tiến độ sprint, tạo task kỹ thuật và phân công nhiệm vụ cho lập trình viên.",
        "server_key": "linear",
        "tools": [
            {"name": "linear_list_issues", "desc": "Xem danh sách công việc và trạng thái tiến độ"},
            {"name": "linear_create_issue", "desc": "Tạo task mới trên bảng Linear kèm mô tả chi tiết"}
        ],
        "turnkey": False,
        "auth_type": "API Key",
        "config_template": {
            "command": "npx",
            "args": ["-y", "mcp-server-linear"],
            "env": {"LINEAR_API_KEY": "${LINEAR_API_KEY}"}
        },
        "fields": [
            {"key": "LINEAR_API_KEY", "label": "Linear Personal API Key (lin_api_...)", "placeholder": "lin_api_xxxxxxxxxxxxxxxxxxxxxx", "required": True}
        ]
    },
    {
        "id": "jira",
        "name": "Jira Software & Agile",
        "icon": "🔷",
        "color": "#0052CC",
        "category": "Ghi Chú & Quản Trị Công Việc",
        "provider": "Atlassian",
        "description": "Tra cứu Jira tickets, cập nhật tiến độ sprint, log thời gian làm việc và tạo bug report.",
        "server_key": "jira",
        "tools": [
            {"name": "jira_get_issue", "desc": "Xem chi tiết ticket Jira (mô tả, người nhận, trạng thái)"},
            {"name": "jira_create_issue", "desc": "Tạo ticket Jira mới trong dự án chỉ định"}
        ],
        "turnkey": False,
        "auth_type": "Atlassian API Token",
        "config_template": {
            "command": "npx",
            "args": ["-y", "jira-mcp"],
            "env": {"JIRA_HOST": "${JIRA_HOST}", "JIRA_EMAIL": "${JIRA_EMAIL}", "JIRA_API_TOKEN": "${JIRA_API_TOKEN}"}
        },
        "fields": [
            {"key": "JIRA_HOST", "label": "Jira Host URL", "placeholder": "https://your-company.atlassian.net", "required": True},
            {"key": "JIRA_EMAIL", "label": "Atlassian Account Email", "placeholder": "ryan@genesis.corp", "required": True},
            {"key": "JIRA_API_TOKEN", "label": "Atlassian API Token", "placeholder": "ATATT3x...", "required": True}
        ]
    },
    {
        "id": "confluence",
        "name": "Confluence Enterprise Wiki",
        "icon": "📚",
        "color": "#172B4D",
        "category": "Ghi Chú & Quản Trị Công Việc",
        "provider": "Atlassian",
        "description": "Đọc và cập nhật quy trình làm việc chuẩn (SOP), tài liệu kiến trúc và biên bản họp công ty trên Confluence.",
        "server_key": "confluence",
        "tools": [
            {"name": "confluence_search", "desc": "Tìm kiếm tài liệu nội bộ trong Confluence Space"},
            {"name": "confluence_get_page", "desc": "Đọc nội dung trang quy trình / kiến trúc"}
        ],
        "turnkey": False,
        "auth_type": "Atlassian API Token",
        "config_template": {
            "command": "npx",
            "args": ["-y", "confluence-mcp"],
            "env": {"CONFLUENCE_HOST": "${CONFLUENCE_HOST}", "CONFLUENCE_EMAIL": "${CONFLUENCE_EMAIL}", "CONFLUENCE_API_TOKEN": "${CONFLUENCE_API_TOKEN}"}
        },
        "fields": [
            {"key": "CONFLUENCE_HOST", "label": "Confluence Host URL", "placeholder": "https://your-company.atlassian.net/wiki", "required": True},
            {"key": "CONFLUENCE_EMAIL", "label": "Atlassian Account Email", "placeholder": "ryan@genesis.corp", "required": True},
            {"key": "CONFLUENCE_API_TOKEN", "label": "Atlassian API Token", "placeholder": "ATATT3x...", "required": True}
        ]
    },
    {
        "id": "trello",
        "name": "Trello Kanban Boards",
        "icon": "📋",
        "color": "#0079BF",
        "category": "Ghi Chú & Quản Trị Công Việc",
        "provider": "Atlassian",
        "description": "Quản lý thẻ công việc trực quan dạng Kanban, di chuyển thẻ giữa các danh sách To-Do, In-Progress, Done.",
        "server_key": "trello",
        "tools": [
            {"name": "trello_get_cards", "desc": "Xem danh sách thẻ trên bảng Trello"},
            {"name": "trello_add_card", "desc": "Thêm thẻ công việc mới vào cột chỉ định"}
        ],
        "turnkey": False,
        "auth_type": "API Key & Token",
        "config_template": {
            "command": "npx",
            "args": ["-y", "trello-mcp"],
            "env": {"TRELLO_API_KEY": "${TRELLO_API_KEY}", "TRELLO_TOKEN": "${TRELLO_TOKEN}"}
        },
        "fields": [
            {"key": "TRELLO_API_KEY", "label": "Trello API Key", "placeholder": "Tạo tại trello.com/power-ups/admin", "required": True},
            {"key": "TRELLO_TOKEN", "label": "Trello Token", "placeholder": "ATTA...", "required": True}
        ]
    },
    {
        "id": "obsidian",
        "name": "Obsidian Local Vault",
        "icon": "💎",
        "color": "#7C3AED",
        "category": "Ghi Chú & Quản Trị Công Việc",
        "provider": "Dynalist Inc.",
        "description": "Liên kết trực tiếp vào thư mục ghi chú Markdown cá nhân của Sếp trong Obsidian Vault.",
        "server_key": "obsidian",
        "tools": [
            {"name": "obsidian_search", "desc": "Tìm kiếm từ khóa trong toàn bộ ghi chú Obsidian"},
            {"name": "obsidian_append_note", "desc": "Thêm nội dung vào nhật ký hàng ngày (Daily Note)"}
        ],
        "turnkey": False,
        "auth_type": "Local Vault Path",
        "config_template": {
            "command": "npx",
            "args": ["-y", "mcp-obsidian", "--vault", "${VAULT_PATH}"]
        },
        "fields": [
            {"key": "VAULT_PATH", "label": "Đường dẫn thư mục Vault", "placeholder": "/home/ryan/Documents/ObsidianVault", "required": True}
        ]
    },

    # ================= 4. LẬP TRÌNH & DEVOPS =================
    {
        "id": "github",
        "name": "GitHub Cloud",
        "icon": "🐙",
        "color": "#24292E",
        "category": "Lập Trình & DevOps",
        "provider": "GitHub, Inc.",
        "description": "Quản lý repository, tìm kiếm mã nguồn, duyệt Pull Request, tạo Issue và commit code tự động.",
        "server_key": "genos-hub",
        "tools": [
            {"name": "search_code", "desc": "Tìm kiếm hàm hoặc tệp tin trong toàn bộ kho code"},
            {"name": "create_pull_request", "desc": "Tạo Pull Request đề xuất cập nhật tính năng mới"},
            {"name": "github_issue_create", "desc": "Mở Issue mới theo dõi lỗi phần mềm"}
        ],
        "turnkey": True,
        "auth_type": "OAuth2 / Hub Key",
        "default_command": "node /home/ryan/mcp-genos-bridge.js"
    },
    {
        "id": "gitlab",
        "name": "GitLab Enterprise",
        "icon": "🦊",
        "color": "#FC6D26",
        "category": "Lập Trình & DevOps",
        "provider": "GitLab Inc.",
        "description": "Quản lý dự án mã nguồn GitLab tự triển khai (Self-hosted) hoặc đám mây, theo dõi pipeline CI/CD.",
        "server_key": "gitlab",
        "tools": [
            {"name": "gitlab_list_projects", "desc": "Liệt kê danh sách dự án GitLab"},
            {"name": "gitlab_create_mr", "desc": "Tạo Merge Request cập nhật mã nguồn"}
        ],
        "turnkey": False,
        "auth_type": "Personal Access Token",
        "config_template": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-gitlab"],
            "env": {"GITLAB_PERSONAL_ACCESS_TOKEN": "${GITLAB_TOKEN}", "GITLAB_API_URL": "${GITLAB_URL}"}
        },
        "fields": [
            {"key": "GITLAB_URL", "label": "GitLab API URL", "placeholder": "https://gitlab.com/api/v4", "required": False},
            {"key": "GITLAB_TOKEN", "label": "Personal Access Token (glpat-...)", "placeholder": "glpat-xxxxxxxxxxxxxxxxxxxx", "required": True}
        ]
    },
    {
        "id": "docker",
        "name": "Docker Engine DevOps",
        "icon": "🐳",
        "color": "#2496ED",
        "category": "Lập Trình & DevOps",
        "provider": "Docker Community",
        "description": "Giám sát container, xem logs lỗi, restart dịch vụ và kiểm tra trạng thái hạ tầng hệ thống.",
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
        "id": "kubernetes",
        "name": "Kubernetes Cluster",
        "icon": "☸️",
        "color": "#326CE5",
        "category": "Lập Trình & DevOps",
        "provider": "Cloud Native Computing Foundation",
        "description": "Theo dõi trạng thái Pods, Nodes, Deployments trên cụm máy chủ Kubernetes của doanh nghiệp.",
        "server_key": "kubernetes",
        "tools": [
            {"name": "k8s_get_pods", "desc": "Xem danh sách và trạng thái các Pods"},
            {"name": "k8s_get_logs", "desc": "Trích xuất logs của Pod bị lỗi CrashLoopBackOff"}
        ],
        "turnkey": True,
        "auth_type": "Local Kubeconfig",
        "config_template": {
            "command": "npx",
            "args": ["-y", "kubernetes-mcp"]
        }
    },
    {
        "id": "sentry",
        "name": "Sentry Error Tracking",
        "icon": "🛡️",
        "color": "#362D59",
        "category": "Lập Trình & DevOps",
        "provider": "Functional Software",
        "description": "Bắt lỗi ngoại lệ, phân tích stack trace và theo dõi cảnh báo sự cố kỹ thuật theo thời gian thực.",
        "server_key": "sentry",
        "tools": [
            {"name": "sentry_list_issues", "desc": "Liệt kê các sự cố và ngoại lệ mới phát sinh"},
            {"name": "sentry_get_issue", "desc": "Xem chi tiết stack trace và ngữ cảnh của lỗi"}
        ],
        "turnkey": False,
        "auth_type": "Auth Token",
        "config_template": {
            "command": "npx",
            "args": ["-y", "@sentry/mcp-server"],
            "env": {"SENTRY_AUTH_TOKEN": "${SENTRY_AUTH_TOKEN}", "SENTRY_ORG": "${SENTRY_ORG}"}
        },
        "fields": [
            {"key": "SENTRY_AUTH_TOKEN", "label": "Sentry User Auth Token", "placeholder": "sntrys_...", "required": True},
            {"key": "SENTRY_ORG", "label": "Organization Slug", "placeholder": "genesis-corp", "required": True}
        ]
    },
    {
        "id": "cloudflare",
        "name": "Cloudflare DNS & Workers",
        "icon": "🟧",
        "color": "#F38020",
        "category": "Lập Trình & DevOps",
        "provider": "Cloudflare, Inc.",
        "description": "Quản lý bản ghi tên miền DNS, kiểm tra lưu lượng mạng DDoS và cấu hình quy tắc bảo mật WAF.",
        "server_key": "cloudflare",
        "tools": [
            {"name": "cf_list_dns_records", "desc": "Xem danh sách bản ghi DNS của tên miền"},
            {"name": "cf_update_dns_record", "desc": "Cập nhật địa chỉ IP trỏ về máy chủ mới"}
        ],
        "turnkey": False,
        "auth_type": "API Token",
        "config_template": {
            "command": "npx",
            "args": ["-y", "cloudflare-mcp"],
            "env": {"CLOUDFLARE_API_TOKEN": "${CLOUDFLARE_API_TOKEN}"}
        },
        "fields": [
            {"key": "CLOUDFLARE_API_TOKEN", "label": "Cloudflare API Token", "placeholder": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", "required": True}
        ]
    },

    # ================= 5. CƠ SỞ DỮ LIỆU & BỘ NHỚ =================
    {
        "id": "sqlite",
        "name": "SQLite Database",
        "icon": "🗄️",
        "color": "#003B57",
        "category": "Cơ Sở Dữ Liệu & Bộ Nhớ",
        "provider": "Model Context Protocol",
        "description": "Thao tác đọc/ghi trực tiếp vào file cơ sở dữ liệu heo.db nội bộ của Heo OS (quản lý tin nhắn, công việc, danh bạ 360).",
        "server_key": "sqlite",
        "tools": [
            {"name": "read_query", "desc": "Truy vấn bảng trong file SQLite heo.db"},
            {"name": "write_query", "desc": "Cập nhật dữ liệu vào file SQLite heo.db"}
        ],
        "turnkey": True,
        "auth_type": "Zero-Config (Local DB)",
        "config_template": {
            "command": "npx",
            "args": ["-y", "mcp-server-sqlite", "--db", "${DB_PATH}"]
        },
        "fields": [
            {"key": "DB_PATH", "label": "Đường dẫn file database (.db)", "placeholder": "/home/ryan/heo-harness/data/heo.db", "required": False}
        ]
    },
    {
        "id": "postgres",
        "name": "PostgreSQL Database",
        "icon": "🐘",
        "color": "#336791",
        "category": "Cơ Sở Dữ Liệu & Bộ Nhớ",
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
        "category": "Cơ Sở Dữ Liệu & Bộ Nhớ",
        "provider": "Model Context Protocol",
        "description": "Truy vấn dữ liệu tài chính, bán hàng và nhân sự từ MySQL/MariaDB Server.",
        "server_key": "mysql",
        "tools": [
            {"name": "mysql_query", "desc": "Thực thi truy vấn SQL trên MySQL"},
            {"name": "mysql_tables", "desc": "Liệt kê danh sách các bảng"}
        ],
        "turnkey": False,
        "auth_type": "Connection Parameters",
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
        "id": "redis",
        "name": "Redis In-Memory Cache",
        "icon": "🔴",
        "color": "#DC382D",
        "category": "Cơ Sở Dữ Liệu & Bộ Nhớ",
        "provider": "Redis Ltd.",
        "description": "Kiểm tra cache bộ nhớ đệm, quản lý khóa session và tra cứu dữ liệu thời gian thực tốc độ cao.",
        "server_key": "redis",
        "tools": [
            {"name": "redis_get", "desc": "Đọc giá trị của khóa cache Redis"},
            {"name": "redis_set", "desc": "Lưu khóa và dữ liệu vào Redis cache"}
        ],
        "turnkey": False,
        "auth_type": "Redis URI",
        "config_template": {
            "command": "npx",
            "args": ["-y", "redis-mcp", "--url", "${REDIS_URL}"]
        },
        "fields": [
            {"key": "REDIS_URL", "label": "Redis Connection URL", "placeholder": "redis://localhost:6379", "required": True}
        ]
    },
    {
        "id": "mongodb",
        "name": "MongoDB NoSQL Database",
        "icon": "🍃",
        "color": "#47A248",
        "category": "Cơ Sở Dữ Liệu & Bộ Nhớ",
        "provider": "MongoDB Inc.",
        "description": "Truy vấn tài liệu JSON dạng NoSQL, xem collections và bóc tách dữ liệu linh hoạt.",
        "server_key": "mongodb",
        "tools": [
            {"name": "mongodb_find", "desc": "Tìm kiếm tài liệu document trong collection MongoDB"},
            {"name": "mongodb_list_collections", "desc": "Liệt kê danh sách các collection hiện có"}
        ],
        "turnkey": False,
        "auth_type": "MongoDB URI",
        "config_template": {
            "command": "npx",
            "args": ["-y", "mongodb-mcp-server", "--uri", "${MONGODB_URI}"]
        },
        "fields": [
            {"key": "MONGODB_URI", "label": "MongoDB Connection String", "placeholder": "mongodb://localhost:27017/mydb", "required": True}
        ]
    },
    {
        "id": "supabase",
        "name": "Supabase Backend Cloud",
        "icon": "⚡",
        "color": "#3ECF8E",
        "category": "Cơ Sở Dữ Liệu & Bộ Nhớ",
        "provider": "Supabase Inc.",
        "description": "Nền tảng Backend-as-a-Service gồm PostgreSQL, Auth, Storage và Edge Functions đám mây.",
        "server_key": "supabase",
        "tools": [
            {"name": "supabase_query", "desc": "Truy vấn bảng qua Supabase REST API"},
            {"name": "supabase_upload", "desc": "Lưu trữ tệp tin vào Supabase Storage Bucket"}
        ],
        "turnkey": False,
        "auth_type": "Project URL & Service Key",
        "config_template": {
            "command": "npx",
            "args": ["-y", "supabase-mcp"],
            "env": {"SUPABASE_URL": "${SUPABASE_URL}", "SUPABASE_KEY": "${SUPABASE_KEY}"}
        },
        "fields": [
            {"key": "SUPABASE_URL", "label": "Supabase Project URL", "placeholder": "https://xyz.supabase.co", "required": True},
            {"key": "SUPABASE_KEY", "label": "Supabase Service Role Key", "placeholder": "eyJh...", "required": True}
        ]
    },

    # ================= 6. TÌM KIẾM & DỮ LIỆU WEB =================
    {
        "id": "playwright",
        "name": "Web Browser (Playwright)",
        "icon": "🌐",
        "color": "#2E7D32",
        "category": "Tìm Kiếm & Dữ Liệu Web",
        "provider": "Microsoft / Playwright",
        "description": "Điều khiển trình duyệt Chrome lướt web, cào tin tức thị trường, chụp ảnh bằng chứng và tương tác web.",
        "server_key": "playwright",
        "tools": [
            {"name": "browser_navigate", "desc": "Truy cập đường dẫn URL chỉ định"},
            {"name": "browser_click", "desc": "Click vào phần tử nút bấm hoặc liên kết"},
            {"name": "browser_take_screenshot", "desc": "Chụp ảnh màn hình bằng chứng"}
        ],
        "turnkey": True,
        "auth_type": "Local Headless Chrome",
        "config_template": {
            "command": "npx",
            "args": ["-y", "@playwright/mcp", "--browser", "chrome"]
        }
    },
    {
        "id": "brave_search",
        "name": "Brave Search Engine",
        "icon": "🔍",
        "color": "#FB542B",
        "category": "Tìm Kiếm & Dữ Liệu Web",
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
            "env": {"BRAVE_API_KEY": "${BRAVE_API_KEY}"}
        },
        "fields": [
            {"key": "BRAVE_API_KEY", "label": "Brave Search API Key", "placeholder": "BSA...", "required": True}
        ]
    },
    {
        "id": "tavily_search",
        "name": "Tavily AI Search",
        "icon": "🌐",
        "color": "#2563EB",
        "category": "Tìm Kiếm & Dữ Liệu Web",
        "provider": "Tavily AI",
        "description": "Công cụ tìm kiếm AI chuyên sâu, tự động lọc và tóm tắt nguồn tin học thuật & nghiên cứu thị trường.",
        "server_key": "tavily",
        "tools": [
            {"name": "tavily_search", "desc": "Tìm kiếm nguồn tin cậy tối ưu cho mô hình ngôn ngữ lớn"}
        ],
        "turnkey": False,
        "auth_type": "API Key",
        "config_template": {
            "command": "npx",
            "args": ["-y", "tavily-mcp"],
            "env": {"TAVILY_API_KEY": "${TAVILY_API_KEY}"}
        },
        "fields": [
            {"key": "TAVILY_API_KEY", "label": "Tavily API Key (tvly-...)", "placeholder": "tvly-xxxxxxxxxxxxxxxxxxxx", "required": True}
        ]
    },
    {
        "id": "fetch_scraper",
        "name": "Fetch & Web Scraper",
        "icon": "📑",
        "color": "#06B6D4",
        "category": "Tìm Kiếm & Dữ Liệu Web",
        "provider": "Model Context Protocol",
        "description": "Cào nội dung trang web bất kỳ và chuyển đổi thành định dạng Markdown chuẩn cực nhanh.",
        "server_key": "fetch",
        "tools": [
            {"name": "fetch", "desc": "Tải trang web và chuyển đổi HTML thành Markdown sạch"}
        ],
        "turnkey": True,
        "auth_type": "Zero-Config (0đ API)",
        "config_template": {
            "command": "npx",
            "args": ["-y", "mcp-server-fetch"]
        }
    },
    {
        "id": "wikipedia",
        "name": "Wikipedia Knowledge",
        "icon": "📖",
        "color": "#636466",
        "category": "Tìm Kiếm & Dữ Liệu Web",
        "provider": "Wikimedia Foundation",
        "description": "Tra cứu kiến thức bách khoa toàn thư, tiểu sử đối tác, định nghĩa chuyên ngành và sự kiện lịch sử.",
        "server_key": "wikipedia",
        "tools": [
            {"name": "wiki_summary", "desc": "Tra cứu tóm tắt bài viết Wikipedia theo từ khóa"},
            {"name": "wiki_search", "desc": "Tìm kiếm danh sách bài viết liên quan"}
        ],
        "turnkey": True,
        "auth_type": "Zero-Config (0đ API)",
        "config_template": {
            "command": "npx",
            "args": ["-y", "wikipedia-mcp"]
        }
    },

    # ================= 7. TÀI CHÍNH & THỊ TRƯỜNG =================
    {
        "id": "yahoo_finance",
        "name": "Yahoo Finance Market",
        "icon": "📈",
        "color": "#6001D2",
        "category": "Tài Chính & Thị Trường",
        "provider": "Yahoo! Finance",
        "description": "Tra cứu giá cổ phiếu thời gian thực (VN-Index, Apple, VinFast, Google...), chỉ số tài chính và P/E.",
        "server_key": "yahoo-finance",
        "tools": [
            {"name": "get_stock_price", "desc": "Tra cứu giá cổ phiếu và biến động phần trăm"},
            {"name": "get_financials", "desc": "Xem báo cáo tài chính doanh nghiệp niêm yết"}
        ],
        "turnkey": True,
        "auth_type": "Zero-Config (0đ API)",
        "config_template": {
            "command": "npx",
            "args": ["-y", "yahoo-finance-mcp"]
        }
    },
    {
        "id": "binance_crypto",
        "name": "Binance Crypto Market",
        "icon": "🪙",
        "color": "#F0B90B",
        "category": "Tài Chính & Thị Trường",
        "provider": "Binance Exchange",
        "description": "Theo dõi biến động thị trường tiền mã hóa thời gian thực (Bitcoin, Ethereum, USDT) 24/7.",
        "server_key": "binance",
        "tools": [
            {"name": "get_crypto_price", "desc": "Xem giá spot Bitcoin, ETH và khối lượng 24h"},
            {"name": "get_orderbook", "desc": "Xem sổ lệnh khớp mua/bán độ sâu thị trường"}
        ],
        "turnkey": True,
        "auth_type": "Zero-Config (0đ API)",
        "config_template": {
            "command": "npx",
            "args": ["-y", "binance-mcp"]
        }
    },
    {
        "id": "stripe",
        "name": "Stripe Payments & Billing",
        "icon": "💳",
        "color": "#635BFF",
        "category": "Tài Chính & Thị Trường",
        "provider": "Stripe, Inc.",
        "description": "Kiểm tra doanh thu, quản lý khách hàng trả phí thuê bao, tra cứu hóa đơn và xử lý hoàn tiền.",
        "server_key": "stripe",
        "tools": [
            {"name": "stripe_get_balance", "desc": "Xem số dư tài khoản doanh nghiệp Stripe"},
            {"name": "stripe_list_charges", "desc": "Xem các giao dịch thanh toán thành công gần nhất"}
        ],
        "turnkey": False,
        "auth_type": "Stripe Secret Key",
        "config_template": {
            "command": "npx",
            "args": ["-y", "stripe-mcp"],
            "env": {"STRIPE_SECRET_KEY": "${STRIPE_SECRET_KEY}"}
        },
        "fields": [
            {"key": "STRIPE_SECRET_KEY", "label": "Stripe Restricted / Secret Key (rk_... hoặc sk_...)", "placeholder": "rk_live_...", "required": True}
        ]
    },

    # ================= 8. TRÍ TUỆ & TƯ DUY AI =================
    {
        "id": "memory_graph",
        "name": "Memory Knowledge Graph",
        "icon": "🧠",
        "color": "#EC4899",
        "category": "Trí Tuệ & Tư Duy AI",
        "provider": "Anthropic / MCP",
        "description": "Lưu trữ đồ thị tri thức dài hạn, liên kết thông tin giữa các thực thể và bối cảnh của Sếp vĩnh viễn.",
        "server_key": "memory",
        "tools": [
            {"name": "create_entities", "desc": "Tạo thực thể mới trong bộ nhớ tri thức"},
            {"name": "create_relations", "desc": "Tạo mối quan hệ liên kết giữa các thực thể"},
            {"name": "search_nodes", "desc": "Tra cứu mạng lưới thông tin theo từ khóa"}
        ],
        "turnkey": True,
        "auth_type": "Zero-Config (Local)",
        "config_template": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-memory"]
        }
    },
    {
        "id": "sequential_thinking",
        "name": "Sequential Thinking (Tư Duy Sâu)",
        "icon": "🤔",
        "color": "#8B5CF6",
        "category": "Trí Tuệ & Tư Duy AI",
        "provider": "Anthropic / MCP",
        "description": "Khả năng suy luận đa bước tuần tự (tương đương DeepSeek R1 / OpenAI o1), tự kiểm chứng và phân tích vấn đề phức tạp.",
        "server_key": "sequential-thinking",
        "tools": [
            {"name": "sequentialthinking", "desc": "Quy trình tư duy động, lập giả thuyết, rẽ nhánh và thẩm định từng bước"}
        ],
        "turnkey": True,
        "auth_type": "Zero-Config (0đ API)",
        "config_template": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
        }
    },
    {
        "id": "filesystem",
        "name": "Quản Trị Tệp Tin (Local Filesystem)",
        "icon": "📂",
        "color": "#F59E0B",
        "category": "Trí Tuệ & Tư Duy AI",
        "provider": "Model Context Protocol",
        "description": "Đọc, duyệt và quản lý tài liệu trong thư mục làm việc Heo-Harness và Documents của Sếp trên máy chủ.",
        "server_key": "filesystem",
        "tools": [
            {"name": "read_file", "desc": "Đọc nội dung tệp tin văn bản, code, markdown"},
            {"name": "write_file", "desc": "Ghi hoặc sửa nội dung tệp tin tài liệu"},
            {"name": "list_directory", "desc": "Liệt kê danh sách file và thư mục con"},
            {"name": "search_files", "desc": "Tìm kiếm tài liệu theo từ khóa hoặc định dạng"}
        ],
        "turnkey": True,
        "auth_type": "Zero-Config (Cục Bộ)",
        "config_template": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", "/home/ryan/heo-harness", "/home/ryan/Documents"]
        }
    },
    {
        "id": "phone_control",
        "name": "Mobile Phone Control",
        "icon": "📱",
        "color": "#10B981",
        "category": "Trí Tuệ & Tư Duy AI",
        "provider": "Genesis Mobile Bridge",
        "description": "Chụp ảnh màn hình điện thoại, kiểm tra tin nhắn, chuyển file và chạy lệnh shell trên thiết bị cầm tay.",
        "server_key": "genos-hub",
        "tools": [
            {"name": "phone_screenshot", "desc": "Chụp ảnh màn hình điện thoại từ xa"},
            {"name": "phone_control", "desc": "Thao tác chạm, vuốt màn hình cảm ứng"},
            {"name": "phone_shell", "desc": "Chạy lệnh hệ điều hành di động"}
        ],
        "turnkey": True,
        "auth_type": "Genesis Device Bridge",
        "default_command": "node /home/ryan/mcp-genos-bridge.js"
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
            params = dict(form_params or {})
            for k, v in list(params.items()):
                params[k.upper()] = v
                params[k.lower()] = v
            if app_id == "sqlite" and not params.get("DB_PATH"):
                params["DB_PATH"] = "/home/ryan/heo-harness/data/heo.db"

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
