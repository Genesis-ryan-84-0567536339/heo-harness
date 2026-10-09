# TICKET 05a — Gen-Harness Console: Zalo Gateway + WhatsApp Gateway

## Bối cảnh
Tiếp theo các ticket trước (01-02 đã/đang xong). SSOT: `docs/design-reference/Gen-Harness-Product-Spec-LOCKED.md`.
Nguồn thiết kế đích: `docs/design-reference/claude-design-export/Gen-Harness Console.dc.html`.
File chính: `heo_harness/plugins/ui_dashboard/dashboard.html`.

## Phạm vi: 2 màn trong nhóm "MÁY"
1. `zalo` — Kênh Zalo Gateway (`renderZaloHub()`)
2. `whatsapp` — Kênh WhatsApp Gateway (`renderWhatsAppHub()`)

## Việc cần làm
1. Đối chiếu markup/CSS với `Gen-Harness Console.dc.html` + design tokens Nocturne
   (`docs/design-reference/claude-design-export/_ds/*/styles.css`, `readme.md`) — chỉnh cho khớp phong cách.
2. Rà soát và thay các cụm **thương hiệu hệ thống** còn sót ("Heo-Harness", "HEO OS") → "Gen-Harness" /
   "Genesis Harness OS". Các trường **bot_name mặc định** (vd "Bé Heo (Zalo)", "Bé Heo (WhatsApp Gateway)")
   là tên persona người dùng có thể đổi được — giữ nguyên là hợp lệ theo spec mục A1 (Bé Heo = persona tùy
   chọn, không phải bản sắc hệ thống), KHÔNG bắt buộc phải xoá, nhưng nên đổi placeholder ví dụ mặc định sang
   trung tính hơn nếu hợp lý (vd "Trợ Lý Zalo", để user tự đặt tên).
3. Không đổi logic kết nối QR/API thật (đây là tính năng nghiệp vụ đang hoạt động, chỉ chỉnh hình thức).
4. Giữ nguyên bất biến: plugin ID nội bộ, đường dẫn module Python, định danh tác quyền
   (`heo_harness/plugins/auth/__init__.py` — TUYỆT ĐỐI không đụng), API contract hiện có.
5. `python3 -m unittest discover -s tests` và `./doctor.sh` phải pass 100% sau khi sửa.

## KHÔNG làm trong đợt này
- Không đụng màn khác ngoài 2 màn trên.
- Không đổi plugin ID, kiến trúc core, định danh tác quyền, API contract hiện có.
- Không tự push remote / mở PR / merge vào `main`.

## Quy trình bàn giao
- Commit nhỏ, rõ ràng theo từng màn.
- Khi xong (hoặc bế tắc), ghi `docs/design-reference/HANDOFF-05a.md`: đã làm gì, kết quả test/doctor.sh,
  còn gì chưa xong. Dòng cuối bắt đầu bằng `[BÀN GIAO]`.
- Bế tắc quá 3 lần cho cùng vấn đề: dừng, ghi rõ vào HANDOFF-05a.md, không đào sâu vô hạn.
