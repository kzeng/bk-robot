# BK-ROBOT API 文档

## 目录
1. [机器人控制接口](#机器人控制接口)
2. [OBS控制接口](#OBS控制接口)

**以下接口不对外提供，仅作为内部调试使用**
3. [任务管理接口](#任务管理接口)
4. [任务日志接口](#任务日志接口)

## 机器人控制接口

### 1. 发送机器人控制命令
- **请求路径:** `/api/robot/cmd`
- **请求方法:** `POST`
- **功能说明:** 发送机器人控制命令
- **请求参数:**
  ```json
  {
    "cmd": "命令路径",
    "params": "命令参数"
  }
  ```
- **可用命令路径示例:**
  - `/api/move` - 机器人移动功能
  - `/api/move/cancel` - 移动取消功能
  - `/api/robot_status` - 获取机器人当前全局状态
  - `/api/robot_info` - 获取机器人信息
  - `/api/markers/insert` - 点位功能
  - `/api/joy_control` - 机器人直接控制指令
  - `/api/estop` - 机器人急停控制指令
  - `/api/position_adjust` - 校正机器人当前位置
  - `/api/request_data` - 请求机器人实时数据
  - `/api/set_params` - 设置参数
  - `/api/get_params` - 获取参数
  - `/api/wifi/list` - 无线网络接口
  - `/api/map/list` - 地图接口
  - `/api/shutdown` - 关机重启接口
  - `/api/software/get_version` - 软件更新接口
  - `/api/LED/set_luminance` - 设置灯带接口
  - `/api/diagnosis/get_result` - 自诊断接口
  - `/api/get_power_status` - 获取电源状态
  - `/api/get_planned_path` - 获取机器人全局路径
  - `/api/lift_status` - 获取电梯状态
  - `/api/make_plan` - 获取两点间路径
  - `/api/get_current_location` - 获取机器人当前位置
- **命令参数文档:** [机器人控制命令参数说明（PDF）](./WATER（水滴）软件API手册.pdf)
- **返回格式:**
  ```json
  {
    "container": "opt-info",
    "timestamp": 1621234567.89,
    "command": "执行的命令",
    "status": "OK/ERROR",
    "error_message": "错误信息",
    "results": "执行结果"
  }
  ```

### 2. 轮询机器人状态
- **请求路径:** `/api/robot/poll_status`
- **请求方法:** `GET`
- **功能说明:** 获取机器人当前状态
- **返回格式:**
  ```json
  {
    "container": "status-info",
    "timestamp": 1621234567.89,
    "type": "response",
    "command": "/api/robot_status",
    "status": "OK/ERROR",
    "error_message": "错误信息",
    "results": "状态信息"
  }
  ```

## OBS控制接口

### 1. 开始录制
- **请求路径:** `/api/obs/start_recording`
- **请求方法:** `POST`
- **功能说明:** 开始OBS录制
- **返回格式:**
  ```json
  {
    "status": "OK/ERROR",
    "message": "操作结果信息"
  }
  ```

### 2. 停止录制
- **请求路径:** `/api/obs/stop_recording`
- **请求方法:** `POST`
- **功能说明:** 停止OBS录制
- **返回格式:**
  ```json
  {
    "status": "OK",
    "message": "Recording stopped successfully",
    "file_path": "录制文件路径"
  }
  ```

### 3. 拍摄截图
- **请求路径:** `/api/obs/screenshot`
- **请求方法:** `POST`
- **功能说明:** 使用OBS拍摄截图
- **请求参数:**
  ```json
  {
    "position_info": "坐标点别名(可选)"
  }
  ```
- **返回格式:** 根据OBS控制结果返回

## 任务管理接口

### 1. 获取所有盘点任务
- **请求路径:** `/api/tasks` 或 `/tasks`
- **请求方法:** `GET`
- **功能说明:** 获取所有盘点任务列表
- **返回格式:**
  ```json
  [
    {
      "task_id": "任务ID",
      "marker": "标记点",
      "action": "动作类型",
      "create_at": "创建时间",
      "update_at": "更新时间",
      "description": "任务描述"
    }
  ]
  ```

### 2. 创建新盘点任务
- **请求路径:** `/api/tasks` 或 `/tasks`
- **请求方法:** `POST`
- **请求参数:**
  ```json
  {
    "marker": "标记点",
    "action": "动作类型(0:拍照,1:录像)",
    "description": "任务描述"
  }
  ```
- **返回格式:** 创建结果

### 3. 获取单个盘点任务
- **请求路径:** `/api/tasks/<task_id>` 或 `/tasks/<task_id>`
- **请求方法:** `GET`
- **功能说明:** 获取指定ID的任务详情
- **返回格式:**
  ```json
  {
    "task_id": "任务ID",
    "marker": "标记点",
    "action": "动作类型",
    "create_at": "创建时间",
    "update_at": "更新时间",
    "description": "任务描述"
  }
  ```

### 4. 更新盘点任务
- **请求路径:** `/api/tasks/<task_id>` 或 `/tasks/<task_id>`
- **请求方法:** `PUT`
- **请求参数:**
  ```json
  {
    "marker": "标记点",
    "action": "动作类型",
    "description": "任务描述"
  }
  ```
- **返回格式:**
  ```json
  {
    "status": "OK"
  }
  ```

### 5. 执行盘点任务
- **请求路径:** `/api/tasks/<task_id>/run`
- **请求方法:** `POST`
- **功能说明:** 启动指定任务的执行
- **返回格式:**
  ```json
  {
    "status": "OK",
    "message": "Task started successfully",
    "task_log_id": "任务日志ID"
  }
  ```

### 6. 删除盘点任务
- **请求路径:** `/api/tasks/<task_id>` 或 `/tasks/<task_id>`
- **请求方法:** `DELETE`
- **功能说明:** 删除指定ID的任务
- **返回格式:**
  ```json
  {
    "status": "OK"
  }
  ```

## 任务日志接口

### 1. 获取任务执行日志
- **请求路径:** `/api/tasks/<task_id>/logs`
- **请求方法:** `GET`
- **功能说明:** 获取指定任务的所有执行日志
- **返回格式:**
  ```json
  [
    {
      "log_id": "日志ID",
      "start_time": "开始时间",
      "end_time": "结束时间",
      "status": "执行状态",
      "file_count": "文件数量"
    }
  ]
  ```

### 2. 获取分页任务日志
- **请求路径:** `/api/task-logs`
- **请求方法:** `GET`
- **请求参数:**
  - page: 页码(默认1)
  - size: 每页数量(默认10)
- **功能说明:** 分页获取所有任务日志
- **返回格式:** 分页的任务日志列表

### 3. 清空任务日志
- **请求路径:** `/api/task-logs/clear`
- **请求方法:** `POST`
- **功能说明:** 清空所有任务日志

### 4. 获取任务日志详情
- **请求路径:** `/api/task-logs/<log_id>`
- **请求方法:** `GET`
- **功能说明:** 获取指定日志的详细信息
- **返回格式:**
  ```json
  {
    "log_id": "日志ID",
    "task_id": "任务ID",
    "marker": "标记点",
    "action": "动作类型",
    "start_time": "开始时间",
    "end_time": "结束时间",
    "status": "执行状态",
    "file_count": "文件数量",
    "file_paths": "相关文件路径列表"
  }
  ```

## 状态码说明

- 任务状态(status):
  - 1: 进行中
  - 2: 已完成
  - 3: 部分完成
  - 4: 执行失败

- 动作类型(action):
  - 0: 拍照
  - 1: 录像