# swagger_client.MultiFloorApi

All URIs are relative to */*

Method | HTTP request | Description
------------- | ------------- | -------------
[**delete_map**](MultiFloorApi.md#delete_map) | **DELETE** /api/multi-floor/map/v1/stcm | 删除保存的地图
[**dispatch_by_pois**](MultiFloorApi.md#dispatch_by_pois) | **POST** /api/multi-floor/map/v1/pois/:dispatch | 查询POI的最优遍历顺序
[**get_all_pois**](MultiFloorApi.md#get_all_pois) | **GET** /api/multi-floor/map/v1/pois | 获取POI信息
[**get_current_floor**](MultiFloorApi.md#get_current_floor) | **GET** /api/multi-floor/map/v1/floors/:current | 获取机器人所在楼层信息
[**get_current_home_dock**](MultiFloorApi.md#get_current_home_dock) | **GET** /api/multi-floor/map/v1/homedocks/:current | 获取绑定的充电桩
[**get_elevators**](MultiFloorApi.md#get_elevators) | **GET** /api/multi-floor/map/v1/elevators | 获取电梯区域
[**get_elevators_by_id**](MultiFloorApi.md#get_elevators_by_id) | **GET** /api/multi-floor/map/v1/elevators/{elevator_id} | 获取某个电梯的信息
[**get_floors**](MultiFloorApi.md#get_floors) | **GET** /api/multi-floor/map/v1/floors | 获取所有楼层信息
[**get_mutil_floor_home_docks**](MultiFloorApi.md#get_mutil_floor_home_docks) | **GET** /api/multi-floor/map/v1/homedocks | 获取充电桩信息
[**get_pose_relation_to_elevator**](MultiFloorApi.md#get_pose_relation_to_elevator) | **GET** /api/multi-floor/map/v1/elevators/{elevator_id}/pose_relation | 获取机器人与电梯的位置关系
[**get_status**](MultiFloorApi.md#get_status) | **GET** /api/multi-floor/status | 获取地图状态信息
[**reload_stcm**](MultiFloorApi.md#reload_stcm) | **POST** /api/multi-floor/map/v1/stcm/:reload | 重新加载地图
[**save_stcm**](MultiFloorApi.md#save_stcm) | **POST** /api/multi-floor/map/v1/stcm/:save | 持久化保存当前地图
[**search_nearby_home_dock**](MultiFloorApi.md#search_nearby_home_dock) | **POST** /api/multi-floor/map/v1/homedocks/:search_nearby | 查找离机器人最近的充电桩
[**search_nearby_poi**](MultiFloorApi.md#search_nearby_poi) | **POST** /api/multi-floor/map/v1/pois/:search_nearby | 查找最近的POI
[**search_path_points_in_graph**](MultiFloorApi.md#search_path_points_in_graph) | **POST** /api/multi-floor/map/v1/search_path_points | 通过轨道搜索路径点
[**set_current_floor**](MultiFloorApi.md#set_current_floor) | **PUT** /api/multi-floor/map/v1/floors/:current | 设置机器人所在楼层信息
[**set_current_home_dock**](MultiFloorApi.md#set_current_home_dock) | **PUT** /api/multi-floor/map/v1/homedocks/:current | 绑定充电桩
[**set_pose_by_homedock**](MultiFloorApi.md#set_pose_by_homedock) | **PUT** /api/multi-floor/localization/v1/homedock | 根据充电桩重置机器人定位
[**set_pose_by_poi**](MultiFloorApi.md#set_pose_by_poi) | **PUT** /api/multi-floor/localization/v1/pose | 设置机器人位姿
[**sync_stcm**](MultiFloorApi.md#sync_stcm) | **POST** /api/multi-floor/map/v1/stcm/:sync | 同步地图
[**unbind_scene**](MultiFloorApi.md#unbind_scene) | **POST** /api/multi-floor/map/v1/scene/unbind | 解绑云端场景
[**upload_map**](MultiFloorApi.md#upload_map) | **POST** /api/multi-floor/map/v1/stcm | 上传地图到机器人

# **delete_map**
> delete_map()

删除保存的地图

不会清空内存中的当前地图，而是删除文件系统中缓存的地图

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.MultiFloorApi()

try:
    # 删除保存的地图
    api_instance.delete_map()
except ApiException as e:
    print("Exception when calling MultiFloorApi->delete_map: %s\n" % e)
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

# **dispatch_by_pois**
> list[str] dispatch_by_pois(body)

查询POI的最优遍历顺序

给定若干个POI名称，返回调整顺序后的POI名称，使得机器人依次遍历这些POI并回到当前位置的总路径最短。</br>【注】该接口耗时随着POI数量指数增长，请勿传入大量POI。<h4>所需最低固件版本 4.5.0</h4>

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.MultiFloorApi()
body = ['body_example'] # list[str] | 

try:
    # 查询POI的最优遍历顺序
    api_response = api_instance.dispatch_by_pois(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling MultiFloorApi->dispatch_by_pois: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**list[str]**](str.md)|  | 

### Return type

**list[str]**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_all_pois**
> list[MultiFloorPoiInfo] get_all_pois(floor=floor, building=building)

获取POI信息

通过参数指定楼层，不带参数时获取所有楼层的POI。

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.MultiFloorApi()
floor = 'floor_example' # str | 楼层名 (optional)
building = '' # str | 建筑物名 (optional)

try:
    # 获取POI信息
    api_response = api_instance.get_all_pois(floor=floor, building=building)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling MultiFloorApi->get_all_pois: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **floor** | **str**| 楼层名 | [optional] 
 **building** | **str**| 建筑物名 | [optional] 

### Return type

[**list[MultiFloorPoiInfo]**](MultiFloorPoiInfo.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_current_floor**
> CurrentFloorInfo get_current_floor()

获取机器人所在楼层信息

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.MultiFloorApi()

try:
    # 获取机器人所在楼层信息
    api_response = api_instance.get_current_floor()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling MultiFloorApi->get_current_floor: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**CurrentFloorInfo**](CurrentFloorInfo.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_current_home_dock**
> InlineResponse20015 get_current_home_dock()

获取绑定的充电桩

获取机器人当前绑定的充电桩信息，如果没绑定过或dock id无效，返回的result为false。

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.MultiFloorApi()

try:
    # 获取绑定的充电桩
    api_response = api_instance.get_current_home_dock()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling MultiFloorApi->get_current_home_dock: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**InlineResponse20015**](InlineResponse20015.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_elevators**
> list[ElevatorInfo] get_elevators()

获取电梯区域

获取电梯区域内的元素，包括电梯ID以及等待点。

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.MultiFloorApi()

try:
    # 获取电梯区域
    api_response = api_instance.get_elevators()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling MultiFloorApi->get_elevators: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**list[ElevatorInfo]**](ElevatorInfo.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_elevators_by_id**
> ElevatorInfo get_elevators_by_id(elevator_id)

获取某个电梯的信息

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.MultiFloorApi()
elevator_id = 'elevator_id_example' # str | 

try:
    # 获取某个电梯的信息
    api_response = api_instance.get_elevators_by_id(elevator_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling MultiFloorApi->get_elevators_by_id: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **elevator_id** | **str**|  | 

### Return type

[**ElevatorInfo**](ElevatorInfo.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_floors**
> list[FloorInfo] get_floors()

获取所有楼层信息

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.MultiFloorApi()

try:
    # 获取所有楼层信息
    api_response = api_instance.get_floors()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling MultiFloorApi->get_floors: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**list[FloorInfo]**](FloorInfo.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_mutil_floor_home_docks**
> list[MultiFloorDockInfo] get_mutil_floor_home_docks(floor=floor, building=building)

获取充电桩信息

通过Query参数指定楼层，不带参数时获取所有楼层的充电桩

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.MultiFloorApi()
floor = 'floor_example' # str | 楼层名 (optional)
building = '' # str | 建筑物名 (optional)

try:
    # 获取充电桩信息
    api_response = api_instance.get_mutil_floor_home_docks(floor=floor, building=building)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling MultiFloorApi->get_mutil_floor_home_docks: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **floor** | **str**| 楼层名 | [optional] 
 **building** | **str**| 建筑物名 | [optional] 

### Return type

[**list[MultiFloorDockInfo]**](MultiFloorDockInfo.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_pose_relation_to_elevator**
> str get_pose_relation_to_elevator(elevator_id)

获取机器人与电梯的位置关系

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.MultiFloorApi()
elevator_id = 'elevator_id_example' # str | 

try:
    # 获取机器人与电梯的位置关系
    api_response = api_instance.get_pose_relation_to_elevator(elevator_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling MultiFloorApi->get_pose_relation_to_elevator: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **elevator_id** | **str**|  | 

### Return type

**str**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_status**
> InlineResponse20014 get_status()

获取地图状态信息

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.MultiFloorApi()

try:
    # 获取地图状态信息
    api_response = api_instance.get_status()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling MultiFloorApi->get_status: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**InlineResponse20014**](InlineResponse20014.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **reload_stcm**
> reload_stcm(body=body)

重新加载地图

重新加载地图，优先尝试从云端下载，下载失败或机器人不受云端管理时从本地文件读取。<br/> pose为可选字段，pose为空时设置机器人位姿到充电桩前。 <br/>【注意】系统启动时会自动加载地图，该接口一般在部署阶段地图有变更时才需要调用。

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.MultiFloorApi()
body = swagger_client.StcmReloadBody() # StcmReloadBody |  (optional)

try:
    # 重新加载地图
    api_instance.reload_stcm(body=body)
except ApiException as e:
    print("Exception when calling MultiFloorApi->reload_stcm: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**StcmReloadBody**](StcmReloadBody.md)|  | [optional] 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **save_stcm**
> save_stcm()

持久化保存当前地图

从Slamware中读取地图并保存到文件。<br/> 【注意】 多楼层环境中禁止该操作，否则会丢失其他楼层的地图。

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.MultiFloorApi()

try:
    # 持久化保存当前地图
    api_instance.save_stcm()
except ApiException as e:
    print("Exception when calling MultiFloorApi->save_stcm: %s\n" % e)
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

# **search_nearby_home_dock**
> MultiFloorDockInfo search_nearby_home_dock()

查找离机器人最近的充电桩

调用该接口前请确保机器人定位准确。

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.MultiFloorApi()

try:
    # 查找离机器人最近的充电桩
    api_response = api_instance.search_nearby_home_dock()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling MultiFloorApi->search_nearby_home_dock: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**MultiFloorDockInfo**](MultiFloorDockInfo.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **search_nearby_poi**
> NearbyPoiInfo search_nearby_poi()

查找最近的POI

查找离机器人最近的POI信息。其中name有三个特殊值，ON_DOCK表示在桩上，IN_ELEVATOR表示在电梯内，UNKNOWN表示没有POI，此时没有relative_pose字段，其他的值均表示地图中添加的常规POI的名称。

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.MultiFloorApi()

try:
    # 查找最近的POI
    api_response = api_instance.search_nearby_poi()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling MultiFloorApi->search_nearby_poi: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**NearbyPoiInfo**](NearbyPoiInfo.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **search_path_points_in_graph**
> InlineResponse2007 search_path_points_in_graph(body)

通过轨道搜索路径点

在轨道构成的图中，搜索起点到终点的可行路径。

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.MultiFloorApi()
body = swagger_client.V1SearchPathPointsBody() # V1SearchPathPointsBody | 

try:
    # 通过轨道搜索路径点
    api_response = api_instance.search_path_points_in_graph(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling MultiFloorApi->search_path_points_in_graph: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**V1SearchPathPointsBody**](V1SearchPathPointsBody.md)|  | 

### Return type

[**InlineResponse2007**](InlineResponse2007.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **set_current_floor**
> set_current_floor(body)

设置机器人所在楼层信息

正常情况下应当由机器人在乘坐电梯过程中自主切换楼层，该接口仅供特殊情况下（如人工搬运机器人）使用。

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.MultiFloorApi()
body = swagger_client.FloorsCurrentBody() # FloorsCurrentBody | 

try:
    # 设置机器人所在楼层信息
    api_instance.set_current_floor(body)
except ApiException as e:
    print("Exception when calling MultiFloorApi->set_current_floor: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**FloorsCurrentBody**](FloorsCurrentBody.md)|  | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **set_current_home_dock**
> set_current_home_dock(body=body)

绑定充电桩

【注意】如果绑定的充电桩不在启动楼层，则需要先将机器人推到充电桩上，然后调用本接口，此时会同步修改启动楼层并重置地图。

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.MultiFloorApi()
body = swagger_client.HomedocksCurrentBody() # HomedocksCurrentBody |  (optional)

try:
    # 绑定充电桩
    api_instance.set_current_home_dock(body=body)
except ApiException as e:
    print("Exception when calling MultiFloorApi->set_current_home_dock: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**HomedocksCurrentBody**](HomedocksCurrentBody.md)|  | [optional] 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **set_pose_by_homedock**
> set_pose_by_homedock(body=body)

根据充电桩重置机器人定位

将机器人位姿设置到指定的充电桩前，一般用于发生异常后的恢复操作。<h4>所需最低固件版本 6.2.0</h4>

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.MultiFloorApi()
body = swagger_client.V1HomedockBody() # V1HomedockBody |  (optional)

try:
    # 根据充电桩重置机器人定位
    api_instance.set_pose_by_homedock(body=body)
except ApiException as e:
    print("Exception when calling MultiFloorApi->set_pose_by_homedock: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**V1HomedockBody**](V1HomedockBody.md)|  | [optional] 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **set_pose_by_poi**
> bool set_pose_by_poi(body=body)

设置机器人位姿

将机器人位姿设置到指定的POI上，一般用于发生异常后的恢复操作。<h4>所需最低固件版本 4.5.3</h4>

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.MultiFloorApi()
body = swagger_client.V1PoseBody() # V1PoseBody |  (optional)

try:
    # 设置机器人位姿
    api_response = api_instance.set_pose_by_poi(body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling MultiFloorApi->set_pose_by_poi: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**V1PoseBody**](V1PoseBody.md)|  | [optional] 

### Return type

**bool**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **sync_stcm**
> sync_stcm()

同步地图

保存当前地图到文件，并重新加载，相当于save和reload 2个接口的组合。<br/>【注意】 多楼层环境中禁止该操作，否则会丢失其他楼层的地图。<h4>所需最低固件版本  4.2.4</h4>

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.MultiFloorApi()

try:
    # 同步地图
    api_instance.sync_stcm()
except ApiException as e:
    print("Exception when calling MultiFloorApi->sync_stcm: %s\n" % e)
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

# **unbind_scene**
> unbind_scene(body=body)

解绑云端场景

将机器人与云端场景解除绑定，并删除本地地图，在机器人需要换场景部署时调用。<h4>所需最低固件版本  6.2.0</h4>

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.MultiFloorApi()
body = swagger_client.SceneUnbindBody() # SceneUnbindBody |  (optional)

try:
    # 解绑云端场景
    api_instance.unbind_scene(body=body)
except ApiException as e:
    print("Exception when calling MultiFloorApi->unbind_scene: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**SceneUnbindBody**](SceneUnbindBody.md)|  | [optional] 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **upload_map**
> upload_map(body=body)

上传地图到机器人

上传的地图会持久化保存在文件系统中, 但不会加载到Slamware中。<br/> 【注意】当机器人由云端管理时，从云端下载的地图会覆盖本地地图。

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.MultiFloorApi()
body = swagger_client.Object() # Object |  (optional)

try:
    # 上传地图到机器人
    api_instance.upload_map(body=body)
except ApiException as e:
    print("Exception when calling MultiFloorApi->upload_map: %s\n" % e)
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

