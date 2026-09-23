# TICKET 08b — Kiểm kê & dọn dữ liệu giả: Nhóm "Con người & Chất lượng" + toàn bộ KỸ THUẬT · BACKEND

## Bối cảnh
Toàn bộ 21 màn đã dựng xong về giao diện (ticket 01-07). Giờ cần biết: **màn nào / khối nào đang
hiển thị dữ liệu THẬT (nối đúng API/state có sẵn) và màn/khối nào đang hiển thị DỮ LIỆU GIẢ (hardcode,
random, hoặc "dữ liệu mẫu")**. Sếp yêu cầu: liệt kê rõ, và **xoá sạch dữ liệu giả**, thay bằng trạng
thái rỗng trung thực — không được để số liệu bịa đặt gây hiểu nhầm.

File chính: `heo_harness/plugins/ui_dashboard/dashboard.html`. Backend API thật đã có (xem
`tests/test_ui_dashboard.py`, các route `/api/*`): `/api/system/status`, `/api/plugins/list`,
`/api/plugins/catalog`, `/api/plugins/toggle`, `/api/policy/simulate`, `/api/groups/*`, `/api/people/*`,
`/api/config`, `/api/chat`. Có sẵn `data_store` (`heo_harness/core/store.py`) chứa groups/people thật.
Zalo/WhatsApp Gateway có logic QR/kết nối thật — phần đó chắc chắn THẬT, không cần nghi ngờ, chỉ kiểm
tra phần số liệu thống kê hiển thị kèm theo có thật không.

## Phạm vi: các màn thuộc "Con người & Chất lượng" (people, care) + TOÀN BỘ nhóm "KỸ THUẬT · BACKEND"
## (data_factory, assistant, mcp_connectors, modules, governance, zalo, whatsapp)
Cụ thể hub: `people_review`, `intelligence`, `data_factory`, `assistant`, `mcp_connectors`, `modules`,
`governance`, `zalo`, `whatsapp`.

## Việc cần làm — LÀM THEO ĐÚNG THỨ TỰ
1. Với TỪNG hub trong phạm vi trên, đọc kỹ hàm `render*Hub()` tương ứng. Với từng con số/nội dung hiển
   thị, xác định: nó đến từ `state.*` (dữ liệu thật đã có trong app) hay API call thật, HAY là
   hardcode/mảng mẫu viết cứng trong code?
2. Ghi kết quả vào bảng kiểm kê tại `docs/design-reference/AUDIT-DU-LIEU-THAT-GIA-08b.md` (tạo mới,
   đặt tên khác file của ticket 08a vì 2 ticket chạy song song trên 2 worktree khác nhau, sẽ gộp lại
   sau), mỗi dòng: `| Màn hình | Khối/thành phần | THẬT hay GIẢ | Ghi chú (API nào, hay lý do chưa có
   API) |`.
3. Với các khối XÁC ĐỊNH LÀ GIẢ (hardcode mẫu, không nối API thật):
   - **Xoá số liệu giả đó đi.**
   - Thay bằng trạng thái rỗng trung thực, ví dụ: "Chưa có dữ liệu thật — chờ nối API [tên API cần có]"
     kèm icon trung tính, KHÔNG hiển thị số 0 giả hay số bịa. Giữ nguyên layout/style để không vỡ giao
     diện, chỉ đổi nội dung bên trong.
   - Nếu khối đó có thể tính được từ dữ liệu THẬT đã có sẵn trong `state.*` dù chưa hoàn hảo, thì
     **nối vào dữ liệu thật đó** thay vì để trống — ưu tiên dùng thật hơn để trống.
4. Với các khối XÁC ĐỊNH LÀ THẬT (vd logic QR Zalo/WhatsApp, danh sách 11 plugin thật, chat API thật):
   không đụng vào, chỉ ghi nhận vào bảng kiểm kê.
5. `python3 -m unittest discover -s tests` phải pass 100% (không cần chạy `./doctor.sh` riêng — nó tự
   gồm bước này, chạy 1 trong 2 cái là đủ).

## KHÔNG làm trong đợt này
- Không đụng các màn thuộc nhóm KINH DOANH phần NHÌN/HIỂU (có ticket 08a riêng xử lý song song trên
  worktree khác).
- Không tự chế API mới — nếu thiếu API, để trạng thái rỗng + ghi rõ trong bảng kiểm kê API nào cần có.
- Không đổi logic kết nối Zalo/WhatsApp thật, không đổi plugin ID, kiến trúc core, định danh tác quyền,
  API contract hiện có.
- Không tự push remote / mở PR / merge vào `main`.

## Quy trình bàn giao
- Commit nhỏ theo từng màn đã dọn xong.
- Khi xong (hoặc bế tắc), ghi `docs/design-reference/HANDOFF-08b.md`: tóm tắt bảng kiểm kê, đã xoá/thay
  bao nhiêu khối giả, kết quả test. Dòng CUỐI CÙNG in ra màn hình phải bắt đầu CHÍNH XÁC bằng
  `[BÀN GIAO]`.
- Bế tắc quá 3 lần cho cùng một vấn đề: dừng lại, ghi rõ vào HANDOFF-08b.md, không đào sâu vô hạn.
