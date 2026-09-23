# TICKET 09b — DỰNG LẠI TỪNG MÀN 1, LẤY NGUYÊN HTML TỪ MOCKUP LÀM CHUẨN (Nhóm B)

## Bối cảnh — ĐỌC KỸ, ĐÂY LÀ THAY ĐỔI PHƯƠNG PHÁP LÀM VIỆC
Các ticket trước (01-08) cho agy "đối chiếu" file thiết kế rồi tự viết lại markup — dẫn tới sai lệch
nhiều chỗ (thiếu thành phần, không giống 100%). **Từ ticket này trở đi, cách làm đổi hẳn**: file
`docs/design-reference/claude-design-export/Gen-Harness Console.dc.html` là NGUỒN DUY NHẤT — với mỗi
màn, phải **trích đúng khối HTML tương ứng trong file đó và dùng gần như nguyên văn**, chỉ chuyển đổi
cú pháp template (`{{ biến }}`, `sc-if`, `sc-for`) sang cách dựng chuỗi HTML JS đang dùng trong
`dashboard.html` hiện tại, **KHÔNG được viết lại/diễn giải lại bằng ý hiểu riêng**. Giữ đúng cấu
trúc/class/style của mockup, không đơn giản hoá hay bỏ bớt.

Có ticket 09a làm song song phần còn lại trên worktree khác — KHÔNG đụng tới các hub ngoài bảng dưới
đây để tránh xung đột khi gộp lại sau.

## Bảng các khối màn hình cần dựng (đọc dòng trong file mockup)

| Dòng bắt đầu | Khối mockup | Hub trong dashboard.html |
|---|---|---|
| 1252 | isSupply | `workbench` (Cung↔Cầu) |
| 1551 | isSearch | `chat_intelligence` |
| 1649 | isOpportunity | `work` |
| 1704 | isPeople | `people_review` |
| 1763 | isCare | `intelligence` |
| 1852 | isWorkbench (mockup gọi là "Bàn làm việc") | `workbench_action` |
| 1953 | isAgents | `assistant` |
| 2038 | isApi | CHƯA có màn — thêm subtab mới vào `assistant` |
| 2157 | isPlugins (khung chung) | `modules` |
| 2189 | isPlugList | subtab `modules` |
| 2303 | isPlugMarket | subtab `modules` |
| 2329 | isMcp | `mcp_connectors` |
| 2495 | isSystem (khung chung, còn nhiều subtab bên dưới — đọc tiếp tới hết file hoặc hết phần `<sc-if>` liên quan) | `governance` |

## Việc cần làm — LÀM LẦN LƯỢT TỪNG DÒNG TRONG BẢNG, THEO ĐÚNG THỨ TỰ
Với MỖI khối:
1. Đọc đúng đoạn HTML trong file mockup (từ dòng bắt đầu tới hết khối, tới `<sc-if>` tiếp theo).
2. Mở hàm `render*Hub()` tương ứng, thay markup hiện tại bằng bản chuyển thể sát nguyên văn từ mockup.
3. Chỗ mockup dùng `{{ x }}`/`sc-for` với dữ liệu mẫu → thay bằng biến/API thật đã có (đối chiếu
   `docs/design-reference/AUDIT-DU-LIEU-THAT-GIA-08b.md` nếu ticket 08b đã tạo ra file này). Chưa có
   nguồn thật thì để trạng thái rỗng trung thực (không bịa số), đánh dấu `// TODO`. Với `zalo`/
   `whatsapp` (không có trong bảng vì đã tương đối tốt) — nếu tiện thì đối chiếu luôn nhưng không bắt
   buộc trong ticket này.
4. **Tự kiểm tra bằng ảnh chụp thật** trước khi coi màn đó xong:
   ```
   fuser -k 5299/tcp 2>/dev/null; sleep 1
   cd <thư mục hiện tại> && HARNESS_PORT=5299 PYTHONPATH="$PWD" nohup python3 -m heo_harness.app > /tmp/preview-09b.log 2>&1 &
   sleep 5
   google-chrome --headless --disable-gpu --no-sandbox --window-size=1600,1000 \
     --screenshot=/tmp/screen_<ten_hub>.png "http://127.0.0.1:5299/#/<hub>"
   ```
   So khớp từng thành phần vừa dựng với HTML mockup gốc — xác nhận đủ thành phần, đúng bố cục trước
   khi qua màn tiếp theo.
5. Commit riêng cho từng màn xong, rồi mới sang dòng tiếp theo.
6. Sau khi xong TOÀN BỘ bảng: `./doctor.sh` phải pass 100% (đã bao gồm chạy test suite, không cần chạy
   thêm `unittest discover` riêng).

## Giữ nguyên tuyệt đối
- Plugin ID nội bộ, đường dẫn module Python, định danh tác quyền (`heo_harness/plugins/auth/__init__.py`
  — TUYỆT ĐỐI không đụng), API contract hiện có.
- Sidebar/header đã đúng từ ticket 07 — không đụng lại, chỉ đụng nội dung BÊN TRONG từng màn trong bảng.

## KHÔNG làm trong đợt này
- Không đụng các hub ngoài bảng trên (thuộc ticket 09a, worktree khác).
- Không tự chế API mới phức tạp, không tự push remote / mở PR / merge vào `main`.

## Quy trình bàn giao
- Chưa xong hết bảng khi hết giờ/quota: ghi rõ vào `docs/design-reference/HANDOFF-09b.md` đã xong tới
  đâu, còn lại gì.
- Xong hết bảng: ghi tổng kết vào `docs/design-reference/HANDOFF-09b.md`, dòng CUỐI CÙNG in ra màn hình
  phải bắt đầu CHÍNH XÁC bằng `[BÀN GIAO]`.
- Bế tắc quá 3 lần cho cùng 1 màn: ghi rõ vào HANDOFF-09b.md, chuyển màn tiếp theo, không đào sâu vô hạn.
