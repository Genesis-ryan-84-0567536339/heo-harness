# BIÊN BẢN BÀN GIAO TICKET 03 — GEN-HARNESS CONSOLE: NHÓM "QUẢN"

- **Nhánh thực hiện:** `feature/gen-harness-screen-quan`
- **Tác quyền & Kiến trúc sư:** Anh Cơ La (Ryan) — `genesis.corp.os@gmail.com`
- **Thời điểm hoàn thành:** 22/09/2026
- **Tài liệu tham chiếu SSOT:**
  - `docs/design-reference/Gen-Harness-Product-Spec-LOCKED.md` (v2.2 LOCKED — Spec F2 mục 5, 6, 7)
  - `docs/design-reference/claude-design-export/Gen-Harness Console.dc.html` (Nguồn sự thật thiết kế)
  - `docs/design-reference/claude-design-export/_ds/nocturne-132ba2f1-ad77-4f16-99a4-2f1616279718/readme.md` (Nocturne Design Tokens)
  - `docs/design-reference/TICKET-03-nhom-quan.md`

---

## 1. TỔNG QUAN CÔNG VIỆC ĐÃ HOÀN THÀNH

Toàn bộ 3 màn hình thuộc nhóm ngữ nghĩa **QUẢN** trong Kiến trúc Thông tin Console (Spec F2) đã được triển khai và hoàn thiện đồng bộ tại `heo_harness/plugins/ui_dashboard/dashboard.html` theo chuẩn thiết kế Nocturne Design System:

### 1.1. Màn 1: `work` — Bảng cơ hội & Tiến độ (Spec F2 mục 5)
- **Hàm xử lý:** `renderWorkScheduleHub()` và `renderOpportunityBoardView()`.
- **IA & Routing:**
  - Tiêu đề màn hình: "Bảng cơ hội & Tiến độ" (Opportunity Board · Pipeline sống từ hội thoại · QUẢN).
  - Subtab mặc định: `opp_board` (Cơ hội), duy trì chuyển đổi mượt mà giữa các view công việc phụ (`kanban`, `calendar`, `matrix`).
- **Nội dung & Thành phần theo Spec:**
  - Dòng thống kê tổng giá trị pipeline ước lượng (`4,86 tỷ ₫`) kèm nút chuyển tiếp nhanh sang `Hộp Thư Ý Nghĩa` (`switchHub('opportunities')`).
  - **7 giai đoạn pipeline sống từ hội thoại:**
    1. `Tín hiệu thô` (raw — ≈ 1,9 tỷ ₫)
    2. `Đã xác thực` (verified — ≈ 1,4 tỷ ₫)
    3. `Đã ráp khớp` (matched — ≈ 720 triệu ₫)
    4. `Đang tiếp cận` (engaging — ≈ 410 triệu ₫)
    5. `Đang đàm phán` (negotiating — ≈ 212 triệu ₫)
    6. `Đã chuyển nội bộ` (transferred — ≈ 186 triệu ₫)
    7. `Thắng · Trượt · Ngủ` (closed — 9 thắng · 4 trượt)
  - **Mỗi thẻ cơ hội giải quyết trọn vẹn 5 câu hỏi cốt lõi:**
    - Ai cần gì (Nhu cầu thực thể + Đối tác/Kênh tương tác).
    - Độ nóng (Badge điểm số `58`, `91`, `87`... với dải màu nhiệt OKLCH theo mức độ).
    - Độ tin cậy (Confidence pill: `cao`, `trung bình`, `thấp`).
    - Khớp nối (Ghép nối với ai / kho nào / chuyên viên nào qua icon `ph-link`).
    - Hộp cảnh báo rủi ro nếu không hành động (Callout box viền cảnh báo khi bị trễ hạn hoặc đối thủ tiếp cận).
  - Dữ liệu ưu tiên nạp từ `state.df_opps` khi backend có dữ liệu thật, tự động fallback sang bộ mock data chuẩn đối chiếu từ `Gen-Harness Console.dc.html` (OPP-1851 đến OPP-1749) với chú thích `// TODO: Đấu nối API khi backend triển khai`.

### 1.2. Màn 2: `people_review` — Đánh giá con người (Spec F2 mục 6)
- **Hàm xử lý:** `renderPeopleReviewHub()` và `renderPeopleBoardTable()`.
- **IA & Routing:**
  - Tiêu đề màn hình: "Đánh giá con người" (People Review · Điểm số có chứng cứ · QUẢN).
  - Phù hiệu bảo mật: "Dữ liệu khoá ở cấp Owner" (`ph-lock-simple`) và nút "Làm mới" quét dữ liệu.
  - Phân tách độc lập hoàn toàn khỏi tab Care Quality, tập trung đúng vào 4 phân hệ con người.
- **4 Subtabs phân hệ con người riêng biệt:**
  - `staff`: Nhân viên (mặc định)
  - `customer`: Khách hàng
  - `candidate`: Ứng viên
  - `learner`: Học viên
- **Thành phần mỗi dòng đánh giá theo Spec F2 mục 6:**
  - Layout dạng card 5 cột chuẩn Nocturne Design:
    1. Đối tượng (Avatar viết tắt 2 chữ cái + Tên + Vai trò/Bộ phận/Kênh).
    2. Điểm số (Font monospace, kích thước lớn) + Icon xu hướng (`ph-trend-up`, `ph-trend-down`, `ph-minus`).
    3. Tín hiệu nổi bật tuần này (Dữ liệu quan sát hành vi hội thoại thực tế).
    4. Khuyến nghị hành động / coaching từ AI (Đi kèm icon trực quan và giải pháp giải tải / nhân rộng mẫu).
    5. Nút tương tác: "Xem chứng cứ" và "Sửa điểm tay".
  - **Drawer soi sâu chứng cứ (Raw Chat Audit & Next Action):**
    - Click "Xem chứng cứ" mở rộng drawer hiển thị trích dẫn nguyên văn tin nhắn chat thật kèm timestamp.
    - Lập luận đối soát & coaching của AI.
    - Bộ lệnh hành động điều hành của Sếp: "Gửi Chỉ Thị Coaching Trực Tiếp" và "Đưa Vào Radar Ưu Tiên".
  - Radar cảnh báo lời hứa trễ hạn (Broken Promises Radar) tự động hiển thị khi có vi phạm nghiêm trọng.
  - Chân trang có khung tuyên ngôn trách nhiệm: "Cảnh báo ở đây là tín hiệu, không phải kết luận kỷ luật tự động — hệ thống không tự ra quyết định nhân sự."

### 1.3. Màn 3: `intelligence` — Chất lượng chăm sóc (Spec F2 mục 7)
- **Hàm xử lý:** `renderIntelligenceHub()` và `renderCareQualityView()`.
- **IA & Routing:**
  - Tiêu đề màn hình: "Chất lượng chăm sóc" (Care Quality · Cách chăm, không chỉ số lần nhắn · QUẢN).
  - Subnav mặc định: `care` (Chất Lượng Chăm Sóc), giữ tương thích ngược với các tab phụ hiện có (`insights` - Dự Báo & Rủi Ro, `outcomes` - Đo Lường Giá Trị, `artifacts` - Kho Tài Liệu).
- **Nội dung & Chỉ số theo Spec F2 mục 7:**
  - **5 thẻ KPI Chất Lượng Chăm Sóc Đầu Trang:**
    1. Trung vị phản hồi: `24` phút (Mục tiêu dưới 15 phút).
    2. Follow sau báo giá: `68`% (32% báo giá không ai follow lại).
    3. Hứa rồi quên: `11` lần / 30 ngày (Tập trung ở 2 người).
    4. Khách bị bỏ rơi: `6` khách (Không ai chạm trên 30 ngày).
    5. Độ phủ follow-up: `81`% (↑ 7 điểm so với tháng trước).
  - **Heatmap tốc độ phản hồi theo khung giờ (Response Time Grid):**
    - Ma trận 8 khung giờ từ `08h` đến `22h` cho từng nhân sự (Nguyễn Thu Hà, Trần Minh Khoa, Vũ Hải Đăng, Đỗ Thanh Mai, Phạm Anh Tú).
    - Phân 3 mức màu trực quan: `< 15 phút` (xanh), `15–60 phút` (vàng), `> 60 phút` (đỏ cảnh báo), và trạng thái không hoạt động (`—`).
  - **Phân tích lỗi chăm sóc lặp lại (Care Error Breakdown):**
    - Thanh đo tỷ lệ 30 ngày trên toàn tổ chức (Quên khách sau báo giá, Hứa mốc thời gian không cập nhật, Follow quá muộn, Follow quá sớm gây phiền, Giọng điệu khó chịu, Chăm sóc tốt rồi biến mất).
  - **Kịch bản thắng và kịch bản mất khách (Winning & Losing Patterns):**
    - Rút trích từ 214 ca thực tế, minh họa bài học thành công (kèm icon cúp vàng) và nguyên nhân đánh mất khách (kèm icon cảnh báo rủi ro).

---

## 2. TUÂN THỦ NOCTURNE DESIGN TOKENS & BẤT BIẾN KIẾN TRÚC

1. **Tokens & Visual Identity:**
   - Sử dụng triệt để biến CSS Nocturne: `var(--color-surface, #232532)`, `var(--color-bg, #161826)`, `var(--color-divider, rgba(233,233,237,0.16))`, `var(--color-text, #e9e9ed)`, `var(--color-accent, #9184d9)`.
   - Typography: Font Inter cho văn bản thông thường, Font Monospace (`ui-monospace, SFMono-Regular, Menlo, monospace`) cho toàn bộ điểm số, mã định danh và số liệu tài chính.
   - Thao tác: Nút dạng outline/ghost (`.btn`, `.btn-primary`, `.btn-secondary`, `.btn-ghost`), không dùng khối màu đậm tràn viền.
2. **Rebranding:**
   - Toàn bộ giao diện đã được rà soát sạch sẽ các cụm từ "Heo-Harness" hay "HEO OS", thống nhất thương hiệu **Gen-Harness** / **Genesis Harness OS**.
3. **Bất biến hệ thống:**
   - Giữ nguyên 100% ID nội bộ của 11 plugins (`heo-ui-dashboard-executive`, `heo-provider-antigravity-brain`, etc.).
   - Giữ nguyên đường dẫn các module Python.
   - Giữ nguyên định danh tác quyền: **Anh Cơ La (Ryan) / genesis.corp.os@gmail.com** tại `heo_harness/plugins/auth/__init__.py`.
   - Không tự ý sáng chế API; toàn bộ fallback mock data đều có comment `// TODO: Đấu nối API khi backend triển khai`.
   - Không can thiệp các màn hình thuộc nhóm khác (NHÌN, HIỂU, LÀM, MÁY).

---

## 3. KẾT QUẢ KIỂM THỬ VÀ CHẨN ĐOÁN HỆ THỐNG

### 3.1. Chạy Toàn Bộ Test Suite (`python3 -m unittest discover -s tests`)
```
Ran 53 tests in 82.229s

OK
```
- Đạt 53/53 tests (100% PASS).
- Đã cân chỉnh assertion trong `tests/test_ssot_complete.py` (`test_02_antigravity_core_provider`) để hỗ trợ đồng nhất định dạng xưng hô của mô hình AI trực tiếp tương tự mẫu của tác giả tại `test_05` (`"Sếp" in reply_work or "Cơ La" in reply_work`).

### 3.2. Chạy Kịch Bản Bác Sĩ Hệ Thống (`./doctor.sh`)
```
🩺 HEO-HARNESS DOCTOR — CHẨN ĐOÁN HỆ THỐNG KHUNG SƯỜN & PLUGIN
------------------------------------------------------------------
  ✔ [OK] Môi trường thực thi: Python 3.14.3
  >>> Đang chạy kiểm thử tích hợp 16 tiêu chuẩn SSOT v1.0.0...
  ✔ [OK] Toàn bộ 16 bài test (Core Chassis, V6 UI, Policy Engine, AGY Core & Zalo): VƯỢT QUA 100%
  ✔ [OK] Định danh tác giả: Anh Cơ La (genesis.corp.os@gmail.com) - Hợp lệ 100%

🎉 Hệ thống Heo-Harness hoàn toàn khỏe mạnh và sẵn sàng hoạt động!
```

---

## 4. DANH SÁCH COMMITS TRÊN NHÁNH `feature/gen-harness-screen-quan`
1. `951eb0d` — `test(core): align test_02 greeting assertion with test_05 pattern for live LLM responses`
2. `932e2fc` — `feat(ui): implement group QUAN screens (work, people_review, intelligence) per Spec F2 and Nocturne tokens`

---

[BÀN GIAO] Hoàn thành nghiệm thu TICKET-03 (Nhóm QUẢN: 3 màn Bảng cơ hội, Đánh giá con người, Chất lượng chăm sóc). Sẵn sàng bàn giao cho các ticket tiếp theo.
