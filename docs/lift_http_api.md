# **LIFT HTTP API 文档**

## 概述
LIFT HTTP API 提供了一组接口，用于通过 HTTP 请求控制升降机的操作。以下是支持的接口及其说明。

## 基础 URL
```
http://<host>:<port>/api/lift/<command>
```
- `<host>`: 服务器地址
- `<port>`: 服务器端口，默认为 5057
- `<command>`: 控制命令

## 支持的命令

| 命令               | HTTP 方法 | 描述             |
|--------------------|-----------|------------------|
| status             | GET       | 获取升降机状态   |
| move_to_position_one | POST      | 移动到一号位     |
| move_to_position_two | POST      | 移动到二号位     |
| move_to_position_three | POST   | 移动到三号位     |
| move_up            | POST      | 上升             |
| move_down          | POST      | 下降             |
| reset              | POST      | 复位             |
| stop_moving_up     | POST      | 停止上升         |
| stop_moving_down   | POST      | 停止下降         |

## 请求示例

### 获取状态
```
GET /api/lift/status HTTP/1.1
Host: <host>:<port>
```

### 移动到一号位
```
POST /api/lift/move_to_position_one HTTP/1.1
Host: <host>:<port>
```

### 上升
```
POST /api/lift/move_up HTTP/1.1
Host: <host>:<port>
```

## 响应

### 状态响应
```
HTTP/1.1 200 OK
Content-Type: application/json

{
    "status": "success",
    "message": "Lift is connected",
    "connected": true
}
```

### 命令成功响应
```
HTTP/1.1 200 OK
Content-Type: application/json

{
    "status": "success",
    "command": "<command>"
}
```

### 错误响应
```
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
    "error": "Invalid command"
}
```

```
HTTP/1.1 500 Internal Server Error
Content-Type: application/json

{
    "error": "<error_message>"
}
```

## 注意事项
- 确保服务器已启动并且升降机硬件已正确连接
- 如果升降机未初始化，某些命令可能会失败
- 状态码说明:
  - 200: 成功
  - 400: 无效命令
  - 500: 服务器错误
  - 503: 服务不可用(升降机未连接)
