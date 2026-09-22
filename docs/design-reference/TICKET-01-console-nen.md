# TICKET 01 — Gen-Harness Console: Nền UI + màn Tổng quan điều hành

## Bối cảnh (đọc trước khi làm)
- Dự án đang đổi tên chính thức: **Heo-Harness → Gen-Harness (Genesis Harness OS)**. SSOT duy nhất:
  `docs/design-reference/Gen-Harness-Product-Spec-LOCKED.md` (v2.2 LOCKED).
- Bản thiết kế đích **đã hoàn thiện**, xuất từ Claude Design, là nguồn sự thật cho layout/nav/copy:
  `docs/design-reference/claude-design-export/Gen-Harness Console.dc.html`
- Design system "Nocturne" (`docs/design-reference/claude-design-export/_ds/*/styles.css` + `readme.md`)
  **đã được áp dụng một phần** vào `heo_harness/plugins/ui_dashboard/dashboard.html` hiện tại — so khớp
  `:root` tokens trong file đó, màu/token đã đúng. KHÔNG cần làm lại phần token màu từ đầu.
- File cần sửa chính: `heo_harness/plugins/ui_dashboard/dashboard.html` (~12.6k dòng, single-file app).
  Backend API đã có sẵn, không cần viết lại: `/api/system/status`, `/api/plugins/list`,
  `/api/plugins/catalog`, `/api/plugins/toggle`, `/api/policy/simulate`, `/api/groups/update`,
  `/api/people/update`, `/api/config`, `/api/chat`.

## Việc cần làm (CHỈ trong phạm vi này)

1. **Rebrand toàn bộ text hiển thị cho người dùng** trong `dashboard.html`: "HEO OS",
   "AGY-ASSIS / HEO OS — V6 Executive Intelligence Console", mọi chỗ mặc định gọi persona là
   "Bé Heo" → đổi theo tên chính thức trong spec ("Gen-Harness" / "Genesis Harness OS").
   **TUYỆT ĐỐI KHÔNG đổi**: plugin ID nội bộ (vd `heo-ui-dashboard-executive`), đường dẫn module
   Python (`heo_harness/...`), và định danh tác quyền "Anh Cơ La / genesis.corp.os@gmail.com" trong
   `heo_harness/plugins/auth/__init__.py` — `doctor.sh` kiểm tra định danh này, đổi là hỏng SSOT.

2. **Dựng lại điều hướng (IA) theo đúng 5 nhóm ở spec mục F2**: Nhìn → Hiểu → Quản → Làm → Máy,
   đối chiếu chính xác tên nhóm/icon/thứ tự với sidebar trong `Gen-Harness Console.dc.html`
   (đó là nguồn sự thật). Thay thế cấu trúc "4 domain" hiện tại.

3. **Dựng đầy đủ 1 màn hình ưu tiên: "Tổng quan điều hành" (Command Overview)**, đúng spec
   mục F2 phần 1 + F4 nhóm "Vận hành hệ thống":
   - Sức khỏe hệ thống (plugin / kênh / nghẽn / lỗi đã cách ly) — nối vào `/api/plugins/list`,
     `/api/system/status` đã có.
   - Nhiệt kế hoạt động (số hội thoại, số người chủ động, số group đang nóng).
   - Hàng đợi cần xử lý (cơ hội / cảnh báo / việc đến hạn / tin chờ duyệt).
   - 5 đối tượng đáng chú ý nhất hôm nay.
   - 5 tín hiệu thị trường/chủ đề đang nổi.
   - Mức tin cậy dữ liệu.
   - Khối nào backend chưa có API thì dùng dữ liệu mock rõ ràng (đánh dấu `TODO` trong comment),
     KHÔNG tự chế API mới phức tạp — việc đó ngoài phạm vi đợt 1.
   - Markup/CSS phải bám sát layout thật trong `Gen-Harness Console.dc.html` cho đúng màn hình này.

4. **Cập nhật test cho khớp rebrand**: `tests/test_ui_dashboard.py` hiện assert các chuỗi
   "HEO OS", "Executive Intelligence" — sửa cho khớp tên mới. KHÔNG xoá test, không giảm coverage.
   `doctor.sh` không cần sửa (phần định danh tác quyền tách biệt, không liên quan branding).

5. `python3 -m unittest discover -s tests` phải pass 100%. `./doctor.sh` phải pass.

## KHÔNG làm trong đợt này
- Không đổi plugin ID / tên module Python / kiến trúc core (Context, EventBus, PluginManager).
- Không đổi định danh tác quyền.
- Không dựng 11 màn hình còn lại trong spec F2 — chỉ 1 màn Tổng quan điều hành.
- Không đổi API contract hiện có (chỉ được thêm field mới, không đổi/xoá field đang dùng).
- Không tự push remote, không tự mở PR, không tự merge vào `main`.

## Quy trình bàn giao
- Làm việc ngay trên nhánh hiện tại `feature/gen-harness-console-v1` (đây đã là worktree cô lập).
- Commit rõ ràng theo từng bước nhỏ, message tiếng Việt hoặc Anh đều được, miễn rõ nghĩa.
- Khi xong (hoặc khi bế tắc), ghi vào `docs/design-reference/HANDOFF.md`:
  - Đã làm gì, còn gì chưa xong.
  - Kết quả `python3 -m unittest discover -s tests` và `./doctor.sh`.
  - Bắt đầu dòng cuối bằng `[BÀN GIAO]` để dễ nhận diện.
- Nếu bế tắc quá 3 lần thử cho cùng một vấn đề: dừng lại, ghi rõ vấn đề vào `HANDOFF.md`,
  không đào sâu vô hạn — chờ Kỹ sư trưởng xem lại.
