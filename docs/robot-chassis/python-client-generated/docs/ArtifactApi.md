# swagger_client.ArtifactApi

All URIs are relative to */*

Method | HTTP request | Description
------------- | ------------- | -------------
[**add_lines**](ArtifactApi.md#add_lines) | **POST** /api/core/artifact/v1/lines/{usage} | 添加虚拟线段
[**add_pois**](ArtifactApi.md#add_pois) | **POST** /api/core/artifact/v1/pois | 添加POI
[**add_rectangle_area**](ArtifactApi.md#add_rectangle_area) | **POST** /api/core/artifact/v1/rectangle-areas/{usage} | 添加矩形区域
[**adjust_pois**](ArtifactApi.md#adjust_pois) | **POST** /api/core/artifact/v1/pois/:adjust | 优化POI位姿
[**clear_lines**](ArtifactApi.md#clear_lines) | **DELETE** /api/core/artifact/v1/lines/{usage} | 清空某一类虚拟线段
[**clear_pois**](ArtifactApi.md#clear_pois) | **DELETE** /api/core/artifact/v1/pois | 清空POI
[**clear_rectangle_areas**](ArtifactApi.md#clear_rectangle_areas) | **DELETE** /api/core/artifact/v1/rectangle-areas/{usage} | 清空某一类矩形区域
[**delete_laser_landmarks**](ArtifactApi.md#delete_laser_landmarks) | **DELETE** /api/core/artifact/v1/laser-landmarks | 清空激光地标
[**delete_poi**](ArtifactApi.md#delete_poi) | **DELETE** /api/core/artifact/v1/pois/{poi_id} | 删除POI
[**edit_rectangle_area**](ArtifactApi.md#edit_rectangle_area) | **PUT** /api/core/artifact/v1/rectangle-areas/{usage}/{id} | 编辑矩形区域
[**get_current_pois**](ArtifactApi.md#get_current_pois) | **GET** /api/core/artifact/v1/pois | 获取当前地图中的所有POI
[**get_laser_landmark_update**](ArtifactApi.md#get_laser_landmark_update) | **GET** /api/core/artifact/v1/laser-landmarks/:update | 获取激光地标更新状态
[**get_laser_landmarks**](ArtifactApi.md#get_laser_landmarks) | **GET** /api/core/artifact/v1/laser-landmarks | 获取激光地标
[**get_lines**](ArtifactApi.md#get_lines) | **GET** /api/core/artifact/v1/lines/{usage} | 获取虚拟线段
[**get_poi_by_id**](ArtifactApi.md#get_poi_by_id) | **GET** /api/core/artifact/v1/pois/{poi_id} | 根据ID查找POI
[**get_rectangle_areas**](ArtifactApi.md#get_rectangle_areas) | **GET** /api/core/artifact/v1/rectangle-areas/{usage} | 获取矩形区域
[**modify_lines**](ArtifactApi.md#modify_lines) | **PUT** /api/core/artifact/v1/lines/{usage} | 修改虚拟线段
[**modify_poi**](ArtifactApi.md#modify_poi) | **PUT** /api/core/artifact/v1/pois/{poi_id} | 修改POI
[**put_laser_landmarks**](ArtifactApi.md#put_laser_landmarks) | **PUT** /api/core/artifact/v1/laser-landmarks | 设置激光地标
[**remove_laser_landmarks**](ArtifactApi.md#remove_laser_landmarks) | **POST** /api/core/artifact/v1/laser-landmarks/:remove | 删除激光地标
[**remove_line_by_id**](ArtifactApi.md#remove_line_by_id) | **DELETE** /api/core/artifact/v1/lines/{usage}/{id} | 删除虚拟线段
[**remove_rectangle_area_by_id**](ArtifactApi.md#remove_rectangle_area_by_id) | **DELETE** /api/core/artifact/v1/rectangle-areas/{usage}/{id} | 删除矩形区域
[**set_laser_landmark_update**](ArtifactApi.md#set_laser_landmark_update) | **PUT** /api/core/artifact/v1/laser-landmarks/:update | 设置取激光地标更新状态

# **add_lines**
> bool add_lines(usage, body=body)

添加虚拟线段

添加时id为无效字段，可为任意值。

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.ArtifactApi()
usage = 'usage_example' # str | * `tracks` 虚拟轨道 * `walls` 虚拟墙 
body = [swagger_client.Line()] # list[Line] |  (optional)

try:
    # 添加虚拟线段
    api_response = api_instance.add_lines(usage, body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ArtifactApi->add_lines: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **usage** | **str**| * &#x60;tracks&#x60; 虚拟轨道 * &#x60;walls&#x60; 虚拟墙  | 
 **body** | [**list[Line]**](Line.md)|  | [optional] 

### Return type

**bool**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **add_pois**
> add_pois(body)

添加POI

调用方应当随机生成一个UUID作为id, metadata中的display_name用于界面显示, type用于区分POI类型。<br/> 在建图过程中添加POI时，建议不包含Pose，此时会用机器人当前位置创建POI，并且记录传感器观测信息，在闭环后会进行位姿调整。

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.ArtifactApi()
body = swagger_client.PoseEntry() # PoseEntry | 

try:
    # 添加POI
    api_instance.add_pois(body)
except ApiException as e:
    print("Exception when calling ArtifactApi->add_pois: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**PoseEntry**](PoseEntry.md)|  | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **add_rectangle_area**
> bool add_rectangle_area(usage, body=body)

添加矩形区域

不同类型的矩形区域，所需要的metadata也不同，请参考文档描述。

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.ArtifactApi()
usage = swagger_client.RectangleAreaUsage() # RectangleAreaUsage | 
body = swagger_client.RectangleareasUsageBody() # RectangleareasUsageBody |  (optional)

try:
    # 添加矩形区域
    api_response = api_instance.add_rectangle_area(usage, body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ArtifactApi->add_rectangle_area: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **usage** | [**RectangleAreaUsage**](.md)|  | 
 **body** | [**RectangleareasUsageBody**](RectangleareasUsageBody.md)|  | [optional] 

### Return type

**bool**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **adjust_pois**
> adjust_pois()

优化POI位姿

如果在建图时添加POI，则在闭环后POI会跟着调整位姿，调用该接口可以进一步减少位姿调整的误差。<br/> 【注意】仅在闭环后调用有效，其他时候无需调用。<h4>所需最低固件版本  4.2.4</h4>

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.ArtifactApi()

try:
    # 优化POI位姿
    api_instance.adjust_pois()
except ApiException as e:
    print("Exception when calling ArtifactApi->adjust_pois: %s\n" % e)
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

# **clear_lines**
> bool clear_lines(usage)

清空某一类虚拟线段

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.ArtifactApi()
usage = 'usage_example' # str | * `tracks` 虚拟轨道 * `walls` 虚拟墙 

try:
    # 清空某一类虚拟线段
    api_response = api_instance.clear_lines(usage)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ArtifactApi->clear_lines: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **usage** | **str**| * &#x60;tracks&#x60; 虚拟轨道 * &#x60;walls&#x60; 虚拟墙  | 

### Return type

**bool**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **clear_pois**
> bool clear_pois()

清空POI

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.ArtifactApi()

try:
    # 清空POI
    api_response = api_instance.clear_pois()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ArtifactApi->clear_pois: %s\n" % e)
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

# **clear_rectangle_areas**
> bool clear_rectangle_areas(usage)

清空某一类矩形区域

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.ArtifactApi()
usage = swagger_client.RectangleAreaUsage() # RectangleAreaUsage | 

try:
    # 清空某一类矩形区域
    api_response = api_instance.clear_rectangle_areas(usage)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ArtifactApi->clear_rectangle_areas: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **usage** | [**RectangleAreaUsage**](.md)|  | 

### Return type

**bool**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_laser_landmarks**
> bool delete_laser_landmarks()

清空激光地标

清空所有激光地标<h4>所需最低固件版本：5.1.1</h4>

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.ArtifactApi()

try:
    # 清空激光地标
    api_response = api_instance.delete_laser_landmarks()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ArtifactApi->delete_laser_landmarks: %s\n" % e)
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

# **delete_poi**
> bool delete_poi(poi_id)

删除POI

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.ArtifactApi()
poi_id = '38400000-8cf0-11bd-b23e-10b96e4ef00d' # str | 

try:
    # 删除POI
    api_response = api_instance.delete_poi(poi_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ArtifactApi->delete_poi: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **poi_id** | [**str**](.md)|  | 

### Return type

**bool**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **edit_rectangle_area**
> bool edit_rectangle_area(usage, id, body=body)

编辑矩形区域

修改指定ID的矩形区域坐标或metadata。

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.ArtifactApi()
usage = swagger_client.RectangleAreaUsage() # RectangleAreaUsage | 
id = 56 # int | 
body = swagger_client.UsageIdBody() # UsageIdBody |  (optional)

try:
    # 编辑矩形区域
    api_response = api_instance.edit_rectangle_area(usage, id, body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ArtifactApi->edit_rectangle_area: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **usage** | [**RectangleAreaUsage**](.md)|  | 
 **id** | **int**|  | 
 **body** | [**UsageIdBody**](UsageIdBody.md)|  | [optional] 

### Return type

**bool**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_current_pois**
> list[PoseEntry] get_current_pois()

获取当前地图中的所有POI

POI指Point of interest, 也称为星标或兴趣点，用于标记地图上的某个位姿，以及若干与业务逻辑相关的metadata。

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.ArtifactApi()

try:
    # 获取当前地图中的所有POI
    api_response = api_instance.get_current_pois()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ArtifactApi->get_current_pois: %s\n" % e)
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

# **get_laser_landmark_update**
> bool get_laser_landmark_update()

获取激光地标更新状态

Slamware是否正在自动更新激光地标<h4>所需最低固件版本：5.1.1</h4>

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.ArtifactApi()

try:
    # 获取激光地标更新状态
    api_response = api_instance.get_laser_landmark_update()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ArtifactApi->get_laser_landmark_update: %s\n" % e)
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

# **get_laser_landmarks**
> list[PoseEntry] get_laser_landmarks()

获取激光地标

激光地标指激光雷达识别到的反光板位置。<h4>所需最低固件版本：5.1.1</h4>

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.ArtifactApi()

try:
    # 获取激光地标
    api_response = api_instance.get_laser_landmarks()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ArtifactApi->get_laser_landmarks: %s\n" % e)
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

# **get_lines**
> list[Line] get_lines(usage)

获取虚拟线段

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.ArtifactApi()
usage = 'usage_example' # str | * `tracks` 虚拟轨道 * `walls` 虚拟墙 

try:
    # 获取虚拟线段
    api_response = api_instance.get_lines(usage)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ArtifactApi->get_lines: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **usage** | **str**| * &#x60;tracks&#x60; 虚拟轨道 * &#x60;walls&#x60; 虚拟墙  | 

### Return type

[**list[Line]**](Line.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_poi_by_id**
> PoseEntry get_poi_by_id(poi_id)

根据ID查找POI

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.ArtifactApi()
poi_id = '38400000-8cf0-11bd-b23e-10b96e4ef00d' # str | 

try:
    # 根据ID查找POI
    api_response = api_instance.get_poi_by_id(poi_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ArtifactApi->get_poi_by_id: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **poi_id** | [**str**](.md)|  | 

### Return type

[**PoseEntry**](PoseEntry.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_rectangle_areas**
> list[RectangleArea] get_rectangle_areas(usage)

获取矩形区域

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.ArtifactApi()
usage = swagger_client.RectangleAreaUsage() # RectangleAreaUsage | 

try:
    # 获取矩形区域
    api_response = api_instance.get_rectangle_areas(usage)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ArtifactApi->get_rectangle_areas: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **usage** | [**RectangleAreaUsage**](.md)|  | 

### Return type

[**list[RectangleArea]**](RectangleArea.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **modify_lines**
> bool modify_lines(usage, body=body)

修改虚拟线段

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.ArtifactApi()
usage = 'usage_example' # str | * `tracks` 虚拟轨道 * `walls` 虚拟墙 
body = [swagger_client.Line()] # list[Line] |  (optional)

try:
    # 修改虚拟线段
    api_response = api_instance.modify_lines(usage, body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ArtifactApi->modify_lines: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **usage** | **str**| * &#x60;tracks&#x60; 虚拟轨道 * &#x60;walls&#x60; 虚拟墙  | 
 **body** | [**list[Line]**](Line.md)|  | [optional] 

### Return type

**bool**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **modify_poi**
> bool modify_poi(body, poi_id)

修改POI

请求报文中pose和metadata可以只包含其中一个，则另一个字段保持不变。

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.ArtifactApi()
body = swagger_client.PoisPoiIdBody() # PoisPoiIdBody | 
poi_id = '38400000-8cf0-11bd-b23e-10b96e4ef00d' # str | 

try:
    # 修改POI
    api_response = api_instance.modify_poi(body, poi_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ArtifactApi->modify_poi: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**PoisPoiIdBody**](PoisPoiIdBody.md)|  | 
 **poi_id** | [**str**](.md)|  | 

### Return type

**bool**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **put_laser_landmarks**
> bool put_laser_landmarks(body)

设置激光地标

将从地图中读出的激光地标信息设置到Slamware中<h4>所需最低固件版本：5.1.1</h4>

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.ArtifactApi()
body = [swagger_client.PoseEntry()] # list[PoseEntry] | 

try:
    # 设置激光地标
    api_response = api_instance.put_laser_landmarks(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ArtifactApi->put_laser_landmarks: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**list[PoseEntry]**](PoseEntry.md)|  | 

### Return type

**bool**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **remove_laser_landmarks**
> bool remove_laser_landmarks(body)

删除激光地标

删除部分激光地标, 请求报文为ID数组，ID来自获取激光地标接口返回内容的id字段。<h4>所需最低固件版本：5.1.1</h4>

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.ArtifactApi()
body = [56] # list[int] | 

try:
    # 删除激光地标
    api_response = api_instance.remove_laser_landmarks(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ArtifactApi->remove_laser_landmarks: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**list[int]**](int.md)|  | 

### Return type

**bool**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **remove_line_by_id**
> bool remove_line_by_id(usage, id)

删除虚拟线段

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.ArtifactApi()
usage = 'usage_example' # str | * `tracks` 虚拟轨道 * `walls` 虚拟墙 
id = 56 # int | 

try:
    # 删除虚拟线段
    api_response = api_instance.remove_line_by_id(usage, id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ArtifactApi->remove_line_by_id: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **usage** | **str**| * &#x60;tracks&#x60; 虚拟轨道 * &#x60;walls&#x60; 虚拟墙  | 
 **id** | **int**|  | 

### Return type

**bool**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **remove_rectangle_area_by_id**
> bool remove_rectangle_area_by_id(usage, id)

删除矩形区域

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.ArtifactApi()
usage = swagger_client.RectangleAreaUsage() # RectangleAreaUsage | 
id = 56 # int | 

try:
    # 删除矩形区域
    api_response = api_instance.remove_rectangle_area_by_id(usage, id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ArtifactApi->remove_rectangle_area_by_id: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **usage** | [**RectangleAreaUsage**](.md)|  | 
 **id** | **int**|  | 

### Return type

**bool**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **set_laser_landmark_update**
> bool set_laser_landmark_update(body)

设置取激光地标更新状态

设置是否允许Slamware自动更新激光地标<h4>所需最低固件版本：5.1.1</h4>

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.ArtifactApi()
body = swagger_client.LaserlandmarksUpdateBody() # LaserlandmarksUpdateBody | 

try:
    # 设置取激光地标更新状态
    api_response = api_instance.set_laser_landmark_update(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ArtifactApi->set_laser_landmark_update: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**LaserlandmarksUpdateBody**](LaserlandmarksUpdateBody.md)|  | 

### Return type

**bool**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

