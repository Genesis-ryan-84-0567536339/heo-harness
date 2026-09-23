# TICKET 07 — Gen-Harness Console: SỬA LẠI KHUNG SƯỜN (Nav + Header) CHO ĐÚNG BẢN THIẾT KẾ GỐC

## Bối cảnh — ĐỌC KỸ, ĐÂY LÀ TICKET SỬA LỖI QUAN TRỌNG
Các ticket trước (01-06) đã dựng sidebar theo **5 nhóm Nhìn/Hiểu/Quản/Làm/Máy** lấy từ mô tả chữ trong
`Gen-Harness-Product-Spec-LOCKED.md`. Đây là **SAI** — khi đối chiếu trực tiếp với file thiết kế gốc
`docs/design-reference/claude-design-export/Gen-Harness Console.dc.html` (ảnh chụp so sánh đã xác nhận),
cấu trúc điều hướng THẬT trong bản thiết kế khác hẳn. Ticket này sửa lại khung sườn (sidebar + header)
cho khớp ĐÚNG bản thiết kế — đây là phần dùng chung cho toàn bộ app nên chỉ sửa 1 lần ở đây, áp dụng
cho tất cả các màn.

**Nguyên tắc bắt buộc cho ticket này**: PORT (chuyển thể) đúng cấu trúc dữ liệu và cách trình bày từ file
thiết kế gốc, KHÔNG diễn giải lại qua lời tả. Đọc kỹ đoạn code JS sau trong file
`docs/design-reference/claude-design-export/Gen-Harness Console.dc.html`:
- Dòng ~2849-2879: mảng `NAV` — đây là cấu trúc điều hướng THẬT (2 domain, có group/children lồng nhau).
- Dòng ~2880-2899: object `TITLES` — tiêu đề/phụ đề/nhãn cho từng màn.
- Dòng ~2926-2960: logic tính `crumbDomain`/`crumbGroup` và cách build cây nav (`navDomains`, `railLeaf`).
- Dòng 33-160: markup `<aside>` (sidebar) và `<header>` (thanh trên) — layout thật, style thật.

## Việc cần làm

### 1. Sidebar: đổi từ "5 nhóm phẳng" sang đúng cấu trúc 2 domain lồng nhau của mockup
- **Domain 1 "Kinh doanh"** (crumb: KINH DOANH), gồm các mục/nhóm con:
  - `overview` → Tổng quan điều hành (đã có, data-hub hiện tại: `command`)
  - Nhóm "Hàng đợi & Hành động": `inbox` Hộp thư ý nghĩa (→ hub `opportunities`), `workbench` Bàn làm việc
    (→ hub `workbench_action`)
  - `directory` Nhóm & Con người (→ hub `directory`)
  - Nhóm "Bản đồ quan hệ" (`graph`, → hub `relationship_radar`): con `profile` Hồ sơ sống, `notebook` Sổ
    tay nhận thức (2 mục này CHƯA có màn riêng — tạm để cùng trỏ vào hub `relationship_radar`, đánh dấu
    `// TODO: tách màn riêng khi có ticket sau`)
  - Nhóm "Cơ hội & Thị trường": `opportunity` Bảng cơ hội (→ hub `work`), `supply` Cung↔Cầu (→ hub
    `workbench`), `search` Kho hội thoại (→ hub `chat_intelligence`)
  - Nhóm "Con người & Chất lượng": `people` Đánh giá con người (→ hub `people_review`), `care` Chất lượng
    chăm sóc (→ hub `intelligence`)
- **Domain 2 "Kỹ thuật · Backend"** (crumb: KỸ THUẬT), gồm:
  - Nhóm "Tầng dữ liệu": `raw`/`rules`/`clean` Kho dữ liệu thô/Quy tắc sàng lọc/Kho sạch SSOT (3 mục này
    CHƯA có màn riêng — tạm trỏ chung vào hub `data_factory`, đánh dấu TODO), `identity` Hợp nhất danh
    tính (CHƯA có màn riêng — tạm trỏ vào hub `data_factory`, đánh dấu TODO)
  - Nhóm "Agent & Model": `agents` Danh tính Agent (→ hub `assistant`), `api` API & Model (CHƯA có màn
    riêng — tạm trỏ vào hub `assistant`, đánh dấu TODO), `mcp` MCP Hub (→ hub `mcp_connectors`)
  - `plugins` Plugin & Tiện ích (→ hub `modules`)
  - `system` Điều khiển hệ thống (→ hub `governance`)
- Badge số: CHỈ hiển thị trên mục lá (leaf item) có dữ liệu thật (đối chiếu `state.*` hiện có), KHÔNG
  hiển thị badge mặc định trên mọi mục như bản đang có hiện giờ (mockup không làm vậy).
- Nhóm cha (vd "Hàng đợi & Hành động") có thể mở/thu gọn (expand/collapse) — port đúng hành vi
  `navOpen` trong mockup nếu hợp lý, không bắt buộc pixel-perfect animation.

### 2. Header: dọn lại cho khớp mockup (dòng 111-141 của file mockup)
Header ĐÚNG chỉ gồm (từ trái sang phải):
- Breadcrumb: `phaseLabel` (KINH DOANH/KỸ THUẬT) › `crumbGroup` (nếu có) › tiêu đề màn + phụ đề.
- Bên phải: pill "X kênh · Y nhóm" (dùng data thật), pill "tự trị N" (mức tự trị hiện tại), pill "Z%"
  (độ tin cậy dữ liệu), nút bookmark, nút tìm kiếm.
- **XOÁ HẲN** các pill dư thừa hiện đang có: "Runtime trực chiến", "DCI: 98% (Tin Cậy)" (trùng ý với pill
  %  tin cậy dữ liệu nên gộp lại), "👑 OWNER", "🛠️ Builder OS", "Kiểm tra sức khỏe", "Terminal",
  "GEN-HARNESS ĐANG CHẠY" — đây là tàn dư từ giao diện Heo cũ, không có trong thiết kế mới.

### 3. Giữ nguyên tuyệt đối
- Toàn bộ 21 hàm `render*Hub()` hiện có — KHÔNG viết lại nội dung bên trong từng màn, chỉ đổi cách nav
  trỏ tới chúng.
- `switchHub()`/`renderActiveHub()` logic hiện có — chỉ sửa phần liên quan tới sidebar/header, không đổi
  cách các case hoạt động.
- Plugin ID nội bộ, đường dẫn module Python, định danh tác quyền (`heo_harness/plugins/auth/__init__.py`
  — TUYỆT ĐỐI không đụng), API contract hiện có.
- `python3 -m unittest discover -s tests` và `./doctor.sh` phải pass 100% sau khi sửa.

## KHÔNG làm trong đợt này
- Không xây màn hình mới cho các mục đang tạm trỏ dùng chung (`profile`, `notebook`, `raw`, `rules`,
  `clean`, `identity`, `api`) — chỉ trỏ tạm + đánh dấu TODO như hướng dẫn ở trên.
- Không tự push remote / mở PR / merge vào `main`.

## Quy trình bàn giao
- Commit nhỏ, rõ ràng (vd: 1 commit cho sidebar, 1 commit cho header).
- Khi xong (hoặc bế tắc), ghi `docs/design-reference/HANDOFF-07.md`: đã làm gì, kết quả test/doctor.sh,
  còn gì chưa xong (đặc biệt liệt kê rõ các mục đang tạm trỏ dùng chung cần tách sau). Dòng CUỐI CÙNG
  in ra màn hình phải bắt đầu CHÍNH XÁC bằng `[BÀN GIAO]` (không lồng trong câu văn khác).
- Bế tắc quá 3 lần cho cùng một vấn đề: dừng lại, ghi rõ vào HANDOFF-07.md, không đào sâu vô hạn.
