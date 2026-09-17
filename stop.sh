#!/usr/bin/env bash
# Dừng Heo-Harness an toàn
pkill -f "python3 -m heo_harness.app" 2>/dev/null || pkill -f "heo_harness" 2>/dev/null || true
echo "✔ Đã gửi tín hiệu dừng Heo-Harness an toàn."
