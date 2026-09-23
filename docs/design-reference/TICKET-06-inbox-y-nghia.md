# TICKET 06 — Gen-Harness Console: Hộp thư ý nghĩa (Inbox of Meaning)

## Bối cảnh
Ticket cuối cùng còn thiếu trong lộ trình — bị bỏ sót khi lên kế hoạch ban đầu (chỉ có 20/21 màn được
giao ticket). SSOT: `docs/design-reference/Gen-Harness-Product-Spec-LOCKED.md`. Nguồn thiết kế đích:
`docs/design-reference/claude-design-export/Gen-Harness Console.dc.html`.
File chính: `heo_harness/plugins/ui_dashboard/dashboard.html`.

## Phạm vi: 1 màn trong nhóm "NHÌN"
`opportunities` — Hộp thư ý nghĩa (`renderOpportunitiesHub()`), hiện title là "Inbox Ý Nghĩa & Bảng
Cơ Hội (Opportunities)".

## Việc cần làm
1. Đối chiếu với spec mục F2 phần 2 (Inbox of Meaning): đây KHÔNG phải inbox tin nhắn thô, mà là hàng
   đợi các **đơn vị ý nghĩa** — cơ hội mới, hỏi giá, than phiền, hẹn, tài liệu cần soạn, tin chờ duyệt,
   cảnh báo, ứng viên cần xem. Mỗi item phải có đủ: nguồn, đối tượng, mức ưu tiên, điểm số, tóm tắt 2
   câu, hành động đề xuất, chứng cứ (nút drill-down xem chứng cứ gốc).
2. Đối chiếu markup/CSS với `Gen-Harness Console.dc.html` + design tokens Nocturne
   (`docs/design-reference/claude-design-export/_ds/*/styles.css`, `readme.md`) — chỉnh cho khớp phong
   cách (card, tag priority, button hành động).
3. Nếu backend chưa có API cho khối nào, dùng dữ liệu mock rõ ràng đánh dấu
   `// TODO: Đấu nối API khi backend triển khai`, không tự chế API mới phức tạp.
4. Rà soát và thay các cụm thương hiệu hệ thống còn sót ("Heo-Harness", "HEO OS") → "Gen-Harness" /
   "Genesis Harness OS".
5. Giữ nguyên bất biến: plugin ID nội bộ, đường dẫn module Python, định danh tác quyền
   (`heo_harness/plugins/auth/__init__.py` — TUYỆT ĐỐI không đụng), API contract hiện có.
6. `python3 -m unittest discover -s tests` và `./doctor.sh` phải pass 100% sau khi sửa.

## KHÔNG làm trong đợt này
- Không đụng màn khác ngoài `opportunities`.
- Không đổi plugin ID, kiến trúc core, định danh tác quyền, API contract hiện có.
- Không tự push remote / mở PR / merge vào `main`.

## Quy trình bàn giao
- Commit nhỏ, rõ ràng.
- Khi xong (hoặc bế tắc), ghi `docs/design-reference/HANDOFF-06.md`: đã làm gì, kết quả test/doctor.sh,
  còn gì chưa xong. Dòng cuối bắt đầu bằng `[BÀN GIAO]`.
- Bế tắc quá 3 lần cho cùng một vấn đề: dừng lại, ghi rõ vào HANDOFF-06.md, không đào sâu vô hạn.
