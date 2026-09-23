# TICKET 11 — Dựng lại Zalo Gateway + WhatsApp Gateway theo chuẩn Nocturne (backend đã xác nhận THẬT)

## Bối cảnh
Nhóm "Tầng dữ liệu" và "Agent & Model" đã xong. Còn 2 màn kỹ thuật quan trọng: `zalo`, `whatsapp` —
đây là 2 màn có **backend thật đã xác nhận hoạt động** (Kỹ sư trưởng đã tự tay `npm install` và khởi
động bridge thật, tạo ra QR đăng nhập thật từ Zalo/WhatsApp — xem log `logs/zalo-bridge-test.log`,
`logs/whatsapp-bridge-test.log` nếu tò mò), nhưng **giao diện vẫn dùng class CSS cũ** (`class="hub-header"`,
`class="btn sm"`, `class="hub-subnav-btn"`) — KHÔNG phải style Nocturne inline như các màn đã dựng lại.

**Lưu ý quan trọng**: 2 màn này KHÔNG có khối tương ứng trong file mockup
`Gen-Harness Console.dc.html` (mockup không thiết kế riêng cho Zalo/WhatsApp Gateway) — vì vậy đây
KHÔNG phải "trích nguyên văn mockup" như các ticket trước, mà là **tự dựng lại theo đúng ngôn ngữ thiết
kế Nocturne** (tham khảo `docs/design-reference/claude-design-export/_ds/*/styles.css` và `readme.md`,
và tham khảo cách các màn đã dựng xong khác — vd `renderDataFactoryIdentityView()`,
`renderRefineryRulesView()` — dùng biến CSS `var(--color-*)`, cỡ chữ/khoảng cách/bo góc giống hệt).

File cần sửa: `heo_harness/plugins/ui_dashboard/dashboard.html`, hàm `renderZaloHub()` (dòng ~3444) và
`renderWhatsAppHub()` (dòng ~3474), cùng các view con `renderZaloGatewayView()` (~3729),
`renderWhatsAppGatewayView()` (~3534). GIỮ NGUYÊN toàn bộ logic thật bên trong (QR polling, toggle
kênh, đồng bộ nhóm, gửi tin nhắn thử...) — chỉ đổi lớp trình bày HTML/CSS, không đổi hành vi.

## Việc cần làm
1. Đổi toàn bộ `class="hub-header"`, `class="hub-subnav-btn"`, `class="btn sm"`... sang style Nocturne
   inline (`style="background:var(--color-surface,#232532); border:1px solid var(--color-divider,...)..."`)
   giống các màn đã dựng lại khác. Giữ nguyên bố cục tổng thể (header + subnav 2 tab + nội dung QR/log).
2. Rà soát text: các placeholder mặc định như "Bé Heo (Zalo)", "Bé Heo (WhatsApp Gateway)" là TÊN
   PERSONA người dùng tự đặt được (spec cho phép giữ, không phải bản sắc hệ thống bắt buộc) — giữ
   nguyên logic, chỉ đổi style hiển thị nếu cần.
3. QR code, trạng thái kết nối, số liệu (tin nhắn vào/ra...) đều đã lấy từ `state.zalo`/`state.whatsapp`
   thật — XÁC NHẬN LẠI không có số bịa nào chen vào trong lúc sửa style.
4. `./doctor.sh` phải pass 100% sau khi sửa.

## TUYỆT ĐỐI KHÔNG
- KHÔNG bịa dữ liệu giả bất kỳ chỗ nào.
- KHÔNG tự thêm `zalo`/`whatsapp` vào `NAV`/`NAV_MAP`/`TITLES`/sidebar — 2 màn này ĐANG CỐ Ý bị ẩn khỏi
  menu (theo yêu cầu của Sếp: trang nào xong mới lộ ra). Kỹ sư trưởng sẽ tự kiểm tra bằng ảnh chụp và
  QUYẾT ĐỊNH khi nào thêm vào nav — không phải việc của ticket này.
- KHÔNG đổi logic bridge/QR/kết nối thật, không đổi plugin ID, kiến trúc core, định danh tác quyền, API
  contract hiện có.
- Không tự push remote / mở PR / merge vào `main`.

## Quy trình bàn giao
- Commit riêng cho Zalo, riêng cho WhatsApp.
- Ghi `docs/design-reference/HANDOFF-11.md`: đã đổi gì, xác nhận không có dữ liệu giả, kết quả doctor.sh.
  Dòng CUỐI CÙNG in ra màn hình phải bắt đầu CHÍNH XÁC bằng `[BÀN GIAO]`.
- Bế tắc quá 3 lần cho cùng vấn đề: dừng lại, ghi rõ vào HANDOFF-11.md, không đào sâu vô hạn.
