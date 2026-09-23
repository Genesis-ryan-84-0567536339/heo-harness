# BIÊN BẢN BÀN GIAO TICKET 11 — ZALO & WHATSAPP GATEWAY NOCTURNE REBUILD

**Dự án:** HEO-HARNESS / GEN-HARNESS EXECUTIVE OS  
**Tác giả:** Anh Cơ La (Ryan) — `genesis.corp.os@gmail.com`  
**Branch thực hiện:** `feature/gen-harness-zalo-whatsapp-nocturne-11`  
**Trạng thái kiểm định:** `./doctor.sh` PASS 100% (16/16 test suites)  

---

## 1. NỘI DUNG THỰC HIỆN
Đã tái cấu trúc toàn diện tầng giao diện của hai cổng kết nối kênh trọng yếu:
1. **Zalo Gateway:**
   - Hàm cha `renderZaloHub()`: Thay header và subnav cũ (`hub-header`, `hub-subnav`, `hub-subnav-btn`) bằng header Nocturne flex wrap, typography SSOT, nút toggle trạng thái kênh và subnav pills bo tròn 999px kèm icon Phosphor (`ph-chat-circle-dots`).
   - Hàm con `renderZaloGatewayView()`: Triệt tiêu class CSS cũ (`card`, `card-pad`, `btn sm`, `badge`, `form-input`, `form-select`). Chuyển toàn bộ sang style inline Nocturne:
     - Card Trạng Thái Kết Nối Zalo Gateway: Header với dot trạng thái màu, status badge chuẩn font monospace, box hiển thị kết nối hoặc QR image thật sạch sẽ, details danh bạ/ID/tag-filter chuẩn typography, 3 nút hành động (`Làm Mới QR`, `Restart Bridge`, `Đăng Xuất`).
     - 4-metric strip: Thống kê số tin 24h, số lần được tag, độ trễ, thời gian trực chiến đồng bộ Nocturne.
     - Card Gửi Tin Nhắn Outbound: Select nhóm đích, input nội dung chỉ đạo và nút gửi tin kiểm thử màu tím accent (`var(--acc)`).
     - Card Cấu Hình Riêng Biệt Kênh Zalo Gateway: Độc lập 100%, pill "Tách Biệt Tuyệt Đối", input tên bot, select 7 phong cách thái độ ứng xử, textarea chỉ thị kênh (channel directives) và nút lưu cấu hình.
     - Card Nhật Ký Tin Nhắn Zalo Thực Tế: Badge số lượng tin nhắn, nút Làm Mới, render session log từng tin nhắn 1-1 / Nhóm với badge tinh tế.
2. **WhatsApp Gateway (Multi-Device):**
   - Hàm cha `renderWhatsAppHub()`: Chuyển đổi sang cấu trúc header Nocturne, nút toggle kênh và nút Làm Mới QR WhatsApp, subnav pills chuẩn Phosphor icon (`ph-whatsapp-logo`).
   - Hàm con `renderWhatsAppGatewayView()`: Loại bỏ toàn bộ class CSS cũ, áp dụng đầy đủ bộ style Nocturne chuẩn hóa đồng bộ với Zalo Gateway:
     - Card Trạng Thái WhatsApp Multi-Device Gateway: Hỗ trợ hiển thị QR Meta thật và trạng thái thiết bị ghép nối.
     - 4-metric strip: Giữ nguyên cấu trúc dữ liệu thời gian thực.
     - Card Gửi Tin Nhắn Outbound E.164: Form nhập số điện thoại / ID nhóm và nội dung gửi tin.
     - Card Cấu Hình Riêng Biệt Kênh WhatsApp Gateway: Độc lập 100%, lưu trữ cấu hình persona và channel directives cho đối tác quốc tế.
     - Card Nhật Ký Tin Nhắn WhatsApp Thực Tế: Quản lý session log tin nhắn đến/đi.

---

## 2. XÁC NHẬN TÍNH TOÀN VẸN LOGIC & DỮ LIỆU THẬT
- **Không bịa bất kỳ dữ liệu giả nào:** Toàn bộ dữ liệu hiển thị (tên tài khoản bot, số điện thoại, UID, QR code stream, số tin nhắn hôm nay, danh sách nhóm, nội dung tin nhắn) đều được liên kết trực tiếp với các state thật (`state.zalo`, `state.whatsapp`, `state.groups`, `state.zalo_messages`, `state.whatsapp_messages`).
- **Bảo tồn 100% logic backend & DOM IDs:** Tất cả các id element phục vụ JavaScript (`zalo-qr-image`, `zalo-qr-status-msg`, `zalo-qr-timer`, `zalo-qr-scanned-alert`, `zalo-test-group`, `zalo-test-msg`, `zalo-cfg-bot-name`, `zalo-cfg-persona`, `zalo-cfg-notes`, `whatsapp-qr-image`, `wa-target-input`, `wa-message-input`, `wa-cfg-bot-name`, `wa-cfg-persona`, `wa-cfg-notes`) và các hàm handler API backend (`toggleChannel`, `syncZaloGroups`, `refreshZaloQR`, `restartZaloBridge`, `openZaloLogoutModal`, `toggleZaloFilter`, `sendZaloTestMessage`, `saveZaloChannelConfig`, `refreshZaloMessages`, `refreshWhatsAppQR`, `restartWhatsAppBridge`, `openWhatsAppLogoutModal`, `sendWhatsAppTestMessage`, `saveWhatsAppChannelConfig`, `refreshWhatsAppMessages`) được giữ nguyên vẹn.

---

## 3. ĐIỀU HƯỚNG & BẢO MẬT GIAO DIỆN
- Tuân thủ tuyệt đối quy định: Không tự ý thêm `zalo` hay `whatsapp` vào `NAV`, `NAV_MAP`, `TITLES` hay sidebar. Hai màn hình tiếp tục ở trạng thái ẩn an toàn, chờ Kỹ sư trưởng trực tiếp xem xét và phê duyệt.

---

## 4. XÁC THỰC THỊ GIÁC (HEADLESS SCREENSHOTS)
- Màn Zalo Gateway mới: `/tmp/screen_zalo_nocturne.png` (URL `#/zalo`)
- Màn WhatsApp Gateway mới: `/tmp/screen_whatsapp_nocturne.png` (URL `#/whatsapp`)

---

## 5. DANH SÁCH COMMITS
1. Commit 1 (`98fcd58`): `feat(ui): rebuild Zalo Gateway views with Nocturne styling (Ticket 11)`
2. Commit 2 (`9b0bd9e`): `feat(ui): rebuild WhatsApp Gateway views with Nocturne styling (Ticket 11)`
