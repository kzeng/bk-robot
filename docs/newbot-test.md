# 新底座现场测试指南

## 底座接口测试入口

进入路径：

```text
系统设置 -> 测试与计划任务 -> 底座接口测试
```

页面使用当前系统配置中的底座地址，例如：

```text
ROBOT_BASE_URL = http://192.168.10.10:1440
```

左侧是思岚 REST API 接口列表，右侧可填写请求路径、Query 参数和 JSON 请求体。点击“执行”后，响应结果会显示在右侧结果框中。写操作会弹出确认窗口，避免误操作。

## application 接口用途

`application` 分类不是盘点业务接口，而是底座系统的应用管理接口，主要用于：

- 查看底座已安装应用。
- 安装应用包。
- 查询某个应用状态。
- 启动、停止或重启底座应用。

现场盘点、导航、同步点位、回充、状态检查通常不需要使用 `application`。除非厂家明确要求安装或重启某个底座端应用，否则不要随意执行写操作。

## 推荐现场测试顺序

### 1. 确认底座在线

搜索并执行：

```text
GET /api/core/system/v1/robot/info
```

用途：确认 IP、端口、网络和底座服务都正常。

### 2. 查看电量和充电状态

搜索并执行：

```text
GET /api/core/system/v1/power/status
```

重点查看：

- `batteryPercentage`
- `isCharging`
- `dockingStatus`

### 3. 查看健康状态

搜索并执行：

```text
GET /api/core/system/v1/robot/health
```

重点查看：

- `hasError`
- `hasFatal`

注意：健康状态不是急停状态，只用于判断底座是否存在系统错误。

### 4. 精确读取急停状态

搜索并执行：

```text
GET /api/core/system/v1/parameter
```

Query 参数填写：

```text
param=base.emergency_stop
```

结果含义：

- `on`：急停中。
- `off`：未急停。

### 5. 查看多楼层地图

搜索并执行：

```text
GET /api/multi-floor/map/v1/floors
```

用途：确认底座是否存在多地图/多楼层数据。

再执行：

```text
GET /api/multi-floor/map/v1/floors/:current
```

用途：查看机器人当前所在楼层。

### 6. 查看 POI 点位

搜索并执行：

```text
GET /api/multi-floor/map/v1/pois
```

用途：验证现场人员在思岚工具中录入的 11 位 `mid` 点位和 `CD*` 充电点是否能被上位机读取。

普通点位命名规则：

```text
11 位数字字符串，例如 01020301041
```

充电点允许：

```text
CD*
```

### 7. 查看当前动作

搜索并执行：

```text
GET /api/core/motion/v1/actions/:current
```

用途：机器人移动、回充、取消动作后，查看底座当前 action 状态。

## 谨慎执行的写操作

以下接口会改变机器人状态，必须在现场安全确认后再执行。

### 触发急停

接口：

```text
PUT /api/core/system/v1/parameter
```

JSON 请求体：

```json
{
  "param": "base.emergency_stop",
  "value": "on"
}
```

### 解除急停

接口：

```text
PUT /api/core/system/v1/parameter
```

JSON 请求体：

```json
{
  "param": "base.emergency_stop",
  "value": "off"
}
```

### 取消当前动作

接口：

```text
DELETE /api/core/motion/v1/actions/:current
```

用途：取消当前移动、回充或其他正在执行的动作。

### 回充或移动

接口：

```text
POST /api/core/motion/v1/actions
```

用途：创建回充、移动等动作。该接口需要填写 JSON 请求体，必须先确认动作类型和参数格式。

## 建议测试流程

1. 执行 `robot/info`，确认底座连接正常。
2. 执行 `power/status`，确认电源和充电状态。
3. 执行 `robot/health`，确认无严重错误。
4. 执行 `parameter?param=base.emergency_stop`，确认急停状态。
5. 执行 `floors` 和 `floors/:current`，确认多楼层地图。
6. 执行 `pois`，确认点位命名和充电点。
7. 执行 `actions/:current`，确认当前动作状态。
8. 在安全区域内，再测试取消动作、急停、解除急停、回充等写操作。
