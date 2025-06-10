# NOTES

## use python3.8 venv
- conda create -n venv-py38-robot python=3.8
- see requirements.txt for detail python packages 

## set pip package source 
pip config set global.index-url https://repo.huaweicloud.com/repository/pypi/simple



## todo

| Feature              | Status |
|----------------------|--------|
| User Login           | Done   |
| Setting              | Done   |
| Task Management      | Done   |
| Task Details         | Done   |
| Task Log Management  | Done   |
| Data Management      | Done   |
| Control Panel        | Done   |



## issue


## prompt history



## temp info

- shot with position_info
```
curl -X POST http://localhost:5000/api/obs/screenshot \
  -H "Content-Type: application/json" \
  -d '{"position_info": "Marker1"}'
{
  "position": "Marker1",
  "results": [
    {
      "camera_id": 1,
      "filename": "Marker1-s1-s1-20250525_112856.jpg",
      "filepath": "static/screenshots/20250525/Marker1-s1-c1-20250525_112856.jpg",
      "scene": "s1",
      "status": "OK"
    },
    {
      "camera_id": 2,
      "filename": "Marker1-s2-s2-20250525_112856.jpg",
      "filepath": "static/screenshots/20250525/Marker1-s2-c2-20250525_112856.jpg",
      "scene": "s2",
      "status": "OK"
    },
    {
      "camera_id": 3,
      "filename": "Marker1-s3-s3-20250525_112856.jpg",
      "filepath": "static/screenshots/20250525/Marker1-s3-c3-20250525_112856.jpg",
      "scene": "s3",
      "status": "OK"
    }
  ],
  "status": "OK",
  "timestamp": "20250525_112856"
}
```



## run obs with headless
```bash
obs --minimize-to-tray
```

sudo apt-get update && sudo apt-get install -y v4l-utils


对MagicView-UVC800摄像头进行了优化：

图像参数优化：

调整了亮度、对比度和饱和度到最佳值
增强了锐度以提高清晰度
设置了合适的伽马值以改善动态范围
曝光控制：

使用手动曝光模式以获得更稳定的图像
设置了较短的曝光时间以减少模糊
启用了背光补偿以改善光照不均的情况
色彩控制：

使用手动白平衡以保持色彩一致性
设置了适合室内的色温(4600K)
增强了色彩饱和度以获得更生动的图像
对焦和其他设置：

关闭自动对焦以避免抖动
设置了固定的焦距值
正确设置了电源频率以避免闪烁

(venv) (base) zengkai@zengkai-ThinkPad-X260:~/Codes/bk-robot$ v4l2-ctl -d /dev/video2 --list-ctrls --all
Driver Info:
        Driver name      : uvcvideo
        Card type        : MagicView-UVC800: MagicView-UVC
        Bus info         : usb-0000:00:14.0-1.1
        Driver version   : 6.8.12
        Capabilities     : 0x84a00001
                Video Capture
                Metadata Capture
                Streaming
                Extended Pix Format
                Device Capabilities
        Device Caps      : 0x04200001
                Video Capture
                Streaming
                Extended Pix Format
Media Driver Info:
        Driver name      : uvcvideo
        Model            : MagicView-UVC800: MagicView-UVC
        Serial           : SN0001
        Bus info         : usb-0000:00:14.0-1.1
        Media version    : 6.8.12
        Hardware revision: 0x00000100 (256)
        Driver version   : 6.8.12
Interface Info:
        ID               : 0x03000002
        Type             : V4L Video
Entity Info:
        ID               : 0x00000001 (1)
        Name             : MagicView-UVC800: MagicView-UVC
        Function         : V4L2 I/O
        Flags            : default
        Pad 0x01000007   : 0: Sink
          Link 0x02000010: from remote pad 0x100000a of entity 'Extension 3' (Video Pixel Formatter): Data, Enabled, Immutable
Priority: 2
Video input : 0 (Camera 1: ok)
Format Video Capture:
        Width/Height      : 1920/1080
        Pixel Format      : 'MJPG' (Motion-JPEG)
        Field             : None
        Bytes per Line    : 0
        Size Image        : 4147789
        Colorspace        : sRGB
        Transfer Function : Default (maps to sRGB)
        YCbCr/HSV Encoding: Default (maps to ITU-R 601)
        Quantization      : Default (maps to Full Range)
        Flags             : 
Crop Capability Video Capture:
        Bounds      : Left 0, Top 0, Width 1920, Height 1080
        Default     : Left 0, Top 0, Width 1920, Height 1080
        Pixel Aspect: 1/1
Selection Video Capture: crop_default, Left 0, Top 0, Width 1920, Height 1080, Flags: 
Selection Video Capture: crop_bounds, Left 0, Top 0, Width 1920, Height 1080, Flags: 
Streaming Parameters Video Capture:
        Capabilities     : timeperframe
        Frames per second: 5.000 (5/1)
        Read buffers     : 0

User Controls

                     brightness 0x00980900 (int)    : min=-64 max=64 step=1 default=0 value=64
                       contrast 0x00980901 (int)    : min=0 max=64 step=1 default=32 value=64
                     saturation 0x00980902 (int)    : min=0 max=128 step=1 default=48 value=48
                            hue 0x00980903 (int)    : min=-40 max=40 step=1 default=0 value=0
        white_balance_automatic 0x0098090c (bool)   : default=1 value=1
                          gamma 0x00980910 (int)    : min=72 max=500 step=1 default=100 value=100
                           gain 0x00980913 (int)    : min=0 max=100 step=1 default=0 value=100
           power_line_frequency 0x00980918 (menu)   : min=0 max=2 default=1 value=1 (50 Hz)
                                0: Disabled
                                1: 50 Hz
                                2: 60 Hz
      white_balance_temperature 0x0098091a (int)    : min=2800 max=6500 step=1 default=4600 value=4600 flags=inactive
                      sharpness 0x0098091b (int)    : min=0 max=6 step=1 default=4 value=4
         backlight_compensation 0x0098091c (int)    : min=0 max=1 step=1 default=1 value=1

Camera Controls

                  auto_exposure 0x009a0901 (menu)   : min=0 max=3 default=3 value=3 (Aperture Priority Mode)
                                1: Manual Mode
                                3: Aperture Priority Mode
         exposure_time_absolute 0x009a0902 (int)    : min=1 max=5000 step=1 default=157 value=157 flags=inactive
     exposure_dynamic_framerate 0x009a0903 (bool)   : default=0 value=0
                   pan_absolute 0x009a0908 (int)    : min=-36000 max=36000 step=3600 default=0 value=0
                  tilt_absolute 0x009a0909 (int)    : min=-36000 max=36000 step=3600 default=0 value=0
                 focus_absolute 0x009a090a (int)    : min=1 max=1023 step=1 default=170 value=250 flags=inactive
     focus_automatic_continuous 0x009a090c (bool)   : default=1 value=1
                  zoom_absolute 0x009a090d (int)    : min=0 max=9 step=1 default=0 value=0
(venv) (base) zengkai@zengkai-ThinkPad-X260:~/Codes/bk-robot$ 



(base) zengkai@zengkai-ThinkPad-X260:~$ exiftool ~/Codes/bk-robot/static/screenshots/20250609/Unknown-Camera6-20250609_215109.jpg
ExifTool Version Number         : 12.40
File Name                       : Unknown-Camera6-20250609_215109.jpg
Directory                       : /home/zengkai/Codes/bk-robot/static/screenshots/20250609
File Size                       : 496 KiB
File Modification Date/Time     : 2025:06:09 21:51:09+08:00
File Access Date/Time           : 2025:06:09 21:51:12+08:00
File Inode Change Date/Time     : 2025:06:09 21:51:09+08:00
File Permissions                : -rw-rw-r--
File Type                       : JPEG
File Type Extension             : jpg
MIME Type                       : image/jpeg
JFIF Version                    : 1.01
Resolution Unit                 : None
X Resolution                    : 1
Y Resolution                    : 1
Image Width                     : 1920
Image Height                    : 1080
Encoding Process                : Progressive DCT, Huffman coding
Bits Per Sample                 : 8
Color Components                : 3
Y Cb Cr Sub Sampling            : YCbCr4:2:0 (2 2)
Image Size                      : 1920x1080
Megapixels                      : 2.1



# 针对图书馆书架拍照场景，需优化MagicView-UVC800摄像头参数以适应图书馆典型光线（荧光灯或LED，4000–5500K，300–500 lux），解决过曝问题，确保书脊文字清晰、色彩准确，适合图书自动盘点。以下基于之前的`v4l2-ctl`输出和EXIF数据，结合图书馆环境特点，提供调整后的参数及代码。

---

### 图书馆环境分析
- **光线**：图书馆通常使用明亮荧光灯或LED（4000–5500K），光线均匀但可能有书封反光。
- **问题**：过曝由高亮度（64）、高增益（100）和较长曝光时间（157）引起，需降低曝光相关参数并优化文字清晰度。
- **目标**：减少过曝，增强文字可读性，保持色彩自然，适应书架距离（0.5–2米）。

### 优化后的拍照参数（图书馆场景）
以下参数针对图书馆光线调整，基于MagicView-UVC800的控制范围。

#### 1. 基础图像参数
- **亮度**：设为 **16**（原64）。
  - **原因**：图书馆光线充足但不过于强烈，16降低过曝风险，保留细节。
- **对比**：设为 **40**（原64）。
  - **原因**：适中对比增强书脊文字边缘，40避免过高丢失亮暗细节。
- **饱和**：设为 **80**（原48）。
  - **原因**：提高饱和度改善书封色彩区分，80适合明亮环境不过分浓烈。
- **锐化**：设为 **6**（原4）。
  - **原因**：最大锐化提升文字和细节清晰度，适合图书盘点。
- **伽马**：设为 **120**（原100）。
  - **原因**：略高伽马改善中灰对比，增强文字可读性。

#### 2. 曝光设置
- **自动曝光**：保持 **1（手动模式）**（不变）。
  - **原因**：手动模式确保一致曝光，适合自动化处理。
- **曝光时间**：设为 **80**（原157）。
  - **原因**：缩短曝光时间减少光线摄入，缓解过曝。80为起点，若过曝可调至50–70。
- **增益**：设为 **20**（原100）。
  - **原因**：高增益增加噪点，20在图书馆光线下提供清晰图像。

#### 3. 白平衡
- **自动白平衡**：保持 **0（手动）**（不变）。
  - **原因**：手动控制确保荧光灯下色彩一致。
- **白平衡温度**：设为 **5000K**（原4600K）。
  - **原因**：图书馆荧光/LED灯通常4000–5500K，5000K匹配光线，减少色偏。

#### 4. 对焦及其他设置
- **自动对焦**：保持 **0（手动）**（不变）。
  - **原因**：固定对焦确保书架拍摄一致性。
- **对焦值**：设为 **200**（原250）。
  - **原因**：书架距离约0.5–2米，200更适合，建议测试150–300以优化。
- **背光补偿**：设为 **0**（原1）。
  - **原因**：图书馆光线均匀，背光补偿可能加剧过曝，关闭以保持平衡。
- **电源频率**：保持 **1（50 Hz）**（不变）。
  - **原因**：匹配区域电源频率，避免闪烁。

#### 5. 分辨率与帧率
- **分辨率**：保持 **1920x1080**（不变）。
  - **原因**：足够捕捉书脊细节。
- **帧率**：保持 **5 FPS**（不变）。
  - **原因**：静态拍摄无需高帧率。

---

### 更新后的代码
以下为适配图书馆环境的Python代码：

```python
# Configure image quality settings for MagicView cameras in library environment
try:
    if is_magicview:
        # 1. 基础图像参数
        subprocess.run(['v4l2-ctl', '-d', device_path, '--set-ctrl=brightness=16'])      # 降低亮度避免过曝
        subprocess.run(['v4l2-ctl', '-d', device_path, '--set-ctrl=contrast=40'])        # 适中对比增强文字
        subprocess.run(['v4l2-ctl', '-d', device_path, '--set-ctrl=saturation=80'])      # 增强书封色彩
        subprocess.run(['v4l2-ctl', '-d', device_path, '--set-ctrl=sharpness=6'])        # 最大锐化提升文字
        subprocess.run(['v4l2-ctl', '-d', device_path, '--set-ctrl=gamma=120'])          # 优化中灰对比
        
        # 2. 曝光设置
        subprocess.run(['v4l2-ctl', '-d', device_path, '--set-ctrl=auto_exposure=1'])    # 手动曝光模式
        subprocess.run(['v4l2-ctl', '-d', device_path, '--set-ctrl=exposure_time_absolute=80'])  # 缩短曝光时间
        subprocess.run(['v4l2-ctl', '-d', device_path, '--set-ctrl=gain=20'])            # 降低增益减少噪点
        
        # 3. 白平衡
        subprocess.run(['v4l2-ctl', '-d', device_path, '--set-ctrl=white_balance_automatic=0'])    # 手动白平衡
        subprocess.run(['v4l2-ctl', '-d', device_path, '--set-ctrl=white_balance_temperature=5000'])  # 图书馆光线
        
        # 4. 对焦及其他设置
        subprocess.run(['v4l2-ctl', '-d', device_path, '--set-ctrl=focus_automatic_continuous=0'])  # 手动对焦
        subprocess.run(['v4l2-ctl', '-d', device_path, '--set-ctrl=focus_absolute=200'])           # 优化书架距离
        subprocess.run(['v4l2-ctl', '-d', device_path, '--set-ctrl=backlight_compensation=0'])     # 关闭背光补偿
        subprocess.run(['v4l2-ctl', '-d', device_path, '--set-ctrl=power_line_frequency=1'])       # 50 Hz
        
        self._log('info', f"MagicView camera parameters optimized for {device_path} in library lighting")
    else:
        # 通用相机设置
        if 'brightness' in controls:
            subprocess.run(['v4l2-ctl', '-d', device_path, '--set-ctrl=brightness=128'])
        if 'contrast' in controls:
            subprocess.run(['v4l2-ctl', '-d', device_path, '--set-ctrl=contrast=128'])
        if 'saturation' in controls:
            subprocess.run(['v4l2-ctl', '-d', device_path, '--set-ctrl=saturation=128'])
except:
    self._log('warning', f"Some controls could not be set for {device_path}")
```

---

### 额外建议
1. **测试与微调**：
   - 在图书馆实际光线下测试，检查书脊文字清晰度和过曝情况。
   - 若过曝仍存在，降低`exposure_time_absolute`（如50）或`gain`（如10）。
   - 调整`focus_absolute`（150–300范围），确保书架距离下文字锐利。

2. **光线控制**：
   - 避免光滑书封反光，可略微调整相机角度或使用漫射器。
   - 若图书馆光线区域差异大，考虑为不同区域（如窗边vs.内侧）创建参数配置文件。

3. **图像处理**：
   - 当前JPEG文件（496 KiB）偏小，可能因MJPG压缩过高。检查抓图软件压缩设置，尽量提高质量。
   - 若文字不清晰，可用OpenCV后处理增强对比或锐化。

4. **验证设置**：
   - 应用参数后，运行`v4l2-ctl -d /dev/video2 --list-ctrls`确认设置生效。

5. **相机局限**：
   - 若优化后效果仍不足，MagicView-UVC800可能受限于硬件性能。考虑升级至更高动态范围的摄像头。

---

### 参数变化总结
| 参数                     | 原值       | 新值       | 原因                             |
|--------------------------|------------|------------|----------------------------------|
| 亮度                     | 64         | 16         | 减少过曝                        |
| 对比                     | 64         | 40         | 增强文字，保留细节              |
| 饱和                     | 48         | 80         | 改善书封色彩                    |
| 锐化                     | 4          | 6          | 提升文字清晰度                  |
| 伽马                     | 100        | 120        | 改善中灰对比                    |
| 曝光时间                 | 157        | 80         | 减少光线摄入                    |
| 增益                     | 100        | 20         | 降低噪点和过曝                  |
| 白平衡温度               | 4600K      | 5000K      | 匹配图书馆荧光灯                |
| 对焦值                   | 250        | 200        | 优化书架距离                    |
| 背光补偿                 | 1          | 0          | 避免不必要曝光增强              |

这些参数应显著改善图书馆书架拍摄的过曝问题并提升图像质量。请在图书馆测试并根据效果微调。如需进一步帮助（如后处理或特定区域优化），请告知！