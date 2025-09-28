# import cv2
# import os
# import sys

# def extract_frames(video_path, output_dir, interval_seconds=3):
#     """
#     从视频文件中以指定时间间隔抽取帧并保存为无损 PNG 图像。

#     参数:
#     - video_path: str, 视频文件路径。
#     - output_dir: str, 输出目录路径（若不存在，将自动创建）。
#     - interval_seconds: int 或 float, 时间间隔（秒），默认 3 秒。

#     返回:
#     - int, 成功保存的帧数。
#     """
#     # 打开视频文件
#     cap = cv2.VideoCapture(video_path)
#     if not cap.isOpened():
#         print(f"错误: 无法打开视频文件 {video_path}")
#         return 0

#     # 获取视频属性
#     fps = cap.get(cv2.CAP_PROP_FPS)
#     total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
#     frame_interval = int(interval_seconds * fps)  # 计算帧间隔

#     if frame_interval <= 0:
#         print("错误: 间隔时间过小或 FPS 为零")
#         cap.release()
#         return 0

#     # 创建输出目录
#     os.makedirs(output_dir, exist_ok=True)

#     # 获取视频文件名（无扩展名）用于命名输出文件
#     base_name = os.path.splitext(os.path.basename(video_path))[0]
#     frame_count = 0
#     current_frame = 0

#     print(f"视频 FPS: {fps}, 总帧数: {total_frames}, 抽帧间隔: {frame_interval} 帧")

#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             break

#         # 仅在间隔帧位置保存
#         if current_frame % frame_interval == 0:
#             output_path = os.path.join(output_dir, f"{base_name}_{frame_count:03d}.png")
#             cv2.imwrite(output_path, frame, [cv2.IMWRITE_PNG_COMPRESSION, 0])  # 无损 PNG (压缩级别 0)
#             frame_count += 1
#             print(f"保存帧 {current_frame}: {output_path}")

#         current_frame += 1

#     cap.release()
#     print(f"抽取完成，共保存 {frame_count} 帧。")
#     return frame_count

# # 示例用法
# if __name__ == "__main__":
#     if len(sys.argv) < 2:
#         print("用法: python script.py <video_path> [output_dir] [interval_seconds]")
#         sys.exit(1)

#     video_path = sys.argv[1]
#     output_dir = sys.argv[2] if len(sys.argv) > 2 else "extracted_frames"
#     interval_seconds = float(sys.argv[3]) if len(sys.argv) > 3 else 3.0

#     extract_frames(video_path, output_dir, interval_seconds)



# version:2 ##################################################
# import cv2
# import os
# import sys
# from PIL import Image
# import numpy as np

# def extract_frames(video_path, output_dir, interval_seconds=3):
#     """
#     从视频文件中以指定时间间隔抽取帧并保存为无损 PNG 图像。

#     参数:
#     - video_path: str, 视频文件路径。
#     - output_dir: str, 输出目录路径（若不存在，将自动创建）。
#     - interval_seconds: int 或 float, 时间间隔（秒），默认 3 秒。

#     返回:
#     - int, 成功保存的帧数。
#     """
#     # 打开视频文件
#     cap = cv2.VideoCapture(video_path)
#     if not cap.isOpened():
#         print(f"错误: 无法打开视频文件 {video_path}")
#         return 0

#     # 获取视频属性
#     fps = cap.get(cv2.CAP_PROP_FPS)
#     total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
#     width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
#     height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
#     frame_interval = int(interval_seconds * fps)  # 计算帧间隔

#     if frame_interval <= 0:
#         print("错误: 间隔时间过小或 FPS 为零")
#         cap.release()
#         return 0

#     # 输出视频分辨率信息
#     print(f"视频 FPS: {fps}, 总帧数: {total_frames}, 分辨率: {width}x{height}, 抽帧间隔: {frame_interval} 帧")

#     # 创建输出目录
#     os.makedirs(output_dir, exist_ok=True)

#     # 获取视频文件名（无扩展名）用于命名输出文件
#     base_name = os.path.splitext(os.path.basename(video_path))[0]
#     frame_count = 0
#     current_frame = 0

#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             break

#         # 仅在间隔帧位置保存
#         if current_frame % frame_interval == 0:
#             # OpenCV 帧为 BGR，转换为 RGB 以供 Pillow 使用
#             frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#             pil_image = Image.fromarray(frame_rgb)
#             output_path = os.path.join(output_dir, f"{base_name}_{frame_count:03d}.png")
#             pil_image.save(output_path, 'PNG', compress_level=0)  # 无损 PNG 压缩级别 0
#             frame_count += 1
#             print(f"保存帧 {current_frame}: {output_path}")

#         current_frame += 1

#     cap.release()
#     print(f"抽取完成，共保存 {frame_count} 帧。")
#     return frame_count

# # 示例用法
# if __name__ == "__main__":
#     if len(sys.argv) < 2:
#         print("用法: python script.py <video_path> [output_dir] [interval_seconds]")
#         sys.exit(1)

#     video_path = sys.argv[1]
#     output_dir = sys.argv[2] if len(sys.argv) > 2 else "extracted_frames"
#     interval_seconds = float(sys.argv[3]) if len(sys.argv) > 3 else 3.0

#     extract_frames(video_path, output_dir, interval_seconds)




#version:3 ##################################################
import cv2
import os
import sys
from PIL import Image
import numpy as np

def extract_frames(video_path, output_dir, interval_seconds=3):
    """
    从视频文件中以指定时间间隔抽取帧并保存为无损 PNG 图像。

    参数:
    - video_path: str, 视频文件路径。
    - output_dir: str, 输出目录路径（若不存在，将自动创建）。
    - interval_seconds: int 或 float, 时间间隔（秒），默认 3 秒。

    返回:
    - int, 成功保存的帧数。
    """
    # 打开视频文件
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"错误: 无法打开视频文件 {video_path}")
        return 0

    # 获取视频属性
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_interval = int(interval_seconds * fps)  # 计算帧间隔

    if frame_interval <= 0:
        print("错误: 间隔时间过小或 FPS 为零")
        cap.release()
        return 0

    # 输出视频分辨率信息
    print(f"视频 FPS: {fps}, 总帧数: {total_frames}, 分辨率: {width}x{height}, 抽帧间隔: {frame_interval} 帧")

    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    # 获取视频文件名（无扩展名）用于命名输出文件
    base_name = os.path.splitext(os.path.basename(video_path))[0]
    frame_count = 0

    # 计算最大可抽取次数（从第1个间隔开始）
    max_extractions = (total_frames - 1) // frame_interval  # 减1以从间隔开始
    print(f"预计抽取次数: {max_extractions}")

    for i in range(1, max_extractions + 1):
        target_frame = i * frame_interval
        if target_frame >= total_frames:
            break

        # 设置视频位置到目标帧
        cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
        ret, frame = cap.read()
        if not ret:
            continue

        # 计算当前帧时间（秒）
        time_offset = target_frame / fps

        # 格式化 freq 和 offset：统一使用1位小数
        freq_str = f"{interval_seconds:.1f}"
        offset_str = f"{time_offset:.1f}"

        # 生成文件名
        output_filename = f"{base_name}-freq-{freq_str}-offset-{offset_str}.png"
        output_path = os.path.join(output_dir, output_filename)

        # OpenCV 帧为 BGR，转换为 RGB 以供 Pillow 使用
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(frame_rgb)
        pil_image.save(output_path, 'PNG', compress_level=0)  # 无损 PNG 压缩级别 0
        frame_count += 1
        print(f"保存帧 {target_frame} (时间 {time_offset}s): {output_path}")

    cap.release()
    print(f"抽取完成，共保存 {frame_count} 帧。")
    return frame_count

# 示例用法
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python script.py <video_path> [output_dir] [interval_seconds]")
        sys.exit(1)

    video_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "extracted_frames"
    interval_seconds = float(sys.argv[3]) if len(sys.argv) > 3 else 3.0

    extract_frames(video_path, output_dir, interval_seconds)