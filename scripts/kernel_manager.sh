#!/bin/bash

echo "===== 🧠 LINUX KERNEL 管理助手 ====="
CURRENT=$(uname -r)
echo "🟢 当前正在使用的内核版本: $CURRENT"

# 提取已安装的内核版本（仅 image 包）
KERNELS=$(dpkg --list | grep linux-image | grep -vE 'meta|unsigned' | awk '{print $2}' | sort)
echo
echo "📦 已安装的内核包："
echo "$KERNELS" | nl

# 提取版本号（如 6.6.0-13-generic）
VERSIONS=$(echo "$KERNELS" | sed -n 's/linux-image-\(.*\)/\1/p')

# 推荐保留当前和最新两个版本
TO_KEEP=()
TO_KEEP+=("$CURRENT")
ALL_VERSIONS=($(echo "$VERSIONS"))
if [ "${#ALL_VERSIONS[@]}" -gt 1 ]; then
    TO_KEEP+=("${ALL_VERSIONS[-2]}")
fi

echo
echo "✅ 推荐保留版本："
for ver in "${TO_KEEP[@]}"; do
    echo "  - $ver"
done

echo
echo "🗑️ 可选择删除的旧版本："
for ver in "${ALL_VERSIONS[@]}"; do
    if [[ ! " ${TO_KEEP[*]} " =~ $ver ]]; then
        echo "  [ ] $ver"
    fi
done

echo
read -p "⚠️ 是否要进入交互式删除旧内核的界面？(y/n): " CONFIRM
if [[ "$CONFIRM" != "y" ]]; then
    echo "👋 已取消删除操作。"
    exit 0
fi

for ver in "${ALL_VERSIONS[@]}"; do
    if [[ "$ver" != "$CURRENT" ]]; then
        read -p "🔸 是否删除 $ver ? (y/n): " CHOICE
        if [[ "$CHOICE" == "y" ]]; then
            echo "🔧 正在删除 $ver ..."
            sudo apt-get remove --purge -y "linux-image-$ver" "linux-headers-$ver" "linux-modules-$ver" "linux-modules-extra-$ver"
        else
            echo "⏭️ 跳过 $ver"
        fi
    fi
done

echo
read -p "🧭 是否设置默认启动某个内核版本？(y/n): " SET_DEF
if [[ "$SET_DEF" == "y" ]]; then
    echo "可用内核版本："
    for idx in "${!ALL_VERSIONS[@]}"; do
        echo "  [$idx] ${ALL_VERSIONS[$idx]}"
    done
    read -p "请输入要设置为默认启动的内核编号: " IDX
    CHOSEN=${ALL_VERSIONS[$IDX]}

    echo "✍️ 设置默认启动: $CHOSEN"
    sudo sed -i "s|^GRUB_DEFAULT=.*|GRUB_DEFAULT=\"Advanced options for OpenKylin>OpenKylin, with Linux $CHOSEN\"|" /etc/default/grub
    sudo update-grub
    echo "✅ 已设置默认内核为 $CHOSEN"
else
    echo "❌ 未更改默认启动内核"
fi

echo
echo "🎉 完成！"
