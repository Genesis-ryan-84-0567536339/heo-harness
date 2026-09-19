#!/usr/bin/env bash
# ==============================================================================
# HEO-HARNESS: Script Khởi Chạy Hệ Thống Điều Hành V6 (Hỗ trợ Docker & Local)
# Tác giả: Anh Cơ La (genesis.corp.os@gmail.com)
# ==============================================================================
set -e

SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do
    DIR="$(cd -P "$(dirname "$SOURCE")" && pwd)"
    SOURCE="$(readlink "$SOURCE")"
    [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE"
done
BASE_DIR="$(cd -P "$(dirname "$SOURCE")" && pwd)"
cd "$BASE_DIR"

MODE="${1:-docker}"

echo "🐷 [Heo-Harness] Khởi Động V6 Executive Intelligence OS..."
echo "🌐 Bảng Điều Khiển Web & Kho Add-ins: http://127.0.0.1:5088"

if [ "$MODE" = "local" ]; then
    echo "⚡ Chế độ: Khởi chạy trực tiếp (Local Python Mode)..."
    export HARNESS_PORT=5088
    export PYTHONPATH="$BASE_DIR:${PYTHONPATH:-}"
    exec python3 -m heo_harness.app
else
    echo "🐳 Chế độ: Khởi chạy Container Docker / Podman độc lập (Container: heo-harness-executive)..."
    
    # Ưu tiên docker compose hoặc podman compose
    if command -v docker &>/dev/null; then
        docker compose up -d --build
    elif command -v podman-compose &>/dev/null; then
        podman-compose up -d
    else
        echo "⚠️ Không tìm thấy docker/podman compose. Tự động chuyển sang chế độ Local Python..."
        export HARNESS_PORT=5088
        export PYTHONPATH="$BASE_DIR:${PYTHONPATH:-}"
        exec python3 -m heo_harness.app
    fi
    
    echo "✔ Container 'heo-harness-executive' đã chạy ngầm thành công!"
    echo "👉 Truy cập ngay: http://127.0.0.1:5088"
fi
