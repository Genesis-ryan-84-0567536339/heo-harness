# -*- coding: utf-8 -*-
import json
import os

AUDIT_DATA = [
    # 1. Brand & Identity
    {
        "id": "SPEC-01",
        "category": "Brand & Identity",
        "name": "Đổi tên sản phẩm sang Gen-Harness",
        "spec_req": "Đổi tên chính thức từ Heo-Harness / Bé Heo sang Gen-Harness (Genesis Harness OS). Bỏ hoàn toàn danh xưng cố định Bé Heo ở cấp độ hệ điều hành.",
        "current_state": "Hệ thống vẫn giữ tên Heo-Harness, HEO OS, heo-harness repo, docs vẫn là HEO-HARNESS & AGY-ASSIS.",
        "status": "REFACTOR",
        "status_label": "🔵 Cần Tái Cấu Trúc",
        "pct": 20,
        "gap": "Cần đổi tên repo/thương hiệu, cập nhật title UI, docs, config sang Gen-Harness (Genesis Harness OS).",
        "source_ref": "heo_harness/core/, dashboard.html, GEMINI.md"
    },
    {
        "id": "SPEC-02",
        "category": "Brand & Identity",
        "name": "Đa danh tính Agent Identity (Multi-Identity Engine)",
        "spec_req": "Agent Bot không còn mặc định là Bé Heo. User tự định nghĩa: tên gọi, vai trò, xưng hô, giọng điệu, phạm vi việc, ngôn ngữ, mức tự trị riêng cho từng agent.",
        "current_state": "Đã có Persona Studio, Global Directives, custom tone theo group. Tuy nhiên bot vẫn mặc định xưng 'Bé Heo' - 'Sếp', nick Zalo 'Heo'. Chưa có Entity Agent Identity độc lập.",
        "status": "WIP",
        "status_label": "🟡 Đang Hoàn Thiện",
        "pct": 40,
        "gap": "Tách lõi Persona thành Agent Identity Engine cho phép tạo/sửa/nhân bản nhiều Agent trên cùng chassis mà không đụng lõi dữ liệu.",
        "source_ref": "heo_harness/plugins/persona/__init__.py, store.py"
    },
    {
        "id": "SPEC-03",
        "category": "Brand & Identity",
        "name": "Thư viện Persona Templates có sẵn",
        "spec_req": "Cung cấp mẫu template sẵn: Trợ lý thương mại, Key Account junior, Admin hậu cần, CSKH, Recruiter, Thư ký cá nhân; 'Bé Heo' chỉ là template hoài niệm tắt mặc định.",
        "current_state": "Đang tích hợp 7 thái độ persona điều hành (Chiến Lược, Thực Thi, Phân Tích...) và skills persona, nhưng chưa tổ chức thành thư viện Agent Profile Templates.",
        "status": "WIP",
        "status_label": "🟡 Đang Hoàn Thiện",
        "pct": 45,
        "gap": "Đóng gói các template vai trò kinh doanh (Commercial, CSKH, HR, Secretary) thành 1-click install profiles.",
        "source_ref": "skills/, heo_harness/plugins/persona/"
    },

    # 2. Operating Loop (LISTEN - STRUCTURE - SCORE - MATCH - ACT - LEARN)
    {
        "id": "SPEC-04",
        "category": "Operating Loop",
        "name": "[LISTEN] Radar thu nạp đa kênh",
        "spec_req": "Lắng nghe Zalo, WhatsApp, Telegram, Facebook, LinkedIn và có thể mở rộng Discord, Email, Webhook.",
        "current_state": "Zalo Gateway hoạt động thực tế 100% (cổng 5051). WhatsApp Gateway module Baileys sẵn sàng (cổng 5052, chờ QR). Chưa có Telegram, FB, LinkedIn.",
        "status": "WIP",
        "status_label": "🟡 Đang Hoàn Thiện",
        "pct": 50,
        "gap": "Cần kích hoạt WhatsApp live và phát triển tiếp 2 kênh quan trọng kế tiếp: Telegram Bot API và Facebook Business/Personal webhook.",
        "source_ref": "heo_harness/plugins/channel_zalo/, channel_whatsapp/"
    },
    {
        "id": "SPEC-05",
        "category": "Operating Loop",
        "name": "[LISTEN] Ranh giới & Quy tắc lắng nghe phân tầng",
        "spec_req": "Chế độ: chỉ @tag mới trả lời, lắng nghe im lặng (passive monitor), hoặc chủ động bắt tín hiệu (proactive signal catch) theo từng group/kênh.",
        "current_state": "Đã có toggle tag_filter, reply_non_owners, bot_active per group trong Zalo & WhatsApp.",
        "status": "DONE",
        "status_label": "🟢 Đạt Chuẩn",
        "pct": 85,
        "gap": "Bổ sung thêm chế độ 'Chủ động bắt tín hiệu thương mại' (không reply công khai nhưng ngầm gửi về hàng đợi cơ hội).",
        "source_ref": "channel_zalo/bot.js, data/active_groups.json"
    },
    {
        "id": "SPEC-06",
        "category": "Operating Loop",
        "name": "[STRUCTURE] Conversation Data Factory - Tách Thực thể",
        "spec_req": "Tách thực thể từ chat: người, công ty, hàng hóa, địa điểm, mức giá ước lượng, số lượng.",
        "current_state": "Hiện tại mới lưu raw chat message vào SQLite và mảng JSON log, chưa có NER (Named Entity Recognition) hoặc LLM Extraction pipeline.",
        "status": "MISSING",
        "status_label": "🔴 Còn Thiếu",
        "pct": 20,
        "gap": "Xây dựng Background Worker trích xuất Entity tự động từ các tin nhắn mới vào bảng SQLite `entities`.",
        "source_ref": "heo_harness/core/store.py, data/heo.db"
    },
    {
        "id": "SPEC-07",
        "category": "Operating Loop",
        "name": "[STRUCTURE] Nhận diện Ý định (Intent Recognition)",
        "spec_req": "Phân loại ý định: hỏi giá, than phiền, tìm đối tác, xin việc, chốt lịch, giao hàng, thanh toán...",
        "current_state": "Chat chỉ xử lý hỏi đáp trực tiếp (Direct Q&A), chưa phân loại gắn nhãn Intent cho từng đoạn hội thoại.",
        "status": "MISSING",
        "status_label": "🔴 Còn Thiếu",
        "pct": 15,
        "gap": "Tạo Intent Classifier (Prompt-based qua Gemini Flash 0đ) tự động gán nhãn cho các incoming messages.",
        "source_ref": "heo_harness/plugins/provider_antigravity/"
    },
    {
        "id": "SPEC-08",
        "category": "Operating Loop",
        "name": "[STRUCTURE] Trích xuất Sự kiện nguyên tử (Atomic Events)",
        "spec_req": "Biến hội thoại thành các sự kiện nguyên tử: AskedPrice, Complained, PromisedDelivery, ScheduledMeeting, SentQuotation, MentionsCompetitor, WentSilent.",
        "current_state": "Chưa có bảng sự kiện nguyên tử (Events table). Tin nhắn vẫn được lưu theo mô hình đoạn chat thông thường.",
        "status": "MISSING",
        "status_label": "🔴 Còn Thiếu",
        "pct": 15,
        "gap": "Định nghĩa Schema Event-Driven trong SQLite và Event Bus để biến mỗi message quan trọng thành 1 Domain Event.",
        "source_ref": "heo_harness/core/events.py, data/heo.db"
    },
    {
        "id": "SPEC-09",
        "category": "Operating Loop",
        "name": "[SCORE] Evaluation Fabric - Chấm điểm đa chiều",
        "spec_req": "Chấm điểm tiềm năng, mức độ gắn kết, rủi ro churn, hiệu suất phản hồi, độ nóng cơ hội, và độ tin cậy dữ liệu (data confidence).",
        "current_state": "Có bảng mô phỏng tĩnh / work metrics trong state, chưa có engine tính điểm động dựa trên hành vi chat thật.",
        "status": "MISSING",
        "status_label": "🔴 Còn Thiếu",
        "pct": 20,
        "gap": "Phát triển plugin `gen-intelligence-evaluator` tự động chấm điểm hồ sơ theo công thức minh bạch.",
        "source_ref": "heo_harness/plugins/policy_gate/, store.py"
    },
    {
        "id": "SPEC-10",
        "category": "Operating Loop",
        "name": "[SCORE] Tính năng Giải thích điểm số (Explainable AI)",
        "spec_req": "Mọi điểm số trên Console đều phải giải thích được ('Vì sao khách này 82 điểm', 'Vì sao nhân viên này bị cảnh báo').",
        "current_state": "Chưa có logic giải thích điểm số.",
        "status": "MISSING",
        "status_label": "🔴 Còn Thiếu",
        "pct": 10,
        "gap": "Bổ sung trường `score_reason` và `evidence_message_ids` trong snapshot đánh giá.",
        "source_ref": "Spec Mục C3, E6"
    },
    {
        "id": "SPEC-11",
        "category": "Operating Loop",
        "name": "[MATCH] Opportunity Engine - Lọc & Khai thác cơ hội",
        "spec_req": "Lắng nghe nhiều group để phát hiện người cần hàng/dịch vụ/đối tác; xếp hạng độ nóng và tin cậy; tránh spam.",
        "current_state": "Chưa có Opportunity Engine.",
        "status": "MISSING",
        "status_label": "🔴 Còn Thiếu",
        "pct": 10,
        "gap": "Xây dựng detector phát hiện từ khóa nhu cầu (cần mua, tìm xưởng, báo giá, tuyển...) trong các nhóm Zalo/WhatsApp.",
        "source_ref": "Spec Mục E3"
    },
    {
        "id": "SPEC-12",
        "category": "Operating Loop",
        "name": "[MATCH] Ráp cung với cầu & Hàng đợi cơ hội",
        "spec_req": "Ráp cung với cầu (bên cần mua với bên bán hoặc nhân viên phụ trách), tạo hàng đợi cho người dùng phê duyệt xử lý.",
        "current_state": "Chưa có logic ráp cung-cầu.",
        "status": "MISSING",
        "status_label": "🔴 Còn Thiếu",
        "pct": 5,
        "gap": "Tích hợp bảng Catalog sản phẩm/dịch vụ nội bộ để so khớp với nhu cầu bắt được từ group chat.",
        "source_ref": "Spec Mục E3"
    },
    {
        "id": "SPEC-13",
        "category": "Operating Loop",
        "name": "[ACT] System of Action - Hành động có kiểm soát",
        "spec_req": "Nhắn, im lặng có chủ đích, soạn sẵn chờ duyệt, tạo task, nhắc việc, ghi CRM, tạo đơn nháp ERP, gán người.",
        "current_state": "Đã có các action: Gửi tin nhắn Zalo, Tạo file Word/Excel, Tạo ảnh AI, Quản lý danh sách Approval chờ duyệt.",
        "status": "WIP",
        "status_label": "🟡 Đang Hoàn Thiện",
        "pct": 55,
        "gap": "Kết nối luồng phê duyệt (Approvals) trực tiếp vào các tác vụ thương mại (soạn hợp đồng, gửi báo giá vào chat).",
        "source_ref": "ui_dashboard/__init__.py, tool_office/"
    },
    {
        "id": "SPEC-14",
        "category": "Operating Loop",
        "name": "[ACT] Thang 6 mức tự trị (Autonomy Levels 0-6)",
        "spec_req": "Thang tự trị từ Mức 0 (Chỉ ghi nhận) đến Mức 6 (Tự thực thi whitelist). Cho phép cấu hình theo kênh, theo việc.",
        "current_state": "Đã có kiểm soát quyền chủ nhân và cơ chế PIN, nhưng chưa chia thành thang 6 mức tự trị có thể điều chỉnh qua UI.",
        "status": "WIP",
        "status_label": "🟡 Đang Hoàn Thiện",
        "pct": 35,
        "gap": "Thêm thanh trượt Autonomy Level (0-6) trong cài đặt từng group và từng Agent Identity.",
        "source_ref": "Spec Mục H1, heo_harness/plugins/policy_gate/"
    },
    {
        "id": "SPEC-15",
        "category": "Operating Loop",
        "name": "[LEARN] Vòng lặp học và làm giàu hồ sơ (Feedback Loop)",
        "spec_req": "Kết quả hành động (chốt deal, bị từ chối, than phiền) tự động quay lại cập nhật Living Profile và tinh chỉnh tiêu chí chấm điểm.",
        "current_state": "Chưa có cơ chế feedback loop tự động.",
        "status": "MISSING",
        "status_label": "🔴 Còn Thiếu",
        "pct": 10,
        "gap": "Ghi nhận outcome sau mỗi deal/case vào hồ sơ khách hàng để tính tỷ lệ chuyển đổi.",
        "source_ref": "Spec Mục C1.6"
    },

    # 3. 10 Màn Hình Console UI (Spec Mục F2)
    {
        "id": "SPEC-16",
        "category": "Console Screens",
        "name": "[UI-01] Command Overview - Màn hình điều hành 10 phút",
        "spec_req": "Sức khỏe hệ thống, nhiệt kế hoạt động, hàng đợi cần xử lý (cơ hội/cảnh báo/hạn), 5 đối tượng đáng chú ý nhất, 5 tín hiệu thị trường.",
        "current_state": "Dashboard Nocturne Executive có: System Health, Kênh kết nối, Quick Actions, Stats số lượng. Chưa có 5 đối tượng đáng chú ý và 5 tín hiệu thị trường.",
        "status": "WIP",
        "status_label": "🟡 Đang Hoàn Thiện",
        "pct": 65,
        "gap": "Bổ sung 2 widget cốt lõi: 'Top 5 Đối Tượng Đáng Chú Ý Hôm Nay' và '5 Tín Hiệu Cơ Hội / Thị Trường Đang Nổi'.",
        "source_ref": "heo_harness/plugins/ui_dashboard/dashboard.html"
    },
    {
        "id": "SPEC-17",
        "category": "Console Screens",
        "name": "[UI-01] Chỉ số Độ tin cậy dữ liệu (Data Confidence Index)",
        "spec_req": "Hiển thị % hồ sơ thiếu danh tính, % điểm số tin cậy thấp, % sự kiện chưa gán người, giúp lãnh đạo không tự tin sai.",
        "current_state": "Chưa có widget tính toán và hiển thị Data Confidence.",
        "status": "MISSING",
        "status_label": "🔴 Còn Thiếu",
        "pct": 15,
        "gap": "Thêm công thức quét tỷ lệ dữ liệu khuyết thiếu và hiển thị thanh Data Confidence trên Overview.",
        "source_ref": "Spec Mục F4"
    },
    {
        "id": "SPEC-18",
        "category": "Console Screens",
        "name": "[UI-02] Inbox of Meaning - Hộp thư ý nghĩa",
        "spec_req": "Hàng đợi đơn vị ý nghĩa (cơ hội mới, hỏi giá, than phiền, lịch hẹn, tài liệu cần soạn, tin chờ duyệt, ứng viên). Có tóm tắt 2 câu và đề xuất hành động.",
        "current_state": "Hiện có Live Console xem tin nhắn raw của Zalo/WhatsApp và tab Approvals. Chưa gộp thành Inbox of Meaning.",
        "status": "WIP",
        "status_label": "🟡 Đang Hoàn Thiện",
        "pct": 35,
        "gap": "Chuyển đổi giao diện Chat Log thông thường thành Thẻ Đơn Vị Ý Nghĩa (Actionable Meaning Cards).",
        "source_ref": "dashboard.html (Tab Live Console & Approvals)"
    },
    {
        "id": "SPEC-19",
        "category": "Console Screens",
        "name": "[UI-03] Relationship Map - Bản đồ quan hệ đồ thị sống",
        "spec_req": "Danh sách lọc mạnh + Đồ thị Node/Edge trực quan (người/tổ chức/group). Thấy rõ ai là cầu nối, ai đang lạnh, nhân viên nào ôm quá nhiều việc.",
        "current_state": "Có tab Groups 360 và Person 360 dạng danh sách/thẻ tĩnh. Chưa có đồ thị mạng lưới quan hệ trực quan (Graph/Canvas).",
        "status": "WIP",
        "status_label": "🟡 Đang Hoàn Thiện",
        "pct": 40,
        "gap": "Tích hợp thư viện đồ thị quan hệ (D3.js hoặc Vis.js) để trực quan hóa tương tác giữa các bên.",
        "source_ref": "dashboard.html (Tab Groups & Person 360)"
    },
    {
        "id": "SPEC-20",
        "category": "Console Screens",
        "name": "[UI-04] Living Profile - Hồ sơ sống đa kênh",
        "spec_req": "Gộp danh tính đa kênh, tóm tắt 8-12 dòng tự cập nhật, điểm số + giải thích, timeline sự kiện, tài liệu đã gửi, task mở, mức tự trị riêng.",
        "current_state": "Đã có giao diện Person 360 chi tiết: thông tin, nhóm tham gia, lịch sử tin nhắn, ghi chú, toggle bot. Thiếu tóm tắt AI tự động và timeline sự kiện.",
        "status": "WIP",
        "status_label": "🟡 Đang Hoàn Thiện",
        "pct": 50,
        "gap": "Bổ sung AI Summary Generator (8-12 dòng) và hiển thị Timeline sự kiện nguyên tử thay cho danh sách tin thô.",
        "source_ref": "ui_dashboard/__init__.py, dashboard.html"
    },
    {
        "id": "SPEC-21",
        "category": "Console Screens",
        "name": "[UI-05] Opportunity Board - Bảng cơ hội sống từ chat",
        "spec_req": "Kanban pipeline cơ hội sống từ hội thoại (Tín hiệu thô -> Đã xác thực -> Ráp khớp -> Tiếp cận -> Đàm phán -> Nội bộ -> Thắng/Trượt).",
        "current_state": "Hiện có tab Workload Matrix và Works (quản lý công việc chung), chưa có Kanban Board chuyên dụng cho Cơ hội thương mại.",
        "status": "MISSING",
        "status_label": "🔴 Còn Thiếu",
        "pct": 25,
        "gap": "Xây dựng màn hình Opportunity Kanban Board kết nối trực tiếp với các tín hiệu bắt được từ chat Zalo/WhatsApp.",
        "source_ref": "Spec Mục F2.5"
    },
    {
        "id": "SPEC-22",
        "category": "Console Screens",
        "name": "[UI-06] People Review - Đánh giá con người 4 phân hệ",
        "spec_req": "4 Board riêng: Nhân viên, Khách hàng, Ứng viên, Học viên. Điểm, xu hướng lên/xuống, tín hiệu nổi bật tuần, khuyến nghị coaching, xem chứng cứ.",
        "current_state": "Chưa phân loại 4 nhóm đối tượng đánh giá riêng biệt.",
        "status": "MISSING",
        "status_label": "🔴 Còn Thiếu",
        "pct": 20,
        "gap": "Thêm phân vùng People Review 4 tab (Staff, Customers, Candidates, Trainees) trong Navigation Console.",
        "source_ref": "Spec Mục F2.6"
    },
    {
        "id": "SPEC-23",
        "category": "Console Screens",
        "name": "[UI-07] Care Quality - Giám sát chất lượng chăm sóc",
        "spec_req": "Đo lường: tốc độ phản hồi theo giờ, tỷ lệ follow sau báo giá, tỷ lệ hứa rồi quên, cảnh báo khách bị bỏ rơi, kịch bản chốt đơn thành công/thất bại.",
        "current_state": "Chưa có màn hình đo lường chỉ số Care Quality.",
        "status": "MISSING",
        "status_label": "🔴 Còn Thiếu",
        "pct": 15,
        "gap": "Viết bộ phân tích đo lường độ trễ trả lời (Response Latency) giữa tin nhắn khách và tin nhắn sale trong các group.",
        "source_ref": "Spec Mục F2.7"
    },
    {
        "id": "SPEC-24",
        "category": "Console Screens",
        "name": "[UI-08] Knowledge & Search - Kho hội thoại có não",
        "spec_req": "Tìm kiếm thông minh: theo ý định, người, mức giá, cảm xúc, tìm mẫu ('những khách từng hỏi X chưa chốt deal').",
        "current_state": "Tab Chat Big Data Intelligence đã hỗ trợ tìm kiếm từ khóa realtime, lọc theo kênh, xuất kết quả. Chưa có semantic search theo ý định.",
        "status": "WIP",
        "status_label": "🟡 Đang Hoàn Thiện",
        "pct": 50,
        "gap": "Thêm bộ lọc tìm kiếm theo Ý định (Hỏi giá, Than phiền, Chốt đơn) và Khoảng thời gian không tương tác.",
        "source_ref": "dashboard.html (Tab Chat Big Data)"
    },
    {
        "id": "SPEC-25",
        "category": "Console Screens",
        "name": "[UI-09] Workbench - Bàn soạn thảo & Hành động thương mại",
        "spec_req": "Nơi soạn báo giá, hợp đồng, biên bản, dịch thuật, tạo task, kéo dữ liệu ERP/CRM trực tiếp vào ngữ cảnh.",
        "current_state": "Có tab Office Suite (sinh Word .docx, Excel .xlsx), Media tool, Translate. Chưa hợp nhất thành Commercial Copilot Workbench liền mạch.",
        "status": "WIP",
        "status_label": "🟡 Đang Hoàn Thiện",
        "pct": 55,
        "gap": "Tạo giao diện soạn thảo báo giá/hợp đồng nhanh 1-click từ thông tin của khách trong hồ sơ Person 360.",
        "source_ref": "heo_harness/plugins/tool_office/, dashboard.html"
    },
    {
        "id": "SPEC-26",
        "category": "Console Screens",
        "name": "[UI-10] System Control - Quản trị Khung sườn & Kỹ thuật",
        "spec_req": "Quản trị Plugin, Circuit Breaker, Policy Gate, RBAC, PIN, MCP Connectors, Logs, Docker.",
        "current_state": "Rất hoàn thiện: 11 Plugins, Circuit Breaker monitor, 5-layer Policy, PIN Security, 48 App MCP Hub, SQLite & Filesystem MCP live.",
        "status": "DONE",
        "status_label": "🟢 Đạt Chuẩn",
        "pct": 95,
        "gap": "Bảo trì và bổ sung các metrics giám sát tài nguyên chi tiết hơn.",
        "source_ref": "heo_harness/core/, dashboard.html"
    },
    {
        "id": "SPEC-27",
        "category": "Console Screens",
        "name": "[UI-10] Agent Identity Studio trong System Control",
        "spec_req": "Màn hình tạo mới agent, đổi tên/role/giọng, gán kênh/group, chỉnh mức tự trị, bật/tắt từng agent, xem audit trail agent đã nói gì.",
        "current_state": "Đã có Persona Studio và Directives Editor, nhưng đang định hình 1 con bot duy nhất.",
        "status": "WIP",
        "status_label": "🟡 Đang Hoàn Thiện",
        "pct": 45,
        "gap": "Nâng cấp giao diện Persona Studio thành Multi-Agent Manager (Thêm/Sửa/Xóa Agent Profiles độc lập).",
        "source_ref": "dashboard.html (Tab Persona Studio)"
    },

    # 4. Mô Hình Dữ Liệu & Hợp Nhất Danh Tính
    {
        "id": "SPEC-28",
        "category": "Data & SSOT",
        "name": "Mô hình thực thể chuẩn hóa (Canonical Entities)",
        "spec_req": "Quản lý 16 thực thể: Identity, Channel Account, Organization, Group, Relationship, Thread, Event, Intent, Opportunity, Deal, Document, Task, Alert...",
        "current_state": "Đã quản lý: Account, Groups, People, Works, Calendar, Approvals, Policies, Audits, Live Logs trong SQLite/JSON store.",
        "status": "WIP",
        "status_label": "🟡 Đang Hoàn Thiện",
        "pct": 60,
        "gap": "Bổ sung các bảng còn khuyết: `opportunities`, `deals`, `atomic_events`, `identity_links` trong SQLite.",
        "source_ref": "heo_harness/core/store.py, data/heo.db"
    },
    {
        "id": "SPEC-29",
        "category": "Data & SSOT",
        "name": "Hợp nhất danh tính đa kênh (Identity Resolution)",
        "spec_req": "Gợi ý 2 tài khoản trên Zalo & WhatsApp có thể là một người thật; cho phép gộp/tách tay; giữ lịch sử liên kết.",
        "current_state": "Tài khoản Zalo và WhatsApp đang được lưu ở 2 danh sách riêng, chưa có cơ chế Match & Merge đa kênh.",
        "status": "MISSING",
        "status_label": "🔴 Còn Thiếu",
        "pct": 20,
        "gap": "Xây dựng thuật toán so khớp SĐT / Tên và giao diện 'Hợp nhất danh tính' (Merge Contacts).",
        "source_ref": "Spec Mục G2"
    },
    {
        "id": "SPEC-30",
        "category": "Data & SSOT",
        "name": "Kiến trúc Sự kiện nguyên tử (Event-Driven Persistence)",
        "spec_req": "Xây dựng hệ thống quanh Sự kiện có nghĩa thay vì chỉ lưu text chat thông thường.",
        "current_state": "Store hiện tại lưu tin nhắn theo format chat thông thường (`recent_messages`, `recent_live_logs`).",
        "status": "MISSING",
        "status_label": "🔴 Còn Thiếu",
        "pct": 25,
        "gap": "Chuyển đổi lưu trữ sang mô hình Event Store kèm metadata phong phú.",
        "source_ref": "Spec Mục G3"
    },
    {
        "id": "SPEC-31",
        "category": "Data & SSOT",
        "name": "Single Source of Truth (SSOT)",
        "spec_req": "Dữ liệu hồ sơ, điểm số, cơ hội, task phải về một kho logic duy nhất; plugin không giữ sự thật riêng.",
        "current_state": "Tuân thủ nghiêm ngặt: toàn bộ plugin đọc/ghi thông qua `ctx.inject('data_store')` với SQLite `data/heo.db` và `heo_state.json`.",
        "status": "DONE",
        "status_label": "🟢 Đạt Chuẩn",
        "pct": 95,
        "gap": "Duy trì tính nhất quán khi mở rộng các bảng dữ liệu mới.",
        "source_ref": "heo_harness/core/store.py"
    },

    # 5. MCP & Kết Nối Doanh Nghiệp
    {
        "id": "SPEC-32",
        "category": "MCP & Enterprise",
        "name": "Hệ thống MCP Connectors (ERP, CRM, HRM, File)",
        "spec_req": "Nối ERP, CRM, HRM, lịch, kho tài liệu để hội thoại và vận hành không sống hai thế giới riêng.",
        "current_state": "Đã tích hợp Turnkey App Connectors Hub với 48 enterprise apps, 22 kết nối, 56 tools.",
        "status": "DONE",
        "status_label": "🟢 Đạt Chuẩn",
        "pct": 80,
        "gap": "Tự động kích hoạt công cụ tra cứu tồn kho / pipeline CRM ngay trong lúc chat với khách.",
        "source_ref": "heo_harness/plugins/ui_dashboard/, artifacts/"
    },
    {
        "id": "SPEC-33",
        "category": "MCP & Enterprise",
        "name": "MCP Server SQLite & Filesystem nội bộ",
        "spec_req": "MCP Server truy xuất cơ sở dữ liệu lớn và tệp tin hệ thống an toàn.",
        "current_state": "Đang chạy nền trực tiếp 2 MCP servers: `mcp-server-sqlite` và `@modelcontextprotocol/server-filesystem`.",
        "status": "DONE",
        "status_label": "🟢 Đạt Chuẩn",
        "pct": 100,
        "gap": "Đã vận hành ổn định 100%.",
        "source_ref": "package.json, tmux heo-harness"
    },
    {
        "id": "SPEC-34",
        "category": "MCP & Enterprise",
        "name": "Commercial Copilot - Trợ lý mậu dịch",
        "spec_req": "Hỗ trợ đàm phán nhóm, phiên dịch trực tiếp, soạn hợp đồng/báo giá, nhắc lịch, ăn dữ liệu từ hồ sơ + ERP.",
        "current_state": "Đã có công cụ Office Reporter xuất file Word/Excel từ mẫu và AI Translation.",
        "status": "WIP",
        "status_label": "🟡 Đang Hoàn Thiện",
        "pct": 60,
        "gap": "Tự động trích xuất các điều khoản thỏa thuận trong chat để điền tự động vào template hợp đồng Word.",
        "source_ref": "heo_harness/plugins/tool_office/"
    },
    {
        "id": "SPEC-35",
        "category": "MCP & Enterprise",
        "name": "Bộ công cụ Đa phương tiện & Văn phòng (Office & Media)",
        "spec_req": "Xử lý tài liệu Word, bảng tính Excel, Audio TTS/STT, và Tranh ảnh AI sinh tạo.",
        "current_state": "Hoàn thiện 100% với 2 plugin chuyên trách: `heo-tool-office-reporter` và `heo-tool-media-processor`.",
        "status": "DONE",
        "status_label": "🟢 Đạt Chuẩn",
        "pct": 95,
        "gap": "Hoạt động hoàn chỉnh.",
        "source_ref": "heo_harness/plugins/tool_office/, tool_media/"
    },

    # 6. Bảo Mật, Phân Quyền & Đạo Đức
    {
        "id": "SPEC-36",
        "category": "Security & Ethics",
        "name": "Phân quyền RBAC Console phân tầng",
        "spec_req": "Phân tầng quyền hạn: Owner (toàn cảnh), Manager (thấy team), Operator (hàng đợi việc), Agent nhân viên, Auditor (xem log).",
        "current_state": "Đã có cấu trúc Boss Profiles (Chủ nhân, Phó ban điều hành, Khách demo) và xác thực tác quyền.",
        "status": "WIP",
        "status_label": "🟡 Đang Hoàn Thiện",
        "pct": 60,
        "gap": "Thực thi phân quyền view ẩn/hiện thực tế trên Console UI dựa theo role đang đăng nhập.",
        "source_ref": "heo_harness/plugins/auth/, store.py"
    },
    {
        "id": "SPEC-37",
        "category": "Security & Ethics",
        "name": "Tường lửa Policy Gate 5 tầng thẩm định",
        "spec_req": "Kiểm duyệt an toàn hội thoại, chống can thiệp trái phép, whitelist người gửi và lọc lệnh nhạy cảm.",
        "current_state": "Đã hoàn thành 100% với plugin `heo-policy-gate-firewall` bảo vệ 24/7.",
        "status": "DONE",
        "status_label": "🟢 Đạt Chuẩn",
        "pct": 95,
        "gap": "Vận hành hoàn hảo.",
        "source_ref": "heo_harness/plugins/policy_gate/"
    },
    {
        "id": "SPEC-38",
        "category": "Security & Ethics",
        "name": "Bảo mật PIN Admin SHA-256",
        "spec_req": "Xác thực PIN bảo vệ các thao tác can thiệp nhóm hoặc tác vụ điều hành nhạy cảm.",
        "current_state": "Đã tích hợp hoàn thiện xác thực mã PIN bảo vệ nhóm và thao tác hệ thống.",
        "status": "DONE",
        "status_label": "🟢 Đạt Chuẩn",
        "pct": 100,
        "gap": "Đã vượt qua bài kiểm tra thực tế.",
        "source_ref": "heo_harness/plugins/auth/, channel_zalo/"
    },
    {
        "id": "SPEC-39",
        "category": "Security & Ethics",
        "name": "Bảo vệ PII & Thiết kế có trách nhiệm",
        "spec_req": "Không soi mói đời tư, có chế độ ẩn dữ liệu nhạy cảm, dọn sạch PII khỏi code, không tự động kết án kỷ luật.",
        "current_state": "Đã loại bỏ 100% PII nhạy cảm (SĐT, Email, UID) khỏi mã nguồn runtime theo các commit gần nhất.",
        "status": "DONE",
        "status_label": "🟢 Đạt Chuẩn",
        "pct": 90,
        "gap": "Duy trì nguyên tắc bảo mật thông tin trong các bản cập nhật kế tiếp.",
        "source_ref": "Git commit 18113f3, 1703ad0"
    },

    # 7. Lộ Trình 6 Pha (Phases 0 - 5)
    {
        "id": "SPEC-40",
        "category": "Phases Roadmap",
        "name": "Phase 0 — Khung sống (Chassis & Plugins)",
        "spec_req": "Chassis ổn định, plugin độc lập không sập máy, Console mở được, log đọc được.",
        "current_state": "Đạt 100%. `./doctor.sh` kiểm thử 16/16 test PASS, chassis DSH hoạt động vững chắc.",
        "status": "DONE",
        "status_label": "🟢 Đạt Chuẩn",
        "pct": 100,
        "gap": "Đã hoàn tất trọn vẹn Phase 0.",
        "source_ref": "doctor.sh, heo_harness/core/"
    },
    {
        "id": "SPEC-41",
        "category": "Phases Roadmap",
        "name": "Phase 1 — Nhìn thấy được (Listen & Meaning Inbox)",
        "spec_req": "Zalo + 1 kênh nữa. Hội thoại được cấu trúc thành người/sự kiện/hàng đợi ý nghĩa. Overview + Inbox of Meaning dùng hàng ngày.",
        "current_state": "Zalo đã trực chiến, WhatsApp sẵn sàng. Đang thiếu bước cấu trúc tin thô thành Hàng Đợi Ý Nghĩa.",
        "status": "WIP",
        "status_label": "🟡 Đang Hoàn Thiện",
        "pct": 60,
        "gap": "Hoàn thiện Inbox of Meaning để người dùng không phải đọc tin nhắn thô.",
        "source_ref": "Spec Mục L (Phase 1)"
    },
    {
        "id": "SPEC-42",
        "category": "Phases Roadmap",
        "name": "Phase 2 — Hiểu được (Living Profiles & Early Warning)",
        "spec_req": "Hồ sơ động, gộp danh tính, search có não, điểm số có giải thích. Cảnh báo khách lạnh và việc bị quên.",
        "current_state": "Đã có Person 360 và Chat Search cơ bản. Chưa có gộp danh tính và hệ thống cảnh báo sớm (Early Warning).",
        "status": "WIP",
        "status_label": "🟡 Đang Hoàn Thiện",
        "pct": 35,
        "gap": "Phát triển bộ cảnh báo khách lạnh (Cold Lead Warning) và gộp liên hệ đa kênh.",
        "source_ref": "Spec Mục L (Phase 2)"
    },
    {
        "id": "SPEC-43",
        "category": "Phases Roadmap",
        "name": "Phase 3 — Quản được (Relationship Map & Opportunity Board)",
        "spec_req": "Bản đồ quan hệ đồ thị, đánh giá nhân viên/khách, chất lượng chăm sóc, Opportunity Kanban Board.",
        "current_state": "Có quản lý nhóm và danh sách thành viên. Chưa có đồ thị quan hệ và bảng cơ hội.",
        "status": "MISSING",
        "status_label": "🔴 Còn Thiếu",
        "pct": 20,
        "gap": "Triển khai Relationship Graph và Opportunity Kanban Board.",
        "source_ref": "Spec Mục L (Phase 3)"
    },
    {
        "id": "SPEC-44",
        "category": "Phases Roadmap",
        "name": "Phase 4 — Làm được (Quotation, ERP/CRM, Autonomy 4-5)",
        "spec_req": "Báo giá tự động, soạn thảo hợp đồng, nhắc việc, kết nối ERP/CRM sâu, mức tự trị 4-5.",
        "current_state": "Đã có công cụ sinh tài liệu Office, quản lý task và duyệt approval.",
        "status": "WIP",
        "status_label": "🟡 Đang Hoàn Thiện",
        "pct": 50,
        "gap": "Nâng mức tự trị và liên kết dữ liệu hồ sơ tự động điền form báo giá.",
        "source_ref": "Spec Mục L (Phase 4)"
    },
    {
        "id": "SPEC-45",
        "category": "Phases Roadmap",
        "name": "Phase 5 — Phủ được (Scale Multi-Group & Market Opportunity)",
        "spec_req": "Đủ các kênh lớn. Ráp nối cơ hội trên quy mô hàng trăm nhóm. Tuyển dụng & đào tạo học viên.",
        "current_state": "Hệ thống đang phục vụ ở quy mô nhóm nội bộ và khách hàng trực tiếp.",
        "status": "MISSING",
        "status_label": "🔴 Còn Thiếu",
        "pct": 15,
        "gap": "Mở rộng năng lực xử lý đồng thời nhiều tài khoản kênh và group cộng đồng lớn.",
        "source_ref": "Spec Mục L (Phase 5)"
    }
]

# Calculate statistics
total_items = len(AUDIT_DATA)
done_items = len([x for x in AUDIT_DATA if x["status"] == "DONE"])
wip_items = len([x for x in AUDIT_DATA if x["status"] == "WIP"])
missing_items = len([x for x in AUDIT_DATA if x["status"] == "MISSING"])
refactor_items = len([x for x in AUDIT_DATA if x["status"] == "REFACTOR"])

total_pct = sum(x["pct"] for x in AUDIT_DATA) / total_items

# By domain calculation
tech_categories = ["Security & Ethics", "MCP & Enterprise"]
tech_items = [x for x in AUDIT_DATA if x["category"] in tech_categories or x["id"] == "SPEC-40"]
tech_pct = sum(x["pct"] for x in tech_items) / len(tech_items)

product_categories = ["Operating Loop", "Console Screens", "Data & SSOT"]
product_items = [x for x in AUDIT_DATA if x["category"] in product_categories]
product_pct = sum(x["pct"] for x in product_items) / len(product_items)

print(f"Total: {total_items} items")
print(f"Done: {done_items} | WIP: {wip_items} | Missing: {missing_items} | Refactor: {refactor_items}")
print(f"Overall Completion: {total_pct:.1f}%")
print(f"Technical Chassis Score: {tech_pct:.1f}%")
print(f"Product Intelligence Score: {product_pct:.1f}%")

with open("/home/ryan/heo-harness/data/spec_audit_data.json", "w", encoding="utf-8") as f:
    json.dump({
        "stats": {
            "total_items": total_items,
            "done_items": done_items,
            "wip_items": wip_items,
            "missing_items": missing_items,
            "refactor_items": refactor_items,
            "total_pct": round(total_pct, 1),
            "tech_pct": round(tech_pct, 1),
            "product_pct": round(product_pct, 1)
        },
        "items": AUDIT_DATA
    }, f, ensure_ascii=False, indent=2)

print("Saved data to data/spec_audit_data.json")
