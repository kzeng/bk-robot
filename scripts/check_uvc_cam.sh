#!/bin/bash

echo "=== 检查 MagicView 摄像头连接情况 ==="
lsusb | grep -i "0edc:3080" && echo "✔ 摄像头连接正常" || echo "✘ 未检测到 MagicView 摄像头 (VID:PID 0edc:3080)"

echo
echo "=== 检查是否存在 /dev/video* 设备节点 ==="
if ls /dev/video* 2>/dev/null; then
    echo "✔ 已检测到视频设备"
else
    echo "✘ 未检测到 /dev/video* 设备"
fi

echo
echo "=== 检查 uvcvideo 模块是否已加载 ==="
if lsmod | grep -q uvcvideo; then
    echo "✔ uvcvideo 模块已加载"
else
    echo "✘ uvcvideo 模块未加载，尝试加载..."
    sudo modprobe uvcvideo && echo "✔ uvcvideo 模块加载成功" || echo "✘ 无法加载 uvcvideo 模块"
fi

echo
echo "=== 检查 dmesg 中是否识别视频设备 ==="
dmesg | grep -i -E "uvcvideo|video|usb" | tail -n 20

echo
echo "=== 检查内核是否启用 USB_VIDEO_CLASS ==="
if zcat /proc/config.gz | grep -q "CONFIG_USB_VIDEO_CLASS"; then
    zcat /proc/config.gz | grep CONFIG_USB_VIDEO_CLASS
else
    echo "✘ 无法读取内核配置，可能未启用 /proc/config.gz"
fi

echo
echo "=== 重载 udev 并触发设备检测 ==="
sudo udevadm control --reload
sudo udevadm trigger
sleep 1

echo
echo "=== 再次检查 /dev/video* 是否生成 ==="
if ls /dev/video* 2>/dev/null; then
    echo "✔ 设备节点已生成"
else
    echo "✘ 设备节点仍未生成，请检查硬件兼容性或驱动问题"
fi

echo
echo "=== 检查结束 ==="
