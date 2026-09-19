#!/usr/bin/env bash
# ==============================================================================
# HEO-HARNESS: LAUNCHER DEEPSEEK HARNESS (DSH) OFFICIAL WEB UI
# Cổng mặc định: 3080
# ==============================================================================

export PATH="/home/ryan/.nvm/versions/node/v24.21.0/bin:/usr/local/bin:/usr/bin:$PATH"
export DISPLAY="${DISPLAY:-:0}"
export WAYLAND_DISPLAY="${WAYLAND_DISPLAY:-wayland-0}"
export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/run/user/1000}"
export DBUS_SESSION_BUS_ADDRESS="${DBUS_SESSION_BUS_ADDRESS:-unix:path=/run/user/1000/bus}"

SESSION_NAME="dsh-official-web"
URL_FILE="/home/ryan/.dsh/web_url.txt"

# 1. Kiểm tra session tmux
if ! tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
    tmux new-session -d -s "$SESSION_NAME" -c "$HOME" "dsh web --port 3080 --no-open"
    # Chờ DSH web khởi động và sinh token (tối đa 10s)
    URL=""
    for i in {1..20}; do
        sleep 0.5
        # Cờ -J để tmux nối liền dòng (join wrapped lines), không bao giờ bị cắt cụt token
        OUTPUT=$(tmux capture-pane -t "$SESSION_NAME" -J -p 2>/dev/null)
        URL=$(echo "$OUTPUT" | grep -o 'http://127\.0\.0\.1:3080/?token=[a-zA-Z0-9_-]*' | tail -n 1)
        if [ -n "$URL" ]; then
            echo "$URL" > "$URL_FILE"
            break
        fi
    done
else
    # Lấy token URL đầy đủ (dùng -J chống xuống dòng)
    OUTPUT=$(tmux capture-pane -t "$SESSION_NAME" -J -p 2>/dev/null)
    URL=$(echo "$OUTPUT" | grep -o 'http://127\.0\.0\.1:3080/?token=[a-zA-Z0-9_-]*' | tail -n 1)
    if [ -z "$URL" ] && [ -f "$URL_FILE" ]; then
        URL=$(cat "$URL_FILE")
    fi
fi

# Nếu chưa có URL token chuẩn, restart lại session để sinh token mới tinh
if [ -z "$URL" ]; then
    tmux kill-session -t "$SESSION_NAME" 2>/dev/null
    tmux new-session -d -s "$SESSION_NAME" -c "$HOME" "dsh web --port 3080 --no-open"
    sleep 2
    OUTPUT=$(tmux capture-pane -t "$SESSION_NAME" -J -p 2>/dev/null)
    URL=$(echo "$OUTPUT" | grep -o 'http://127\.0\.0\.1:3080/?token=[a-zA-Z0-9_-]*' | tail -n 1)
    if [ -n "$URL" ]; then
        echo "$URL" > "$URL_FILE"
    fi
fi

# 2. Mở trình duyệt Google Chrome với token URL chuẩn xác
if [ -n "$URL" ]; then
    echo "Launching: $URL"
    google-chrome "$URL" >/dev/null 2>&1 &
else
    google-chrome "http://127.0.0.1:3080/" >/dev/null 2>&1 &
fi
