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

# Kiểm tra nếu session tmux chưa chạy
if ! tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
    tmux new-session -d -s "$SESSION_NAME" -c "$HOME" "dsh web --port 3080 --no-open"
    # Chờ DSH web khởi động và sinh token (tối đa 10s)
    URL=""
    for i in {1..20}; do
        sleep 0.5
        OUTPUT=$(tmux capture-pane -t "$SESSION_NAME" -p 2>/dev/null)
        URL=$(echo "$OUTPUT" | grep -o 'http://127\.0\.0\.1:3080/?token=[a-zA-Z0-9_-]*' | tail -n 1)
        if [ -n "$URL" ]; then
            break
        fi
    done
else
    # Lấy token URL từ pane hiện tại nếu có
    OUTPUT=$(tmux capture-pane -t "$SESSION_NAME" -p 2>/dev/null)
    URL=$(echo "$OUTPUT" | grep -o 'http://127\.0\.0\.1:3080/?token=[a-zA-Z0-9_-]*' | tail -n 1)
    if [ -z "$URL" ]; then
        URL="http://127.0.0.1:3080/"
    fi
fi

# Mở Google Chrome với URL DSH
if [ -n "$URL" ]; then
    google-chrome "$URL" >/dev/null 2>&1 &
else
    google-chrome "http://127.0.0.1:3080/" >/dev/null 2>&1 &
fi
