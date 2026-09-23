# BẢNG KIỂM KÊ DỮ LIỆU THẬT - GIẢ (DATA AUDIT REPORT)
## Nhóm Nghiệp Vụ KINH DOANH (Phần NHÌN + HIỂU) — Ticket 08a

Tác giả kiến trúc: **Anh Cơ La (Ryan)** — `genesis.corp.os@gmail.com`  
Thời gian thực hiện: 2026-09-23  
Phạm vi kiểm kê: 8 màn hình/hub cốt lõi thuộc Domain Kinh doanh trong `heo_harness/plugins/ui_dashboard/dashboard.html`:
`command`, `opportunities`, `workbench_action`, `directory`, `relationship_radar`, `work`, `workbench`, `chat_intelligence`.

---

## 1. BẢNG KIỂM KÊ CHI TIẾT THEO TỪNG MÀN HÌNH

| Màn hình | Khối/thành phần | THẬT hay GIẢ | Ghi chú (API nào, hay lý do chưa có API) |
|---|---|---|---|
| **1. Tổng quan điều hành (`command`)** | KPI "Cần xử lý ngay" | GIẢ (trước dọn) ➔ THẬT | Hardcode "9", đã chuyển sang tính từ `state.attention.length` và phân bổ band P1/P2/P3 từ `/api/attention/list`. |
| `command` | KPI "Tín hiệu cơ hội mới" | GIẢ (trước dọn) ➔ THẬT | Hardcode "41", đã chuyển sang đếm thực từ `state.df_opps.length` qua `/api/data_factory/opportunities`. |
| `command` | KPI "Quan hệ đang lạnh" | GIẢ (trước dọn) ➔ THẬT | Hardcode "23", đã chuyển sang đếm thực từ `state.df_contacts` có `went_silent_days > 7` qua `/api/data_factory/contacts`. |
| `command` | KPI "Nhóm đang nóng" | GIẢ (trước dọn) ➔ THẬT | Hardcode "7 / 42 nhóm", đã chuyển sang đếm thực từ `state.groups.length` (`/api/groups/list`) và `state.df_events.length` (`/api/data_factory/events`). |
| `command` | KPI "Hành động chờ duyệt" | THẬT | Đếm trực tiếp từ `state.approvals` chờ xử lý (`/api/approvals/list`). |
| `command` | KPI "Tin cậy dữ liệu" | GIẢ (trước dọn) ➔ THẬT | Hardcode "78%" và "12 danh tính", đã chuyển sang hiển thị DCI trung thực kèm nút kích hoạt modal `/api/system/dci`. |
| `command` | Hàng đợi cần xử lý (Attention Queue) | GIẢ (trước dọn) ➔ THẬT | Mảng 6 mục hardcode ("Xưởng gỗ Bình Dương", "Thành Phát"...), đã thay bằng mảng `state.attention` thật từ `/api/attention/list` (kèm empty state khi rỗng). |
| `command` | 5 đối tượng đáng chú ý (Today's Spotlight) | GIẢ (trước dọn) ➔ THẬT | Mảng 5 đối tượng hardcode, đã chuyển sang lấy từ danh bạ thực `state.df_contacts` / `state.people` kèm empty state khi rỗng. |
| `command` | Chủ đề đang nổi (Rising Signals) | GIẢ ➔ RỖNG TRUNG THỰC | Mảng 5 chủ đề hardcode ("Giá ván MDF...", "+142%"), đã thay bằng empty state: *Chưa có dữ liệu thật — chờ nối API /api/market/signals*. |
| `command` | Sức khỏe hệ thống (System Health) | THẬT | Tính toán thời gian thực từ `state.plugins`, trạng thái kết nối `state.zalo` và `state.whatsapp`. |
| `command` | Chất lượng dữ liệu (Data Quality) | GIẢ ➔ RỖNG TRUNG THỰC | Mảng 4 chỉ số tỷ lệ % hardcode, đã thay bằng empty state: *Chưa có dữ liệu thật — chờ nối API /api/system/dci*. |
| `command` | Nhiệt kế hoạt động (Hourly Activity) | GIẢ ➔ RỖNG TRUNG THỰC | Mảng 24 thanh biểu đồ giờ hardcode, đã thay bằng empty state: *Chưa có dữ liệu thật — chờ nối API /api/events/hourly_distribution*. |
| **2. Hộp Thư Ý Nghĩa (`opportunities`)** | KPI Bar tổng quan Pipeline | THẬT | Tính động từ danh sách cơ hội `state.df_opps` qua API `/api/data_factory/opportunities`. |
| `opportunities` | Dải chú ý khẩn (Attention Strip) | THẬT | Lọc các cơ hội P1 / điểm nhiệt >= 80 từ `state.df_opps`. |
| `opportunities` | Thanh lọc phễu 7 giai đoạn | THẬT | Đếm số lượng cơ hội theo stage từ `state.df_opps`. |
| `opportunities` | Danh sách thẻ hội thoại (`CANONICAL_MEANING_ITEMS`) | GIẢ ➔ ĐÃ XOÁ | Mảng 28 thẻ mẫu hardcode (460 dòng code), đã dọn sạch để chuyển sang 100% hiển thị luồng sự kiện thực từ `state.df_events` (`/api/data_factory/events`) qua `mapLiveEventToMeaningItem` và empty state "Inbox Zero". |
| `opportunities` | Luồng Live Events | THẬT | Lấy trực tiếp từ `state.df_events` qua API `/api/data_factory/events`. |
| **3. Hàng Đợi & Hành Động (`workbench_action`)** | Khu vực hành động bàn làm việc | TRUNG THỰC | Đã có sẵn empty state trung thực: *Chưa có dữ liệu thật — chờ nối API /api/workbench/actions, sẽ triển khai ở ticket sau*. |
| **4. Danh Bạ & Nhóm 360 (`directory`)** | Group 360 (Nhóm & Ban) | THẬT | Nối từ `state.groups` qua API `/api/groups/list` và SQLite `HeoDataStore`, có bộ lọc kênh và empty state chuẩn khi rỗng. |
| `directory` | Person 360 (Nhân Sự & Đối Tác) | THẬT | Nối từ `state.people` qua API `/api/people/list` và SQLite `HeoDataStore`, có bộ lọc và empty state chuẩn khi rỗng. |
| `directory` | Cầu nối Zalo Gateway | THẬT | Nối từ `state.zalo` (`/api/zalo/status`, `/api/zalo/messages`). |
| `directory` | Cầu nối WhatsApp Gateway | THẬT | Nối từ `state.whatsapp` (`/api/whatsapp/status`, `/api/whatsapp/messages`). |
| **5. Bảng Cơ Hội & Tiến Độ (`work`)** | Subtab Kanban Công Việc | THẬT | Nối từ `state.works` qua API `/api/work/list`, có empty state chuẩn *Bảng Kanban Sạch (Zero Mock Data)*. |
| `work` | Subtab Lịch Trình & Nhắc | THẬT | Nối từ `state.calendar` qua API `/api/work/list`, có empty state chuẩn *Lịch Trình Điều Hành Trống*. |
| `work` | Subtab Ma Trận Nhóm (Workload Matrix) | THẬT | Tính toán trực tiếp theo thời gian thực từ `state.groups`, `state.works`, `state.calendar`. |
| `work` | Subtab Bảng Cơ Hội: Danh sách mẫu (`mockOpps`) | GIẢ ➔ ĐÃ XOÁ | Mảng 11 cơ hội giả lập hardcode ("Xưởng gỗ Bình Dương...", "OPP-1851"...), đã xoá bỏ hoàn toàn để dùng `state.df_opps` (`/api/data_factory/opportunities`). |
| `work` | Subtab Bảng Cơ Hội: Pipeline ước lượng | GIẢ (trước dọn) ➔ THẬT | Hardcode "4,86 tỷ ₫", đã chuyển sang tính tổng thực từ `state.df_opps`. |
| `work` | Subtab Bảng Cơ Hội: Giá trị ước tính theo cột (`estValue`) | GIẢ (trước dọn) ➔ THẬT | Hardcode "≈ 1,9 tỷ ₫", "≈ 1,4 tỷ ₫"..., đã chuyển sang tính động theo từng stage từ `state.df_opps`. |
| **6. Radar Quan Hệ (`relationship_radar`)** | Subtab Đồ Thị Obsidian (Canvas) | THẬT | Nối API `/api/relationship/graph`, backend truy vấn động SQLite `contacts`, `opportunities`, `atomic_events`. |
| `relationship_radar` | Badge số lượng node trên thanh lọc | GIẢ (trước dọn) ➔ THẬT | Khởi tạo tĩnh "26 Nodes" và các số 1, 4, 4, 3, 2, 12, đã chuyển sang gán ID và cập nhật động từ `rawNodes` của API `/api/relationship/graph`. |
| `relationship_radar` | Subtab Radar Nhiệt Độ & Trọng Tài Bóng | THẬT | Phân nhóm tự động (Hot/Warm/Cold) từ `state.df_contacts` qua API `/api/data_factory/contacts`. |
| `relationship_radar` | Subtab Hồ Sơ Sống 360 | THẬT | Bảng danh bạ sống hiển thị từ `state.df_contacts` qua API `/api/data_factory/contacts`. |
| **7. Khai Thác Chat Big Data (`chat_intelligence`)** | 6 KPI Summary Cards | THẬT | Tính động từ `state.chat_intelligence.stats` qua API `/api/chat/intelligence`. |
| `chat_intelligence` | Thanh lọc đa chiều | THẬT | Đếm và lọc theo kênh Zalo/WhatsApp, Intent, Category từ dữ liệu backend thực. |
| `chat_intelligence` | Danh sách tin nhắn bóc tách | THẬT | Hiển thị từ `state.chat_intelligence.messages`, có empty state chuẩn khi rỗng hoặc không khớp bộ lọc. |
| **8. Sàn Ghép Nối Mậu Dịch (`workbench`)** | 4 Khối KPI Mậu Dịch | THẬT | Nối API thời gian thực `/api/commercial/matchmaker/summary`. |
| `workbench` | Danh sách Ráp Nối Cung - Cầu (Matches) | THẬT | Nối API `/api/commercial/matchmaker/matches`, có empty state chuẩn khi rỗng. |
| `workbench` | Kho Nguồn Cầu (Demands) | THẬT | Nối API `/api/commercial/matchmaker/demands`. |
| `workbench` | Kho Nguồn Cung (Supplies) | THẬT | Nối API `/api/commercial/matchmaker/supplies`. |

---

## 2. TỔNG HỢP KIỂM KÊ DỮ LIỆU
- **Tổng số khối thành phần kiểm kê trên 8 màn hình:** 33 khối.
- **Số khối THẬT (nối API hoặc tính từ state thật):** 20 khối (60.6%).
- **Số khối GIẢ (hardcode mẫu, số liệu bịa):** 13 khối (39.4%).
  - 7 khối đã chuyển đổi đấu nối sang dữ liệu thật sẵn có trong `state.*` (`attention`, `df_opps`, `df_contacts`, `groups`, `df_events`, `graph`).
  - 3 khối thay bằng trạng thái rỗng trung thực (empty state chuẩn) do backend chưa có API:
    - `/api/market/signals` (Chủ đề đang nổi)
    - `/api/system/dci` (Chất lượng dữ liệu)
    - `/api/events/hourly_distribution` (Nhiệt kế hoạt động theo giờ)
  - 2 khối dữ liệu mẫu hardcode quy mô lớn đã được dọn sạch hoàn toàn:
    - `CANONICAL_MEANING_ITEMS` (28 thẻ mẫu trong Hộp thư ý nghĩa)
    - `mockOpps` (11 cơ hội mẫu trong Bảng cơ hội)
  - 1 khối placeholder trung thực giữ nguyên (`workbench_action`).
