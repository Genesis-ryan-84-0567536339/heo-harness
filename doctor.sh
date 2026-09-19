#!/usr/bin/env bash
# ==============================================================================
# HEO-HARNESS DOCTOR: Chẩn đoán sức khỏe khung gầm & toàn vẹn Plugin
# Tác giả: Anh Cơ La (genesis.corp.os@gmail.com)
# ==============================================================================
set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "\n${CYAN}🩺 HEO-HARNESS DOCTOR — CHẨN ĐOÁN HỆ THỐNG KHUNG SƯỜN & PLUGIN${NC}"
echo "------------------------------------------------------------------"

# 1. Kiểm tra Python
if command -v python3 &>/dev/null; then
    PY_VER="$(python3 --version)"
    echo -e "  ${GREEN}✔ [OK]${NC} Môi trường thực thi: $PY_VER"
else
    echo -e "  ${RED}✖ [ERR]${NC} Thiếu python3"
    exit 1
fi

# 2. Kiểm tra Toàn Bộ Unit Test & Kiến Trúc SSOT
echo -e "  ${CYAN}>>> Đang chạy kiểm thử tích hợp 16 tiêu chuẩn SSOT v1.0.0...${NC}"
if python3 -m unittest discover -s tests &>/dev/null; then
    echo -e "  ${GREEN}✔ [OK]${NC} Toàn bộ 16 bài test (Core Chassis, V6 UI, Policy Engine, AGY Core & Zalo): VƯỢT QUA 100%"
else
    echo -e "  ${RED}✖ [ERR]${NC} Phát hiện lỗi trong bài kiểm thử hệ thống!"
    exit 1
fi

# 3. Kiểm tra Tác Quyền Bất Biến
AUTH_FILE="heo_harness/plugins/auth/__init__.py"
if grep -q "Anh Cơ La" "$AUTH_FILE" && grep -q "genesis.corp.os@gmail.com" "$AUTH_FILE"; then
    echo -e "  ${GREEN}✔ [OK]${NC} Định danh tác giả: Anh Cơ La (genesis.corp.os@gmail.com) - Hợp lệ 100%"
else
    echo -e "  ${RED}✖ [ERR]${NC} Định danh tác giả bị thay đổi trái phép!"
    exit 1
fi

echo -e "\n${GREEN}🎉 Hệ thống Heo-Harness hoàn toàn khỏe mạnh và sẵn sàng hoạt động!${NC}\n"
