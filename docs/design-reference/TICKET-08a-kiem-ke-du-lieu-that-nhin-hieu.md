# TICKET 08a — Kiểm kê & dọn dữ liệu giả: Nhóm KINH DOANH (phần NHÌN + HIỂU)

## Bối cảnh
Toàn bộ 21 màn đã dựng xong về giao diện (ticket 01-07). Giờ cần biết: **màn nào / khối nào đang
hiển thị dữ liệu THẬT (nối đúng API/state có sẵn) và màn/khối nào đang hiển thị DỮ LIỆU GIẢ (hardcode,
random, hoặc "dữ liệu mẫu" như đã thấy ở màn Bảng cơ hội)**. Sếp yêu cầu: liệt kê rõ, và **xoá sạch dữ
liệu giả**, thay bằng trạng thái rỗng trung thực — không được để số liệu bịa đặt gây hiểu nhầm.

File chính: `heo_harness/plugins/ui_dashboard/dashboard.html`. Backend API thật đã có (xem
`tests/test_ui_dashboard.py`, các route `/api/*`): `/api/system/status`, `/api/plugins/list`,
`/api/plugins/catalog`, `/api/plugins/toggle`, `/api/policy/simulate`, `/api/groups/*`, `/api/people/*`,
`/api/config`, `/api/chat`. Có sẵn `data_store` (`heo_harness/core/store.py`) chứa groups/people thật.

## Phạm vi: các màn thuộc "Tổng quan điều hành", "Hàng đợi & Hành động", "Nhóm & Con người",
## "Bản đồ quan hệ", "Cơ hội & Thị trường" (hub: command, opportunities, workbench_action, directory,
## relationship_radar, work, workbench, chat_intelligence)

## Việc cần làm — LÀM THEO ĐÚNG THỨ TỰ
1. Với TỪNG hub trong phạm vi trên, đọc kỹ hàm `render*Hub()` tương ứng. Với từng con số/nội dung hiển
   thị, xác định: nó đến từ `state.*` (dữ liệu thật đã có trong app, vd `state.groups`, `state.people`)
   hay API call thật, HAY là hardcode/mảng mẫu viết cứng trong code (vd danh sách "Xưởng gỗ Bình Dương",
   con số "91", "41", "23"...)?
2. Ghi kết quả vào bảng kiểm kê tại `docs/design-reference/AUDIT-DU-LIEU-THAT-GIA.md` (tạo mới), mỗi
   dòng: `| Màn hình | Khối/thành phần | THẬT hay GIẢ | Ghi chú (API nào, hay lý do chưa có API) |`.
3. Với các khối XÁC ĐỊNH LÀ GIẢ (hardcode mẫu, không nối API thật):
   - **Xoá số liệu giả đó đi.**
   - Thay bằng trạng thái rỗng trung thực, ví dụ: "Chưa có dữ liệu thật — chờ nối API [tên API cần có]"
     kèm icon trung tính, KHÔNG hiển thị số 0 giả hay số bịa. Giữ nguyên layout/style (card, khung) để
     không vỡ giao diện, chỉ đổi nội dung bên trong.
   - Nếu khối đó có thể tính được từ dữ liệu THẬT đã có sẵn trong `state.*` dù chưa hoàn hảo (vd đếm số
     nhóm/người thật thay vì con số mẫu), thì **nối vào dữ liệu thật đó** thay vì để trống — ưu tiên
     dùng thật hơn để trống, chỉ để trống khi thực sự không có dữ liệu nguồn nào.
4. Với các khối XÁC ĐỊNH LÀ THẬT: không đụng vào, chỉ ghi nhận vào bảng kiểm kê.
5. `python3 -m unittest discover -s tests` phải pass 100% (không cần chạy `./doctor.sh` riêng — nó tự
   gồm bước này, chạy 1 trong 2 cái là đủ).

## KHÔNG làm trong đợt này
- Không đụng các màn thuộc nhóm KỸ THUẬT · BACKEND (có ticket 08b riêng xử lý song song).
- Không tự chế API mới — nếu thiếu API, để trạng thái rỗng + ghi rõ trong bảng kiểm kê API nào cần có.
- Không đổi plugin ID, kiến trúc core, định danh tác quyền, API contract hiện có.
- Không tự push remote / mở PR / merge vào `main`.

## Quy trình bàn giao
- Commit nhỏ theo từng màn đã dọn xong.
- Khi xong (hoặc bế tắc), ghi `docs/design-reference/HANDOFF-08a.md`: tóm tắt bảng kiểm kê, đã xoá/thay
  bao nhiêu khối giả, kết quả test. Dòng CUỐI CÙNG in ra màn hình phải bắt đầu CHÍNH XÁC bằng
  `[BÀN GIAO]`.
- Bế tắc quá 3 lần cho cùng một vấn đề: dừng lại, ghi rõ vào HANDOFF-08a.md, không đào sâu vô hạn.
