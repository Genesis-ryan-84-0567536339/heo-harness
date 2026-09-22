# TICKET 02 — Gen-Harness Console: Nhóm "HIỂU"

## Bối cảnh
Tiếp theo TICKET-01 (đã xong, đã merge vào `main`: nền UI, IA 5 nhóm, rebrand, màn Tổng quan điều hành).
SSOT: `docs/design-reference/Gen-Harness-Product-Spec-LOCKED.md`. Nguồn thiết kế đích:
`docs/design-reference/claude-design-export/Gen-Harness Console.dc.html`.
Bạn đang làm việc trên nhánh mới tạo từ `main` đã merge — không cần lo về TICKET-01 nữa, nó đã xong.

File chính: `heo_harness/plugins/ui_dashboard/dashboard.html`.

## Phạm vi: 4 màn trong nhóm "HIỂU"
1. `directory` — Nhóm & Con người (`renderDirectoryHub()`)
2. `relationship_radar` — Bản đồ quan hệ & 360 (`renderRelationshipRadarHub()`) — đối chiếu spec F2 mục 3 (Relationship Map) và mục 4 (Living Profile) nếu có phần hồ sơ chi tiết.
3. `workbench` — Cung ↔ Cầu (`renderCommercialWorkbenchHub()`) — tính năng nghiệp vụ riêng của dự án (không có trong 10 màn F2 gốc), giữ nguyên logic nghiệp vụ, chỉ chỉnh hình thức.
4. `chat_intelligence` — Kho hội thoại & Trí tuệ (`renderChatIntelligenceHub()`) — đối chiếu spec F2 mục 8 (Knowledge & Search).

## Việc cần làm
1. Với mỗi màn trên: đối chiếu markup/CSS hiện tại với `Gen-Harness Console.dc.html` và design tokens Nocturne
   (`docs/design-reference/claude-design-export/_ds/*/styles.css`, `readme.md`) — chỉnh cho khớp phong cách
   (card, table, tag, button theo đúng class hệ thống đã tài liệu hoá trong `readme.md`), KHÔNG cần viết lại
   toàn bộ nếu phần lớn đã đúng token (nhiều nơi đã đúng từ trước, chỉ sửa chỗ lệch).
2. Rà soát và thay các cụm mang tính **thương hiệu hệ thống** còn sót: "Heo-Harness", "HEO OS", "AGY-ASSIS / HEO OS"
   → "Gen-Harness" / "Genesis Harness OS". **Không bắt buộc xoá "Bé Heo"** khi nó xuất hiện như một **tên persona
   mặc định có thể đổi được** (ví dụ placeholder/option "Kế thừa phong cách chung của Bé Heo") — theo spec mục A1,
   "Bé Heo" được phép tồn tại như một mẫu persona tùy chọn, không phải bản sắc hệ thống bắt buộc.
3. Không đổi cấu trúc dữ liệu / API. Nếu thấy thiếu API cho phần hiển thị, dùng dữ liệu đã có sẵn trong `state.*`,
   không tự chế API mới.
4. Giữ nguyên bất biến: plugin ID nội bộ, đường dẫn module Python, định danh tác quyền
   (`heo_harness/plugins/auth/__init__.py` — TUYỆT ĐỐI không đụng).
5. `python3 -m unittest discover -s tests` và `./doctor.sh` phải pass 100% sau khi sửa.

## KHÔNG làm trong đợt này
- Không đụng các màn thuộc nhóm khác (NHÌN, QUẢN, LÀM, MÁY) — các ticket song song khác đang xử lý.
- Không đổi plugin ID, kiến trúc core, định danh tác quyền, API contract hiện có.
- Không tự push remote / mở PR / merge vào `main`.

## Quy trình bàn giao
- Làm việc trên nhánh hiện tại của worktree này.
- Commit nhỏ, rõ ràng theo từng màn.
- Khi xong (hoặc bế tắc), ghi `docs/design-reference/HANDOFF-02.md`: đã làm gì, kết quả test/doctor.sh,
  còn gì chưa xong. Dòng cuối bắt đầu bằng `[BÀN GIAO]`.
- Bế tắc quá 3 lần cho cùng vấn đề: dừng, ghi rõ vào HANDOFF-02.md, không đào sâu vô hạn.
