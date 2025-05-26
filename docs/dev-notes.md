标记点marker 为 m1,m2,m3,m4,m5 希望调用/api/move 接口驱动底座运动的同时
调用 /api/robot_status接口监控其状态，
当发现底座到达每个标记点时, 如到达m1时，调用我写的拍照接口（如: take_all_photo()）进行拍照 只到最后一个标记点m5 拍照， 结束。

用Python flask 代码实现 http 接口

通过调用机器人的 `/api/move` 接口驱动底座依次移动到标记点 `m1, m2, m3, m4, m5`，并在每次到达标记点时通过 `/api/robot_status` 接口监控状态，确认到达后调用 `take_all_photo()` 拍照，直到到达最后一个标记点 `m5` 并拍照后结束。以下是基于 Python Flask 的实现方案。

### 假设和说明
1. **API 文档分析**：
   - 根据提供的文档，`/api/move` 接口用于控制机器人移动到指定目标点（可以是 marker 点）。
   - `/api/robot_status` 接口用于获取机器人当前全局状态，包含位置信息，可用于判断是否到达指定 marker。
   - 文档中未提供 `/api/move` 和 `/api/robot_status` 的详细参数和返回值示例，但我假设：
     - `/api/move` 接受 marker 名称作为参数（例如 `marker_name=m1`）。
     - `/api/robot_status` 返回机器人的当前位置（`pose`）和状态（`status`），可以用来判断是否到达目标 marker。
   - `take_all_photo()` 是您提供的拍照接口，我假设它是一个无需参数的函数，直接调用即可。

2. **实现逻辑**：
   - Flask 提供一个 HTTP 接口（例如 `/start_navigation`）来触发导航任务。
   - 使用异步或线程轮询 `/api/robot_status` 检查机器人是否到达目标 marker。
   - 到达每个 marker 后调用 `take_all_photo()`，然后继续移动到下一个 marker，直到 `m5`。

3. **依赖**：
   - 使用 `requests` 库调用机器人 API。
   - 使用 `threading` 或 `asyncio` 实现状态轮询，避免阻塞 Flask 主线程。
   - 假设机器人 API 的基地址为 `http://192.168.10.10:8808`（基于文档 v1.4.0 移除前缀的说明）。

4. **限制**：
   - 由于文档中缺少 `/api/move` 和 `/api/robot_status` 的具体参数和返回值，我将基于合理假设实现代码。如果实际 API 不同，您可能需要调整参数或响应处理逻辑。
   - 假设 `take_all_photo()` 已实现并可直接调用。

### Python Flask 实现代码
以下代码实现了一个 Flask 应用程序，通过 HTTP 接口触发导航任务，依次移动到 `m1` 到 `m5`，并在到达每个 marker 时调用拍照接口。

```python
from flask import Flask, jsonify
import requests
import time
import threading
from http import HTTPStatus

app = Flask(__name__)

# 机器人 API 基地址
ROBOT_API_BASE = "http://192.168.10.10:8808"

# 模拟的拍照接口（您需要替换为实际实现）
def take_all_photo():
    print("Taking photos...")
    # 假设这是您实现的拍照逻辑
    time.sleep(1)  # 模拟拍照耗时
    print("Photos taken successfully.")

# 调用 /api/move 驱动机器人移动到指定 marker
def move_to_marker(marker_name):
    url = f"{ROBOT_API_BASE}/api/move?marker_name={marker_name}"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        if data.get("status") == "OK":
            print(f"Move command sent to {marker_name}")
            return True
        else:
            print(f"Failed to send move command to {marker_name}: {data.get('error_message')}")
            return False
    except requests.RequestException as e:
        print(f"Error calling /api/move for {marker_name}: {e}")
        return False

# 检查机器人是否到达目标 marker
def check_robot_arrival(marker_name):
    url = f"{ROBOT_API_BASE}/api/robot_status"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        if data.get("status") == "OK":
            # 假设 robot_status 返回 pose 和 marker_name 字段
            current_marker = data.get("results", {}).get("marker_name")
            if current_marker == marker_name:
                print(f"Robot arrived at {marker_name}")
                return True
            return False
        else:
            print(f"Error in robot status: {data.get('error_message')}")
            return False
    except requests.RequestException as e:
        print(f"Error calling /api/robot_status: {e}")
        return False

# 导航任务主逻辑，运行在单独线程中
def navigation_task(marker_list, callback):
    for marker in marker_list:
        # 发送移动指令
        if not move_to_marker(marker):
            callback({"error": f"Failed to initiate move to {marker}"}, HTTPStatus.INTERNAL_SERVER_ERROR)
            return

        # 轮询机器人状态直到到达
        while True:
            if check_robot_arrival(marker):
                take_all_photo()  # 到达后拍照
                break
            time.sleep(1)  # 每秒检查一次状态

        # 如果是最后一个 marker，结束任务
        if marker == marker_list[-1]:
            callback({"message": "Navigation and photo capture completed"}, HTTPStatus.OK)
            return

# Flask 接口，触发导航任务
@app.route("/start_navigation", methods=["GET"])
def start_navigation():
    marker_list = ["m1", "m2", "m3", "m4", "m5"]
    
    def callback(response, status_code):
        # 回调函数，用于将结果发送到客户端
        app.response = (jsonify(response), status_code)
    
    # 在单独线程中运行导航任务，避免阻塞 Flask
    threading.Thread(target=navigation_task, args=(marker_list, callback)).start()
    return jsonify({"message": "Navigation started"}), HTTPStatus.ACCEPTED

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
```

### 代码说明
1. **Flask 应用**：
   - 定义了一个 `/start_navigation` 接口，客户端通过 GET 请求触发导航任务。
   - 返回 HTTP 202 (Accepted) 状态，表示任务已启动，结果将异步返回。

2. **导航逻辑**：
   - `move_to_marker(marker_name)`：调用 `/api/move` 接口，发送移动指令到指定 marker。
   - `check_robot_arrival(marker_name)`：轮询 `/api/robot_status` 接口，检查机器人是否到达目标 marker。
   - `navigation_task(marker_list, callback)`：主导航逻辑，依次处理 `m1` 到 `m5`，在到达每个 marker 后调用 `take_all_photo()`，最后通过回调返回结果。

3. **异步处理**：
   - 使用 `threading.Thread` 在单独线程中运行导航任务，避免阻塞 Flask 主线程。
   - 状态轮询每秒检查一次 `/api/robot_status`，以减少 API 调用频率。

4. **拍照接口**：
   - `take_all_photo()` 是模拟的拍照函数，您需要替换为实际实现。
   - 假设拍照逻辑无需参数，且执行完成后返回控制权。

5. **错误处理**：
   - 包含基本的错误处理，捕获 API 请求异常并打印错误信息。
   - 如果移动指令失败，任务会中止并返回错误响应。

### 使用方法
1. **运行 Flask 应用**：
   ```bash
   python robot_navigation.py
   ```
   Flask 服务器将在 `http://0.0.0.0:5000` 启动。

2. **触发导航**：
   使用浏览器或 `curl` 访问：
   ```bash
   curl http://localhost:5000/start_navigation
   ```
   返回：
   ```json
   {"message": "Navigation started"}
   ```

3. **监控日志**：
   - 控制台会打印机器人移动、状态检查和拍照的日志。
   - 任务完成后，客户端可以通过回调获取最终结果。

### 注意事项
1. **API 基地址**：
   - 代码假设机器人 API 地址为 `http://192.168.10.10:8808`。请根据实际环境修改 `ROBOT_API_BASE`。

2. **API 参数和响应**：
   - 由于文档中 `/api/move` 和 `/api/robot_status` 的具体参数和返回值不完整，我假设 `/api/move` 接受 `marker_name` 参数，`/api/robot_status` 返回 `marker_name` 字段。如果实际 API 不同，请提供详细格式，我可以调整代码。

3. **拍照接口**：
   - 您需要将 `take_all_photo()` 替换为实际的拍照逻辑。如果该函数需要参数或返回特定结果，请告知以便调整。

4. **轮询间隔**：
   - 当前每秒检查一次状态（`time.sleep(1)`）。您可以根据机器人移动速度调整间隔。

5. **异步结果返回**：
   - 当前实现使用线程运行任务，客户端需另行检查任务状态（如通过日志或额外的状态查询接口）。如果需要实时返回结果，可以添加 WebSocket 或长轮询机制。



```python
from flask import Flask, jsonify
import requests
import time
import threading
from http import HTTPStatus

app = Flask(__name__)

# 机器人 API 基地址
ROBOT_API_BASE = "http://192.168.10.10:8808"

# 模拟的拍照接口（您需要替换为实际实现）
def take_all_photo():
    print("Taking photos...")
    # 假设这是您实现的拍照逻辑
    time.sleep(1)  # 模拟拍照耗时
    print("Photos taken successfully.")

# 调用 /api/move 驱动机器人移动到指定 marker
def move_to_marker(marker_name):
    url = f"{ROBOT_API_BASE}/api/move?marker_name={marker_name}"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        if data.get("status") == "OK":
            print(f"Move command sent to {marker_name}")
            return True
        else:
            print(f"Failed to send move command to {marker_name}: {data.get('error_message')}")
            return False
    except requests.RequestException as e:
        print(f"Error calling /api/move for {marker_name}: {e}")
        return False

# 检查机器人是否到达目标 marker
def check_robot_arrival(marker_name):
    url = f"{ROBOT_API_BASE}/api/robot_status"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        if data.get("status") == "OK":
            # 假设 robot_status 返回 pose 和 marker_name 字段
            current_marker = data.get("results", {}).get("marker_name")
            if current_marker == marker_name:
                print(f"Robot arrived at {marker_name}")
                return True
            return False
        else:
            print(f"Error in robot status: {data.get('error_message')}")
            return False
    except requests.RequestException as e:
        print(f"Error calling /api/robot_status: {e}")
        return False

# 导航任务主逻辑，运行在单独线程中
def navigation_task(marker_list, callback):
    for marker in marker_list:
        # 发送移动指令
        if not move_to_marker(marker):
            callback({"error": f"Failed to initiate move to {marker}"}, HTTPStatus.INTERNAL_SERVER_ERROR)
            return

        # 轮询机器人状态直到到达
        while True:
            if check_robot_arrival(marker):
                take_all_photo()  # 到达后拍照
                break
            time.sleep(1)  # 每秒检查一次状态

        # 如果是最后一个 marker，结束任务
        if marker == marker_list[-1]:
            callback({"message": "Navigation and photo capture completed"}, HTTPStatus.OK)
            return

# Flask 接口，触发导航任务
@app.route("/start_navigation", methods=["GET"])
def start_navigation():
    marker_list = ["m1", "m2", "m3", "m4", "m5"]
    
    def callback(response, status_code):
        # 回调函数，用于将结果发送到客户端
        app.response = (jsonify(response), status_code)
    
    # 在单独线程中运行导航任务，避免阻塞 Flask
    threading.Thread(target=navigation_task, args=(marker_list, callback)).start()
    return jsonify({"message": "Navigation started"}), HTTPStatus.ACCEPTED

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

```