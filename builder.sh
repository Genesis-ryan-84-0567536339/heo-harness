#!/usr/bin/env bash
# ==============================================================================
# GEN-HARNESS BUILDER: Mở Giao Diện Lập Kế Hoạch & Quản Trị Tiến Độ Thi Công
# Tham chiếu SSOT Goal: Gen-Harness-Product-Spec-LOCKED.md
# Tác giả: Anh Cơ La (genesis.corp.os@gmail.com)
# ==============================================================================
set -e

URL="http://127.0.0.1:5088/builder"

echo "🛠️ [Gen-Harness Builder] Đang mở giao diện Lập Kế Hoạch & Quản Trị Thi Công..."
echo "🌐 URL: $URL"

if command -v xdg-open &>/dev/null; then
    xdg-open "$URL" &>/dev/null &
elif command -v google-chrome &>/dev/null; then
    google-chrome "$URL" &>/dev/null &
elif command -v firefox &>/dev/null; then
    firefox "$URL" &>/dev/null &
else
    echo "👉 Vui lòng mở trình duyệt và truy cập: $URL"
fi

echo "✔ Đã gửi lệnh mở giao diện Builder!"
