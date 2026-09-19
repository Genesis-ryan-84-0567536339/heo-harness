#!/usr/bin/env bash
# ==============================================================================
# HEO-HARNESS: Script Dừng Hệ Thống An Toàn
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

echo "🛑 Đang dừng Heo-Harness..."

# 1. Dừng container nếu đang chạy
if command -v docker &>/dev/null; then
    docker compose down 2>/dev/null || true
elif command -v podman-compose &>/dev/null; then
    podman-compose down 2>/dev/null || true
fi

# 2. Dừng process local nếu có
pkill -f "python3 -m heo_harness.app" 2>/dev/null || pkill -f "heo_harness" 2>/dev/null || true

echo "✔ Đã dừng toàn bộ Heo-Harness an toàn."
