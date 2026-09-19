#!/usr/bin/env bash
# ==============================================================================
# HEO-HARNESS CONTAINER ENTRYPOINT
# Tác giả: Anh Cơ La (genesis.corp.os@gmail.com)
# ==============================================================================
set -e

ACTION="${1:-run}"

case "$ACTION" in
    run|daemon)
        echo "🐷 [Heo-Harness Docker] Đang khởi động V6 Executive OS trong container..."
        export HARNESS_PORT="${HARNESS_PORT:-5088}"
        export PYTHONPATH="/app:${PYTHONPATH:-}"
        exec python3 -m heo_harness.app
        ;;
    doctor|check)
        echo "🩺 [Heo-Harness Docker] Đang chạy chẩn đoán sức khỏe..."
        exec bash /app/doctor.sh
        ;;
    test)
        echo "🧪 [Heo-Harness Docker] Đang chạy kiểm thử tích hợp 16 tiêu chuẩn..."
        export PYTHONPATH="/app:${PYTHONPATH:-}"
        exec python3 -m unittest discover -s /app/tests -v
        ;;
    bash|sh)
        exec /bin/bash
        ;;
    *)
        exec "$@"
        ;;
esac
