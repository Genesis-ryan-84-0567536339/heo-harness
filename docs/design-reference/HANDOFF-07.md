# BÁO CÁO HOÀN THÀNH TICKET-07: SỬA LẠI KHUNG SƯỜN (NAV + HEADER) THEO MOCKUP GỐC

- **Ticket:** `TICKET-07 — Gen-Harness Console: SỬA LẠI KHUNG SƯỜN (Nav + Header) CHO ĐÚNG BẢN THIẾT KẾ GỐC`
- **Kiến trúc sư & Tác quyền:** Anh Cơ La (Ryan) — `genesis.corp.os@gmail.com`
- **Branch:** `feature/gen-harness-khung-suon-fix`
- **Mockup đối chiếu chuẩn SSOT:** `docs/design-reference/claude-design-export/Gen-Harness Console.dc.html` (dòng 33-160, 2849-2911, 2926-2983)

---

## 1. CÁC HẠNG MỤC ĐÃ HOÀN THÀNH

### A. Tái Cấu Trúc Sidebar Navigation (2 Domain Phân Cấp Chuẩn Mockup)
1. **Xóa bỏ mô hình 5 nhóm phẳng (Nhìn/Hiểu/Quản/Làm/Máy):** Thay thế bằng cây điều hướng 2 Domain phân tầng chính xác từ mảng `NAV` của mockup.
2. **Domain 1 — Kinh doanh (`business` · KINH DOANH · `#34d399`):**
   - `overview` → Tổng quan điều hành (`command`)
   - Nhóm `Hàng đợi & Hành động`:
     - `inbox` → Hộp thư ý nghĩa (`opportunities`)
     - `workbench` → Bàn làm việc (`workbench_action`)
   - `directory` → Nhóm & Con người (`directory`)
   - Nhóm `Bản đồ quan hệ` (`graph` → `relationship_radar`):
     - `profile` → Hồ sơ sống (tạm trỏ `relationship_radar`, subtab `profiles`, đánh dấu `// TODO: tách màn riêng khi có ticket sau`)
     - `notebook` → Sổ tay nhận thức (tạm trỏ `relationship_radar`, subtab `notes`, đánh dấu `// TODO: tách màn riêng khi có ticket sau`)
   - Nhóm `Cơ hội & Thị trường`:
     - `opportunity` → Bảng cơ hội (`work`)
     - `supply` → Cung ↔ Cầu (`workbench`)
     - `search` → Kho hội thoại (`chat_intelligence`)
   - Nhóm `Con người & Chất lượng`:
     - `people` → Đánh giá con người (`people_review`)
     - `care` → Chất lượng chăm sóc (`intelligence`)
3. **Domain 2 — Kỹ thuật · Backend (`tech` · KỸ THUẬT · `#b5abfc`):**
   - Nhóm `Tầng dữ liệu`:
     - `raw` → Kho dữ liệu thô (tạm trỏ `data_factory`, subtab `raw`, đánh dấu `// TODO: tách màn riêng khi có ticket sau`)
     - `rules` → Quy tắc sàng lọc (tạm trỏ `data_factory`, subtab `rules`, đánh dấu `// TODO: tách màn riêng khi có ticket sau`)
     - `clean` → Kho sạch SSOT (tạm trỏ `data_factory`, subtab `clean`, đánh dấu `// TODO: tách màn riêng khi có ticket sau`)
     - `identity` → Hợp nhất danh tính (tạm trỏ `data_factory`, subtab `identity`, đánh dấu `// TODO: tách màn riêng khi có ticket sau`)
   - Nhóm `Agent & Model`:
     - `agents` → Danh tính Agent (`assistant`, subtab `identity`)
     - `api` → API & Model (tạm trỏ `assistant`, subtab `quota`, đánh dấu `// TODO: tách màn riêng khi có ticket sau`)
     - `mcp` → MCP Hub (`mcp_connectors`)
   - `plugins` → Plugin & Tiện ích (`modules`)
   - `system` → Điều khiển hệ thống (`governance`)
4. **Cơ chế Badge tinh gọn:**
   - Badge số CHỈ hiển thị trên các mục lá (leaf items) có dữ liệu thật: `overview` (attention P1), `inbox` (opportunities count), `workbench` (6), `opportunity` (works count), `supply` (27), `raw` (18k), `identity` (12), `mcp` (7), `plugins` (11).
   - Xóa bỏ triệt để việc gán badge mặc định trên tất cả các mục.
5. **Hành vi mở/thu gọn nhóm cha (`navOpen`):**
   - Hỗ trợ đóng mở các nhóm cha (`state.navOpen`) kèm icon caret chuyển trạng thái `ph-caret-down` / `ph-caret-right`.
   - Vạch chỉ báo kích hoạt (`nav-active-bar`) ở cạnh trái cho mục lá và nhóm cha đang hoạt động; chấm tròn `nav-dot` đổi màu accent cho mục con.
   - Giữ nguyên cơ chế bảo mật RBAC: `applyRbacRestrictions` tiếp tục bắt đúng `data-hub="people_review"` và `data-hub="security_pin"`.

---

### B. Tái Thiết Kế Header Topbar (Nocturne Breadcrumb & Clean Pills)
1. **Breadcrumb phân tầng Nocturne:**
   - Trái sang phải: Nhãn phân tầng `phaseLabel` (`KINH DOANH` / `KỸ THUẬT`) › `crumbGroup` (nếu mục thuộc nhóm con lồng nhau) › `pageTitle` (Tiêu đề màn) + `pageSub` (Phụ đề giải thích ý nghĩa khi không có crumbGroup).
2. **Cụm Pill & Tiện Ích Bên Phải Tinh Gọn:**
   - Pill kết nối kênh & nhóm: `4 kênh · 42 nhóm` với chấm xung nhịp `gnPulse` thời gian thực.
   - Pill tự trị: `tự trị 4` (hiển thị mức tự trị vận hành trên thang 0–6).
   - Pill tin cậy dữ liệu: `78%` (kết nối trực tiếp modal kiểm định chất lượng dữ liệu DCI).
   - Nút Bookmark: góc nhìn đã lưu.
   - Nút Search: tìm theo ý định (chuyển nhanh sang kho hội thoại & tri thức).
3. **Xóa hẳn 100% các pill tàn dư Heo cũ:**
   - Đã gỡ bỏ: `Runtime trực chiến`, `DCI: 98% (Tin Cậy)`, `👑 OWNER`, `🛠️ Builder OS`, `Kiểm tra sức khỏe`, `Terminal`, `GEN-HARNESS ĐANG CHẠY` / `Tạm dừng Trợ Lý AI`.

---

## 2. DANH SÁCH 7 MỤC MÀN HÌNH ĐANG TẠM TRỎ DÙNG CHUNG (CẦN TÁCH SAU)
Các mục này đã được định tuyến tạm thời vào các hub sẵn có kèm chú thích `// TODO: tách màn riêng khi có ticket sau` trong code:

| # | Khóa Nav | Tên Màn Hình | Hub Hiện Tại | Subtab Tạm | Ghi Chú Kế Hoạch |
|---|---|---|---|---|---|
| 1 | `profile` | Hồ sơ sống (Living Profile) | `relationship_radar` | `profiles` | Tách giao diện hồ sơ 360 từng ID cá nhân/tổ chức ở ticket sau |
| 2 | `notebook` | Sổ tay nhận thức (Cognitive Notebook) | `relationship_radar` | `notes` | Tách sổ tay ghi nhận lũy tiến trí nhớ agent ở ticket sau |
| 3 | `raw` | Kho dữ liệu thô (Raw Lake) | `data_factory` | `raw` | Tách màn hình giám sát ingestion lake ở ticket sau |
| 4 | `rules` | Quy tắc sàng lọc (Refinery Rules) | `data_factory` | `rules` | Tách màn hình định nghĩa rules sàng lọc sự kiện ở ticket sau |
| 5 | `clean` | Kho sạch SSOT (Clean Store) | `data_factory` | `clean` | Tách màn hình lưu trữ SSOT & working memory ở ticket sau |
| 6 | `identity` | Hợp nhất danh tính (Identity Resolution)| `data_factory` | `identity` | Tách màn hình liên kết đối tượng đa kênh ở ticket sau |
| 7 | `api` | API & Model Settings | `assistant` | `quota` | Tách bảng điều khiển khóa API, model endpoint & quota ở ticket sau |

---

## 3. BẢO TOÀN KIẾN TRÚC & TÁC QUYỀN
- **21 hàm `render*Hub()`:** Giữ nguyên vẹn 100% logic hiển thị bên trong từng hub.
- **Tác quyền bất biến:** Anh Cơ La (`genesis.corp.os@gmail.com`) được bảo toàn tại `heo_harness/plugins/auth/__init__.py`.
- **Hệ thống Plugin & API backend:** Không thay đổi bất kỳ plugin ID hay API endpoint nào.

---

## 4. KẾT QUẢ KIỂM THỬ & CHẨN ĐOÁN HỆ THỐNG
- **`python3 -m unittest discover -s tests`:** 53/53 tests VƯỢT QUA 100% (OK).
- **`./doctor.sh`:** 16/16 checks VƯỢT QUA 100%, tác quyền hợp lệ, hệ thống hoàn toàn khỏe mạnh.

---

## 5. CÁC COMMIT THỰC HIỆN
1. `517ca3f`: `feat(ui): restructure sidebar navigation into 2 domains per dc.html mockup`
2. `61f2f95`: `feat(ui): redesign header with Nocturne breadcrumb and clean pills per mockup`
3. Commit tài liệu bàn giao `HANDOFF-07.md`.
