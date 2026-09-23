# BẢNG KIỂM KÊ DỮ LIỆU THẬT / GIẢ — TICKET 08b
## Nhóm "Con người & Chất lượng" + Toàn bộ KỸ THUẬT · BACKEND

- **Thời điểm kiểm kê:** 23/09/2026
- **Tác quyền & Kiến trúc sư:** Anh Cơ La (Ryan) — `genesis.corp.os@gmail.com`
- **Tài liệu tham chiếu SSOT:** `docs/design-reference/TICKET-08b-kiem-ke-du-lieu-that-quan-lam-may.md`, `Gen-Harness-Product-Spec-LOCKED.md`
- **Phạm vi kiểm kê:** 9 hubs: `people_review`, `intelligence`, `data_factory`, `assistant`, `mcp_connectors`, `modules`, `governance`, `zalo`, `whatsapp`.

---

## 1. BẢNG KIỂM KÊ TỔNG HỢP

| Màn hình / Phân hệ | Khối / thành phần | THẬT hay GIẢ | Ghi chú (API nào, hay lý do chưa có API) |
| :--- | :--- | :---: | :--- |
| **people_review** | Tabs đếm số lượng (Nhân viên, Khách hàng, Ứng viên, Học viên) | **GIẢ** (fallback) | Fallback cứng '28', '96', '11', '13'. Dữ liệu thật từ `/api/people_review/summary`. Đã dọn bỏ fallback giả, thay bằng `counts[key]?.count ?? '—'`. |
| **people_review** | Radar Lời Hứa Trễ Hạn (Broken Promises) | **THẬT** | Nối trực tiếp `/api/care_quality/broken_promises?status=UNRESOLVED`. Khi không có vi phạm, panel ẩn tự động. |
| **people_review** | Bảng chi tiết People Board Table (`mockDataset`) | **GIẢ** (fallback) | `mockDataset` chứa 11 hồ sơ nhân sự giả (Nguyễn Thu Hà, Trần Minh Khoa, Vũ Hải Đăng, Đỗ Thanh Mai, Phạm Anh Tú...). Đã xoá sạch mockDataset, thay bằng trạng thái rỗng trung thực khi chưa có dữ liệu từ `/api/people_review/list`. |
| **people_review** | Thao tác giải quyết / nhắc nhở lời hứa & coaching | **THẬT** | Nối API thật: `/api/care_quality/resolve_promise`, `/api/care_quality/remind_promise`, `/api/people_review/coaching`. |
| **intelligence (care)** | 5 thẻ KPI Chất Lượng Chăm Sóc (careKpis) | **GIẢ** | Hardcode tĩnh: 24 phút, 68%, 11 lần, 6 khách, 81%. Thay bằng dữ liệu từ `/api/care_quality/summary` hoặc hiển thị `—` kèm thông báo chờ tích lũy dữ liệu. |
| **intelligence (care)** | Heatmap Tốc độ phản hồi theo khung giờ (`careGrid`) | **GIẢ** | Hardcode ma trận 5 nhân sự x 8 khung giờ. Xoá bỏ dữ liệu giả, thay bằng trạng thái rỗng trung thực chờ dữ liệu từ `/api/care_quality/records`. |
| **intelligence (care)** | Khối Lỗi chăm sóc lặp lại (`carePatterns`) | **GIẢ** | Hardcode 6 mẫu lỗi: 19 lần, 11 lần, 9 lần... Xoá bỏ dữ liệu giả, thay bằng trạng thái rỗng trung thực. |
| **intelligence (care)** | Khối Kịch bản thắng và mất khách (`careScripts`) | **GIẢ** | Hardcode 4 kịch bản (32 ca thắng, 18 ca thắng, 15 ca mất, 22 ca mất). Xoá bỏ dữ liệu giả, thay bằng trạng thái rỗng trung thực. |
| **data_factory** | 4 thẻ KPI Data Factory (Bản ghi thô, Tin cậy kho sạch) | **GIẢ** (một phần) | `18.412 bản ghi thô` và `94.2% kho sạch` là số bịa viết cứng. Đã nối vào `stats.total_raw_messages` hoặc hiển thị `—`. `Sự kiện nguyên tử` và `Cơ hội phát hiện` là THẬT (nối `stats.total_events`, `stats.total_opportunities`). |
| **data_factory** | Bảng dòng sự kiện nguyên tử (`rawRows`) | **GIẢ** | Hardcode 12 dòng tĩnh (`GRP-ZL-0114`, `MDF E1 17mm`...). Đã dọn bỏ, nối thẳng vào mảng `state.df_events` thật từ `/api/data_factory/events` và trạng thái rỗng nếu chưa có sự kiện. |
| **data_factory** | Khối Phân bổ bản ghi thô theo nhóm (`rawByGroup`) | **GIẢ** | Hardcode 7 nhóm tĩnh (6.412, 4.108...). Đã thay bằng dữ liệu nhóm thật từ `state.groups` hoặc trạng thái rỗng trung thực. |
| **data_factory** | Khối Lịch sử sàng lọc (`refineryRuns`) | **GIẢ** | Hardcode 5 lượt chạy tĩnh (486 bản ghi, 512 bản ghi...). Đã thay bằng trạng thái rỗng chờ lệnh kích hoạt. |
| **data_factory** | Nút bấm Chạy sàng lọc & Xuất tập thô | **THẬT** | Nối API `/api/data_factory/process_message` và export JSON/CSV thật. |
| **assistant** | Live Console Chat (`renderAssistantChatView`) | **THẬT** | Nối API `/api/chat` realtime với lõi Google Antigravity CLI và chọn ngữ cảnh Nhóm/Nhân sự thật. |
| **assistant** | Cấu hình Sếp & 7 Persona (`renderHeoSettingsView`) | **THẬT** | Nối API `/api/config`, lưu trữ vào `data_store` (SQLite) và phân quyền bảo vệ PIN. |
| **assistant** | Quota AI & Đổi Model (`renderQuotaView`) | **THẬT** | Nối `state.google`, `state.quota`, API `/api/check_quota`, `/api/switch_model`, `/api/set_effort`. |
| **assistant** | Runners Hub (`renderRunnersHubView`) | **THẬT** | Trực tiếp kích hoạt prompt tạo Word, Excel, Lo-Fi, Vector qua `/api/chat`. |
| **assistant** | Agent Identity Studio (`renderAgentIdentityStudioView`) | **THẬT** | Nối API `/api/agent_identities`, lưu trữ 6 danh tính tác tử trong SQLite. |
| **mcp_connectors** | 4 thẻ KPI MCP Hub | **GIẢ** (một phần) | Hardcode: `/ 7 đã cài`, `2 đang tắt`, `23/61 tool`, `1.482 lượt gọi`, `9 lượt chặn`, `620ms`. Đã dọn số bịa, nối số máy chủ thật từ `mcpData.servers` và hiển thị `—` cho telemetry chưa nối API. |
| **mcp_connectors** | Danh sách máy chủ kết nối (`defaultServers`) | **GIẢ** | Hardcode 5 máy chủ ảo (ERP Genesis, CRM Genesis, Lịch & Họp, Kho tài liệu, HRM). Đã dọn bỏ, nối thẳng vào danh sách máy chủ THẬT từ `mcpData.servers` (`gen-hub`, `google-drive`) từ `/api/mcp/connectors`. |
| **mcp_connectors** | Nhật ký gọi công cụ MCP (`mcpLogList`) | **GIẢ** | Hardcode 9 dòng nhật ký giả với timestamp tĩnh. Đã thay bằng trạng thái rỗng trung thực: chờ lệnh gọi công cụ từ Agent. |
| **mcp_connectors** | Kho ứng dụng 1-Click MCP (`renderMcpAppCatalogView`) | **THẬT** | Nối 14 connectors chuẩn hóa từ `mcp_manager` (`heo_harness/core/mcp_manager.py`). |
| **mcp_connectors** | Cấu hình MCP tùy chỉnh (`renderMcpCustomBuilderView`) | **THẬT** | Nối API `/api/mcp/custom`, `/api/mcp/connect`, `/api/mcp/disconnect`. |
| **modules** | 5 thẻ KPI Plugin & Tiện ích | **THẬT** | Tính toán động 100% từ `state.plugins` thật (`/api/plugins/list`). |
| **modules** | Bảng danh sách Plugin (`renderInstalledPluginsView`) | **THẬT** (danh sách) / **GIẢ** (cột RAM) | Danh sách plugin, trạng thái Bật/Tắt, Circuit Breaker là THẬT từ `/api/plugins/list`. Cột bộ nhớ `memMap` hardcode ('48 MB', '72 MB'...) đã được dọn sang `—` (chờ đo lường). |
| **modules** | Thứ tự nạp DSH (`loadOrderList`) | **GIẢ** (thời gian ms) | Các con số mili-giây ('82ms', '41ms', '214ms'...) là giả. Đã bỏ số ms giả, chỉ giữ thứ tự tầng kiến trúc chuẩn DSH kèm trạng thái 'Sẵn sàng'. |
| **modules** | Nhật ký vòng đời (`lifecycleLogs`) | **GIẢ** | Hardcode 7 dòng log tĩnh kèm giờ bịa đặt. Đã thay bằng trạng thái rỗng trung thực chờ log sự kiện từ EventBus. |
| **modules** | Executive Skills & Chợ Tiện Ích Marketplace | **THẬT** | Nối API `/api/skills/list` và `/api/plugins/catalog`. |
| **governance** | Mã PIN Admin SHA-256 (`renderAdminPinView`) | **THẬT** | Nối API `/api/set_pin`, `/api/pin/clear`, `/api/pin/verify` và tác quyền Anh Cơ La bất biến. |
| **governance** | Phê Duyệt An Ninh SSOT (`renderApprovalsView`) | **THẬT** | Nối API `/api/approvals/list` và `/api/approvals/action`. |
| **governance** | Sổ Cái Kiểm Toán (`renderAuditsView`) | **THẬT** | Nối API `/api/audit/list` từ bảng SQLite `audits`. Bổ sung trạng thái rỗng khi chưa có bản ghi. |
| **governance** | Live Stream Logs (`renderRealTimeLogsView`) | **THẬT** | Polling `/api/logs` thời gian thực 1.5s/chu kỳ, lọc theo kênh và loại chat. |
| **governance** | Giám Sát Hạ Tầng (`renderInfraView`) | **THẬT** | Nối `state.metrics` từ `/api/system/status`. Dọn bỏ fallback số cứng. |
| **zalo** | Trạng thái kết nối, QR Code cá nhân & Dispatch | **THẬT** | Nối trực tiếp WebSocket/Long-polling backend Zalo `/api/zalo/*`. |
| **zalo** | 4-metric strip (Tin 24h, Được tag, Độ trễ, Thời gian trực) | **GIẢ** (fallback) | Khi chưa có thống kê thật, fallback hiển thị số giả: '1.244' tin, '31' tag, '0,42s', '99,9%'. Đã xoá sạch số bịa, nối `zmsgs.length`, số tag thật hoặc hiển thị `—`. |
| **whatsapp** | Trạng thái kết nối, Pairing Code & Multi-Device QR | **THẬT** | Nối trực tiếp Baileys Bridge `/api/whatsapp/*`. |
| **whatsapp** | 4-metric strip (Tin 24h, Được tag, Độ trễ, Thời gian trực) | **GIẢ** (fallback) | Khi chưa có thống kê thật, fallback hiển thị số giả: '96' tin, '9' tag, '0,51s', '99,5%'. Đã xoá sạch số bịa, nối `msgs.length`, số tag thật hoặc hiển thị `—`. |

---

## 2. KẾ HOẠCH HÀNH ĐỘNG DỌN DẸP & THAY THẾ (ACTION PLAN)

1. **`zalo` & `whatsapp`:**
   - Xoá triệt để các fallback số liệu bịa ('1.244', '31', '0,42s', '99,9%' của Zalo và '96', '9', '0,51s', '99,5%' của WhatsApp). Thay bằng số liệu tính từ mảng tin nhắn thực tế hoặc `—`.
2. **`people_review`:**
   - Xoá fallback cứng '28', '96', '11', '13' trên tabs.
   - Xoá toàn bộ `mockDataset` (11 hồ sơ nhân sự giả).
   - Render bảng dữ liệu thật nếu có từ API, nếu không có render trạng thái rỗng trung thực (`empty-state`) có icon trung tính, thông báo rõ ràng "Chưa có dữ liệu đánh giá [phân hệ] thật — chờ đồng bộ từ API /api/people_review/list".
3. **`intelligence (care)`:**
   - Dọn sạch 5 thẻ KPI tĩnh `careKpis`.
   - Dọn sạch heatmap tĩnh `careGrid`.
   - Dọn sạch `carePatterns` và `careScripts` tĩnh.
   - Thay thế bằng khối trạng thái rỗng trung thực: "Chưa có dữ liệu chất lượng chăm sóc thật — chờ tích lũy từ hội thoại Zalo/WhatsApp và API /api/care_quality/records".
4. **`data_factory`:**
   - Xoá số bịa 18.412 và 94.2% trong KPI cards. Nối số thật từ `stats` hoặc `—`.
   - Xoá 12 dòng `rawRows` tĩnh. Nối thẳng vào `state.df_events` thật từ API `/api/data_factory/events`. Nếu rỗng, hiển thị empty state.
   - Xoá `rawByGroup` tĩnh. Nối `state.groups` thật hoặc empty state.
   - Xoá `refineryRuns` tĩnh. Thay bằng empty state.
5. **`mcp_connectors`:**
   - Xoá các số bịa trong KPI cards (7 đã cài, 23/61 tool, 1.482 lượt, 620ms).
   - Xoá `defaultServers` (5 máy chủ ảo). Nối `mcpData.servers` thật (`gen-hub`, `google-drive`) từ `/api/mcp/connectors`.
   - Xoá 9 dòng `mcpLogList` tĩnh. Thay bằng empty state trung thực.
6. **`modules`:**
   - Xoá `memMap` hardcode trong bảng plugins, thay bằng `—`.
   - Bỏ các số mili-giây giả trong `loadOrderList`.
   - Xoá `lifecycleLogs` tĩnh, thay bằng empty state trung thực.
7. **`governance` & `assistant`:**
   - Dọn fallback số cứng trong `renderInfraView` (RAM, Disk, CPU).
   - Thêm trạng thái rỗng trung thực cho `renderAuditsView` và `renderQuotaView`.

---

## 3. KẾT QUẢ THỰC HIỆN & DANH SÁCH COMMITS

| STT | Màn hình / Phân hệ | Nội dung đã dọn dẹp | Trạng thái | Commit Hash |
| :---: | :--- | :--- | :---: | :--- |
| 1 | **zalo & whatsapp** | Xoá toàn bộ fallback số liệu bịa ('1.244', '31', '0,42s', '99,9%' & '96', '9', '0,51s', '99,5%'). Tính động từ dữ liệu thật hoặc `—`. | **HOÀN THÀNH** | `d981595` |
| 2 | **people_review** | Xoá số đếm cứng tabs ('28', '96', '11', '13'). Xoá 11 hồ sơ nhân sự giả `mockDataset`. Thêm empty-state trung thực cho bảng và care quality tab. | **HOÀN THÀNH** | `c24f1b1` |
| 3 | **intelligence (care)** | Xoá 5 thẻ KPI tĩnh `careKpis`. Xoá heatmap tĩnh `careGrid`. Xoá `carePatterns` và `careScripts` tĩnh. Thêm empty states có hướng dẫn kết nối API. | **HOÀN THÀNH** | `03d9adb` |
| 4 | **data_factory** | Xoá số bịa 18.412 và 94.2% trong KPIs. Xoá 12 dòng `rawRows` tĩnh, nối thẳng `state.df_events` thật (43 sự kiện nguyên tử trong SQLite). Xoá `rawByGroup` tĩnh, nối nhóm thật. Xoá 5 lượt `refineryRuns` tĩnh, thay bằng empty state. | **HOÀN THÀNH** | `ac6f571` |
| 5 | **mcp_connectors** | Xoá các số KPI bịa (7 đã cài, 23/61 tool, 1.482 lượt, 620ms). Xoá 5 server ảo `defaultServers`, nối máy chủ THẬT (`gen-hub`, `google-drive`) từ `/api/mcp/connectors`. Xoá 9 dòng nhật ký giả `mcpLogList`, thay bằng empty state. | **HOÀN THÀNH** | `246d964` |
| 6 | **modules** | Xoá `memMap` hardcode ('48 MB', '72 MB'...) trong bảng plugin, thay bằng `—`. Bỏ số mili-giây giả trong `loadOrderList`. Xoá 7 dòng `lifecycleLogs` tĩnh, thay bằng empty state. | **HOÀN THÀNH** | `edec610` |
| 7 | **governance & assistant** | Xoá fallback số cứng RAM, Disk, CPU trong `renderInfraView`. Thêm empty state cho `renderAuditsView` và `renderQuotaView`. | **HOÀN THÀNH** | `a433257` |

---

## 4. TỔNG KẾT TUÂN THỦ NGUYÊN TẮC
- 100% dữ liệu giả được lập danh mục và dọn sạch khỏi giao diện.
- Không phát minh API ảo — nếu chưa có API telemetry, hiển thị dấu gạch ngang `—` kèm ghi chú trung thực.
- Mọi dữ liệu sẵn có trong backend (43 sự kiện Data Factory, 2 máy chủ MCP thật, danh sách plugin, cấu hình Sếp...) được ưu tiên kết nối hiển thị.
- Giữ nguyên định danh tác quyền Anh Cơ La (`genesis.corp.os@gmail.com`) và 11 plugin chuẩn SSOT.
