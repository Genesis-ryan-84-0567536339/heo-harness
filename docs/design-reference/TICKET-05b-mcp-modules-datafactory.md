# TICKET 05b — Gen-Harness Console: MCP Hub + Modules + Data Factory

## Bối cảnh
Tiếp theo các ticket trước (01-03 đã/đang xong). SSOT: `docs/design-reference/Gen-Harness-Product-Spec-LOCKED.md`.
Nguồn thiết kế đích: `docs/design-reference/claude-design-export/Gen-Harness Console.dc.html`.
File chính: `heo_harness/plugins/ui_dashboard/dashboard.html`.

## Phạm vi: 3 màn trong nhóm "MÁY"
1. `mcp_connectors` — Kho Ứng Dụng MCP Hub (`renderMcpConnectorsHub()`)
2. `modules` — Module & Skills Hub (`renderModulesHub()`) — liệt kê plugin: **giữ nguyên 100% plugin ID nội bộ**
   (vd `heo-ui-dashboard-executive`, `heo-provider-*`...) khi hiển thị — đây là ID kỹ thuật, không phải branding.
3. `data_factory` — Data Factory (`renderDataFactoryHub()`)

## Việc cần làm
1. Đối chiếu markup/CSS với `Gen-Harness Console.dc.html` + design tokens Nocturne
   (`docs/design-reference/claude-design-export/_ds/*/styles.css`, `readme.md`) — chỉnh cho khớp phong cách.
2. Rà soát và thay các cụm **thương hiệu hệ thống** còn sót ("Heo-Harness", "HEO OS") → "Gen-Harness" /
   "Genesis Harness OS" trong PHẦN MÔ TẢ/TIÊU ĐỀ hiển thị — không đổi plugin ID kỹ thuật.
3. Giữ nguyên bất biến: plugin ID nội bộ, đường dẫn module Python, định danh tác quyền
   (`heo_harness/plugins/auth/__init__.py` — TUYỆT ĐỐI không đụng), API contract hiện có.
4. `python3 -m unittest discover -s tests` và `./doctor.sh` phải pass 100% sau khi sửa.

## KHÔNG làm trong đợt này
- Không đụng màn khác ngoài 3 màn trên.
- Không đổi plugin ID, kiến trúc core, định danh tác quyền, API contract hiện có.
- Không tự push remote / mở PR / merge vào `main`.

## Quy trình bàn giao
- Commit nhỏ, rõ ràng theo từng màn.
- Khi xong (hoặc bế tắc), ghi `docs/design-reference/HANDOFF-05b.md`: đã làm gì, kết quả test/doctor.sh,
  còn gì chưa xong. Dòng cuối bắt đầu bằng `[BÀN GIAO]`.
- Bế tắc quá 3 lần cho cùng vấn đề: dừng, ghi rõ vào HANDOFF-05b.md, không đào sâu vô hạn.
