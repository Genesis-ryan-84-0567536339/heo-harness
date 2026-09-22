# TICKET 03 — Gen-Harness Console: Nhóm "QUẢN"

## Bối cảnh
Tiếp theo TICKET-01 (đã xong, đã merge vào `main`: nền UI, IA 5 nhóm, rebrand, màn Tổng quan điều hành).
SSOT: `docs/design-reference/Gen-Harness-Product-Spec-LOCKED.md`. Nguồn thiết kế đích:
`docs/design-reference/claude-design-export/Gen-Harness Console.dc.html`.
Đây là worktree/nhánh riêng — có 2 ticket khác (nhóm HIỂU, nhóm LÀM+MÁY) đang chạy song song trên
worktree khác, không đụng file của bạn, không cần quan tâm.

File chính: `heo_harness/plugins/ui_dashboard/dashboard.html`.

## Phạm vi: 3 màn trong nhóm "QUẢN"
1. `work` — Bảng cơ hội & Tiến độ (`renderWorkScheduleHub()`) — đối chiếu spec F2 mục 5 (Opportunity Board).
2. `people_review` — Đánh giá con người (`renderPeopleReviewHub()`) — đối chiếu spec F2 mục 6 (People Review).
3. `intelligence` — Chất lượng chăm sóc (`renderIntelligenceHub()`) — đối chiếu spec F2 mục 7 (Care Quality).

## Việc cần làm
1. Với mỗi màn trên: đối chiếu markup/CSS hiện tại với `Gen-Harness Console.dc.html` và design tokens Nocturne
   (`docs/design-reference/claude-design-export/_ds/*/styles.css`, `readme.md`) — chỉnh cho khớp phong cách
   (card, table, tag, button theo đúng class hệ thống trong `readme.md`). Nhiều nơi có thể đã đúng token từ
   trước, chỉ sửa chỗ lệch, không viết lại toàn bộ.
2. Đối chiếu nội dung với spec F2 mục 5/6/7: đảm bảo các thành phần bắt buộc có mặt (vd People Review cần điểm
   số + xu hướng + tín hiệu nổi bật + khuyến nghị + nút xem chứng cứ theo mục 6; Care Quality cần các chỉ số ở
   mục 7). Nếu thiếu, bổ sung bằng dữ liệu đã có trong `state.*` hoặc dữ liệu mock rõ ràng đánh dấu
   `// TODO: Đấu nối API khi backend triển khai` — không tự chế API mới.
3. Rà soát và thay các cụm mang tính **thương hiệu hệ thống** còn sót ("Heo-Harness", "HEO OS") → "Gen-Harness" /
   "Genesis Harness OS". Không bắt buộc xoá "Bé Heo" khi là tên persona tùy chọn (xem spec mục A1).
4. Giữ nguyên bất biến: plugin ID nội bộ, đường dẫn module Python, định danh tác quyền
   (`heo_harness/plugins/auth/__init__.py` — TUYỆT ĐỐI không đụng), API contract hiện có.
5. `python3 -m unittest discover -s tests` và `./doctor.sh` phải pass 100% sau khi sửa.

## KHÔNG làm trong đợt này
- Không đụng các màn thuộc nhóm khác (NHÌN, HIỂU, LÀM, MÁY).
- Không đổi plugin ID, kiến trúc core, định danh tác quyền, API contract hiện có.
- Không tự push remote / mở PR / merge vào `main`.

## Quy trình bàn giao
- Commit nhỏ, rõ ràng theo từng màn.
- Khi xong (hoặc bế tắc), ghi `docs/design-reference/HANDOFF-03.md`: đã làm gì, kết quả test/doctor.sh,
  còn gì chưa xong. Dòng cuối bắt đầu bằng `[BÀN GIAO]`.
- Bế tắc quá 3 lần cho cùng vấn đề: dừng, ghi rõ vào HANDOFF-03.md, không đào sâu vô hạn.
