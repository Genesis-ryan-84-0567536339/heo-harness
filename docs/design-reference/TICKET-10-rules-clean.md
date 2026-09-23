# TICKET 10 — Data Factory: Quy tắc sàng lọc (isRules) + Kho sạch & Trí nhớ (isClean)

## Bối cảnh
Tiếp theo 09b (đã xong toàn bộ). Đây là 2 màn CÒN LẠI cuối cùng của nhóm "Tầng dữ liệu" (Kỹ thuật ·
Backend) — màn `raw` (Kho dữ liệu thô) Kỹ sư trưởng đã tự làm xong, `identity` Kỹ sư trưởng đang làm
riêng. Chỉ còn `rules` và `clean` là việc của ticket này.

**CẢNH BÁO QUAN TRỌNG — ĐỌC KỸ TRƯỚC KHI LÀM**: 2 màn này trong file mockup mô tả các tính năng
**HOÀN TOÀN MỚI** (rule editor, trí nhớ tạm/working memory, tham số agent) — sau khi rà soát kỹ,
**KHÔNG có API backend thật nào tương ứng** cho các khối: `refineryRules` (danh sách quy tắc), `weights`
(trọng số chấm điểm), `testOutput` (kết quả chạy thử), `cleanRows` (bản ghi sạch theo ID), `memory`
(trí nhớ tạm), `agentParams` (tham số agent). Sếp đã yêu cầu **TUYỆT ĐỐI KHÔNG bịa dữ liệu giả** —
vì vậy nhiệm vụ của ticket này là dựng ĐÚNG khung/cấu trúc/style trực quan như mockup, nhưng **mọi
khối liệt kê ở trên đều phải hiển thị trạng thái RỖNG TRUNG THỰC** (không phải 1-2 dòng ví dụ minh hoạ,
mà là thông báo rõ ràng "Chưa có dữ liệu thật — chờ nối API [tên tính năng]"), TRỪ PHI bạn tìm thấy
API thật sau khi tự grep kỹ (`grep -rn` trong `heo_harness/core/` và `heo_harness/plugins/`) — nếu tìm
thấy thật thì dùng thật, ghi rõ trong HANDOFF-10.md đã tìm thấy nguồn nào.

File mockup: `docs/design-reference/claude-design-export/Gen-Harness Console.dc.html`
- `isRules`: dòng 511-616 (khối `<sc-if value="{{ isRules }}">`)
- `isClean`: dòng 617-717 (khối `<sc-if value="{{ isClean }}">`)

File chính cần sửa: `heo_harness/plugins/ui_dashboard/dashboard.html`. Hàm hiện tại `renderDataFactoryHub()`
(dòng ~10793) đang gộp chung raw/rules/clean — Kỹ sư trưởng vừa tách phần `raw` ra dùng dữ liệu thật
qua `state.df_events`. Bạn cần thêm phần xử lý cho subtab `rules` và `clean` (dùng `state.subtabs.data_factory`
hoặc tương tự cơ chế subtab đã có ở các hub khác như `directory`/`zalo` để biết đang xem subtab nào).

## Việc cần làm
1. Đọc kỹ 2 khối mockup nêu trên, trích cấu trúc HTML/CSS gần như nguyên văn.
2. Với TỪNG khối dữ liệu con (`refineryRules`, `weights`, `testOutput`, `cleanRows`, `memory`,
   `agentParams`): grep tìm API/state thật tương ứng. Nếu không có, dùng mảng RỖNG `[]` và hiển thị
   thông báo rỗng trung thực (tham khảo cách Kỹ sư trưởng đã làm ở `renderDataFactoryHub` phần raw:
   `triggerConfig.length === 0 ? '<div>Chưa có dữ liệu thật...</div>' : ...`).
3. Nút "Chạy thử trên 100 bản ghi", "Thêm quy tắc", ô "Chạy thử một bản ghi" trong mockup: đây là
   TÍNH NĂNG MỚI chưa có backend — để nút hiển thị nhưng khi bấm hiện thông báo rõ ràng
   `showToast('Tính năng này chưa nối API thật, sẽ triển khai ở ticket sau.')`, KHÔNG giả lập kết quả giả.
4. Giữ đúng style Nocturne (biến CSS `var(--color-*)`, font-size, radius) khớp mockup — không dùng lại
   class cũ (`card`, `btn sm`, `data-table`...).
5. `./doctor.sh` phải pass 100% sau khi sửa (đã bao gồm chạy test suite).

## TUYỆT ĐỐI KHÔNG
- KHÔNG bịa bất kỳ số liệu/tên/nội dung mẫu nào (kể cả 1 dòng ví dụ) cho các khối chưa có API thật.
- KHÔNG tự thêm `rules`/`clean` vào `NAV`/`NAV_MAP`/`TITLES`/sidebar — Kỹ sư trưởng sẽ tự kiểm tra bằng
  ảnh chụp và thêm vào nav SAU KHI xác nhận đạt yêu cầu. Ghi rõ trong HANDOFF-10.md rằng đã dựng xong
  hàm render nhưng CHƯA nối vào nav, cần Kỹ sư trưởng duyệt trước.
- Không đổi plugin ID, kiến trúc core, định danh tác quyền, API contract hiện có.
- Không tự push remote / mở PR / merge vào `main`.

## Quy trình bàn giao
- Commit riêng cho từng màn (`rules` rồi `clean`).
- Ghi `docs/design-reference/HANDOFF-10.md`: liệt kê rõ khối nào có API thật (nêu tên API), khối nào
  để rỗng trung thực. Dòng CUỐI CÙNG in ra màn hình phải bắt đầu CHÍNH XÁC bằng `[BÀN GIAO]`.
- Bế tắc quá 3 lần cho cùng vấn đề: dừng lại, ghi rõ vào HANDOFF-10.md, không đào sâu vô hạn.
