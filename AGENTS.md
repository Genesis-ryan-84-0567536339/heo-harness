# HEO-HARNESS: AGENT GUIDELINES & DSH DEVELOPMENT STANDARDS

Tác giả: **Anh Cơ La (Ryan)** — `genesis.corp.os@gmail.com`

Mọi AI coding assistant khi làm việc trong dự án này phải tuân theo các chỉ dẫn sau:

## 1. NGUYÊN TẮC DSH
- Triết lý cốt lõi: "Everything is a Plugin".
- Base class: `BasePlugin` trong `heo_harness/core/plugin.py`.
- Service Sharing: Qua `Context` (`ctx.provide`, `ctx.get`, `ctx.inject`).
- Asynchronous Events: Qua `EventBus` (`bus.emit`, `bus.on`, `bus.apply_hook`).
- Error Handling: Bắt buộc dùng `safe_execute` hoặc Error Boundary kèm `CircuitBreaker`.

## 2. QUY CHUẨN ĐẶT TÊN PLUGIN
- **Công thức:** `heo-<tên plugin>-<chức năng>`
- Ví dụ:
  - `heo-provider-antigravity-brain`
  - `heo-channel-zalo-gateway`
  - `heo-policy-gate-firewall`
  - `heo-persona-heo-attitude`
  - `heo-auth-rbac-security`
  - `heo-tool-media-processor`
  - `heo-tool-office-reporter`
  - `heo-ui-dashboard-executive`

## 3. MÔ HÌNH VÀ TÁC QUYỀN
- Core Agent mặc định: Google Antigravity CLI gói tháng (0đ API token).
- Secondary: DeepSeek V3/R1 (Mặc định TẮT).
- Tác quyền duy nhất: Anh Cơ La.
