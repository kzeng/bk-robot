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

  --------------------------------


  可以。下面直接给你一套“能落地”的流程，覆盖环境核对、交叉编译内核模块、部署与排错。你只需要按步骤做就行。

---

# 先回答你的两个问题

**1) 你的环境是否满足开发所需？**
基本满足，但需要补齐几样工具与“目标内核”的配置信息/符号表，才能保证编译出的模块能被 OpenKylin 上正在运行的内核正确加载（vermagic 必须匹配）。

**2) 可以怎么做（完整指导如下）**

---

# A. 在 Orange Pi（OpenKylin）上收集“目标内核信息”

> 目的：拿到**准确的内核版本、配置和符号版本**，保证模块兼容。

在板子上执行（注意记录输出）：

```bash
uname -a
modinfo -F vermagic $(ls /lib/modules/* -d | xargs -n1 basename)
zcat /proc/config.gz | head
```

保存以下文件到你的 PC（Ubuntu 22.04）上（可用 `scp`）：

```bash
# 强烈建议全拿
/proc/config.gz                       # 运行内核的配置
/lib/modules/$(uname -r)/Module.symvers  # 符号版本（若有）
/lib/modules/$(uname -r)/build/.config   # 如存在则也拷贝
```

> 如果 `/proc/config.gz` 不存在，通常能在 `/boot/config-$(uname -r)` 找到。

---

# B. 在 PC（Ubuntu 22.04）上准备交叉编译环境

安装工具链与依赖：

```bash
sudo apt update
sudo apt install -y git build-essential gcc-aarch64-linux-gnu \
  bc bison flex libssl-dev libncurses5-dev dwarves \
  fakeroot cpio
```

克隆 OrangePi 提供的 RK3588 内核源码（你给的仓库分支）：

```bash
git clone https://github.com/orangepi-xunlong/linux-orangepi.git
cd linux-orangepi
git checkout orange-pi-5.10-rk3588
```

设置编译环境变量：

```bash
export ARCH=arm64
export CROSS_COMPILE=aarch64-linux-gnu-
```

把从板子上拷下来的配置与符号表放到源码树里：

```bash
# 假设你把文件放在 ~/ok-kernel-info/
zcat ~/ok-kernel-info/config.gz > .config    # 或者直接拷贝 config-xxx 到 .config
# 如果有 Module.symvers 一定要放到源码根目录
cp ~/ok-kernel-info/Module.symvers . 2>/dev/null || true
```

准备内核构建环境（不编内核，只做模块所需的准备）：

```bash
make olddefconfig          # 基于 .config 补齐缺省项
make prepare modules_prepare
```

---

# C. 确认并开启与 U 盘相关的关键模块

> 你的症状是 `lsusb` 能看到，但 `lsblk` 没有 `/dev/sd*`：通常是 **USB 存储与 SCSI/块设备模块缺失** 或 **文件系统驱动缺失**。

确保至少如下选项为 **m**（模块）或 **y**（内建）：

* **USB 主机与控制器：**

  * `CONFIG_USB_XHCI_HCD`
  * `CONFIG_USB_XHCI_PCI`（如走 PCIe XHCI）
  * `CONFIG_USB_DWC3` / `CONFIG_USB_DWC3_ROCKCHIP`（RK3588 常见）
* **USB 存储栈：**

  * `CONFIG_USB_STORAGE`（usb-storage）
  * `CONFIG_USB_UAS`（UASP，可选）
* **SCSI / 块设备：**

  * `CONFIG_SCSI`、`CONFIG_BLK_DEV_SD`（sd\_mod）
  * `CONFIG_SCSI_SCAN_ASYNC`（可选）
* **常见文件系统（根据你的 U 盘格式选）：**

  * FAT/exFAT：`CONFIG_VFAT_FS`、`CONFIG_MSDOS_FS`、`CONFIG_EXFAT_FS`、`CONFIG_NLS_CODEPAGE_437`、`CONFIG_NLS_ISO8859_1`
  * NTFS3（内核驱动）：`CONFIG_NTFS3_FS`
  * ext4：`CONFIG_EXT4_FS`

进入菜单配置检查/修改：

```bash
make menuconfig
# 逐项定位并改为 <M> 或 <*>（建议 <M> 以便热插拔加载）
```

修改后再次：

```bash
make olddefconfig
make prepare modules_prepare
```

---

# D. 只编你需要的模块（更快）

按目录单独编译（示例）：

```bash
# USB 存储
make M=drivers/usb/storage modules

# SCSI 块设备（sd_mod 等）
make M=drivers/scsi modules

# Rockchip DWC3 控制器（如需要）
make M=drivers/usb/dwc3 modules

# XHCI 主机（如需要）
make M=drivers/usb/host modules

# 文件系统（举例：exFAT/NTFS3）
make M=fs/exfat modules
make M=fs/ntfs3 modules
```

输出的 `.ko` 会在对应子目录里。

**注意 vermagic：**
编完随手检查一个模块：

```bash
modinfo drivers/usb/storage/usb-storage.ko | grep vermagic
```

它必须与板子上 `modinfo -F vermagic` 的字符串**完全一致**。
若不一致，说明 .config 或编译器版本和目标内核不一致；通常通过使用目标板导出的 `.config` + `Module.symvers` 就能匹配。如果目标内核开启了 `CONFIG_MODVERSIONS` 而你缺少匹配的 `Module.symvers`，模块很容易加载失败。这种情况下，**必须**拿到目标板的 `Module.symvers`，或使用同一份源码/配置重构一次内核与模块。

---

# E. 安装到板子并加载

把编好的 `.ko` 复制到板子，例如放在专用目录：

```bash
# 在 PC 上打包
mkdir -p outmods/extra
# 按需拷入
cp drivers/usb/storage/usb-storage.ko outmods/extra/
cp drivers/scsi/sd_mod.ko outmods/extra/
cp drivers/usb/storage/uas.ko outmods/extra/    # 可选
# (如有) exfat/ntfs3 也拷进去
cp fs/exfat/exfat.ko outmods/extra/ 2>/dev/null || true
cp fs/ntfs3/ntfs3.ko outmods/extra/ 2>/dev/null || true
tar czf outmods.tgz -C outmods .
```

拷到板子上并安装：

```bash
# 在板子上
sudo tar xzf /path/to/outmods.tgz -C /lib/modules/$(uname -r)/
sudo depmod -a $(uname -r)

# 试加载
sudo modprobe usb-storage
sudo modprobe sd_mod
sudo modprobe uas      # 如需要
```

插入 U 盘，查看日志：

```bash
dmesg -w
```

若识别成功，应出现 `sdX` 之类块设备。也可用：

```bash
lsblk
```

---

# F. 手动挂载与自动挂载

**手动挂载（示例 FAT32）：**

```bash
sudo mkdir -p /mnt/usb
sudo mount -t vfat -o uid=1000,gid=1000,umask=022 /dev/sda1 /mnt/usb
```

**exFAT：** 如果没用内核 exfat 模块，也可以在用户态装工具：

```bash
sudo apt install -y exfatprogs   # openKylin 源若兼容
# 或使用内核 exfat.ko，直接 mount -t exfat /dev/sda1 /mnt/usb
```

**NTFS：** 内核 `ntfs3` 模块（性能好），或用户态 `ntfs-3g`（慢但兼容广）。

**自动挂载：** 安装/启用 `udisks2`、桌面环境会自动提示挂载（服务器环境通常没有）。

---

# G. 常见陷阱与快速排错

1. **vermagic 不匹配（最常见）**
   `modprobe` 报错 “invalid module format”。

* 核对 `modinfo xxx.ko | grep vermagic` 与 `uname -r`、板子上 `modinfo -F vermagic`。
* 确保使用**同一源码分支**与**板子导出的 .config + Module.symvers** 编译。
* 交叉编译器版本差异也会影响 vermagic 中的 “SMP preempt mod\_unload …” 字段。

2. **USB 主机控制器驱动缺失或端口用错**

* RK3588 上不同 USB 口可能由不同控制器（xhci/dwc3）；确认对应驱动启用。
* 尝试不同物理 USB 口；避免用 OTG 设备模式的口。
* `dmesg` 中应看到 `xhci`/`dwc3` 初始化与 `new high-speed/ SuperSpeed USB device`。

3. **供电不足或线材问题**

* 机械硬盘 U 盘/SSD 盒子可能需要 Y 线或外接供电。
* `dmesg` 有反复掉线或 `reset SuperSpeed USB device` 可怀疑供电/线材。

4. **仅看到 `lsusb`，无 `sdX`**

* 必须加载 `usb-storage`（或 `uas`）+ `sd_mod` 才会生成块设备。
* `dmesg` 里应看到 `scsi hostX`、`sd X:Y:Z:0`、`Attached SCSI removable disk` 等。

5. **文件系统不支持**

* 块设备出现了，但 `mount` 报未知文件系统。编译或安装相应的 FS 模块（exFAT/NTFS3 等），或用用户态工具。

---

# H. 如果你只想“验证模块缺不缺”，不立刻编译

在板子上先试：

```bash
# 看内核是否内建/有模块
zcat /proc/config.gz | egrep 'USB_STORAGE|USB_UAS|BLK_DEV_SD|SCSI|DWC3|XHCI|VFAT|EXFAT|NTFS3'
# 看是否已有模块文件
find /lib/modules/$(uname -r) -name 'usb-storage.ko*' -o -name 'sd_mod.ko*' -o -name 'uas.ko*'
```

若缺失，再走上面的编译流程。

---

## 小结

* 你的 Ubuntu 22.04 + 提供的 OrangePi 内核源码，**可以**编出所需模块。
* **关键是匹配**：用板子导出的 `.config` 与（尽量）`Module.symvers`，并保持同分支源码。
* 先补齐 `usb-storage`、`sd_mod`、（可选）`uas` 与相应文件系统模块，基本就能让 U 盘在 `lsblk` 里出现并挂载。

如果你愿意，我也可以根据你板子上 `uname -a` 与 `modinfo -F vermagic` 的实际输出，直接给你一组精确到命令行的 **最小化编译脚本**（一步跑完）。


------------------

没问题！我把脚本改成**优先使用本地内核源码树**（默认：`~/Codes/OPI5/linux-orangepi`），不再去 clone；如果需要你也可以用环境变量覆盖。其余流程不变：自动从板子抓配置/符号表 → 套到你的源码树 → 只编 USB/存储/常见文件系统模块 → 打包推送并加载验证。

把下面存为 `build_rk3588_usb_modules.sh`，在 Ubuntu 22.04 上执行：

```bash
chmod +x build_rk3588_usb_modules.sh
./build_rk3588_usb_modules.sh
# 或者覆盖变量：
# BOARD_SSH=orangepi@192.168.1.88 KERNEL_SRC=~/Codes/OPI5/linux-orangepi ./build_rk3588_usb_modules.sh
```

```bash
#!/usr/bin/env bash
set -euo pipefail

### ======= 可配置项 =======
BOARD_SSH="${BOARD_SSH:-root@192.168.1.88}"   # 你的板子 SSH
KERNEL_SRC="${KERNEL_SRC:-$HOME/Codes/OPI5/linux-orangepi}"  # 已准备好的源码树路径
KERNEL_BRANCH="${KERNEL_BRANCH:-orange-pi-5.10-rk3588}"      # 你已经切到该分支即可
CROSS_COMPILE="${CROSS_COMPILE:-aarch64-linux-gnu-}"
ARCH="${ARCH:-arm64}"

# 需要编译的模块目录（按需裁剪/保留）
MOD_DIRS=(
  "drivers/usb/storage"   # usb-storage / uas
  "drivers/scsi"          # sd_mod
  "drivers/usb/host"      # xhci
  "drivers/usb/dwc3"      # dwc3 / dwc3-rockchip
  "fs/exfat"              # exfat（可选）
  "fs/ntfs3"              # ntfs3（可选）
)

WORKDIR="${WORKDIR:-$PWD/rk3588-usb-build}"
OUTPKG_NAME="${OUTPKG_NAME:-rk3588-usb-mods.tgz}"

### ======= 前置检查 =======
echo "[*] 安装依赖（如已安装会跳过）..."
sudo apt-get update -y
sudo apt-get install -y git build-essential gcc-aarch64-linux-gnu \
  bc bison flex libssl-dev libncurses5-dev dwarves fakeroot cpio

if [ ! -d "$KERNEL_SRC" ]; then
  echo "[X] 找不到内核源码目录：$KERNEL_SRC"
  echo "    请确认它已存在且已切换到 $KERNEL_BRANCH 分支，或用 KERNEL_SRC=... 覆盖。"
  exit 1
fi

cd "$KERNEL_SRC"
# 如果不在目标分支，给出提示（不强制切换）
CUR_BRANCH="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown)"
if [ "$CUR_BRANCH" != "$KERNEL_BRANCH" ]; then
  echo "[!] 当前分支是 $CUR_BRANCH，目标建议为 $KERNEL_BRANCH（脚本继续，但可能导致不匹配）。"
fi

### ======= 抓取目标板内核信息 =======
mkdir -p "$WORKDIR/target-info"
echo "[*] 从板子抓取内核配置/符号表..."
if ssh "$BOARD_SSH" 'test -f /proc/config.gz'; then
  ssh "$BOARD_SSH" 'cat /proc/config.gz' > "$WORKDIR/target-info/config.gz"
else
  KR=$(ssh "$BOARD_SSH" 'uname -r')
  ssh "$BOARD_SSH" "cat /boot/config-${KR}" > "$WORKDIR/target-info/config" || true
fi
ssh "$BOARD_SSH" 'uname -a' > "$WORKDIR/target-info/uname-a.txt" || true
ssh "$BOARD_SSH" 'uname -r' > "$WORKDIR/target-info/uname-r.txt" || true
if ssh "$BOARD_SSH" 'test -f /lib/modules/$(uname -r)/Module.symvers'; then
  ssh "$BOARD_SSH" 'cat /lib/modules/$(uname -r)/Module.symvers' > "$WORKDIR/target-info/Module.symvers"
fi
ssh "$BOARD_SSH" 'modinfo -F vermagic $(ls /lib/modules/* -d 2>/dev/null | xargs -n1 basename 2>/dev/null | head -n1) 2>/dev/null || true' \
  > "$WORKDIR/target-info/vermagic.txt" || true

echo "[*] 目标 uname -a:"
cat "$WORKDIR/target-info/uname-a.txt" || true
echo "[*] 目标 vermagic:"
cat "$WORKDIR/target-info/vermagic.txt" || true

### ======= 准备 .config 与符号表 =======
echo "[*] 套用目标 .config / Module.symvers..."
if [ -f "$WORKDIR/target-info/config.gz" ]; then
  zcat "$WORKDIR/target-info/config.gz" > .config
elif [ -f "$WORKDIR/target-info/config" ]; then
  cp "$WORKDIR/target-info/config" .config
else
  echo "[!] 未拿到目标内核配置（/proc/config.gz 或 /boot/config-*）。继续使用现有配置，可能 vermagic 不匹配。"
fi

if [ -f "$WORKDIR/target-info/Module.symvers" ]; then
  cp "$WORKDIR/target-info/Module.symvers" .
fi

export ARCH CROSS_COMPILE
make olddefconfig
make prepare modules_prepare

### ======= 确保关键选项开启（优先编成模块） =======
echo "[*] 确认关键配置（缺则启用为模块）..."
[ -x scripts/config ] || make scripts

enable_m () { ./scripts/config --module "$1" || ./scripts/config --enable "$1" || true; }

# USB Host/Controller
enable_m CONFIG_USB_XHCI_HCD
enable_m CONFIG_USB_XHCI_PLATFORM
enable_m CONFIG_USB_DWC3
enable_m CONFIG_USB_DWC3_ROCKCHIP

# USB Storage / UAS
enable_m CONFIG_USB_STORAGE
enable_m CONFIG_USB_UAS

# SCSI / 块设备
enable_m CONFIG_SCSI
enable_m CONFIG_BLK_DEV_SD
./scripts/config --enable CONFIG_SCSI_SCAN_ASYNC || true

# 常见文件系统
enable_m CONFIG_VFAT_FS
enable_m CONFIG_MSDOS_FS
enable_m CONFIG_EXFAT_FS
enable_m CONFIG_NLS_CODEPAGE_437
enable_m CONFIG_NLS_ISO8859_1
enable_m CONFIG_NTFS3_FS
enable_m CONFIG_EXT4_FS

make olddefconfig
make prepare modules_prepare

### ======= 编译模块 =======
echo "[*] 开始编译所需模块目录..."
for d in "${MOD_DIRS[@]}"; do
  echo "    -> make M=${d} modules"
  make -j"$(nproc)" M="${d}" modules
done

### ======= 校验 vermagic =======
echo "[*] 校验 vermagic..."
BUILD_VERMAGIC="$(/usr/sbin/modinfo drivers/usb/storage/usb-storage.ko 2>/dev/null | awk '/vermagic/{$1=\"\"; sub(/^ /,\"\"); print}')"
TARGET_VERMAGIC="$(cat \"$WORKDIR/target-info/vermagic.txt\" 2>/dev/null || true)"
echo "    build vermagic:  ${BUILD_VERMAGIC:-<unknown>}"
echo "    target vermagic: ${TARGET_VERMAGIC:-<unknown>}"
if [ -n "${TARGET_VERMAGIC:-}" ] && [ -n "${BUILD_VERMAGIC:-}" ] && [ "$BUILD_VERMAGIC" != "$TARGET_VERMAGIC" ]; then
  echo "[!] 警告：vermagic 不匹配，加载可能失败。建议务必使用目标板导出的 .config 与 Module.symvers。"
fi

### ======= 收集与打包 =======
echo "[*] 收集 .ko 并打包..."
OUTROOT="$WORKDIR/outmods/extra"
mkdir -p "$OUTROOT"
find drivers/usb/storage -name "*.ko" -exec cp -v {} "$OUTROOT"/ \;
find drivers/scsi        -name "sd_mod.ko" -exec cp -v {} "$OUTROOT"/ \;
find drivers/usb/host    -name "*.ko" -exec cp -v {} "$OUTROOT"/ \;
find drivers/usb/dwc3    -name "*.ko" -exec cp -v {} "$OUTROOT"/ \;
find fs/exfat            -name "*.ko" -exec cp -v {} "$OUTROOT"/ \; 2>/dev/null || true
find fs/ntfs3            -name "*.ko" -exec cp -v {} "$OUTROOT"/ \; 2>/dev/null || true

cat > "$WORKDIR/outmods/install_and_load.sh" <<'EOS'
#!/usr/bin/env bash
set -euo pipefail
KREL="$(uname -r)"
MODBASE="/lib/modules/${KREL}"
echo "[*] 安装到 ${MODBASE}/extra ..."
sudo mkdir -p "${MODBASE}/extra"
sudo cp -v extra/*.ko "${MODBASE}/extra/" || true
echo "[*] depmod ..."
sudo depmod -a "${KREL}"
echo "[*] 加载模块（按需忽略报错）..."
sudo modprobe usb-storage || true
sudo modprobe uas || true
sudo modprobe sd_mod || true
echo "[*] 最新内核日志："
dmesg | tail -n 80
echo "[*] 若看到 /dev/sdX，请用 lsblk 验证。"
EOS
chmod +x "$WORKDIR/outmods/install_and_load.sh"

tar -C "$WORKDIR/outmods" -czf "$WORKDIR/${OUTPKG_NAME}" .

### ======= 推送并执行 =======
echo "[*] 推送包到板子并安装..."
scp "$WORKDIR/${OUTPKG_NAME}" "$BOARD_SSH:/tmp/${OUTPKG_NAME}"
ssh "$BOARD_SSH" "cd /tmp && tar xzf ${OUTPKG_NAME} && sudo bash outmods/install_and_load.sh"

echo "[✓] 完成。现在在板子上插拔 U 盘并执行： dmesg -w / lsblk 查看是否出现 /dev/sdX"
```

### 小提示

* 你的源码树已经在目标分支就最好；若不是，建议 `git checkout orange-pi-5.10-rk3588` 再执行脚本，避免符号/接口差异。
* 如果 `vermagic` 仍不匹配，优先检查两点：

  1. 使用的 `.config` 是否来自**正在运行**的那套内核；
  2. 目标板 `/lib/modules/$(uname -r)/Module.symvers` 是否已拷入源码根目录。

需要我把 `MOD_DIRS` 再按你板子具体 USB 控制器精简（例如只留 `dwc3-rockchip`）的话，贴上你板子 `dmesg | grep -i -E "dwc3|xhci"` 的片段即可。
----------------

对，就是说这个脚本是通过 **SSH 远程登录** 到你的 Orange Pi 板子去取配置文件和安装模块的，所以：

* 板子上必须运行 **SSH 服务（sshd）**，这样 PC 才能通过 `ssh root@192.168.1.88` 访问。
* `BOARD_SSH` 这一行的意思是：

  * 如果你运行脚本时没有自己设置 `BOARD_SSH` 这个变量，就默认用 `root@192.168.1.88` 这个账号和IP。
  * 你可以在运行脚本时修改，比如：

    ```bash
    BOARD_SSH=orangepi@192.168.1.100 ./build_rk3588_usb_modules.sh
    ```

    这样就会用 `orangepi` 账号连接 `192.168.1.100` 这个地址的板子。

---

### 在 OpenKylin / Orange Pi 上开启 SSH

如果板子上没启用 SSH，可以这样做（假设是基于 Debian/Ubuntu 系）：

```bash
sudo apt update
sudo apt install openssh-server
sudo systemctl enable ssh
sudo systemctl start ssh
```

检查是否运行中：

```bash
sudo systemctl status ssh
```

确认 IP 地址（脚本里要用的）：

```bash
ip addr show
```

------------------------

好，给你“全自动（密码方式）”版。一句话概括：脚本里填上 `BOARD_USER`、`BOARD_HOST`、`BOARD_PASS`，它会用 `sshpass` 自动完成所有 `ssh/scp` 操作，全程不再交互输入密码。

---

# 一键脚本（自动输入密码版）

保存为 `build_rk3588_usb_modules.sh`，然后执行：

```bash
chmod +x build_rk3588_usb_modules.sh
./build_rk3588_usb_modules.sh
# 或在执行时覆盖变量：
# BOARD_USER=bk BOARD_HOST=192.168.1.88 BOARD_PASS=12345678 ./build_rk3588_usb_modules.sh
```

```bash
#!/usr/bin/env bash
set -euo pipefail

### ======= 连接与路径配置（按需改） =======
BOARD_USER="${BOARD_USER:-bk}"
BOARD_HOST="${BOARD_HOST:-192.168.1.88}"
BOARD_PASS="${BOARD_PASS:-12345678}"   # <—— 你的密码；也可在运行命令行里覆盖
BOARD="${BOARD_USER}@${BOARD_HOST}"

# 你的本地内核源码树（已准备好并切到 RK3588 分支）
KERNEL_SRC="${KERNEL_SRC:-$HOME/Codes/OPI5/linux-orangepi}"
KERNEL_BRANCH="${KERNEL_BRANCH:-orange-pi-5.10-rk3588}"

# 工具链与体系架构
CROSS_COMPILE="${CROSS_COMPILE:-aarch64-linux-gnu-}"
ARCH="${ARCH:-arm64}"

# 需要编译的模块目录（可精简）
MOD_DIRS=(
  "drivers/usb/storage"   # usb-storage / uas
  "drivers/scsi"          # sd_mod
  "drivers/usb/host"      # xhci
  "drivers/usb/dwc3"      # dwc3 / dwc3-rockchip
  "fs/exfat"              # exfat（可选）
  "fs/ntfs3"              # ntfs3（可选）
)

WORKDIR="${WORKDIR:-$PWD/rk3588-usb-build}"
OUTPKG_NAME="${OUTPKG_NAME:-rk3588-usb-mods.tgz}"

### ======= 准备依赖（含 sshpass） =======
echo "[*] 安装依赖（如已安装会跳过）..."
sudo apt-get update -y
sudo apt-get install -y git build-essential gcc-aarch64-linux-gnu \
  bc bison flex libssl-dev libncurses5-dev dwarves fakeroot cpio sshpass

# 基于 sshpass 的 SSH/SCP 包装
SSH_CMD=(sshpass -p "$BOARD_PASS" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "$BOARD")
SCP_CMD=(sshpass -p "$BOARD_PASS" scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null)

### ======= 检查源码树 =======
if [ ! -d "$KERNEL_SRC" ]; then
  echo "[X] 找不到内核源码目录：$KERNEL_SRC"
  echo "    请确认它已存在且已切到 $KERNEL_BRANCH 分支，或用 KERNEL_SRC=... 覆盖。"
  exit 1
fi

cd "$KERNEL_SRC"
CUR_BRANCH="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown)"
if [ "$CUR_BRANCH" != "$KERNEL_BRANCH" ]; then
  echo "[!] 当前分支是 $CUR_BRANCH，建议切换到 $KERNEL_BRANCH（脚本继续，但可能导致不匹配）。"
fi

### ======= 从板子抓取目标信息 =======
mkdir -p "$WORKDIR/target-info"
echo "[*] 从板子抓取内核配置/符号表..."

if "${SSH_CMD[@]}" 'test -f /proc/config.gz'; then
  "${SSH_CMD[@]}" 'cat /proc/config.gz' > "$WORKDIR/target-info/config.gz"
else
  KR="$("${SSH_CMD[@]}" 'uname -r' || true)"
  if [ -n "$KR" ]; then
    "${SSH_CMD[@]}" "cat /boot/config-${KR}" > "$WORKDIR/target-info/config" || true
  fi
fi

"${SSH_CMD[@]}" 'uname -a' > "$WORKDIR/target-info/uname-a.txt" || true
"${SSH_CMD[@]}" 'uname -r' > "$WORKDIR/target-info/uname-r.txt" || true

if "${SSH_CMD[@]}" 'test -f /lib/modules/$(uname -r)/Module.symvers'; then
  "${SSH_CMD[@]}" 'cat /lib/modules/$(uname -r)/Module.symvers' > "$WORKDIR/target-info/Module.symvers"
fi

"${SSH_CMD[@]}" 'modinfo -F vermagic $(ls /lib/modules/* -d 2>/dev/null | xargs -n1 basename 2>/dev/null | head -n1) 2>/dev/null || true' \
  > "$WORKDIR/target-info/vermagic.txt" || true

echo "[*] 目标 uname -a:"
cat "$WORKDIR/target-info/uname-a.txt" || true
echo "[*] 目标 vermagic:"
cat "$WORKDIR/target-info/vermagic.txt" || true

### ======= 套用目标 .config / 符号表 =======
echo "[*] 套用 .config / Module.symvers..."
if [ -f "$WORKDIR/target-info/config.gz" ]; then
  zcat "$WORKDIR/target-info/config.gz" > .config
elif [ -f "$WORKDIR/target-info/config" ]; then
  cp "$WORKDIR/target-info/config" .config
else
  echo "[!] 未拿到目标内核配置（/proc/config.gz 或 /boot/config-*）。继续使用现有配置，可能 vermagic 不匹配。"
fi

if [ -f "$WORKDIR/target-info/Module.symvers" ]; then
  cp "$WORKDIR/target-info/Module.symvers" .
fi

export ARCH CROSS_COMPILE
make olddefconfig
make prepare modules_prepare

### ======= 确保关键选项开启（优先模块） =======
echo "[*] 校验并启用关键配置..."
[ -x scripts/config ] || make scripts
enable_m () { ./scripts/config --module "$1" || ./scripts/config --enable "$1" || true; }

# USB Host/Controller
enable_m CONFIG_USB_XHCI_HCD
enable_m CONFIG_USB_XHCI_PLATFORM
enable_m CONFIG_USB_DWC3
enable_m CONFIG_USB_DWC3_ROCKCHIP

# USB Storage / UAS
enable_m CONFIG_USB_STORAGE
enable_m CONFIG_USB_UAS

# SCSI / 块设备
enable_m CONFIG_SCSI
enable_m CONFIG_BLK_DEV_SD
./scripts/config --enable CONFIG_SCSI_SCAN_ASYNC || true

# 常见文件系统
enable_m CONFIG_VFAT_FS
enable_m CONFIG_MSDOS_FS
enable_m CONFIG_EXFAT_FS
enable_m CONFIG_NLS_CODEPAGE_437
enable_m CONFIG_NLS_ISO8859_1
enable_m CONFIG_NTFS3_FS
enable_m CONFIG_EXT4_FS

make olddefconfig
make prepare modules_prepare

### ======= 编译需要的模块 =======
echo "[*] 按目录编译模块..."
for d in "${MOD_DIRS[@]}"; do
  echo "    -> make M=${d} modules"
  make -j"$(nproc)" M="${d}" modules
done

### ======= 校验 vermagic =======
echo "[*] 校验 vermagic..."
BUILD_VERMAGIC="$(/usr/sbin/modinfo drivers/usb/storage/usb-storage.ko 2>/dev/null | awk '/vermagic/{$1=""; sub(/^ /,""); print}')"
TARGET_VERMAGIC="$(cat "$WORKDIR/target-info/vermagic.txt" 2>/dev/null || true)"
echo "    build vermagic:  ${BUILD_VERMAGIC:-<unknown>}"
echo "    target vermagic: ${TARGET_VERMAGIC:-<unknown>}"
if [ -n "${TARGET_VERMAGIC:-}" ] && [ -n "${BUILD_VERMAGIC:-}" ] && [ "$BUILD_VERMAGIC" != "$TARGET_VERMAGIC" ]; then
  echo "[!] 警告：vermagic 不匹配，加载可能失败。建议务必使用目标板导出的 .config 与 Module.symvers。"
fi

### ======= 收集/打包并推送 =======
echo "[*] 收集 .ko 并打包..."
OUTROOT="$WORKDIR/outmods/extra"
mkdir -p "$OUTROOT"
find drivers/usb/storage -name "*.ko" -exec cp -v {} "$OUTROOT"/ \;
find drivers/scsi        -name "sd_mod.ko" -exec cp -v {} "$OUTROOT"/ \;
find drivers/usb/host    -name "*.ko" -exec cp -v {} "$OUTROOT"/ \;
find drivers/usb/dwc3    -name "*.ko" -exec cp -v {} "$OUTROOT"/ \;
find fs/exfat            -name "*.ko" -exec cp -v {} "$OUTROOT"/ \; 2>/dev/null || true
find fs/ntfs3            -name "*.ko" -exec cp -v {} "$OUTROOT"/ \; 2>/dev/null || true

cat > "$WORKDIR/outmods/install_and_load.sh" <<'EOS'
#!/usr/bin/env bash
set -euo pipefail
KREL="$(uname -r)"
MODBASE="/lib/modules/${KREL}"
echo "[*] 安装到 ${MODBASE}/extra ..."
sudo mkdir -p "${MODBASE}/extra"
sudo cp -v extra/*.ko "${MODBASE}/extra/" || true
echo "[*] depmod ..."
sudo depmod -a "${KREL}"
echo "[*] 加载模块（按需忽略报错）..."
sudo modprobe usb-storage || true
sudo modprobe uas || true
sudo modprobe sd_mod || true
echo "[*] 最近内核日志："
dmesg | tail -n 80
echo "[*] 如看到 /dev/sdX，请用 lsblk 验证。"
EOS
chmod +x "$WORKDIR/outmods/install_and_load.sh"

tar -C "$WORKDIR/outmods" -czf "$WORKDIR/${OUTPKG_NAME}" .

echo "[*] 推送并安装..."
"${SCP_CMD[@]}" "$WORKDIR/${OUTPKG_NAME}" "${BOARD}:/tmp/${OUTPKG_NAME}"
"${SSH_CMD[@]}" "cd /tmp && tar xzf ${OUTPKG_NAME} && sudo bash outmods/install_and_load.sh"

echo "[✓] 完成。现在在板子上插拔 U 盘并用： dmesg -w / lsblk 观察是否出现 /dev/sdX"
```

---

## 要点与安全提醒

* 这个脚本使用 `sshpass`，会把密码以进程参数的形式传给 `ssh/scp`。在同机用户可通过进程列表看到命令行参数。**建议仅用于内网临时自动化**。
* 更安全的长期方案是**配置公钥免密**（`ssh-copy-id bk@IP`），然后把脚本里的 `sshpass` 改回标准 `ssh/scp`。
* 如果遇到 `Permission denied`，请确认板子上：

  * `openssh-server` 已安装并启动：`sudo systemctl status ssh`
  * 用户 `bk` 具备 `sudo` 权限（脚本里会执行 `sudo`）。没有的话可去掉 `sudo` 或给 `bk` 加权限。

需要我把 `MOD_DIRS` 按你 `dmesg` 里实际控制器（比如只留 `dwc3-rockchip`）进一步精简吗？贴一段 `dmesg | egrep -i 'dwc3|xhci'` 我来给你裁。



