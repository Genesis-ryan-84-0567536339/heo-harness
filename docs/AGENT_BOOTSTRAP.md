# QUY TẮC BOOTSTRAP & SỔ NHẬT KÝ BÀN GIAO AGENT (AGENT HANDOVER LEDGER)

> **CẤP ĐỘ HIỆU LỰC:** BẮT BUỘC (MANDATORY SSOT RULE)  
> **ÁP DỤNG CHO:** Mọi AI Agent tham gia thiết kế, lập trình, kiểm thử và vận hành dự án Gen-Harness (Heo OS).  
> **TÁC QUYỀN DUY NHẤT:** Anh Cơ La (Ryan) — `genesis.corp.os@gmail.com`  
> **MỤC TIÊU TOÀN CỤC (SSOT GOAL):** Tuân thủ tuyệt đối [Gen-Harness-Product-Spec-LOCKED.md](../docs/Gen-Harness-Product-Spec-LOCKED.md) (v2.2 LOCKED).

---

## 1. ĐIỀU KHOẢN CỐT LÕI (THE GOLDEN RULE)

Mọi AI Agent khi thực hiện bất kỳ lượt xây dựng, nâng cấp hoặc sửa đổi mã nguồn nào:

> **TRƯỚC KHI in báo cáo hoàn tất ra màn hình CLI cho Sếp Ryan, BẮT BUỘC PHẢI GHI NHẬT KÝ BÀN GIAO vào hệ thống Ledger.**

Việc này đảm bảo:
1. **Duy trì liên tục bối cảnh**: Phiên sau hoặc agent khác khi được kích hoạt sẽ lập tức đọc nhật ký gần nhất và nắm bắt ngay công việc đang dang dở mà không tốn token quét lại từ đầu.
2. **Bảo toàn mục tiêu toàn cục (SSOT Goal)**: Không bị trôi mục tiêu, không đi lệch khỏi 45 tiêu chuẩn của bản Spec LOCKED v2.2.
3. **Minh bạch & Trách nhiệm**: Mọi thay đổi đều được ký nhận mã phiên, danh sách tệp thay đổi, tiêu chí SPEC hoàn thành và kết quả kiểm thử.

---

## 2. PHƯƠNG THỨC GHI NHẬT KÝ

AI Agent có thể ghi nhật ký bằng một trong hai cách:

### Cách 1: Ghi trực tiếp vào file JSON (Ưu tiên khi làm việc offline/CLI)
Mở tệp `data/agent_build_logs.json` và chèn bản ghi mới vào cuối mảng JSON, sau đó đồng bộ sang thư mục song song:
`/home/ryan/Documents/Ryan-Workplace/Heo-Harness/data/agent_build_logs.json`

### Cách 2: Gọi API nội bộ qua HTTP (Khuyên dùng khi Web Dashboard đang chạy)
Gửi yêu cầu HTTP POST tới cổng 5088:
```http
POST /api/builder/logs HTTP/1.1
Host: 127.0.0.1:5088
Content-Type: application/json

{
  "agent_name": "Antigravity Executive Agent",
  "milestone": "MS-2, MS-3",
  "title": "Triển khai Conversation Data Factory & Opportunity Kanban",
  "summary": "Tóm tắt súc tích theo cấu trúc BLUF & MECE...",
  "specs_completed": ["SPEC-06", "SPEC-07", "SPEC-08"],
  "files_modified": [
    "heo_harness/core/data_factory.py",
    "tests/test_data_factory_milestones.py"
  ],
  "verification_status": "./doctor.sh PASS 100% (16/16 tests) + 22 unit tests PASS",
  "next_agent_instructions": "Chỉ dẫn chi tiết cho phiên tiếp theo..."
}
```

### Cách 3: Thao tác trực quan trên giao diện Builder OS
Truy cập `http://127.0.0.1:5088/builder` ➔ Chuyển sang Tab **"📝 Nhật Ký Thi Công Agent"** ➔ Bấm **"+ Thêm Nhật Ký Mới"** ➔ Điền biểu mẫu và bấm **"Lưu Nhật Ký & Đồng Bộ SSOT"**.

---

## 3. CẤU TRÚC BẢN GHI NHẬT KÝ CHUẨN

Mỗi bản ghi trong `data/agent_build_logs.json` bắt buộc có các trường sau:

| Trường | Kiểu dữ liệu | Ý nghĩa & Quy chuẩn |
| :--- | :--- | :--- |
| `id` | String | Mã định danh dạng `BUILD-YYYYMMDD-XX` (ví dụ: `BUILD-20260921-03`). |
| `timestamp` | String | Thời gian thực thi `YYYY-MM-DD HH:MM:SS`. |
| `agent_name` | String | Tên định danh agent (ví dụ: `Antigravity Executive Agent`). |
| `milestone` | String | Chặng thi công tương ứng (`MS-1`, `MS-2`, `MS-3`, `MS-4`, `MS-5` hoặc kết hợp). |
| `title` | String | Tiêu đề tóm tắt ngắn gọn của phiên xây dựng (Headline). |
| `summary` | String | Báo cáo súc tích những gì đã làm theo phong thái **BLUF & MECE**. |
| `specs_completed`| Array[String] | Danh sách các mã SPEC từ bản Spec LOCKED đã hoàn thiện (ví dụ: `["SPEC-06", "SPEC-07"]`). |
| `files_modified` | Array[String] | Danh sách các tệp mã nguồn, tài liệu đã tạo mới hoặc chỉnh sửa. |
| `verification_status` | String | Kết quả kiểm thử thực tế. Bắt buộc: `./doctor.sh PASS 100% (16/16 tests)` kèm unit tests. |
| `next_agent_instructions`| String | **CỰC KỲ QUAN TRỌNG:** Lời dặn dò, lưu ý kỹ thuật, tệp cần xử lý tiếp theo và các việc ưu tiên hàng đầu cho AI Agent ca sau. |

---

## 4. QUY TRÌNH TIẾP QUẢN CA (AGENT HANDOVER WORKFLOW)

Khi một AI Agent mới bắt đầu phiên làm việc:

1. **Bước 1 — Đọc Nhật Ký Gần Nhất**:
   Kiểm tra phần tử cuối cùng trong `data/agent_build_logs.json` hoặc mở giao diện `http://127.0.0.1:5088/builder` (Tab Nhật Ký).
2. **Bước 2 — Tiếp Nhận Chỉ Dẫn (`next_agent_instructions`)**:
   Đọc kỹ lời dặn bàn giao của agent tiền nhiệm để nắm ngay hiện trạng mã nguồn, các điểm nghẽn (blockers) và nhiệm vụ tiếp nối.
3. **Bước 3 — Đối Chiếu SSOT**:
   Tra cứu mã SPEC tương ứng trong `docs/Gen-Harness-Product-Spec-LOCKED.md` để đảm bảo thực thi đúng đặc tả.
4. **Bước 4 — Thi Công & Kiểm Thử**:
   Thực thi mã nguồn, tuân thủ nguyên tắc "Everything is a Plugin". Chạy `./doctor.sh` đảm bảo luôn **PASS 100%**.
5. **Bước 5 — Ghi Nhật Ký Bàn Giao**:
   Ghi nhận lượt thi công vào Ledger trước khi báo cáo kết quả lên CLI cho Sếp Ryan.
