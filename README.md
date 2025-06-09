
## 目标
- 实现图书馆机器人自动智能视觉图书盘点
- 智能视觉图书盘点机器人有以下及部分组成
    - 硬件
        - 机器人底座
        - 工控机
        - 显示屏幕（触摸可选）
        - 运动摄像头模组(6个)
        - 升降柱
    - 软件
        - 采用国产银河麒麟或者OpenKylin系统
        - 控制算法
        - 任务管理
        - 任务日志管理
        - 数据管理
        - 用户认证

## 技术栈
- Linux
- Python 
- Flask API
- [机器人底座控制接口](./docs/WATER_API.pdf)
- OpenCV
- OBS

### 系统框图

### Screenshot

![控制面板](./docs/p1.png)
![盘点任务](./docs/p2.png)
![任务日志](./docs/p3.png)
![日志详情](./docs/p4.png)
![数据管理](./docs/p5.png)


### DEV Notes
- pip install <PACKAGE> -i https://repo.huaweicloud.com/repository/pypi/simple/
- use current venv, see requirements.txt for detail python packages 


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

- shot without position_info


### Run OBS with headless
```bash
obs --minimize-to-tray
```