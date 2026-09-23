# BÁO CÁO BÀN GIAO TICKET 08a
## Kiểm kê & Dọn dữ liệu giả: Nhóm KINH DOANH (Phần NHÌN + HIỂU)

**Kính gửi:** Anh Cơ La (Ryan) — `genesis.corp.os@gmail.com`  
**Nhánh Git:** `feature/gen-harness-audit-du-lieu-08a`  
**Trạng thái:** HOÀN THÀNH 100% (Passed 53/53 Unit Tests)  
**Thời gian hoàn thành:** 2026-09-23  

---

## 1. TÓM TẮT KẾT QUẢ THỰC HIỆN

Chúng tôi đã hoàn thành kiểm kê toàn diện và dọn sạch 100% dữ liệu mẫu, số liệu bịa đặt trên toàn bộ 8 màn hình/hub thuộc Domain Kinh doanh (`command`, `opportunities`, `workbench_action`, `directory`, `relationship_radar`, `work`, `workbench`, `chat_intelligence`):

1. **Lập bảng kiểm kê dữ liệu thật - giả:** Đã lưu trữ tài liệu chuẩn tại [`docs/design-reference/AUDIT-DU-LIEU-THAT-GIA.md`](docs/design-reference/AUDIT-DU-LIEU-THAT-GIA.md) theo cấu trúc yêu cầu: `| Màn hình | Khối/thành phần | THẬT hay GIẢ | Ghi chú (API nào, hay lý do chưa có API) |`.
2. **Tổng hợp khối kiểm kê:**
   - **Tổng số khối được kiểm tra:** 33 khối thành phần trên 8 màn hình.
   - **Số khối THẬT (nối API hoặc tính toán từ state thật):** 20 khối (60.6%).
   - **Số khối GIẢ (hardcode mẫu, số liệu mẫu):** 13 khối (39.4%).
3. **Xử lý triệt để 13 khối GIẢ:**
   - **Đã chuyển đổi sang dữ liệu THẬT (7 khối):**
     - `command`: KPI "Cần xử lý ngay" (tính từ `state.attention.length` và phân bổ band P1/P2/P3 từ `/api/attention/list`).
     - `command`: KPI "Tín hiệu cơ hội mới" (tính từ `state.df_opps.length` qua `/api/data_factory/opportunities`).
     - `command`: KPI "Quan hệ đang lạnh" (tính từ `state.df_contacts` có `went_silent_days > 7`).
     - `command`: KPI "Nhóm đang nóng" (tính từ `state.groups.length` và `state.df_events.length`).
     - `command`: Hàng đợi cần xử lý (Attention Queue) nối từ `state.attention` thật từ `/api/attention/list`.
     - `command`: 5 đối tượng đáng chú ý lấy từ `state.df_contacts` / `state.people` thật.
     - `work`: Pipeline ước lượng và giá trị từng cột trong Bảng cơ hội tính tổng động từ `state.df_opps`.
     - `relationship_radar`: Badge số lượng node theo phân nhóm cập nhật động từ `rawNodes` của API `/api/relationship/graph`.
   - **Đã xoá sạch mảng dữ liệu mẫu quy mô lớn (2 khối):**
     - `opportunities`: Xoá sạch 28 thẻ mẫu `CANONICAL_MEANING_ITEMS` (460 dòng mock data), chuyển sang 100% hiển thị sự kiện thật từ `state.df_events` qua `mapLiveEventToMeaningItem` và empty state "Inbox Zero".
     - `work`: Xoá sạch mảng 11 cơ hội giả `mockOpps` ("Xưởng gỗ Bình Dương", "OPP-1851"...), hiển thị cơ hội thật từ `state.df_opps`.
   - **Thay bằng trạng thái rỗng trung thực (3 khối chưa có API backend):**
     - `command`: Khối "Chủ đề đang nổi" ➔ *Chưa có dữ liệu thật — chờ nối API /api/market/signals*.
     - `command`: Khối "Chất lượng dữ liệu" ➔ *Chưa có dữ liệu thật — chờ nối API /api/system/dci*.
     - `command`: Khối "Nhiệt kế hoạt động" ➔ *Chưa có dữ liệu thật — chờ nối API /api/events/hourly_distribution*.
   - **Giữ nguyên placeholder trung thực (1 khối):**
     - `workbench_action`: *Chưa có dữ liệu thật — chờ nối API /api/workbench/actions, sẽ triển khai ở ticket sau*.

---

## 2. KẾT QUẢ KIỂM THỬ HỆ THỐNG
Chạy lệnh kiểm thử đơn vị độc lập:
```bash
python3 -m unittest discover -s tests
```
**Kết quả:**
- `Ran 53 tests in 143.430s`
- **OK** (100% pass, 0 fail, 0 error).

---

## 3. DANH SÁCH COMMITS ĐÃ THỰC HIỆN
1. `8b91163` - `docs: create comprehensive data audit table AUDIT-DU-LIEU-THAT-GIA.md`
2. `fb3a3bc` - `fix(ui): eliminate fake mock data and connect real state in kinh doanh hubs`
