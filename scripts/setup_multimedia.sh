#!/usr/bin/env bash
# ==============================================================================
# Script: setup_multimedia.sh
# Thiết lập toàn diện bộ công cụ Đa Phương Tiện (TTS, STT, AI Image, Audio Producer)
# cho hệ sinh thái HEO-HARNESS
# Tác giả: Anh Cơ La (genesis.corp.os@gmail.com)
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"

echo "🎵 [Heo-Harness] Bắt đầu thiết lập gói Đa Phương Tiện (TTS, STT, AI Art)..."

# 1. Kiểm tra ffmpeg
if command -v ffmpeg >/dev/null 2>&1; then
    echo "✅ Đã tìm thấy ffmpeg: $(ffmpeg -version | head -n 1)"
else
    echo "⚠️ ffmpeg chưa được cài đặt. Vui lòng cài ffmpeg để hòa âm beat nhạc:"
    echo "   sudo apt-get install -y ffmpeg (hoặc sudo dnf install -y ffmpeg)"
fi

# 2. Kiểm tra Node.js và node-edge-tts
if command -v node >/dev/null 2>&1; then
    echo "✅ Đã tìm thấy Node.js: $(node -v)"
    # Cài đặt node-edge-tts vào bridge nếu chưa có
    if [ -f "$BASE_DIR/bridge/package.json" ]; then
        cd "$BASE_DIR/bridge"
        if ! node -e "require('node-edge-tts')" >/dev/null 2>&1; then
            echo "📦 Đang cài đặt node-edge-tts vào bridge/..."
            npm install --save node-edge-tts --no-audit --no-fund || true
        fi
        echo "✅ Thư viện TTS (Microsoft Edge Neural) đã sẵn sàng!"
    fi
fi

# 3. Kiểm tra các beat nhạc mẫu
if [ -d "$BASE_DIR/data/beats" ] && [ "$(ls -A "$BASE_DIR/data/beats" 2>/dev/null)" ]; then
    echo "✅ Thư viện beat âm nhạc acoustic/happy đã sẵn sàng!"
else
    echo "⚠️ Chưa tìm thấy beats trong data/beats. Đang sao chép..."
    mkdir -p "$BASE_DIR/data/beats"
    if [ -d "/home/ryan/heo-agent/data/beats" ]; then
        cp -r /home/ryan/heo-agent/data/beats/* "$BASE_DIR/data/beats/" || true
    fi
fi

echo "🎉 [Heo-Harness] Hoàn tất thiết lập bộ công cụ Đa Phương Tiện!"
