# 编译和启用 Orange Pi RK3588 内核的 USB 存储模块

本指南介绍如何在 Orange Pi 的 `orange-pi-5.10-rk3588` 内核分支中通过 `make menuconfig` 启用 USB 存储支持模块，编译并部署到设备上，以支持 U 盘等 USB 存储设备。

## 前提条件
- Ubuntu/Debian 系统（或其他 Linux 发行版）
- 已安装交叉编译工具链（`aarch64-linux-gnu-gcc`）
- 目标 Orange Pi 设备运行 `orange-pi-5.10-rk3588` 内核
- 基本的终端操作知识

## 步骤

### 1. 安装开发工具和依赖
在你的编译主机上安装必要的工具：

```bash
sudo apt update
sudo apt install build-essential git bc bison flex libssl-dev make gcc g++ libncurses-dev gcc-aarch64-linux-gnu
```

### 2. 克隆内核源代码
克隆 Orange Pi 内核仓库并切换到 `orange-pi-5.10-rk3588` 分支：

```bash
git clone https://github.com/orangepi-xunlong/linux-orangepi.git
cd linux-orangepi
git checkout orange-pi-5.10-rk3588
```

### 3. 获取默认内核配置
Orange Pi 通常提供设备特定的默认配置文件（如 `rockchip_linux_defconfig`）。检查可用配置文件：

```bash
ls arch/arm64/configs/
```

假设使用 `rockchip_linux_defconfig`：

```bash
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- rockchip_linux_defconfig
```

这会生成 `.config` 文件，作为后续配置的基础。

### 4. 使用 `make menuconfig` 启用 USB 存储模块
运行以下命令进入内核配置界面：

```bash
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- menuconfig
```

在 `menuconfig` 界面中，启用 USB 存储支持相关模块：

1. 导航到 `Device Drivers`：
   - 使用箭头键选择 `Device Drivers`，按 Enter 进入。
2. 进入 `USB support`：
   - 找到 `USB support`，按 Enter 进入。
   - 确保以下选项启用（标记为 `<M>` 表示编译为模块）：
     - `USB Mass Storage support`（U 盘和 USB 硬盘支持）
     - 按 `M` 键将该选项设置为模块。
3. 可选：启用相关文件系统支持（U 盘常用 FAT 和 NTFS）：
   - 返回主菜单，进入 `File systems`。
   - 进入 `DOS/FAT/NT Filesystems`。
   - 确保以下选项启用为模块（`<M>`）：
     - `VFAT (Windows-95) fs support`
     - `NTFS file system support`（如果需要 NTFS）
4. 确保 USB 控制器支持：
   - 返回 `Device Drivers` -> `USB support`。
   - 启用 Rockchip 平台的 USB 控制器驱动（如 `USB DWC3` 或 `USB EHCI/OHCI`），标记为 `<M>`。
5. 保存配置：
   - 按 `Esc` 多次返回主菜单，选择 `Save`，然后 `OK`。
   - 退出 `menuconfig`。

### 5. 准备模块编译环境
为模块编译准备内核环境：

```bash
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- modules_prepare
```

### 6. 编译 USB 存储模块
编译所有标记为模块的内核模块（包括 USB 存储模块）：

```bash
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- modules
```

编译完成后，USB 存储模块通常位于以下路径：
- `drivers/usb/storage/usb-storage.ko`（USB 存储核心模块）
- `fs/fat/vfat.ko`（VFAT 文件系统支持）
- `fs/ntfs/ntfs.ko`（NTFS 文件系统支持，若启用）

### 7. 部署模块到 Orange Pi
将编译好的模块传输到 Orange Pi 设备（使用 `scp` 或 USB）：

```bash
scp drivers/usb/storage/usb-storage.ko orangepi@<orange-pi-ip>:/home/orangepi/
scp fs/fat/vfat.ko orangepi@<orange-pi-ip>:/home/orangepi/
scp fs/ntfs/ntfs.ko orangepi@<orange-pi-ip>:/home/orangepi/  # 如果启用了 NTFS
```

替换 `<orange-pi-ip>` 为你的 Orange Pi 的 IP 地址。

### 8. 在 Orange Pi 上加载模块
在 Orange Pi 设备上，执行以下命令加载模块：

```bash
sudo insmod /home/orangepi/usb-storage.ko
sudo insmod /home/orangepi/vfat.ko
sudo insmod /home/orangepi/ntfs.ko  # 如果启用了 NTFS
```

### 9. 测试 U 盘支持
1. 插入 U 盘到 Orange Pi 的 USB 端口。
2. 检查设备是否识别：

   ```bash
   lsblk
   ```

   U 盘通常显示为 `/dev/sdX`（如 `/dev/sda1`）。

3. 挂载 U 盘：
   创建挂载点并挂载：

   ```bash
   sudo mkdir /mnt/usb
   sudo mount /dev/sda1 /mnt/usb
   ls /mnt/usb
   ```

4. 检查日志以调试问题：

   ```bash
   dmesg | grep usb
   ```

### 10. 卸载模块（可选）
如果需要卸载模块：

```bash
sudo rmmod usb_storage
sudo rmmod vfat
sudo rmmod ntfs  # 如果加载了 NTFS
```

### 11. 自动加载模块（可选）
为了让模块在启动时自动加载，编辑 `/etc/modules`：

```bash
echo "usb-storage" | sudo tee -a /etc/modules
echo "vfat" | sudo tee -a /etc/modules
echo "ntfs" | sudo tee -a /etc/modules  # 如果需要 NTFS
```

### 12. 清理
清理编译生成的文件：

```bash
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- clean
```

## 注意事项
- **内核版本匹配**：确保编译的模块与 Orange Pi 设备上的内核版本一致。检查设备内核版本：

  ```bash
  uname -r
  ```

- **模块依赖**：`usb-storage` 可能依赖其他模块（如 `usbcore`）。如果加载失败，使用 `modprobe` 代替 `insmod`：

  ```bash
  sudo modprobe usb-storage
  ```

- **设备树**：确保设备树中启用了 USB 控制器（通常默认启用）。如果 USB 端口不工作，检查 `arch/arm64/boot/dts/rockchip/` 中的 `.dts` 文件。
- **补丁提交**：如果需要提交 USB 相关补丁，参考 GitHub 文档中的要求（如添加 `Signed-off-by:` 和 `Change-Id:` 标签）。

## 常见问题
- **Q: U 盘未识别？**
  A: 检查 `dmesg` 日志，确认 USB 控制器和 `usb-storage` 模块是否正确加载。确保设备树支持 USB。
- **Q: 模块加载失败（“Invalid module format”）？**
  A: 确保模块与内核版本一致，检查 `modinfo usb-storage.ko` 的 `vermagic` 字段。
- **Q: 文件系统不支持？**
  A: 确保启用了 `vfat` 或 `ntfs` 模块，并安装了用户空间工具（如 `ntfs-3g`）。