#!/usr/bin/env bash
# ==============================================================================
# Script: setup_bridge.sh
# Tự động kiểm tra môi trường Node.js và cài đặt dependencies cho Zalo Bridge
# HEO-HARNESS V6 SSOT - Tác giả: Anh Cơ La (genesis.corp.os@gmail.com)
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
BRIDGE_DIR="$BASE_DIR/bridge"

echo "🔍 Đang kiểm tra môi trường Node.js cho Heo-Harness Zalo Bridge..."

if ! command -v node >/dev/null 2>&1; then
    echo "❌ LỖI: Chưa tìm thấy 'node' trong PATH!"
    echo "👉 Vui lòng cài đặt Node.js (phiên bản khuyến nghị >= 18 hoặc 20):"
    echo "   curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -"
    echo "   sudo apt-get install -y nodejs"
    exit 1
fi

NODE_VER=$(node -v)
echo "✅ Đã tìm thấy Node.js ($NODE_VER)"

if ! command -v npm >/dev/null 2>&1; then
    echo "❌ LỖI: Chưa tìm thấy 'npm' trong PATH!"
    exit 1
fi

echo "📦 Đang cài đặt thư viện cho Zalo Bridge tại: $BRIDGE_DIR"
cd "$BRIDGE_DIR"

if [ ! -d "node_modules" ] || [ ! -d "node_modules/zca-js" ]; then
    npm install --no-audit --no-fund
    echo "✅ Đã cài đặt xong dependencies cho Zalo Bridge!"
else
    echo "✅ Dependencies (zca-js) đã sẵn sàng!"
fi

echo "🚀 Zalo Bridge đã sẵn sàng hoạt động cùng Heo-Harness!"
