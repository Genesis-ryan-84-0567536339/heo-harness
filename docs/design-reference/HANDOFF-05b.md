# BÁO CÁO BÀN GIAO TICKET 05b — MCP HUB + MODULES + DATA FACTORY

**Thời gian:** 2026-09-23 01:33:00 +07:00  
**Tác giả sáng lập & Kỹ sư trưởng:** Anh Cơ La (Ryan) — `genesis.corp.os@gmail.com`  
**Nhánh:** `feature/gen-harness-screen-mcp-modules`  
**File sửa đổi chính:** `heo_harness/plugins/ui_dashboard/dashboard.html`

---

## 1. TỔNG QUAN CÔNG VIỆC ĐÃ HOÀN THÀNH

Thực hiện chuẩn hóa hoàn thiện 3 màn hình thuộc nhóm **"MÁY"** theo đúng SSOT `docs/design-reference/Gen-Harness-Product-Spec-LOCKED.md` (Mục E2, E12, F2 mục 10) và thiết kế xuất xưởng `docs/design-reference/claude-design-export/Gen-Harness Console.dc.html`, áp dụng bộ design tokens Nocturne (`#232532`, `rgba(233,233,237,0.16)`, `#e9e9ed`, `#9184d9`, monospace font cho số liệu / ID):

### 1.1. Màn hình 1: `modules` — Plugin & Tiện ích (`renderModulesHub()`)
- **Bảo toàn ID kỹ thuật 100%:** Giữ nguyên vẹn toàn bộ các plugin ID kỹ thuật nội bộ (`heo-ui-dashboard-executive`, `heo-provider-antigravity-brain`, `heo-auth-rbac-security`, `heo-policy-gate-firewall`, `heo-channel-zalo-gateway`, `heo-channel-whatsapp-gateway`, `heo-provider-gemini-orchestrator`, `heo-provider-deepseek-reasoning`, `heo-persona-heo-attitude`, `heo-tool-media-processor`, `heo-tool-office-reporter`) hiển thị chuẩn monospace font, không bị đổi tên hay gắn mác sai quy chuẩn.
- **5 KPI cards Nocturne:** Plugin nền DSH (7), Plugin cài thêm (4), Đang suy giảm (0), Bị cách ly (0), Tác quyền sáng lập (Anh Cơ La).
- **Subnav Tabs chuẩn Nocturne:** `Plugin đang nạp`, `Kỹ năng nghiệp vụ (8)`, `Chợ tiện ích (6)`.
- **Bảng Plugin chuẩn F2:** Đầy đủ các cột: Plugin (icon + tên + ID), Tầng (chassis/provider/channel/tool/ui/persona), Phiên bản, Nguồn, Sandbox (thanh RAM + dung lượng MB), Ngắt mạch (Circuit Breaker), Trạng thái (Khoẻ mạnh / Suy giảm / Đang tắt), Bật (Toggle switch).
- **Khóa an toàn Plugin nền:** Bốn plugin sống còn của khung gầm (`heo-auth-rbac-security`, `heo-policy-gate-firewall`, `heo-provider-antigravity-brain`, `heo-ui-dashboard-executive`) hiển thị icon khóa `ph-lock-simple` với switch làm mờ (opacity 0.55), không thể tắt để tránh sập chassis.
- **Bố cục 2 cột tầng dưới:**
  - Cột 1: Thứ tự nạp & phụ thuộc (`Load order · plugin sau phụ thuộc plugin trước`) từ 01 tới 07 với độ trễ nạp (ms).
  - Cột 2: Nhật ký vòng đời plugin (`Lifecycle log`) với các sự kiện HEALTH, LOAD, DEGRADE, RECOVER, UPDATE, DISABLE.
- **Kỹ năng nghiệp vụ & Chợ tiện ích:** Chuyển đổi toàn bộ thẻ Executive Skills và Marketplace Catalog sang thẻ Nocturne.

### 1.2. Màn hình 2: `mcp_connectors` — Kho Ứng Dụng MCP Hub (`renderMcpConnectorsHub()`)
- **Header & 4 KPI cards:** Máy chủ đã kết nối (5/7), Công cụ đã mở (23 tool), Lượt gọi 24h (1.482 lượt), Độ trễ p95 (620 ms).
- **Subnav Tabs:** Máy chủ kết nối (5), Kho ứng dụng 1-Click (14), Cấu hình MCP tùy chỉnh.
- **Thẻ máy chủ mở rộng (Expandable Server Cards):** Viền trái màu 2px (`border-left`), icon hộp 28x28, tên máy chủ, badge trạng thái, transport (`stdio` / `http+sse`), số liệu gọi 24h & độ trễ p95, switch gạt nóng. Khi mở rộng hiển thị endpoint, chip công cụ (icon mắt cho read, icon bút cho write kèm tooltip cảnh báo), chip agent được phép gọi (`ph-robot`).
- **Bố cục 2 cột tầng dưới:**
  - Cột trái: Bảng nhật ký gọi MCP (`LIVE` dot xanh đập nhịp) với các trường Lúc, Agent, Công cụ, Tham số & kết quả, Thời gian, Kết quả (OK, Chờ duyệt, Bị chặn, Lỗi).
  - Cột phải: Hộp Ranh giới gọi ra ngoài (`Guardrails`) với 4 switch bảo vệ + Hộp Chợ máy chủ MCP kết nối nhanh (PostgreSQL, Notion, Brave, Playwright).
- **Bộ lọc & Custom Builder:** Thanh tìm kiếm đa tiêu chí theo danh mục/trạng thái và form tạo máy chủ MCP tùy chỉnh (stdio/sse) chuẩn Nocturne.

### 1.3. Màn hình 3: `data_factory` — Data Factory (`renderDataFactoryHub()`)
- **Header & 4 KPI cards:** Bản ghi thô 24h (18.412), Sự kiện nguyên tử (24), Cơ hội phát hiện (8), Tỷ lệ tin cậy (94.2%).
- **Thanh lọc chuẩn Nocturne (Filter Pills):** Kênh, Nhóm, Trạng thái, Thời gian, Nhãn (AskedPrice, Complained, v.v.).
- **Bảng luồng sự kiện nguyên tử thời gian thực:** Cột Lúc, Kênh (icon Zalo/WhatsApp), ID nhóm, ID người, Nội dung thô, Phân loại Taxonomy, Tin cậy (đổi màu theo ngưỡng), Trạng thái kho sạch.
- **Bảng điều khiển kích hoạt sàng lọc (Trigger Refinery):** 4 thanh tiến trình theo chu kỳ thời gian (mỗi 15 phút), ngưỡng số lượng (500 bản ghi), số bản ghi mỗi lượt, ngưỡng tin cậy vào kho sạch (>= 0.60).
- **Bảng phụ trợ:** Thô theo nhóm nguồn (kèm thanh tỷ lệ) và Danh sách chu kỳ gần nhất (Refinery runs).

---

## 2. KẾT QUẢ KIỂM THỬ & KIỂM TRA CHẤT LƯỢNG

1. **`./doctor.sh`:**
   - 16/16 tiêu chuẩn SSOT: VƯỢT QUA 100% (Core Chassis, V6 UI, Policy Engine, AGY Core & Zalo).
   - Tác quyền Anh Cơ La (`genesis.corp.os@gmail.com`): Hợp lệ 100%.
2. **`python3 -m unittest discover -s tests`:**
   - 53/53 tests: PASS 100% (thời gian chạy: 74.566s).
3. **Thương hiệu & An toàn kiến trúc:**
   - Đã rà soát sạch các cụm thương hiệu hệ thống cũ ("Heo-Harness", "HEO OS") trong tiêu đề / mô tả giao diện hiển thị thành "Gen-Harness" / "Genesis Harness OS".
   - Tuyệt đối không thay đổi bất kỳ plugin ID kỹ thuật nào (`heo-*`).
   - Giữ nguyên định danh tác quyền, module Python và API contract.

---

## 3. LỊCH SỬ COMMITS ĐÃ TẠO

- `11947b6`: `feat(ui): update modules and skills hub with Nocturne tokens per Spec F2`
- `4d2310d`: `feat(ui): update mcp connectors hub with Nocturne tokens per Spec F2`
- `92a932e`: `feat(ui): update data factory hub with Nocturne tokens per Spec F2`

---

## 4. TỒN ĐỌNG / BƯỚC TIẾP THEO

- Toàn bộ yêu cầu của TICKET 05b đã hoàn thành trọn vẹn 100%. Không có vấn đề bế tắc.
- Sẵn sàng chuyển giao hoặc tiếp tục các ticket kế tiếp theo chỉ đạo của Sếp.

[BÀN GIAO]
