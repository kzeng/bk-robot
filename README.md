

## 目标
- 实现图书馆机器人自动智能视觉图书盘点
- 智能视觉图书盘点机器人有以下及部分组成
    - 硬件
        - 机器人底座
        - 工控机
        - 触摸屏
        - 6个运动摄像头模组
        - 摄像头支架

    - 软件
        - 工控机操作系统采用国产银河麒麟或者OpenKylin 系统
        - OBS 提供摄像头控制接口
        - 自研的软件按照一定的逻辑控制机器人底座和摄像头的行为
        - 对图书馆书架图书进行拍照和录制视频, 照片和视频按一定规则命名和保存


- 应用需求（用户视角）
    - 通过机器人触摸屏提供的易用的GUI, 可以下达盘点等指令
    - 机器人接受语音指令。
- 开发需求（研发视角）
    - python flask 去对接机器人底座接口，去对接OBS 接口，并形成一套完备的统一接口，实现同时控制底座和摄像头
    - 为GUI的开发做好准备
    - 为触摸屏提供一套简单的GUI, 可以用 flask + web 实现


## 技术栈
- python 
- 接口由 flask + web 
- [机器人底座控制接口](http://waterdocs.pages.yunjichina.com.cn/user_manual/exports/water_api.html#water%E6%B0%B4%E6%BB%B4%E8%BD%AF%E4%BB%B6api%E6%89%8B%E5%86%8C)
- OBS 提供websocket 接口来控制多个摄像头拍照


### flowchat 流程图


### Screenshot

![控制面板](./docs/p1.png)
![盘点任务](./docs/p2.png)



