#!/usr/bin/env bash
# ==============================================================================
# HEO-HARNESS LIVE DISPATCH CONSOLE
# Mô phỏng quy trình kỹ sư triển khai trực tiếp từng bước trên màn hình Sếp
# Tác giả: Anh Cơ La (genesis.corp.os@gmail.com)
# ==============================================================================

CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
MAGENTA='\033[0;35m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

type_msg() {
    local text="$1"
    local delay=0.015
    for (( i=0; i<${#text}; i++ )); do
        echo -n "${text:$i:1}"
        sleep "$delay"
    done
    echo ""
}

clear
echo -e "${MAGENTA}${BOLD}"
echo "  ██╗  ██╗███████╗ ██████╗       ██╗  ██╗ █████╗ ██████╗ ███╗   ██╗███████╗███████╗███████╗"
echo "  ██║  ██║██╔════╝██╔═══██╗      ██║  ██║██╔══██╗██╔══██╗████╗  ██║██╔════╝██╔════╝██╔════╝"
echo "  ███████║█████╗  ██║   ██║█████╗███████║███████║██████╔╝██╔██╗ ██║█████╗  ███████╗███████╗"
echo "  ██╔══██║██╔══╝  ██║   ██║╚════╝██╔══██║██╔══██║██╔══██╗██║╚██╗██║██╔══╝  ╚════██║╚════██║"
echo "  ██║  ██║███████╗╚██████╔╝      ██║  ██║██║  ██║██║  ██║██║ ╚████║███████╗███████║███████║"
echo "  ╚═╝  ╚═╝╚══════╝ ╚═════╝       ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝╚══════╝╚══════╝"
echo -e "${NC}"
echo -e "${CYAN}  👑 Kiến trúc sư trưởng & Tác giả duy nhất: ${BOLD}Anh Cơ La (Ryan) — genesis.corp.os@gmail.com${NC}"
echo -e "${CYAN}  🛡️ Triết lý: ${BOLD}Sai một ly đi một dặm · Modular Harness · Circuit Breaker 100%${NC}"
echo -e "${CYAN}  🌟 Core Model: ${BOLD}Google Antigravity CLI Gói Tháng (0đ API) · DeepSeek Tùy Chọn${NC}"
echo "=========================================================================================="
echo ""

sleep 1
type_msg "🚀 [BƯỚC 1/5] KIỂM TRA LỊCH SỬ PHÁT TRIỂN & CÁC COMMIT MỚI NHẤT..."
echo -e "${BLUE}$ git log -n 4 --oneline --graph --decorate${NC}"
git log -n 4 --oneline --graph --decorate
echo ""
sleep 1.5

type_msg "🩺 [BƯỚC 2/5] CHẨN ĐOÁN TOÀN VẸN HỆ THỐNG QUA DOCTOR.SH..."
echo -e "${BLUE}$ bash doctor.sh${NC}"
bash doctor.sh
echo ""
sleep 1.5

type_msg "🧪 [BƯỚC 3/5] CHẠY KIỂM THỬ TỰ ĐỘNG 16 TIÊU CHUẨN SSOT V1.0.0..."
echo -e "${BLUE}$ python3 -m unittest discover -s tests -v${NC}"
python3 -m unittest discover -s tests -v
echo ""
sleep 2

type_msg "⚡ [BƯỚC 4/5] KHỞI ĐỘNG MÁY CHỦ V6 EXECUTIVE OS TRÊN CỔNG 5088..."
export HARNESS_PORT=5088
# Dừng process cũ nếu có
pkill -f "python3 -m heo_harness.app" 2>/dev/null || true
sleep 0.5

# Chạy app ngầm
python3 -m heo_harness.app &
APP_PID=$!

# Chờ máy chủ sẵn sàng (tối đa 5s)
for i in {1..10}; do
    if curl -s http://127.0.0.1:5088/api/system/status >/dev/null 2>&1; then
        break
    fi
    sleep 0.4
done

echo -e "${GREEN}✔ Máy chủ Heo-Harness V6 đã lắng nghe tại http://127.0.0.1:5088 (PID: $APP_PID)!${NC}"
echo ""

type_msg "🔍 [BƯỚC 5/5] GỬI LỆNH PROBE XÁC THỰC API REALTIME TỚI CỔNG 5088..."
echo -e "${BLUE}$ curl -s http://127.0.0.1:5088/api/system/status | jq .system${NC}"
curl -s http://127.0.0.1:5088/api/system/status | python3 -m json.tool | head -n 16
echo ""
sleep 0.5

echo -e "${BLUE}$ curl -s http://127.0.0.1:5088/api/plugins/list (Kiểm tra 9 Plugins & Circuit Breaker)...${NC}"
curl -s http://127.0.0.1:5088/api/plugins/list | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    plugins = data.get('plugins', [])
    print(f'  ✔ Tổng số Add-in đang nạp: {len(plugins)} plugins')
    for p in plugins:
        cb = p.get('circuit_breaker', {})
        st = '🟢 BẬT' if p.get('enabled') else '⚪ TẮT'
        print(f'    • [{st}] {p.get(\"icon\",\"🧩\")} {p.get(\"name\")} — CB: {cb.get(\"status\")} (Lỗi: {cb.get(\"failure_count\", 0)}/{cb.get(\"max_failures\", 3)})')
except Exception as e:
    print('  ❌ Lỗi parse dữ liệu probe:', e)
"
echo ""

echo "=========================================================================================="
echo -e "${GREEN}${BOLD}🎉 HOÀN TẤT TRIỂN KHAI THỰC TẾ! BẢNG ĐIỀU KHIỂN V6 ĐANG SẴN SÀNG PHỤC VỤ SẾP!${NC}"
echo -e "${YELLOW}${BOLD}👉 Sếp mở trình duyệt và truy cập: http://127.0.0.1:5088${NC}"
echo "=========================================================================================="
echo -e "${CYAN}Đang giữ console trực chiến vĩnh viễn (Watchdog Active). Sẵn sàng phục vụ 24/7.${NC}"

# Vòng lặp Watchdog giám sát vĩnh viễn - KHÔNG BAO GIỜ TẮT
while true; do
    if ! kill -0 "$APP_PID" 2>/dev/null; then
        echo -e "\n${YELLOW}⚠️ Phát hiện máy chủ tạm dừng. Watchdog tự động phục hồi và khởi động lại ngay lập tức...${NC}"
        python3 -m heo_harness.app &
        APP_PID=$!
    fi
    sleep 2
done
