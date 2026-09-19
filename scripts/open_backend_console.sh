#!/usr/bin/env bash
# ==============================================================================
# HEO-HARNESS: LAUNCHER MỞ TERMINAL CONSOLE BACKEND DSH
# Tác giả: Anh Cơ La (genesis.corp.os@gmail.com)
# ==============================================================================

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$DIR"

# 1. Kiểm tra session tmux heo-harness
if ! tmux has-session -t heo-harness 2>/dev/null; then
    tmux new-session -d -s heo-harness -c "$DIR" "bash"
    tmux set-option -t heo-harness remain-on-exit on
    tmux send-keys -t heo-harness "./scripts/live_dispatch.sh" C-m
    sleep 1
fi

# 2. Kích hoạt cửa sổ Terminal Ptyxis hiển thị trực tiếp lên màn hình
env DISPLAY=:0 WAYLAND_DISPLAY=wayland-0 XDG_RUNTIME_DIR=/run/user/1000 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus \
    ptyxis --new-window -T "DSH BACKEND CHASSIS — HEO-HARNESS (PORT 5088)" -- tmux attach -t heo-harness &
