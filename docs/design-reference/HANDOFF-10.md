# BIÊN BẢN BÀN GIAO TICKET 10 — DATA FACTORY: RULES & CLEAN

**Dự án:** HEO-HARNESS / GEN-HARNESS EXECUTIVE OS  
**Tác giả:** Anh Cơ La (Ryan) — `genesis.corp.os@gmail.com`  
**Branch thực hiện:** `feature/gen-harness-rules-clean-10`  
**Trạng thái kiểm định:** `./doctor.sh` PASS 100% (16/16 test suites)  

---

## 1. PHẠM VI TRIỂN KHAI THEO SSOT MOCKUP
Thực hiện tái dựng chuẩn xác 2 khối màn hình thuộc Tầng dữ liệu trong Data Factory từ mockup SSOT Nocturne (`docs/design-reference/claude-design-export/Gen-Harness Console.dc.html`):
1. **Màn Quy tắc sàng lọc (`isRules` - Mockup dòng 511-616):**
   - Header: Tiêu đề "Quy tắc sàng lọc", mô tả cơ chế core agent phân loại dữ liệu thô, 2 nút hành động "Chạy thử trên 100 bản ghi" và "Thêm quy tắc" (gắn toast thông báo chưa nối API backend).
   - Lưới 2 cột chuẩn tỉ lệ Nocturne:
     - Cột trái: Khối danh sách quy tắc sàng lọc `refineryRules`.
     - Cột phải: Card "Trọng số chấm điểm" (`weights` - Evaluation Fabric) và Card "Chạy thử một bản ghi" (`testOutput` - Thô vào / Sạch ra).
2. **Màn Kho sạch & Trí nhớ (`isClean` - Mockup dòng 617-717):**
   - Header: Tiêu đề "Kho sạch & Trí nhớ", mô tả dữ liệu đã chuẩn hóa gắn ID nhóm/người và working memory.
   - Lưới 2 cột chuẩn tỉ lệ Nocturne:
     - Cột trái: Card "Bản ghi sạch theo ID" kèm bộ lọc và bảng dữ liệu 7 cột chuẩn SSOT (`ID nhóm`, `ID người`, `Sự kiện`, `Kết luận đã chốt`, `Điểm`, `Chu kỳ`, `Thô`).
     - Cột phải: Card "Trí nhớ tạm" (`memory` - viền tím accent `var(--acc)`, badge `0 / 4.000 token`, 2 nút "Lịch sử nén" & "Sếp ghim thêm") và Card "Tham số agent đang dùng" (`agentParams`).

---

## 2. KẾT QUẢ RÀ SOÁT API BACKEND & ĐỐI CHIẾU TRUNG THỰC

Đã thực hiện grep và rà soát toàn bộ cấu trúc mã nguồn backend (`heo_harness/core/` và `heo_harness/plugins/`) cũng như SQLite schema của `ConversationDataFactory`:

| Khối giao diện | Trạng thái API Backend thật | Xử lý hiển thị trên giao diện |
| :--- | :--- | :--- |
| **`refineryRules`** (Quy tắc sàng lọc) | **CHƯA CÓ** (Không có bảng DB / endpoint API) | Mảng rỗng `[]`, hiển thị **Empty-State trung thực**: *"Chưa có dữ liệu thật — chờ nối API quy tắc sàng lọc (Refinery Rules)"* |
| **`weights`** (Trọng số chấm điểm) | **CHƯA CÓ** (Chưa có endpoint Evaluation Fabric) | Mảng rỗng `[]`, hiển thị **Empty-State trung thực**: *"Chưa có dữ liệu thật — chờ nối API trọng số chấm điểm"* |
| **`testOutput`** (Chạy thử một bản ghi) | **CHƯA CÓ** (Chưa có engine sandbox test trích xuất) | Mảng rỗng `[]`, hiển thị **Empty-State trung thực**: *"Chưa có dữ liệu thật — chờ nối API chạy thử một bản ghi"* |
| **`cleanRows`** (Bản ghi sạch theo ID) | **CHƯA CÓ** (Chỉ có `atomic_events` thô, chưa có bảng clean store riêng) | Mảng rỗng `[]`, hiển thị **Empty-State trung thực**: *"Chưa có dữ liệu thật — chờ nối API kho sạch SSOT (Clean Store)"* |
| **`memory`** (Trí nhớ tạm / Working Memory) | **CHƯA CÓ** (Chưa có API working memory token buffer theo person/group) | Mảng rỗng `[]`, hiển thị **Empty-State trung thực**: *"Chưa có dữ liệu thật — chờ nối API trí nhớ tạm (Working Memory)"* |
| **`agentParams`** (Tham số agent đang dùng) | **CHƯA CÓ** (Chưa có endpoint runtime parameters cho agent) | Mảng rỗng `[]`, hiển thị **Empty-State trung thực**: *"Chưa có dữ liệu thật — chờ nối API tham số agent"* |

> **Cam kết:** Tuyệt đối không bịa dữ liệu giả hay bản ghi mẫu để lấp đầy giao diện. Toàn bộ các nút chức năng mới đều hiển thị toast: `"Tính năng này chưa nối API thật, sẽ triển khai ở ticket sau."`

---

## 3. LƯU Ý VỀ ĐIỀU HƯỚNG (NAVIGATION & ROUTING)
- **Tình trạng Sidebar Nav:** Đã dựng xong 2 hàm render chuyên trách `renderRefineryRulesView()` và `renderCleanStoreView()`, đồng thời định tuyến subtab trong `renderDataFactoryHub()` (`state.subtabs.data_factory === 'rules'` và `'clean'`).
- **Tuân thủ chỉ dẫn cảnh báo:** KHÔNG tự ý sửa đổi hay bổ sung gì vào `NAV`, `NAV_MAP`, `TITLES` ngoài cấu trúc gốc. Việc kích hoạt/hiển thị nav chính thức sẽ do Kỹ sư trưởng duyệt ảnh chụp và xác nhận.

---

## 4. BẰNG CHỨNG XÁC THỰC THỊ GIÁC (HEADLESS SCREENSHOTS)
- Màn Quy tắc sàng lọc: `/tmp/screen_data_factory_rules.png` (URL `#/data_factory/rules`)
- Màn Kho sạch & Trí nhớ: `/tmp/screen_data_factory_clean.png` (URL `#/data_factory/clean`)

---

## 5. DANH SÁCH COMMITS
1. Commit 1 (`3c12d8a`): `feat(ui): rebuild data factory rules view (isRules) with empty state (Ticket 10)`
2. Commit 2 (`207e6f7`): `feat(ui): rebuild data factory clean store view (isClean) with empty state (Ticket 10)`
