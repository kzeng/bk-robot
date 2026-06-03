# swagger_client.DeliveryApi

All URIs are relative to */*

Method | HTTP request | Description
------------- | ------------- | -------------
[**cancel_all_tasks**](DeliveryApi.md#cancel_all_tasks) | **DELETE** /api/delivery/v1/tasks | 取消所有任务
[**cancel_task_by_order_id**](DeliveryApi.md#cancel_task_by_order_id) | **DELETE** /api/delivery/v1/tasks/orders/{order_id} | 根据订单ID取消任务
[**cancel_task_by_task_id**](DeliveryApi.md#cancel_task_by_task_id) | **DELETE** /api/delivery/v1/tasks/{task_id} | 根据Task ID取消任务
[**create_task**](DeliveryApi.md#create_task) | **POST** /api/delivery/v1/tasks | 创建任务
[**create_tasks**](DeliveryApi.md#create_tasks) | **POST** /api/delivery/v1/tasks/:batch | 批量创建任务
[**end_operation**](DeliveryApi.md#end_operation) | **PUT** /api/delivery/v1/tasks/:end_operation | 完成操作
[**end_pickup**](DeliveryApi.md#end_pickup) | **PUT** /api/delivery/v1/tasks/:end_pickup | 结束取物
[**end_task**](DeliveryApi.md#end_task) | **PUT** /api/delivery/v1/tasks/:task_finish | 结束所有任务
[**get_assigned_cargos**](DeliveryApi.md#get_assigned_cargos) | **GET** /api/delivery/v1/cargos/assigned | 获取被占用的外卖舱
[**get_cargo_box**](DeliveryApi.md#get_cargo_box) | **GET** /api/delivery/v1/cargos/{cargo_id}/boxes/{box_id} | 获取Box信息
[**get_cargo_boxes**](DeliveryApi.md#get_cargo_boxes) | **GET** /api/delivery/v1/cargos/{cargo_id}/boxes | 获取某个Cargo所有Box信息
[**get_cargos**](DeliveryApi.md#get_cargos) | **GET** /api/delivery/v1/cargos | 获取所有Cargo信息
[**get_configurations**](DeliveryApi.md#get_configurations) | **GET** /api/delivery/v1/configurations | 获取机器配置信息
[**get_delivery_settings**](DeliveryApi.md#get_delivery_settings) | **GET** /api/delivery/v1/settings | 获取配送相关的设置信息
[**get_language**](DeliveryApi.md#get_language) | **GET** /api/delivery/v1/admin/language | 获取机器人语言
[**get_line_speed**](DeliveryApi.md#get_line_speed) | **GET** /api/delivery/v1/admin/line_speed | 获取配送速度和返航速度
[**get_move_options**](DeliveryApi.md#get_move_options) | **GET** /api/delivery/v1/admin/move_options | 获取运动选项
[**get_operation_result**](DeliveryApi.md#get_operation_result) | **GET** /api/delivery/v1/cargos/{cargo_id}/boxes/{box_id}/operation_result | 查询Box操作结果
[**get_password**](DeliveryApi.md#get_password) | **GET** /api/delivery/v1/admin/password | 获取操作密码
[**get_stage**](DeliveryApi.md#get_stage) | **GET** /api/delivery/v1/stage | 获取当前任务状态
[**get_tasks**](DeliveryApi.md#get_tasks) | **GET** /api/delivery/v1/tasks | 查询任务信息
[**get_voice_resources**](DeliveryApi.md#get_voice_resources) | **GET** /api/delivery/v1/voice_resources | 获取语音包信息
[**get_work_mode**](DeliveryApi.md#get_work_mode) | **GET** /api/delivery/v1/admin/mode | 获取机器人工作模式
[**get_working_time**](DeliveryApi.md#get_working_time) | **GET** /api/delivery/v1/admin/working_time | 获取机器人工作时间
[**operate_box**](DeliveryApi.md#operate_box) | **PUT** /api/delivery/v1/cargos/{cargo_id}/boxes/{box_id}/{op} | 操作Box
[**set_language**](DeliveryApi.md#set_language) | **PUT** /api/delivery/v1/admin/language | 设置机器人语言
[**set_line_speed**](DeliveryApi.md#set_line_speed) | **PUT** /api/delivery/v1/admin/line_speed | 设置配送速度和返航速度
[**set_move_options**](DeliveryApi.md#set_move_options) | **PUT** /api/delivery/v1/admin/move_options | 设置运动选项
[**set_password**](DeliveryApi.md#set_password) | **PUT** /api/delivery/v1/admin/password | 设置操作密码
[**set_task_execution**](DeliveryApi.md#set_task_execution) | **PUT** /api/delivery/v1/tasks/:task_execution | 暂停/继续执行任务
[**set_timeout_settings**](DeliveryApi.md#set_timeout_settings) | **PUT** /api/delivery/v1/settings/timeout | 设置任务的超时时间
[**set_work_mode**](DeliveryApi.md#set_work_mode) | **PUT** /api/delivery/v1/admin/mode | 设置机器人工作模式
[**set_working_time**](DeliveryApi.md#set_working_time) | **PUT** /api/delivery/v1/admin/working_time | 设置机器人工作时间
[**start_pickup**](DeliveryApi.md#start_pickup) | **PUT** /api/delivery/v1/tasks/:start_pickup | 开始取物

# **cancel_all_tasks**
> cancel_all_tasks()

取消所有任务

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DeliveryApi()

try:
    # 取消所有任务
    api_instance.cancel_all_tasks()
except ApiException as e:
    print("Exception when calling DeliveryApi->cancel_all_tasks: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **cancel_task_by_order_id**
> cancel_task_by_order_id(order_id)

根据订单ID取消任务

在机器人端创建的任务，都会包含订单号，因此可以通过订单号取消任务

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DeliveryApi()
order_id = 'order_id_example' # str | 

try:
    # 根据订单ID取消任务
    api_instance.cancel_task_by_order_id(order_id)
except ApiException as e:
    print("Exception when calling DeliveryApi->cancel_task_by_order_id: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **order_id** | **str**|  | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **cancel_task_by_task_id**
> cancel_task_by_task_id(task_id)

根据Task ID取消任务

有些任务是通过云端下发的，可能不存在订单号，因此需要通过Task ID来取消

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DeliveryApi()
task_id = 'task_id_example' # str | 

try:
    # 根据Task ID取消任务
    api_instance.cancel_task_by_task_id(task_id)
except ApiException as e:
    print("Exception when calling DeliveryApi->cancel_task_by_task_id: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **task_id** | **str**|  | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_task**
> InlineResponse20025 create_task(body)

创建任务

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DeliveryApi()
body = swagger_client.PostTaskRequestEntry() # PostTaskRequestEntry | 

try:
    # 创建任务
    api_response = api_instance.create_task(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DeliveryApi->create_task: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**PostTaskRequestEntry**](PostTaskRequestEntry.md)|  | 

### Return type

[**InlineResponse20025**](InlineResponse20025.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_tasks**
> InlineResponse20026 create_tasks(body)

批量创建任务

一次性创建多个任务 <h4>所需最低固件版本 4.3.0</h4>

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DeliveryApi()
body = [swagger_client.PostTaskRequestEntry()] # list[PostTaskRequestEntry] | 

try:
    # 批量创建任务
    api_response = api_instance.create_tasks(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DeliveryApi->create_tasks: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**list[PostTaskRequestEntry]**](PostTaskRequestEntry.md)|  | 

### Return type

[**InlineResponse20026**](InlineResponse20026.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **end_operation**
> end_operation()

完成操作

机器人到达任务点时，该接口用于通知机器人用户已完成操作，可以继续执行任务。

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DeliveryApi()

try:
    # 完成操作
    api_instance.end_operation()
except ApiException as e:
    print("Exception when calling DeliveryApi->end_operation: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **end_pickup**
> end_pickup()

结束取物

通知机器人用户已完成取物。

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DeliveryApi()

try:
    # 结束取物
    api_instance.end_pickup()
except ApiException as e:
    print("Exception when calling DeliveryApi->end_pickup: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **end_task**
> end_task()

结束所有任务

与Delete接口的区别是本接口以成功状态结束所有任务。

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DeliveryApi()

try:
    # 结束所有任务
    api_instance.end_task()
except ApiException as e:
    print("Exception when calling DeliveryApi->end_task: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_assigned_cargos**
> list[AssignedCargoEntry] get_assigned_cargos()

获取被占用的外卖舱

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DeliveryApi()

try:
    # 获取被占用的外卖舱
    api_response = api_instance.get_assigned_cargos()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DeliveryApi->get_assigned_cargos: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**list[AssignedCargoEntry]**](AssignedCargoEntry.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_cargo_box**
> Box get_cargo_box(cargo_id, box_id)

获取Box信息

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DeliveryApi()
cargo_id = '38400000-8cf0-11bd-b23e-10b96e4ef00d' # str | 
box_id = 56 # int | 

try:
    # 获取Box信息
    api_response = api_instance.get_cargo_box(cargo_id, box_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DeliveryApi->get_cargo_box: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cargo_id** | [**str**](.md)|  | 
 **box_id** | **int**|  | 

### Return type

[**Box**](Box.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_cargo_boxes**
> list[Box] get_cargo_boxes(cargo_id)

获取某个Cargo所有Box信息

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DeliveryApi()
cargo_id = '38400000-8cf0-11bd-b23e-10b96e4ef00d' # str | 

try:
    # 获取某个Cargo所有Box信息
    api_response = api_instance.get_cargo_boxes(cargo_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DeliveryApi->get_cargo_boxes: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cargo_id** | [**str**](.md)|  | 

### Return type

[**list[Box]**](Box.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_cargos**
> list[Cargo] get_cargos()

获取所有Cargo信息

只有带货仓的机型支持cargos系列接口

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DeliveryApi()

try:
    # 获取所有Cargo信息
    api_response = api_instance.get_cargos()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DeliveryApi->get_cargos: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**list[Cargo]**](Cargo.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_configurations**
> InlineResponse20021 get_configurations()

获取机器配置信息

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DeliveryApi()

try:
    # 获取机器配置信息
    api_response = api_instance.get_configurations()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DeliveryApi->get_configurations: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**InlineResponse20021**](InlineResponse20021.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_delivery_settings**
> InlineResponse20022 get_delivery_settings()

获取配送相关的设置信息

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DeliveryApi()

try:
    # 获取配送相关的设置信息
    api_response = api_instance.get_delivery_settings()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DeliveryApi->get_delivery_settings: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**InlineResponse20022**](InlineResponse20022.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_language**
> InlineResponse20019 get_language()

获取机器人语言

<h4>所需最低固件版本 4.3.2</h4>

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DeliveryApi()

try:
    # 获取机器人语言
    api_response = api_instance.get_language()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DeliveryApi->get_language: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**InlineResponse20019**](InlineResponse20019.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_line_speed**
> InlineResponse20020 get_line_speed()

获取配送速度和返航速度

<h4>所需最低固件版本 4.5.3</h4>

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DeliveryApi()

try:
    # 获取配送速度和返航速度
    api_response = api_instance.get_line_speed()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DeliveryApi->get_line_speed: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**InlineResponse20020**](InlineResponse20020.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_move_options**
> MoveOptions get_move_options()

获取运动选项

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DeliveryApi()

try:
    # 获取运动选项
    api_response = api_instance.get_move_options()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DeliveryApi->get_move_options: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**MoveOptions**](MoveOptions.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_operation_result**
> InlineResponse20024 get_operation_result(cargo_id, box_id)

查询Box操作结果

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DeliveryApi()
cargo_id = '38400000-8cf0-11bd-b23e-10b96e4ef00d' # str | 
box_id = 56 # int | 

try:
    # 查询Box操作结果
    api_response = api_instance.get_operation_result(cargo_id, box_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DeliveryApi->get_operation_result: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cargo_id** | [**str**](.md)|  | 
 **box_id** | **int**|  | 

### Return type

[**InlineResponse20024**](InlineResponse20024.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_password**
> InlineResponse20017 get_password()

获取操作密码

expires表示密码过期时间，如果不包含这个字段则意味着密码永久有效，enable表示是否启用操作密码

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DeliveryApi()

try:
    # 获取操作密码
    api_response = api_instance.get_password()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DeliveryApi->get_password: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**InlineResponse20017**](InlineResponse20017.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_stage**
> TaskStage get_stage()

获取当前任务状态

* `DEVICE_ERROR` 设备故障，底盘上报了Error信息，机器人无法移动，上位机应当显示故障页面。 * `GOING_TO_TASK_POINT` 正在前往任务点，有些任务（如回盘、取物配送）需要中途停靠某些任务点，完成操作后再前往目标点。 * `ARRIVED_AT_TASK_POINT` 到达任务点，机器人会等待操作完成或超时后再继续下一阶段。 * `ON_DELIVERING` 正在前往目标点，为了兼容采用该名称，实际不一定是配送任务。 * `ARRIVED_AT_TARGET` 到达最终目标点。 * `ON_RETURNING` 正在返航，当机器人有默认停靠点时，该状态表示机器人正在前往该停靠点。 * `GOING_HOME`  正在回桩。 * `IDLE` 空闲，机器人在默认停靠点或桩上时处于该状态。 

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DeliveryApi()

try:
    # 获取当前任务状态
    api_response = api_instance.get_stage()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DeliveryApi->get_stage: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**TaskStage**](TaskStage.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_tasks**
> list[DeliveryTask] get_tasks(type=type, status=status)

查询任务信息

默认返回ready和running状态的所有类型的任务，status为all时表示查询最近的所有任务，包括已成功完成和失败的任务。

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DeliveryApi()
type = 'type_example' # str |  (optional)
status = 'status_example' # str |  (optional)

try:
    # 查询任务信息
    api_response = api_instance.get_tasks(type=type, status=status)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DeliveryApi->get_tasks: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **type** | **str**|  | [optional] 
 **status** | **str**|  | [optional] 

### Return type

[**list[DeliveryTask]**](DeliveryTask.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_voice_resources**
> InlineResponse20023 get_voice_resources()

获取语音包信息

从云端获取语音包信息，网络不好时该接口可能耗时较久。<h4>所需最低固件版本 4.3.2</h4>

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DeliveryApi()

try:
    # 获取语音包信息
    api_response = api_instance.get_voice_resources()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DeliveryApi->get_voice_resources: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**InlineResponse20023**](InlineResponse20023.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_work_mode**
> DeliveryWorkMode get_work_mode()

获取机器人工作模式

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DeliveryApi()

try:
    # 获取机器人工作模式
    api_response = api_instance.get_work_mode()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DeliveryApi->get_work_mode: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**DeliveryWorkMode**](DeliveryWorkMode.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_working_time**
> WorkingTime get_working_time()

获取机器人工作时间

<h4>所需最低固件版本 4.3.3</h4>

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DeliveryApi()

try:
    # 获取机器人工作时间
    api_response = api_instance.get_working_time()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DeliveryApi->get_working_time: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**WorkingTime**](WorkingTime.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **operate_box**
> operate_box(cargo_id, box_id, op)

操作Box

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DeliveryApi()
cargo_id = '38400000-8cf0-11bd-b23e-10b96e4ef00d' # str | 
box_id = 56 # int | 
op = 'op_example' # str | 

try:
    # 操作Box
    api_instance.operate_box(cargo_id, box_id, op)
except ApiException as e:
    print("Exception when calling DeliveryApi->operate_box: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cargo_id** | [**str**](.md)|  | 
 **box_id** | **int**|  | 
 **op** | **str**|  | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **set_language**
> InlineResponse20018 set_language(body)

设置机器人语言

<h4>所需最低固件版本 4.3.2</h4>

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DeliveryApi()
body = swagger_client.AdminLanguageBody() # AdminLanguageBody | 

try:
    # 设置机器人语言
    api_response = api_instance.set_language(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DeliveryApi->set_language: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**AdminLanguageBody**](AdminLanguageBody.md)|  | 

### Return type

[**InlineResponse20018**](InlineResponse20018.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: text/plain

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **set_line_speed**
> set_line_speed(body)

设置配送速度和返航速度

<h4>所需最低固件版本 4.5.3</h4>

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DeliveryApi()
body = swagger_client.AdminLineSpeedBody() # AdminLineSpeedBody | 

try:
    # 设置配送速度和返航速度
    api_instance.set_line_speed(body)
except ApiException as e:
    print("Exception when calling DeliveryApi->set_line_speed: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**AdminLineSpeedBody**](AdminLineSpeedBody.md)|  | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **set_move_options**
> InlineResponse20018 set_move_options(body)

设置运动选项

设置在配送过程中采用的运动选项，比如采用自由导航还是轨道模式。当请求报文为空时表示删除已设置的内容，恢复默认选项。不需要包含包含所有字段，按需设置即可。

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DeliveryApi()
body = swagger_client.MoveOptions() # MoveOptions | 

try:
    # 设置运动选项
    api_response = api_instance.set_move_options(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DeliveryApi->set_move_options: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**MoveOptions**](MoveOptions.md)|  | 

### Return type

[**InlineResponse20018**](InlineResponse20018.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: text/plain

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **set_password**
> InlineResponse20018 set_password(body=body)

设置操作密码

如果enable为false，则表示禁用密码

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DeliveryApi()
body = swagger_client.AdminPasswordBody() # AdminPasswordBody |  (optional)

try:
    # 设置操作密码
    api_response = api_instance.set_password(body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DeliveryApi->set_password: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**AdminPasswordBody**](AdminPasswordBody.md)|  | [optional] 

### Return type

[**InlineResponse20018**](InlineResponse20018.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: text/plain

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **set_task_execution**
> TaskExecutionInfo set_task_execution(body=body)

暂停/继续执行任务

当用户操作APP时，设为false来禁止机器人移动，此时机器人即使收到任务也不会运行；用户完成操作时，设为true允许机器人运动，此时机器人有任务则执行任务，没任务则回桩或回到类型为PARKING的POI

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DeliveryApi()
body = swagger_client.TaskExecutionInfo() # TaskExecutionInfo |  (optional)

try:
    # 暂停/继续执行任务
    api_response = api_instance.set_task_execution(body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DeliveryApi->set_task_execution: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**TaskExecutionInfo**](TaskExecutionInfo.md)|  | [optional] 

### Return type

[**TaskExecutionInfo**](TaskExecutionInfo.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **set_timeout_settings**
> set_timeout_settings(body)

设置任务的超时时间

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DeliveryApi()
body = swagger_client.SettingsTimeoutBody() # SettingsTimeoutBody | 

try:
    # 设置任务的超时时间
    api_instance.set_timeout_settings(body)
except ApiException as e:
    print("Exception when calling DeliveryApi->set_timeout_settings: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**SettingsTimeoutBody**](SettingsTimeoutBody.md)|  | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **set_work_mode**
> InlineResponse20018 set_work_mode(body)

设置机器人工作模式

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DeliveryApi()
body = swagger_client.DeliveryWorkMode() # DeliveryWorkMode | 

try:
    # 设置机器人工作模式
    api_response = api_instance.set_work_mode(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DeliveryApi->set_work_mode: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**DeliveryWorkMode**](DeliveryWorkMode.md)|  | 

### Return type

[**InlineResponse20018**](InlineResponse20018.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: text/plain

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **set_working_time**
> InlineResponse20018 set_working_time(body)

设置机器人工作时间

<h4>所需最低固件版本 4.3.3</h4>

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DeliveryApi()
body = swagger_client.WorkingTime() # WorkingTime | 

try:
    # 设置机器人工作时间
    api_response = api_instance.set_working_time(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DeliveryApi->set_working_time: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**WorkingTime**](WorkingTime.md)|  | 

### Return type

[**InlineResponse20018**](InlineResponse20018.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: text/plain

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **start_pickup**
> start_pickup()

开始取物

通知机器人用户开始取物，一般用于带舱体的机器人，在该接口后再调用开舱指令进行取物，完成后调用end_pickup，如果任务包含多个舱体，则此时自动打开下一个舱门，上位机需要多次调用end_pickup。

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DeliveryApi()

try:
    # 开始取物
    api_instance.start_pickup()
except ApiException as e:
    print("Exception when calling DeliveryApi->start_pickup: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

