#!/bin/bash

echo "===== 🔒 正在禁用系统自动升级功能 ====="

echo "🛑 停止并禁用 unattended-upgrades 服务..."
sudo systemctl stop unattended-upgrades.service
sudo systemctl disable unattended-upgrades.service

echo "🧹 关闭 APT 相关定时服务..."
sudo systemctl stop apt-daily.timer apt-daily.service
sudo systemctl stop apt-daily-upgrade.timer apt-daily-upgrade.service
sudo systemctl disable apt-daily.timer apt-daily.service
sudo systemctl disable apt-daily-upgrade.timer apt-daily-upgrade.service
sudo systemctl mask apt-daily.service apt-daily-upgrade.service

echo "📄 修改 /etc/apt/apt.conf.d/20auto-upgrades..."
AUTO_UPGRADE_FILE="/etc/apt/apt.conf.d/20auto-upgrades"
if [ -f "$AUTO_UPGRADE_FILE" ]; then
    sudo sed -i 's/^APT::Periodic::Update-Package-Lists.*/APT::Periodic::Update-Package-Lists "0";/' "$AUTO_UPGRADE_FILE"
    sudo sed -i 's/^APT::Periodic::Unattended-Upgrade.*/APT::Periodic::Unattended-Upgrade "0";/' "$AUTO_UPGRADE_FILE"
    echo "✔ 修改完成"
else
    echo "⚠️ $AUTO_UPGRADE_FILE 不存在，跳过"
fi

echo "🔕 关闭 motd-news（登录提示升级通知）..."
sudo systemctl disable motd-news.timer motd-news.service 2>/dev/null
sudo systemctl mask motd-news.service 2>/dev/null

echo
echo "✅ 自动升级功能已禁用。推荐重启后生效。"
