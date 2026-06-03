# swagger_client.SlamApi

All URIs are relative to */*

Method | HTTP request | Description
------------- | ------------- | -------------
[**add_home_dock**](SlamApi.md#add_home_dock) | **POST** /api/core/slam/v1/homedocks | 添加充电桩
[**clear_home_docks**](SlamApi.md#clear_home_docks) | **DELETE** /api/core/slam/v1/homedocks | 清空充电桩信息
[**clear_map**](SlamApi.md#clear_map) | **DELETE** /api/core/slam/v1/maps | 清空地图
[**edit_home_dock**](SlamApi.md#edit_home_dock) | **PUT** /api/core/slam/v1/homedocks/{dock_id} | 编辑充电桩信息
[**erase_home_dock**](SlamApi.md#erase_home_dock) | **DELETE** /api/core/slam/v1/homedocks/{dock_id} | 移除一个充电桩
[**get_composite_map**](SlamApi.md#get_composite_map) | **GET** /api/core/slam/v1/maps/stcm | 获取复合地图
[**get_explore_map**](SlamApi.md#get_explore_map) | **GET** /api/core/slam/v1/maps/explore | 获取栅格地图
[**get_home_docks**](SlamApi.md#get_home_docks) | **GET** /api/core/slam/v1/homedocks | 获取所有充电桩信息
[**get_home_pose**](SlamApi.md#get_home_pose) | **GET** /api/core/slam/v1/homepose | 获取充电桩位置
[**get_imu**](SlamApi.md#get_imu) | **GET** /api/core/slam/v1/imu | 获取IMU数据
[**get_known_area**](SlamApi.md#get_known_area) | **GET** /api/core/slam/v1/knownarea | 获取已知区域
[**get_localization_quality**](SlamApi.md#get_localization_quality) | **GET** /api/core/slam/v1/localization/quality | 获取定位质量
[**get_loop_closure**](SlamApi.md#get_loop_closure) | **GET** /api/core/slam/v1/loopclosure/:enable | 是否开启闭环检测
[**get_map_localization**](SlamApi.md#get_map_localization) | **GET** /api/core/slam/v1/localization/:enable | 是否支持定位
[**get_map_update**](SlamApi.md#get_map_update) | **GET** /api/core/slam/v1/mapping/:enable | 是否开启建图
[**get_odo_pose**](SlamApi.md#get_odo_pose) | **GET** /api/core/slam/v1/localization/odopose | 获取机器人里程计位姿
[**get_pose**](SlamApi.md#get_pose) | **GET** /api/core/slam/v1/localization/pose | 获取机器人位姿
[**move_origin_point**](SlamApi.md#move_origin_point) | **PUT** /api/core/slam/v1/maps/origin | 移动地图原点
[**register_home_dock**](SlamApi.md#register_home_dock) | **POST** /api/core/slam/v1/homedocks/:register | 注册充电桩
[**reset_localization_status**](SlamApi.md#reset_localization_status) | **POST** /api/core/slam/v1/localization/status/:reset | 重置定位状态
[**set_composite_map**](SlamApi.md#set_composite_map) | **PUT** /api/core/slam/v1/maps/stcm | 设置复合地图
[**set_home_docks**](SlamApi.md#set_home_docks) | **PUT** /api/core/slam/v1/homedocks | 设置所有充电桩
[**set_home_pose**](SlamApi.md#set_home_pose) | **PUT** /api/core/slam/v1/homepose | 设置充电桩位置
[**set_loop_closure**](SlamApi.md#set_loop_closure) | **PUT** /api/core/slam/v1/loopclosure/:enable | 开启/暂停闭环检测
[**set_map_localization**](SlamApi.md#set_map_localization) | **PUT** /api/core/slam/v1/localization/:enable | 开启/暂停定位
[**set_map_update**](SlamApi.md#set_map_update) | **PUT** /api/core/slam/v1/mapping/:enable | 开启/暂停建图
[**set_pose**](SlamApi.md#set_pose) | **PUT** /api/core/slam/v1/localization/pose | 设置机器人位姿

# **add_home_dock**
> bool add_home_dock(body)

添加充电桩

给机器人添加一个充电桩，metadata需要display_name字段，表示充电桩名称。

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.SlamApi()
body = swagger_client.PoseEntry() # PoseEntry | 

try:
    # 添加充电桩
    api_response = api_instance.add_home_dock(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SlamApi->add_home_dock: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**PoseEntry**](PoseEntry.md)|  | 

### Return type

**bool**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **clear_home_docks**
> PoseEntry clear_home_docks()

清空充电桩信息

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.SlamApi()

try:
    # 清空充电桩信息
    api_response = api_instance.clear_home_docks()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SlamApi->clear_home_docks: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**PoseEntry**](PoseEntry.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **clear_map**
> clear_map()

清空地图

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.SlamApi()

try:
    # 清空地图
    api_instance.clear_map()
except ApiException as e:
    print("Exception when calling SlamApi->clear_map: %s\n" % e)
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

# **edit_home_dock**
> bool edit_home_dock(body, dock_id)

编辑充电桩信息

编辑充电桩信息，id不可修改，只允许修改pose和metadata

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.SlamApi()
body = swagger_client.HomedocksDockIdBody() # HomedocksDockIdBody | 
dock_id = '38400000-8cf0-11bd-b23e-10b96e4ef00d' # str | 

try:
    # 编辑充电桩信息
    api_response = api_instance.edit_home_dock(body, dock_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SlamApi->edit_home_dock: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**HomedocksDockIdBody**](HomedocksDockIdBody.md)|  | 
 **dock_id** | [**str**](.md)|  | 

### Return type

**bool**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **erase_home_dock**
> bool erase_home_dock(dock_id)

移除一个充电桩

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.SlamApi()
dock_id = '38400000-8cf0-11bd-b23e-10b96e4ef00d' # str | 

try:
    # 移除一个充电桩
    api_response = api_instance.erase_home_dock(dock_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SlamApi->erase_home_dock: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **dock_id** | [**str**](.md)|  | 

### Return type

**bool**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_composite_map**
> str get_composite_map()

获取复合地图

包含所有数据的复合地图 </br> 响应报文为二进制字节流，可直接保存为stcm文件.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.SlamApi()

try:
    # 获取复合地图
    api_response = api_instance.get_composite_map()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SlamApi->get_composite_map: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

**str**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/octet-stream

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_explore_map**
> str get_explore_map(min_x=min_x, min_y=min_y, max_x=max_x, max_y=max_y)

获取栅格地图

获取激光探索的栅格地图, 可通过min_x, min_y, max_x, max_y指定获取的范围, 默认获取全部地图. </br> 响应报文为二进制字节流，前32字节为元数据(低位字节在前)，后续为地图数据。 <table border=\"1\" cellspacing='6'><tr><td>位置</td><td>数据类型</td><td>描述</td></tr><tr><td>0-3</td><td>float</td><td>地图起始位置的X坐标</td></tr><tr><td>4-7</td><td>float</td><td>地图起始位置的Y坐标</td></tr><tr><td>8-11</td><td>uint32</td><td>X轴方向栅格数量</td></tr><tr><td>12-15</td><td>uint32</td><td>Y轴方向栅格数量</td></tr><tr><td>16-19</td><td>float</td><td>地图分辨率，每个格子的边长，单位米</td></tr><tr><td>20-31</td><td>byte[]</td><td>预留</td></tr><tr><td>32-35</td><td>uint32</td><td>后续数据的字节数，该值应当等于X轴栅格数*Y轴栅格数</td></tr><tr><td>36-End</td><td>byte[]</td><td>地图数据，每个字节代表一个格子</td></tr></table> 

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.SlamApi()
min_x = 1.2 # float |  (optional)
min_y = 1.2 # float |  (optional)
max_x = 1.2 # float |  (optional)
max_y = 1.2 # float |  (optional)

try:
    # 获取栅格地图
    api_response = api_instance.get_explore_map(min_x=min_x, min_y=min_y, max_x=max_x, max_y=max_y)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SlamApi->get_explore_map: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **min_x** | **float**|  | [optional] 
 **min_y** | **float**|  | [optional] 
 **max_x** | **float**|  | [optional] 
 **max_y** | **float**|  | [optional] 

### Return type

**str**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/octet-stream

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_home_docks**
> list[PoseEntry] get_home_docks()

获取所有充电桩信息

获取机器人的所有充电桩信息。<h4>所需最低固件版本 4.3.2</h4>

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.SlamApi()

try:
    # 获取所有充电桩信息
    api_response = api_instance.get_home_docks()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SlamApi->get_home_docks: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**list[PoseEntry]**](PoseEntry.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_home_pose**
> Pose3D get_home_pose()

获取充电桩位置

获取当前的充电桩位置，如果当前地图中不存在充电桩，则返回404错误

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.SlamApi()

try:
    # 获取充电桩位置
    api_response = api_instance.get_home_pose()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SlamApi->get_home_pose: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**Pose3D**](Pose3D.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_imu**
> ImuData get_imu()

获取IMU数据

获取以机器人坐标系表示的IMU数据

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.SlamApi()

try:
    # 获取IMU数据
    api_response = api_instance.get_imu()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SlamApi->get_imu: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**ImuData**](ImuData.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_known_area**
> Rectangle get_known_area()

获取已知区域

已知区域即当前地图的范围, 机器人的活动空间和各种人工标记元素都应当在此范围内

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.SlamApi()

try:
    # 获取已知区域
    api_response = api_instance.get_known_area()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SlamApi->get_known_area: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**Rectangle**](Rectangle.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_localization_quality**
> int get_localization_quality()

获取定位质量

定位质量范围 0 ~ 100，值越大表示定位越好

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.SlamApi()

try:
    # 获取定位质量
    api_response = api_instance.get_localization_quality()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SlamApi->get_localization_quality: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

**int**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_loop_closure**
> bool get_loop_closure()

是否开启闭环检测

<h4>所需最低固件版本 4.6.0</h4>

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.SlamApi()

try:
    # 是否开启闭环检测
    api_response = api_instance.get_loop_closure()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SlamApi->get_loop_closure: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

**bool**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_map_localization**
> bool get_map_localization()

是否支持定位

返回值true表示支持定位，false表示暂停定位即纯里程模式

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.SlamApi()

try:
    # 是否支持定位
    api_response = api_instance.get_map_localization()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SlamApi->get_map_localization: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

**bool**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_map_update**
> bool get_map_update()

是否开启建图

返回值true表示建图模式，false表示定位模式

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.SlamApi()

try:
    # 是否开启建图
    api_response = api_instance.get_map_update()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SlamApi->get_map_update: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

**bool**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_odo_pose**
> Pose3D get_odo_pose()

获取机器人里程计位姿

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.SlamApi()

try:
    # 获取机器人里程计位姿
    api_response = api_instance.get_odo_pose()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SlamApi->get_odo_pose: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**Pose3D**](Pose3D.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_pose**
> Pose3D get_pose()

获取机器人位姿

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.SlamApi()

try:
    # 获取机器人位姿
    api_response = api_instance.get_pose()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SlamApi->get_pose: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**Pose3D**](Pose3D.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **move_origin_point**
> move_origin_point(body)

移动地图原点

移动地图原点,并更新到slamware系统中

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.SlamApi()
body = swagger_client.MapsOriginBody() # MapsOriginBody | 

try:
    # 移动地图原点
    api_instance.move_origin_point(body)
except ApiException as e:
    print("Exception when calling SlamApi->move_origin_point: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**MapsOriginBody**](MapsOriginBody.md)|  | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **register_home_dock**
> PoseEntry register_home_dock(body)

注册充电桩

根据机器人当前位置在地图上注册一个充电桩

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.SlamApi()
body = swagger_client.HomedocksRegisterBody() # HomedocksRegisterBody | 

try:
    # 注册充电桩
    api_response = api_instance.register_home_dock(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SlamApi->register_home_dock: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**HomedocksRegisterBody**](HomedocksRegisterBody.md)|  | 

### Return type

[**PoseEntry**](PoseEntry.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **reset_localization_status**
> bool reset_localization_status()

重置定位状态

将定位状态重置

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.SlamApi()

try:
    # 重置定位状态
    api_response = api_instance.reset_localization_status()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SlamApi->reset_localization_status: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

**bool**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **set_composite_map**
> set_composite_map(body=body)

设置复合地图

将地图设置到slamware系统中, 以二进制方式读取stcm文件作为request body。</br>机器人位姿会被重置到原点，需要重新设置机器人位姿.<br/> 【注意】地图不会持久化保存，重启后即失效

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.SlamApi()
body = swagger_client.Object() # Object |  (optional)

try:
    # 设置复合地图
    api_instance.set_composite_map(body=body)
except ApiException as e:
    print("Exception when calling SlamApi->set_composite_map: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | **Object**|  | [optional] 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/octet-stream
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **set_home_docks**
> bool set_home_docks(body=body)

设置所有充电桩

设置机器人的所有充电桩信息。<h4>所需最低固件版本 4.3.2</h4>

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.SlamApi()
body = [swagger_client.PoseEntry()] # list[PoseEntry] |  (optional)

try:
    # 设置所有充电桩
    api_response = api_instance.set_home_docks(body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SlamApi->set_home_docks: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**list[PoseEntry]**](PoseEntry.md)|  | [optional] 

### Return type

**bool**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **set_home_pose**
> bool set_home_pose(body=body)

设置充电桩位置

设置当前的充电桩位置，当地图中存在多个充电桩时，需要上位机设置其中一个作为当前使用的桩。

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.SlamApi()
body = swagger_client.Pose3D() # Pose3D |  (optional)

try:
    # 设置充电桩位置
    api_response = api_instance.set_home_pose(body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SlamApi->set_home_pose: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Pose3D**](Pose3D.md)|  | [optional] 

### Return type

**bool**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **set_loop_closure**
> bool set_loop_closure(body=body)

开启/暂停闭环检测

返回值true表示操作成功<h4>所需最低固件版本 4.6.0</h4>

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.SlamApi()
body = swagger_client.LoopclosureEnableBody() # LoopclosureEnableBody |  (optional)

try:
    # 开启/暂停闭环检测
    api_response = api_instance.set_loop_closure(body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SlamApi->set_loop_closure: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**LoopclosureEnableBody**](LoopclosureEnableBody.md)|  | [optional] 

### Return type

**bool**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **set_map_localization**
> bool set_map_localization(body=body)

开启/暂停定位

返回值true表示操作成功

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.SlamApi()
body = swagger_client.LocalizationEnableBody() # LocalizationEnableBody |  (optional)

try:
    # 开启/暂停定位
    api_response = api_instance.set_map_localization(body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SlamApi->set_map_localization: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**LocalizationEnableBody**](LocalizationEnableBody.md)|  | [optional] 

### Return type

**bool**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **set_map_update**
> bool set_map_update(body=body)

开启/暂停建图

返回值true表示操作成功

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.SlamApi()
body = swagger_client.MappingEnableBody() # MappingEnableBody |  (optional)

try:
    # 开启/暂停建图
    api_response = api_instance.set_map_update(body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SlamApi->set_map_update: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**MappingEnableBody**](MappingEnableBody.md)|  | [optional] 

### Return type

**bool**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **set_pose**
> set_pose(body=body)

设置机器人位姿

将机器人强制设置到地图中的某个位置

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.SlamApi()
body = swagger_client.Pose3D() # Pose3D |  (optional)

try:
    # 设置机器人位姿
    api_instance.set_pose(body=body)
except ApiException as e:
    print("Exception when calling SlamApi->set_pose: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Pose3D**](Pose3D.md)|  | [optional] 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

