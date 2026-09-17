# 🐷 HEO-HARNESS (BÉ HEO CHASSIS)

<div align="center">

[![Tác giả](https://img.shields.io/badge/tác_giả-Anh_Cơ_La-purple.svg)](mailto:genesis.corp.os@gmail.com)
[![Phiên bản](https://img.shields.io/badge/phiên_bản-v3.0.0--alpha.1-blue.svg)](https://github.com/Genesis-ryan-84-0567536339/heo-harness)
[![Kiến trúc](https://img.shields.io/badge/kiến_trúc-DeepSeek_Harness_Chassis-pink.svg)](https://github.com/Genesis-ryan-84-0567536339/heo-harness)
[![Bảo mật](https://img.shields.io/badge/cách_ly_lỗi-Circuit_Breaker-emerald.svg)](https://github.com/Genesis-ryan-84-0567536339/heo-harness)
[![Giấy phép](https://img.shields.io/badge/giấy_phép-MIT-green.svg)](LICENSE)

**Khung Sườn AI Agent Runtime Siêu Nhẹ Theo Triết Lý "Everything is a Plugin" (Lấy Cảm Hứng Từ DeepSeek Harness & Cordis Meta-Framework)**

</div>

---

## 🌟 1. Giới Thiệu Tổng Quan

**Heo-Harness** là thế hệ kiến trúc tiếp theo (Next-Generation AI Agent Runtime) trực thuộc hệ sinh thái **Genesis Corp OS**, được sáng lập và phát triển độc lập bởi tác giả **Anh Cơ La (Ryan)**.

Khác với các hệ thống AI bot nguyên khối (Monolithic), Heo-Harness áp dụng triết lý cốt lõi của **DeepSeek Harness (`dsh`)**:
> **"Everything is a Plugin" (Tất cả mọi thứ đều là Plugin)**: Từ Cổng kết nối (Channels), Mô hình (LLMs), Kỹ năng (Tools), Giao diện (UI Web Console) cho đến các Core Agents đều là những module độc lập cắm rút trên một khung sườn (Chassis) siêu nhẹ.

### 🛡️ Nguyên Tắc Cách Ly Lỗi Tuyệt Đối (Circuit Breaker & Error Boundary):
* Mỗi plugin hoạt động trong một **vùng cách ly an toàn**.
* Nếu một plugin mới bị lỗi, crash hay rò rỉ bộ nhớ -> **Lỗi chỉ cô lập bên trong đúng plugin đó**.
* Hệ thống Chassis tự động ngắt mạch an toàn (**Circuit Breaker**), toàn bộ bot Zalo, AI Engine và các tính năng khác **vẫn chạy bình thường 24/7**, không bao giờ bị "lỗi lây"!
* Người dùng có thể **Bật / Tắt / Gỡ bỏ nóng** bất kỳ plugin nào chỉ với 1 cú click ngay trên Bảng điều khiển Web Console.

---

## 📦 2. Bộ 7 Plugin Mặc Định Cài Sẵn (Official Built-in Plugins)

Khi khởi động Heo-Harness lần đầu, hệ thống tự động kích hoạt bộ 7 Plugin chính thức:

| STT | Tên Plugin | Định Danh ID | Danh Mục | Mô Tả Chức Năng |
| :-: | :--- | :--- | :---: | :--- |
| **1** | **Định Danh Tác Quyền & PIN** | `@heo/plugin-auth` | `core` | Bảo vệ bất biến tác quyền sáng lập **Anh Cơ La** (`genesis.corp.os@gmail.com`), quản lý Admin PIN. |
| **2** | **Danh Xưng & 7 Persona** | `@heo/plugin-persona` | `core` | Quản lý danh xưng Sếp Cơ La, tên bot, vai trò `bot_about` và 7 phong cách thái độ (Mặc định, Nghiêm túc, Dẻo miệng, Chuyên nghiệp, Cọc cằn, Troll, Custom). |
| **3** | **Điều Phối AI Gemini** | `@heo/provider-gemini` | `provider` | Core Agent Google AGY CLI / Gemini API với cơ chế tự động xoay vòng đa Key khi hết quota (Failover). |
| **4** | **Cầu Nối Zalo 2 Chiều** | `@heo/channel-zalo` | `channel` | Đăng nhập QR Code, lắng nghe tin nhắn, **chỉ phản hồi khi được @tag tên** trên nhóm Zalo. |
| **5** | **Sáng Tạo Media** | `@heo/tool-media` | `tool` | Kỹ năng lồng ghép beat nhạc acoustic/lo-fi tạo bài hát MP3 hoàn chỉnh và vẽ tranh minh họa AI. |
| **6** | **Tài Liệu Văn Phòng** | `@heo/tool-office` | `tool` | Xuất file báo cáo tài liệu Word (`.docx`) và bảng tính phân tích Excel (`.xlsx`) chuẩn hành chính. |
| **7** | **Web Console & Kho Plugin** | `@heo/ui-dashboard` | `ui` | Bảng điều khiển Web Console HCS (cổng 5066) tích hợp **Kho Plugin Marketplace & Manager**. |

---

## 🛒 3. Kho Plugin Trên Web UI (Plugin Store & Manager)

Truy cập Bảng điều khiển tại: `http://localhost:5066` -> Chọn mục **🧩 Kho Plugin & Tiện Ích**:
1. **Phân khu "Đã Cài Đặt" (Installed):**
   - Xem toàn bộ danh sách plugin đang chạy trên hệ thống.
   - Thẻ theo dõi sức khỏe: `Khỏe Mạnh (Healthy)`, `Cảnh Báo (Degraded)`, `Ngắt Mạch (Error)`.
   - Công tắc **Bật / Tắt Nóng** tức thì (không cần khởi động lại server).
   - Nút **Xem Log Riêng** của từng plugin để chẩn đoán lỗi độc lập.
2. **Phân khu "Chợ Tiện Ích" (Marketplace Catalog):**
   - Danh sách các Core Agent và Plugin mở rộng sẵn sàng cài đặt:
     - 👨‍💻 `@heo/agent-coder`: Core Agent chuyên gia lập trình & gỡ lỗi.
     - 📈 `@heo/agent-finance`: Core Agent cố vấn tài chính & thị trường.
     - ✈️ `@heo/channel-telegram`: Kênh tương tác Telegram Bot song song.
     - 🌐 `@heo/channel-webhook`: Cổng Webhook tự động hóa doanh nghiệp.
     - 📓 `@heo/tool-notion-sync`: Đồng bộ ghi chú & to-do list sang Notion.
     - 🪙 `@heo/tool-crypto-rates`: Theo dõi biến động giá Crypto & Vàng realtime.
   - Nút **`[+ Cài Đặt 1-Click]`** tự động tích hợp ngay vào hệ thống.

---

## 🚀 4. Hướng Dẫn Khởi Chạy

### Cách 1: Chạy trực tiếp bằng Python
```bash
# Cài đặt các gói phụ thuộc
pip install -e .

# Khởi chạy Chassis và Web Console
heo-harness start
```

### Cách 2: Chạy kiểm tra trạng thái và Plugin qua CLI
```bash
# Xem trạng thái hệ thống
heo-harness status

# Xem danh sách plugin đã nạp
heo-harness plugin list

# Tắt tạm thời 1 plugin (Ví dụ tắt plugin media)
heo-harness plugin disable @heo/tool-media

# Bật lại plugin
heo-harness plugin enable @heo/tool-media
```

---

## ✍️ 5. Hướng Dẫn Tự Viết Một Plugin Mới (Trong 1 Phút)

Tạo một tệp Python kế thừa từ `BasePlugin`:

```python
from heo_harness.core.plugin import BasePlugin, PluginMetadata, PluginCategory

class MyCustomPlugin(BasePlugin):
    metadata = PluginMetadata(
        id="@custom/my-tool",
        name="Công Cụ Tùy Biến Của Tôi",
        version="1.0.0",
        author="Anh Cơ La",
        category=PluginCategory.TOOL,
        description="Plugin ví dụ minh họa cách cắm rút vào Heo-Harness",
        icon="⚡"
    )

    def on_enable(self):
        self.log("Plugin tùy biến đã được kích hoạt!")
        # Lắng nghe sự kiện từ EventBus
        self.bus.on("zalo:message_received", self.on_message)

    def on_message(self, msg_data):
        # Thực thi logic an toàn có bọc Circuit Breaker
        self.safe_execute(self._handle, msg_data)

    def _handle(self, msg_data):
        self.log(f"Nhận tin nhắn: {msg_data.get('content')}")
```

---

## ⚖️ 6. Tác Quyền & Giấy Phép Bất Biến

* **Tác giả sáng lập & Kiến trúc sư trưởng duy nhất:** **Anh Cơ La (Ryan)** — Email: `genesis.corp.os@gmail.com`.
* Mọi hành vi sửa đổi, phủ nhận hoặc xóa bỏ định danh tác giả Anh Cơ La trong bất kỳ phiên bản nào đều bị nghiêm cấm theo chính sách bản quyền Genesis Corp OS.
* Giấy phép phân phối: MIT License.
