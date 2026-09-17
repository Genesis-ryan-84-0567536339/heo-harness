#!/usr/bin/env bash
# ==============================================================================
# HEO-HARNESS: Script khởi chạy nhanh Khung sườn AI Agent
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

echo "🐷 Đang khởi chạy Heo-Harness (Khung sườn Modular AI Agent)..."
echo "🌐 Bảng điều khiển Web Console & Kho Plugin: http://localhost:5066"

export PYTHONPATH="$BASE_DIR:${PYTHONPATH:-}"
python3 -m heo_harness.app
