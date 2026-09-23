# BÁO CÁO BÀN GIAO TICKET 09a
## Dựng Lại Đúng Nhóm "Bản Đồ Quan Hệ" (Relationship Radar Hub) Theo Mockup

**Kính gửi:** Anh Cơ La (Ryan) — `genesis.corp.os@gmail.com`  
**Nhánh Git:** `feature/gen-harness-rebuild-mockup-09a`  
**Trạng thái:** HOÀN THÀNH 100% (Visual Verified qua Chrome Headless & Passed Test Suites)  
**Thời gian hoàn thành:** 2026-09-23  

---

## 1. TỔNG QUAN PHẠM VI & KẾT QUẢ THỰC HIỆN

Thực hiện đúng chỉ đạo của Sếp Ryan:
- Bỏ qua phần `data_factory` (raw/rules/clean/identity) đã được hoàn thành trước đó.
- Tập trung toàn lực dựng lại chuẩn xác theo Mockup chuẩn Nocturne (`Gen-Harness Console.dc.html`) cho toàn bộ nhóm **"Bản đồ quan hệ"** (`relationship_radar` hub) bao gồm:
  1. **Bản đồ quan hệ (`graph`):** Mockup dòng 717–929 (`isGraph`, `isGraphList`, `isGraphNodes`, `isGraphView`).
  2. **Hồ sơ sống 360 (`profile`):** Mockup dòng 1340–1490 (`isProfile`).
  3. **Sổ tay nhận thức (`notebook`):** Mockup dòng 929–1103 (`isNotebook`).
- **Nguyên tắc cốt lõi:**
  - Trích nguyên văn cấu trúc HTML/CSS, Typography, Color Tokens từ Mockup Nocturne Design System.
  - **100% dữ liệu thật:** Nối trực tiếp `state.df_contacts`, `state.df_events`, `state.df_opps`, `state.groups`. Tuyệt đối không sinh dữ liệu giả; các phần chưa có dữ liệu nguyên tử hiển thị trạng thái rỗng trung thực kèm chú thích `// TODO`.

---

## 2. CHI TIẾT CÁC MÀN HÌNH ĐÃ DỰNG LẠI

### 2.1. Bản Đồ Quan Hệ (`#graph` / `relationship_radar`)
- **Khung điều khiển & Bộ lọc đa chiều:**
  - 5 chế độ hiển thị: Danh sách (`list`), Người ↔ Người (`people`), Nhóm ↔ Nhóm (`groups`), Luồng chủ đề (`edges`), Canvas Obsidian (`canvas`).
  - 7 chip lọc trạng thái: Tất cả, Độ nóng $\ge$ 80°, 50-79°, Đang lạnh < 50°, Phía ta, Khách hàng, Kênh Zalo.
- **Màn Danh sách (`renderGraphListSection`):**
  - Bảng hồ sơ sống hiển thị đầy đủ: Đối tượng (tên, công ty, avatar), Loại/Chức vụ, Giai đoạn (Nóng/Đang chăm sóc/Đang nguội), Kênh liên lạc (Zalo/WhatsApp), Người phụ trách (Phía ta Sếp & Trợ lý vs Phía đối tác THEM), Độ nóng tương tác kèm thanh đo nhiệt (`heat-bar`), Tiềm năng cơ hội thật, Mức độ rủi ro, Lần chạm gần nhất.
  - Bấm vào bất kỳ dòng nào sẽ chuyển thẳng vào **Hồ sơ sống 360** của đối tượng tương ứng.
- **Màn Biểu đồ mạng lưới (`renderGraphNodesSection`):**
  - Bản đồ quan hệ SVG trung tâm (HQ Trụ sở) kết nối các node liên lạc với góc phân bổ hình học chính xác.
  - Card Thống kê mạng lưới quan hệ (Tổng hồ sơ, Đang nóng, Cầu nối, Trọng tài bóng phía ta).
  - 4 khối nhận định chuyên sâu (System Insights) tính toán trực tiếp từ tương tác thực tế.
- **Màn Luồng chủ đề (`renderGraphViewSection`):**
  - Hiển thị luồng trao đổi thực thể (Ai $\rightarrow$ Chủ đề $\rightarrow$ Đến ai) kèm trọng số tương tác.
  - Card Phân tích cầu nối (Betweenness Bridges) & Phân bổ tải bóng giao tiếp.
- **Tích hợp Canvas Obsidian (`canvas`):** Giữ nguyên động cơ Canvas đồ họa quan hệ cho người dùng thích thao tác kéo thả node.

### 2.2. Hồ Sơ Sống 360 (`#profile`)
- **Nút điều hướng quay lại:** Link "$\leftarrow$ Quay lại bản đồ quan hệ" chuyển mượt mà về radar.
- **Khối định danh đối tượng:**
  - Avatar kích thước chuẩn 52x52px, chức danh, công ty, badge ưu tiên, các kênh liên lạc (Zalo, WhatsApp) và liên kết hợp nhất danh tính.
  - Nút "Gán phụ trách" và "Mở bàn làm việc" (chuyển sang `#workbench`).
- **5 Thẻ Chỉ Số Đo Lường (Metric Cards):**
  1. *Độ nóng tương tác (Heat Score):* Điểm số / 100 kèm đánh giá hành động và link giải trình "Vì sao $\rightarrow$".
  2. *Trọng tài bóng giao tiếp (Ball Possession):* Phía Ta vs Phía Khách, trạng thái thông luồng.
  3. *Tiềm năng doanh thu:* Giá trị deal thực từ `state.df_opps` (ví dụ: 50 triệu đ - Báo giá Chị Mai Phương).
  4. *Rủi ro Churn:* Điểm rủi ro tương tác.
  5. *Độ tin cậy dữ liệu (DCI):* Đánh giá mức độ xác thực SSOT.
- **Hệ thống hiểu gì về đối tượng này:**
  - Tóm tắt tự cập nhật từ phân tích AI với nút "AGY AI Phân Tích Lại".
- **Dòng sự kiện (Event Timeline):**
  - Liệt kê các sự kiện nguyên tử có nghĩa từ `state.df_events` gắn với ID đối tượng, có modal xem chứng cứ tin nhắn gốc.
  - Hiển thị trạng thái rỗng trung thực khi đối tượng chưa phát sinh sự kiện.
- **Thang tự trị đối tượng (Autonomy Level 0–6):**
  - 7 ô chọn mức tự trị từ 0 đến 6 (từ thụ động đến chủ động hoàn toàn).
  - Nối API `/api/contacts/update_autonomy` cập nhật realtime vào bộ nhớ và DB.
- **Khối tài liệu trao đổi, Người nội bộ từng chạm & Ghi chú tay của Sếp:**
  - Hiển thị tài liệu hợp đồng, báo giá đính kèm.
  - Danh sách nhân sự từng tương tác (Sếp Ryan, Trợ lý AI Agent).
  - Khung ghi chú riêng của Sếp với tính năng tự lưu `localStorage`.

### 2.3. Sổ Tay Nhận Thức (`#notebook`)
- **Điều khiển & Hành động:**
  - Header chuẩn Mockup kèm nút "Nén lại toàn bộ" và "Xuất sổ tay".
- **Cột Trái — Danh mục Thực thể:**
  - Tab "Con người" (`state.df_contacts.length`) và "Nhóm" (`state.groups.length`).
  - Ô tìm kiếm nhanh theo ID hoặc tên realtime.
  - Thẻ đối tượng hiển thị thanh chiếm dụng token cửa sổ (`1.842 / 4.000 tokens`) và thời gian cập nhật.
- **Cột Phải — Nội Dung Nhận Thức Lũy Tiến:**
  - Thông tin nhận thức chi tiết:
    1. *Nhận thức hiện tại:* Đặc điểm, nhiệt độ quan hệ, cơ hội đang mở.
    2. *Cần chú ý khi trả lời (ràng buộc chính sách):* Mức tự trị, giới hạn ngân sách phê duyệt.
    3. *Đã học được từ tương tác:* Phong cách làm việc, tốc độ phản hồi.
    4. *Điều chưa biết:* Các khoảng trống thông tin cần bổ sung.
  - Thẻ Gợi nhớ ID dữ liệu (`CNT-001`, `OPP-029712-31bd`).
  - Ngân sách cửa sổ ngữ cảnh (Token breakdown: Hiện tại, Cần chú ý, Đã học).
  - Hành động can thiệp của Sếp: Ghim nhận thức, Yêu cầu AI đọc lại, Xóa bớt ngữ cảnh trôi.
  - Lịch sử mốc lũy tiến nhận thức & Danh sách mục đã nén ra khỏi cửa sổ.

---

## 3. NÂNG CẤP ĐIỀU HƯỚNG & HỖ TRỢ URL HASH ROUTING

Đã tích hợp cơ chế Hash Routing hai chiều vào `dashboard.html`:
- Hỗ trợ mở trực tiếp hoặc bookmark URL:
  - `http://127.0.0.1:5088/#graph` hoặc `#/relationship_radar` $\rightarrow$ Mở Bản đồ quan hệ.
  - `http://127.0.0.1:5088/#profile` $\rightarrow$ Mở Hồ sơ sống 360.
  - `http://127.0.0.1:5088/#notebook` $\rightarrow$ Mở Sổ tay nhận thức.
- Tự động đồng bộ `state.activeNavKey`, breadcrumb tiêu đề, thanh sidebar nav và `window.location.hash` khi người dùng bấm tab hoặc chuyển subtab.

---

## 4. XÁC THỰC THỊ GIÁC (VISUAL VERIFICATION)

Đã chụp ảnh màn hình bằng Google Chrome Headless ở độ phân giải 1600x1000 và kiểm tra visual trực tiếp:
1. `/tmp/screen_rel_graph.png` (155 KB): Bản đồ quan hệ danh sách hồ sơ sống, badge nhiệt độ, kênh Zalo/WhatsApp, bộ lọc đa chế độ.
2. `/tmp/screen_rel_profile.png` (171 KB): Hồ sơ sống 360 của Chị Mai Phương (CNT-001), 5 thẻ đo lường, thang tự trị 0-6, tóm tắt AI.
3. `/tmp/screen_rel_notebook.png` (243 KB): Sổ tay nhận thức 2 cột, cửa sổ token ngữ cảnh, gợi nhớ ID dữ liệu, các mốc lũy tiến.

---

## 5. KẾT QUẢ KIỂM THỬ TỰ ĐỘNG

Chạy toàn bộ các test suite của hệ thống:
- `tests/test_harness_core.py`, `tests/test_rbac.py`, `tests/test_people_review.py`, `tests/test_data_factory_milestones.py`, `tests/test_event_store.py`:
  - **39 tests passed** (OK trong 1.52s).
- `tests/test_ui_dashboard.py`:
  - **8 tests passed** (OK trong 18.74s).

---

## 6. DANH SÁCH FILE THAY ĐỔI
- `heo_harness/plugins/ui_dashboard/dashboard.html`: Cập nhật CSS table, cấu trúc `renderRelationshipRadarHub`, `renderRelationshipGraphHub`, `renderLivingProfile360Section`, `renderCognitiveNotebookSection`, bổ sung Hash router và sync URL.
- `docs/design-reference/HANDOFF-09a.md`: Tài liệu nghiệm thu và bàn giao chi tiết.
