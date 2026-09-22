# BIÊN BẢN BÀN GIAO TICKET 01 — GEN-HARNESS CONSOLE (NỀN UI + TỔNG QUAN ĐIỀU HÀNH)

- **Nhánh thực hiện:** `feature/gen-harness-console-v1`
- **Tác quyền & Kiến trúc sư:** Anh Cơ La (Ryan) — `genesis.corp.os@gmail.com`
- **Thời điểm bàn giao:** 22/09/2026
- **Tài liệu tham chiếu SSOT:**
  - `docs/design-reference/Gen-Harness-Product-Spec-LOCKED.md` (v2.2 LOCKED)
  - `docs/design-reference/claude-design-export/Gen-Harness Console.dc.html` (Nguồn sự thật Design)
  - `docs/design-reference/TICKET-01-console-nen.md`

---

## 1. CÔNG VIỆC ĐÃ HOÀN THÀNH (ĐÚNG PHẠM VI TICKET 01)

### 1.1. Rebranding UI Text Toàn Diện (`dashboard.html`)
- Chuyển đổi toàn bộ tên hiển thị cho người dùng từ "Heo-Harness", "HEO OS", "Bé Heo" sang **"Gen-Harness"**, **"Genesis Harness OS"**.
- Cập nhật tiêu đề trang, meta header, thông báo hệ thống (toast, modal, disclaimer, terminal emulator, setup wizard).
- **Tuyệt đối tuân thủ bất biến kiến trúc:**
  - Giữ nguyên 100% Plugin ID nội bộ (ví dụ: `heo-ui-dashboard-executive`, `heo-provider-*`, `heo-channel-*`).
  - Giữ nguyên cấu trúc thư mục module Python (`heo_harness/...`).
  - Giữ nguyên định danh tác quyền: **Anh Cơ La (Ryan) / genesis.corp.os@gmail.com** tại chân sidebar và `heo_harness/plugins/auth/__init__.py`.

### 1.2. Tái Cấu Trúc Điều Hướng IA 5 Nhóm Ngữ Nghĩa (Spec F2)
Thay thế cấu trúc 4 domain cũ bằng hệ thống 5 nhóm điều hướng chuẩn theo đúng file thiết kế gốc `Gen-Harness Console.dc.html`:
1. **NHÌN (2 màn):**
   - `command`: Tổng quan điều hành
   - `opportunities`: Hộp thư ý nghĩa
2. **HIỂU (4 màn):**
   - `directory`: Nhóm & Con người
   - `relationship_radar`: Bản đồ quan hệ & 360
   - `workbench`: Cung ↔ Cầu
   - `chat_intelligence`: Kho hội thoại & Trí tuệ
3. **QUẢN (3 màn):**
   - `work`: Bảng cơ hội & Tiến độ
   - `people_review`: Đánh giá con người
   - `intelligence`: Chất lượng chăm sóc
4. **LÀM (3 màn):**
   - `workbench_action`: Bàn làm việc
   - `approvals`: Phê duyệt chiến lược
   - `media_vault`: Kho tư liệu & Media
5. **MÁY (9 màn):**
   - `data_factory`: Data Factory
   - `quota`: Agent Quota
   - `assistant`: AI Brain
   - `mcp_connectors`: MCP Hub
   - `modules`: Plugins DSH
   - `zalo`: Zalo Gateway
   - `whatsapp`: WhatsApp Gateway
   - `logs`: Logs
   - `auth_security`: Security PIN

### 1.3. Khắc Phục Lỗi Xung Đột Phân Hệ Điều Hướng (`workbench_action` vs `workbench`)
- **Vấn đề phát hiện:** Nút điều hướng "Bàn làm việc (Soạn & Duyệt)" thuộc nhóm **LÀM** mang `data-hub="workbench_action"` nhưng `onclick` trước đó gọi nhầm `switchHub('workbench')`, dẫn đến việc bôi sáng sai nút "Cung ↔ Cầu" (nhóm **HIỂU**) và hiển thị nhầm sàn mậu dịch.
- **Biện pháp xử lý triệt để:**
  1. Đổi `onclick="switchHub('workbench_action')"` tại nav button nhóm **LÀM**.
  2. Bổ sung nhánh xử lý `workbench_action` trong `switchHub()` và đưa vào danh sách ngoại lệ highlight (`['approvals', 'system_logs', 'ai_brain', 'security_pin', 'workbench_action']`) để bảo đảm active-highlight chính xác 100%.
  3. Thêm `case 'workbench_action'` trong `renderActiveHub()`, hiển thị không gian placeholder chuẩn Nocturne Design Tokens (`renderWorkbenchActionPlaceholder()`) ghi chú rõ ràng `(sẽ triển khai ở ticket sau)`, hoàn toàn tách bạch với sàn Cung ↔ Cầu `workbench`.

### 1.4. Hoàn Thiện Màn Hình Ưu Tiên Số 1: "Tổng Quan Điều Hành" (Command Overview)
Dựng trọn vẹn màn hình theo phong cách Nocturne Design Tokens (`dashboard.html`):
- **6 Thẻ KPI Điều Hành Đầu Trang:**
  - Cần xử lý ngay (6 mục P1/P2/P3).
  - Tín hiệu cơ hội mới (+3 phát hiện hôm nay).
  - Quan hệ đang lạnh (4 đối tác cần hâm nóng).
  - Nhóm đang nóng (2 nhóm có thảo luận dày đặc).
  - Hành động chờ duyệt (2 tác vụ nhạy cảm).
  - Tin cậy dữ liệu (94.2% qua kiểm định).
- **Hàng Đợi Cần Xử Lý (Trọng tâm điều hành bên trái):**
  - Hiển thị danh sách nhiệm vụ phân loại P1/P2/P3 kèm điểm số ưu tiên, phân loại cơ hội/cảnh báo/hành động, và nút xử lý trực tiếp.
- **Cột Phải Đáng Chú Ý:**
  - Khối 5 đối tượng đáng chú ý nhất hôm nay (phân tích mức nhiệt, vai trò và ghi chú).
  - Khối 5 tín hiệu thị trường & chủ đề đang nổi.
- **3 Khối Vận Hành Chân Trang:**
  - Sức khỏe hệ thống: Đấu nối thời gian thực với API `/api/plugins/list` và Circuit Breaker.
  - Chất lượng dữ liệu: Giám sát tỷ lệ làm sạch, phân loại và nhận diện thực thể.
  - Nhiệt kế hoạt động: Biểu đồ trực quan tần suất hội thoại theo 24 khung giờ trong ngày.
- **Dữ liệu Mock:** Được gắn chú thích `// TODO: Đấu nối API khi backend triển khai` rõ ràng, không tự ý sáng chế API ngoài phạm vi Ticket 01.

### 1.5. Cập Nhật Bộ Test Tương Thích Branding Mới
- Cập nhật các câu assert trong `tests/test_ui_dashboard.py` (`test_01_index_html_rendered`) kiểm tra tiêu đề `GEN-HARNESS` và `Genesis Harness OS`, cùng định danh tác quyền `Anh Cơ La (Ryan)`.
- Giữ nguyên toàn bộ coverage và các test case API khác.

---

## 2. NỘI DUNG NGOÀI PHẠM VI & GHI CHÚ KỸ THUẬT CHO KỸ SƯ TRƯỞNG

1. **Revert triệt để file ngoài phạm vi:**
   - Thay đổi thử nghiệm trước đó tại `heo_harness/plugins/provider_antigravity/__init__.py` đã được revert 100% bằng `git checkout` về trạng thái nguyên bản. Working tree hiện chỉ chứa đúng 2 file mã nguồn được phép sửa: `heo_harness/plugins/ui_dashboard/dashboard.html` và `tests/test_ui_dashboard.py`.
2. **Lưu ý về Antigravity Live Test:**
   - Trong quá trình chạy bộ test tích hợp toàn diện `tests/test_ssot_complete.py`, test case `test_02_antigravity_core_provider` gọi trực tiếp Antigravity CLI thực tế. Mặc dù test đã PASS, câu trả lời của mô hình ngôn ngữ có tính phi tất định (non-deterministic). Khuyến nghị Kỹ sư trưởng cân nhắc bổ sung regex linh hoạt hơn cho test case này trong đợt bảo trì backend tiếp theo.
3. **11 Màn Hình Còn Lại Trong Spec F2:**
   - Chưa dựng và không can thiệp, tuân thủ đúng yêu cầu "KHÔNG làm trong đợt này".

---

## 3. KẾT QUẢ KIỂM THỬ HỆ THỐNG

### 3.1. Chạy `tests/test_ui_dashboard.py`
```
Ran 8 tests in 18.694s
OK
```

### 3.2. Chạy `tests/test_ssot_complete.py`
```
Ran 6 tests in 120.196s
OK
```

### 3.3. Chạy `./doctor.sh`
```
🩺 HEO-HARNESS DOCTOR — CHẨN ĐOÁN HỆ THỐNG KHUNG SƯỜN & PLUGIN
------------------------------------------------------------------
  ✔ [OK] Môi trường thực thi: Python 3.14.3
  >>> Đang chạy kiểm thử tích hợp 16 tiêu chuẩn SSOT v1.0.0...
  ✔ [OK] Toàn bộ 16 bài test (Core Chassis, V6 UI, Policy Engine, AGY Core & Zalo): VƯỢT QUA 100%
  ✔ [OK] Định danh tác giả: Anh Cơ La (genesis.corp.os@gmail.com) - Hợp lệ 100%

🎉 Hệ thống Heo-Harness hoàn toàn khỏe mạnh và sẵn sàng hoạt động!
```

---

[BÀN GIAO] Đã hoàn thành 100% yêu cầu kỹ thuật của TICKET 01 trên nhánh feature/gen-harness-console-v1, bộ test và doctor.sh vượt qua toàn bộ.
