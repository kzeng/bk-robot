#!/bin/bash

echo "🔍 正在获取当前内核版本..."
KERNEL_VERSION=$(uname -r)
KERNEL_BASE=$(echo "$KERNEL_VERSION" | sed 's/-generic//')

echo "✅ 当前内核版本: $KERNEL_VERSION"

# 构建要锁定的包名列表
PACKAGES=(
    "linux-image-$KERNEL_VERSION"
    "linux-headers-$KERNEL_VERSION"
    "linux-modules-$KERNEL_VERSION"
    "linux-modules-extra-$KERNEL_VERSION"
)

echo "🛑 正在尝试锁定以下内核相关包："
for pkg in "${PACKAGES[@]}"; do
    echo " - $pkg"
done

echo
echo "🚧 执行锁定操作..."
for pkg in "${PACKAGES[@]}"; do
    if dpkg -l | grep -q "$pkg"; then
        sudo apt-mark hold "$pkg"
        echo "✔ 已锁定 $pkg"
    else
        echo "⚠️  未安装 $pkg，跳过"
    fi
done

echo
echo "🔐 当前被锁定的包如下："
apt-mark showhold | grep "$KERNEL_BASE"

echo
echo "✅ 操作完成。当前内核版本已锁定，后续 apt upgrade 将不会自动替换它。"
