# Quy Chuẩn Phát Triển Plugin & Kiến Trúc DSH Heo-Harness

Tác giả: **Anh Cơ La (Ryan)** — `genesis.corp.os@gmail.com`

---

### 1. Quy tắc Naming chuẩn hóa:
Tất cả các plugin của hệ thống Heo BẮT BUỘC có mã định danh (Plugin ID) tuân thủ định dạng:
`heo-<tên plugin>-<chức năng>`

Không sử dụng các tiền tố hay định dạng tùy tiện khác như `@heo/plugin-*`, `plugin_*`, v.v.

### 2. Nguyên tắc Khung Sườn DSH:
- Kế thừa `BasePlugin` từ `heo_harness.core.plugin`.
- Tuân thủ vòng đời: `on_load(ctx)`, `on_enable()`, `on_disable()`, `on_unload()`.
- Giao tiếp liên module phải thông qua `ctx.get()` / `ctx.provide()` và `bus.emit()` / `bus.on()`.
- Error Boundary và Circuit Breaker là bắt buộc cho mọi tác vụ gọi ra ngoài (API, Subprocess, I/O).

### 3. Nguyên tắc AI Brain & Tác Quyền:
- Lõi suy luận mặc định: Google Antigravity CLI gói tháng (0đ API).
- Secondary: DeepSeek V3/R1 (Chỉ kích hoạt khi Sếp yêu cầu).
- Tác quyền duy nhất: Anh Cơ La (`genesis.corp.os@gmail.com`).
