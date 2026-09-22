# BÁO CÁO BÀN GIAO TICKET 05a — GEN-HARNESS CONSOLE: ZALO GATEWAY + WHATSAPP GATEWAY

**Thời gian:** 2026-09-23 06:15:00 +07:00  
**Tác giả sáng lập & Kỹ sư trưởng:** Anh Cơ La (Ryan) — `genesis.corp.os@gmail.com`  
**Nhánh:** `feature/gen-harness-screen-zalo-whatsapp-v3`  
**File sửa đổi chính:** `heo_harness/plugins/ui_dashboard/dashboard.html`

---

## 1. TỔNG QUAN CÔNG VIỆC ĐÃ HOÀN THÀNH

Thực hiện chuẩn hóa hoàn thiện 2 màn hình thuộc nhóm **"MÁY"** theo đúng SSOT `docs/design-reference/Gen-Harness-Product-Spec-LOCKED.md` (Mục E2, E12, F2 mục 12) và thiết kế mẫu `docs/design-reference/claude-design-export/Gen-Harness Console.dc.html`, áp dụng triệt để bộ design tokens Nocturne (`#232532`, `rgba(233,233,237,0.16)`, `#e9e9ed`, `#9184d9`, `#4ade80`, monospace font cho số liệu / ID):

### 1.1. Màn hình 1: `zalo` — Kênh Zalo Gateway (`renderZaloHub()`, `renderZaloGatewayView()`)
- **Header & Điều khiển kênh:** Tiêu đề chuẩn Nocturne typography, nút chuyển trạng thái BẬT/TẮT kênh với chỉ báo đèn tròn (xanh/đỏ), nút đồng bộ nhóm Zalo (`syncZaloGroups()`).
- **Subnav Tabs phẳng:** `💬 Cổng Kết Nối & QR Gateway` và `🔴 Nhật Ký Bridge Zalo Live` theo tab underline Nocturne.
- **Thẻ trạng thái kết nối & QR Code:**
  - Header thẻ hiển thị dot trạng thái và badge pill chuẩn F2: `CONNECTED (ONLINE)` hoặc `CHỜ KẾT NỐI (CHỜ QUÉT QR)`.
  - Khung mã QR quét trực tiếp bằng camera Zalo điện thoại trên nền trắng sắc nét (`#zalo-qr-image`), bảo toàn đầy đủ các phần tử JavaScript tương tác (`#zalo-qr-status-msg`, `#zalo-qr-timer`, `#zalo-qr-scanned-alert`).
  - Hộp thông tin tài khoản kết nối (UID, Số điện thoại, chế độ lọc tin `@tag Only`, tự động nhận diện Sếp qua PIN).
  - Các nút hành động nghiệp vụ: Làm mới QR (`refreshZaloQR()`), Khởi động lại Bridge (`restartZaloBridge()`), Đăng xuất có xác thực PIN (`openZaloLogoutModal()`).
- **Dải 4 chỉ số thống kê (4-Metric Stats Strip):**
  - Đồng bộ chuẩn thiết kế `Gen-Harness Console.dc.html`: `Tin 24h`, `Được tag`, `Độ trễ`, `Thời gian trực` với typography monospace và bảng màu Nocturne.
- **Bộ gửi tin nhắn trực tiếp qua Gateway (Outbound Test Dispatcher):**
  - Dropdown chọn nhóm đích (`#zalo-test-group`), ô nhập nội dung chỉ đạo (`#zalo-test-msg`) với placeholder trung tính, nút gửi tin kiểm thử (`sendZaloTestMessage()`).
- **Thẻ cấu hình kênh Zalo độc lập 100% (Decoupled Config):**
  - Cấu hình tên bot (`#zalo-cfg-bot-name`), danh mục 7 phong cách thái độ (`#zalo-cfg-persona`), chỉ thị hành xử riêng (`#zalo-cfg-notes`), nút lưu cấu hình (`saveZaloChannelConfig()`).
- **Nhật ký tin nhắn phiên làm việc thực tế (Session Log):**
  - Thẻ tin nhắn Nocturne với nhãn định danh người gửi/nhận, chip phân loại 1-1/Nhóm, timestamp định dạng monospace và hiển thị phản hồi của bot.

### 1.2. Màn hình 2: `whatsapp` — Kênh WhatsApp Gateway (`renderWhatsAppHub()`, `renderWhatsAppGatewayView()`)
- **Header & Điều khiển kênh:** Tiêu đề chuẩn Nocturne typography, nút bật/tắt kênh WhatsApp với dot trạng thái, nút làm mới QR WhatsApp (`refreshWhatsAppQR()`).
- **Subnav Tabs phẳng:** `📱 Cổng Kết Nối & QR Gateway` và `🔴 Nhật Ký Bridge WhatsApp Live`.
- **Thẻ trạng thái kết nối & QR Code (Multi-Device):**
  - Header thẻ hiển thị dot trạng thái và badge pill chuẩn F2: `CONNECTED (ONLINE)` hoặc `CHỜ KẾT NỐI (CHỜ QUÉT QR)`.
  - Khung mã QR WhatsApp Multi-Device trên nền trắng sắc nét (`#whatsapp-qr-image`) kèm chỉ dẫn quét thiết bị liên kết trên ứng dụng di động.
  - Hộp thông tin tài khoản (Tên bot, Số điện thoại/phiên, Thiết bị ghép nối, Chế độ lọc tin nhóm).
  - Nút hành động: Làm mới QR (`refreshWhatsAppQR()`), Khởi động lại Bridge (`restartWhatsAppBridge()`), Đăng xuất an toàn (`openWhatsAppLogoutModal()`).
- **Dải 4 chỉ số thống kê (4-Metric Stats Strip):**
  - Cấu trúc 4 ô thống kê Nocturne: `Tin 24h` (96), `Được tag` (9), `Độ trễ` (0,51s), `Thời gian trực` (99,5%).
- **Bộ gửi tin nhắn nhanh trực tiếp qua Gateway (Quick Outbound Dispatcher):**
  - Ô nhập số điện thoại hoặc nhóm đích E.164 (`#wa-target-input`), ô nhập chỉ đạo (`#wa-message-input`), nút gửi tin nhắn (`sendWhatsAppTestMessage()`).
- **Thẻ cấu hình kênh WhatsApp độc lập 100% (Decoupled Config):**
  - Cấu hình tên bot trên WhatsApp (`#wa-cfg-bot-name`), danh mục phong cách thái độ (`#wa-cfg-persona`), chỉ thị riêng (`#wa-cfg-notes`), nút lưu cấu hình (`saveWhatsAppChannelConfig()`).
- **Nhật ký tin nhắn WhatsApp thực tế (Session Log):**
  - Danh sách tin nhắn phiên trực chiến Nocturne, hiển thị hướng gửi (Outbound/Inbound), nhãn nhóm/1-1, timestamp monospace.

---

## 2. KẾT QUẢ KIỂM THỬ & KIỂM TRA CHẤT LƯỢNG

1. **`./doctor.sh`:**
   - 16/16 tiêu chuẩn SSOT: VƯỢT QUA 100% (Core Chassis, V6 UI, Policy Engine, AGY Core & Zalo).
   - Tác quyền Anh Cơ La (`genesis.corp.os@gmail.com`): Hợp lệ 100%.
2. **`python3 -m unittest discover -s tests`:**
   - 53/53 tests: PASS 100% (Toàn bộ test suite bao gồm Chassis, RBAC, Policy Engine, Zalo, Media, UI Dashboard).
3. **Thương hiệu & An toàn kiến trúc:**
   - Đã rà soát sạch các cụm thương hiệu hệ thống cũ ("Heo-Harness", "HEO OS") chuyển thành "Gen-Harness" / "Genesis Harness OS".
   - Tên bot persona mặc định/placeholder đổi sang trung tính ("Trợ Lý Zalo", "Trợ Lý WhatsApp") theo Spec A1.
   - Giữ nguyên 100% logic kết nối QR thời gian thực, các mã ID DOM (`#zalo-qr-image`, `#whatsapp-qr-image`, v.v.), API backend và định danh tác quyền Anh Cơ La.
   - Giữ nguyên toàn bộ plugin ID kỹ thuật nội bộ (`heo-channel-zalo-gateway`, `heo-channel-whatsapp-gateway`).

---

## 3. LỊCH SỬ COMMITS ĐÃ TẠO

- `a20fa55`: `feat(ui): update zalo gateway screen with Nocturne tokens per Spec F2`
- `10d90f9`: `feat(ui): update whatsapp gateway screen with Nocturne tokens per Spec F2`

---

## 4. TÌNH TRẠNG CÁC MÀN HÌNH KHÁC
- Không can thiệp vào bất kỳ màn hình nào ngoài 2 màn hình được chỉ định trong phạm vi Ticket 05a.
- Không tự ý mở PR hay merge vào nhánh `main`.

---

[BÀN GIAO] Ticket 05a (Zalo Gateway + WhatsApp Gateway) đã hoàn tất 100%, sẵn sàng chuyển sang bước tiếp theo theo quy trình phân công.
