#!/bin/bash

echo "===== 🔐 GNOME Keyring 状态管理助手 ====="

KEYRING_DIR="$HOME/.local/share/keyrings"
AUTOSTART_DIR="$HOME/.config/autostart"
STATUS="未知"

check_keyring_status() {
    echo "🔍 正在检查 keyring 状态..."

    # 检查登录 keyring 文件是否为空
    if [[ -f "$KEYRING_DIR/login.keyring" ]] && [[ ! -s "$KEYRING_DIR/login.keyring" ]]; then
        STATUS="禁用"
    fi

    # 检查 autostart 屏蔽文件
    if ls "$AUTOSTART_DIR"/gnome-keyring-*.desktop 2>/dev/null | grep -q .; then
        STATUS="禁用"
    fi

    # 检查是否有 gnome-keyring 服务运行
    if pgrep -x gnome-keyring-daemon >/dev/null; then
        STATUS="启用"
    elif [[ "$STATUS" != "禁用" ]]; then
        STATUS="可能已禁用"
    fi
}

disable_keyring() {
    echo "⛔ 正在禁用 keyring..."

    mkdir -p "$KEYRING_DIR"
    echo -n "" > "$KEYRING_DIR/login.keyring"
    chmod 600 "$KEYRING_DIR/login.keyring"

    mkdir -p "$AUTOSTART_DIR"
    for comp in pkcs11 secrets ssh; do
        FILE="$AUTOSTART_DIR/gnome-keyring-$comp.desktop"
        echo "[Desktop Entry]
Type=Application
Name=Disable Keyring
Exec=true
X-GNOME-Autostart-enabled=false
" > "$FILE"
        echo "✔ 屏蔽：$FILE"
    done

    systemctl --user mask gnome-keyring-daemon.service gnome-keyring-daemon.socket 2>/dev/null
    echo "✅ 已禁用 keyring，建议重启后生效"
}

enable_keyring() {
    echo "✅ 正在启用 keyring..."

    rm -f "$KEYRING_DIR/login.keyring"
    rm -f "$AUTOSTART_DIR/gnome-keyring-"*.desktop
    systemctl --user unmask gnome-keyring-daemon.service gnome-keyring-daemon.socket 2>/dev/null
    echo "✅ 已启用 keyring，建议重启或重新登录后生效"
}

# 主流程
check_keyring_status

echo
echo "🎯 当前 GNOME Keyring 状态：$STATUS"
echo

read -p "🧭 你希望 [e] 启用 / [d] 禁用 / [q] 退出？(e/d/q): " ACTION

case "$ACTION" in
    e|E)
        enable_keyring
        ;;
    d|D)
        disable_keyring
        ;;
    *)
        echo "🚪 已退出，无更改。"
        ;;
esac
