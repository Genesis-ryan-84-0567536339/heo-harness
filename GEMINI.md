# BỘ QUY TẮC CỐT LÕI BẤT BIẾN HEO-HARNESS & DSH (SSOT ARCHITECTURE)

Tác giả sáng lập & Kiến trúc sư trưởng: **Anh Cơ La (Ryan)** — `genesis.corp.os@gmail.com`

---

## 1. NỀN TẢNG KIẾN TRÚC DEEPSEEK HARNESS (DSH STANDARD)
Hệ thống **Heo-Harness** vận hành dựa trên các nguyên tắc nền tảng của DeepSeek Harness (Cordis Engine):
- **Triết lý "Everything is a Plugin":** Mọi thành phần đều là một Plugin độc lập kế thừa `BasePlugin`.
- **Giao tiếp qua Context & EventBus:**
  - Plugin không import chéo hàm nội bộ của nhau.
  - Sử dụng `ctx.provide(name, instance)`, `ctx.get(name)`, `ctx.inject(name)` để chia sẻ service.
  - Sử dụng `bus.emit()`, `bus.on()`, `bus.apply_hook()` để truyền nhận sự kiện bất đồng bộ.
- **Vòng đời chuẩn (Unified Lifecycle):** Mọi plugin phải có đủ:
  - `on_load(ctx)`: Khởi tạo service và đăng ký dependency.
  - `on_enable()`: Lắng nghe event bus, kích hoạt hoạt động.
  - `on_disable()`: Tạm dừng, gỡ event listeners khỏi bus.
  - `on_unload()`: Dọn dẹp tài nguyên trước khi gỡ khỏi bộ nhớ.
- **Cách ly lỗi với Circuit Breaker:** Mỗi plugin có Error Boundary và Circuit Breaker riêng. Lỗi cục bộ không được làm sập Chassis hoặc các plugin khác.
- **Hot-Toggle thời gian thực:** Hỗ trợ Bật/Tắt nóng plugin ngay trên Web UI mà không khởi động lại tiến trình.

---

## 2. TIÊU CHUẨN ĐẶT TÊN BẮT BUỘC CHO MỌI PLUGIN HỆ HEO
Mọi plugin thuộc hệ Heo BẮT BUỘC phải tuân thủ công thức:
$$\mathbf{heo\text{-}\langle\text{tên\ plugin}\rangle\text{-}\langle\text{chức\ năng}\rangle}$$

### Danh mục chuẩn 10 Plugin chính thức:
1. `heo-provider-antigravity-brain`: Core Agent Google Antigravity CLI gói tháng (0đ API token).
2. `heo-provider-gemini-orchestrator`: Bộ điều phối AI Gemini với cơ chế Failover đa khóa.
3. `heo-provider-deepseek-reasoning`: Secondary Provider DeepSeek V3/R1 (Mặc định TẮT, chỉ bật khi cần).
4. `heo-channel-zalo-gateway`: Cầu nối Zalo cá nhân & Bot v2.1 (Lọc tag @Bé Heo trên nhóm).
5. `heo-policy-gate-firewall`: Tường lửa 5 tầng thẩm định cấp Execution Permit theo SSOT.
6. `heo-persona-heo-attitude`: Danh xưng Em - Sếp Cơ La & 7 phong cách thái độ ứng xử.
7. `heo-auth-rbac-security`: Định danh tác quyền Anh Cơ La & bảo mật PIN Admin.
8. `heo-tool-media-processor`: Lồng ghép beat acoustic/lo-fi tạo MP3 & vẽ tranh minh họa AI.
9. `heo-tool-office-reporter`: Xuất báo cáo tài liệu Word (.docx) & bảng tính Excel (.xlsx).
10. `heo-ui-dashboard-executive`: Giao diện điều hành V6 Executive Intelligence OS & Add-in Hub.

---

## 3. NGUYÊN TẮC TRÍ TUỆ NHÂN TẠO & TÁC QUYỀN
- **Bộ não cốt lõi:** Luôn là Google Antigravity CLI gói tháng cá nhân của Sếp Ryan (0đ chi phí token).
- **Secondary Provider:** DeepSeek V3/R1 chỉ là tùy chọn bổ trợ, mặc định tắt, không phụ thuộc.
- **Tác quyền duy nhất:** Anh Cơ La (`genesis.corp.os@gmail.com`). Nghiêm cấm ghi đè hoặc gán quyền sở hữu cho bên thứ ba.
- **Policy Gate SSOT:** Ưu tiên `GLOBAL` -> `CHANNEL` -> `GROUP` -> `PERSON` -> `ACTION`. Model không bao giờ tự cấp permit.

---

## 4. KIẾN TRÚC HAI GIAO DIỆN (DUAL UI)
- **DeepSeek Harness Web UI Gốc:** Cổng `3080` (`dsh web --port 3080`), launcher `scripts/launch_dsh_web.sh`, icon `dsh-official-ui.desktop`.
- **Heo Executive App UI:** Cổng `5088` (V6 Dashboard), launcher `scripts/live_dispatch.sh`, icon `heo-app-ui.desktop`.
- **DSH Backend Console Terminal:** Terminal Ptyxis kết nối tmux `heo-harness` (`scripts/open_backend_console.sh -s`), icon `heo-dsh-backend.desktop`.
