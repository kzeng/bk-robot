# swagger_client.MotionApi

All URIs are relative to */*

Method | HTTP request | Description
------------- | ------------- | -------------
[**abort_current_action**](MotionApi.md#abort_current_action) | **DELETE** /api/core/motion/v1/actions/:current | 终止当前行为
[**create_action**](MotionApi.md#create_action) | **POST** /api/core/motion/v1/actions | 创建新的运动行为
[**get_action_factories**](MotionApi.md#get_action_factories) | **GET** /api/core/motion/v1/action-factories | 获取所有支持的Action
[**get_action_result**](MotionApi.md#get_action_result) | **GET** /api/core/motion/v1/actions/{action_id} | 查询Action状态
[**get_current_action**](MotionApi.md#get_current_action) | **GET** /api/core/motion/v1/actions/:current | 获取当前行为
[**get_current_speed**](MotionApi.md#get_current_speed) | **GET** /api/core/motion/v1/speed | 获取运动速度
[**get_current_strategy**](MotionApi.md#get_current_strategy) | **GET** /api/core/motion/v1/strategies/:current | 获取当前运动策略
[**get_motion_strategies**](MotionApi.md#get_motion_strategies) | **GET** /api/core/motion/v1/strategies | 获取支持的所有运动策略
[**get_remaining_milestones**](MotionApi.md#get_remaining_milestones) | **GET** /api/core/motion/v1/milestones | 获取剩余目标点
[**get_remaining_path**](MotionApi.md#get_remaining_path) | **GET** /api/core/motion/v1/path | 获取剩余路径点
[**get_remaining_time**](MotionApi.md#get_remaining_time) | **GET** /api/core/motion/v1/time | 获取剩余时间
[**search_path**](MotionApi.md#search_path) | **POST** /api/core/motion/v1/:search_path | 搜索路径
[**set_current_strategy**](MotionApi.md#set_current_strategy) | **PUT** /api/core/motion/v1/strategies/:current | 设置运动策略

# **abort_current_action**
> abort_current_action()

终止当前行为

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.MotionApi()

try:
    # 终止当前行为
    api_instance.abort_current_action()
except ApiException as e:
    print("Exception when calling MotionApi->abort_current_action: %s\n" % e)
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

# **create_action**
> ActionInfo create_action(body)

创建新的运动行为

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.MotionApi()
body = swagger_client.V1ActionsBody() # V1ActionsBody | action_name通过/core/motion/v1/action-factories接口进行查询, options具体内容根据action类型而定

try:
    # 创建新的运动行为
    api_response = api_instance.create_action(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling MotionApi->create_action: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**V1ActionsBody**](V1ActionsBody.md)| action_name通过/core/motion/v1/action-factories接口进行查询, options具体内容根据action类型而定 | 

### Return type

[**ActionInfo**](ActionInfo.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_action_factories**
> list[InlineResponse2005] get_action_factories()

获取所有支持的Action

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.MotionApi()

try:
    # 获取所有支持的Action
    api_response = api_instance.get_action_factories()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling MotionApi->get_action_factories: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**list[InlineResponse2005]**](InlineResponse2005.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_action_result**
> InlineResponse2006 get_action_result(action_id)

查询Action状态

可查询最近20次action的状态, state.status为4表示action已结束，此时通过result判断成功与否。

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.MotionApi()
action_id = 56 # int | 

try:
    # 查询Action状态
    api_response = api_instance.get_action_result(action_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling MotionApi->get_action_result: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **action_id** | **int**|  | 

### Return type

[**InlineResponse2006**](InlineResponse2006.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_current_action**
> ActionInfo get_current_action()

获取当前行为

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.MotionApi()

try:
    # 获取当前行为
    api_response = api_instance.get_current_action()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling MotionApi->get_current_action: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**ActionInfo**](ActionInfo.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_current_speed**
> InlineResponse2008 get_current_speed()

获取运动速度

获取机器人当前运动速度

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.MotionApi()

try:
    # 获取运动速度
    api_response = api_instance.get_current_speed()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling MotionApi->get_current_speed: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**InlineResponse2008**](InlineResponse2008.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_current_strategy**
> str get_current_strategy()

获取当前运动策略

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.MotionApi()

try:
    # 获取当前运动策略
    api_response = api_instance.get_current_strategy()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling MotionApi->get_current_strategy: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

**str**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: text/plain

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_motion_strategies**
> list[str] get_motion_strategies()

获取支持的所有运动策略

运动策略为Slamware一系列内部参数的组合，涉及到运动速度、避障行为等各个方面，不同的策略可适用于不同的场景。一般情况下采用默认策略即可。<h4>所需最低固件版本 4.2.4</h4>

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.MotionApi()

try:
    # 获取支持的所有运动策略
    api_response = api_instance.get_motion_strategies()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling MotionApi->get_motion_strategies: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

**list[str]**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_remaining_milestones**
> InlineResponse2007 get_remaining_milestones()

获取剩余目标点

当前Action剩余的目标点

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.MotionApi()

try:
    # 获取剩余目标点
    api_response = api_instance.get_remaining_milestones()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling MotionApi->get_remaining_milestones: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**InlineResponse2007**](InlineResponse2007.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_remaining_path**
> InlineResponse2007 get_remaining_path()

获取剩余路径点

当前Action剩余的路径点

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.MotionApi()

try:
    # 获取剩余路径点
    api_response = api_instance.get_remaining_path()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling MotionApi->get_remaining_path: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**InlineResponse2007**](InlineResponse2007.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_remaining_time**
> float get_remaining_time()

获取剩余时间

获取机器人到目的地的剩余运动时间（估计值）

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.MotionApi()

try:
    # 获取剩余时间
    api_response = api_instance.get_remaining_time()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling MotionApi->get_remaining_time: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

**float**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **search_path**
> InlineResponse2007 search_path(body)

搜索路径

搜索从机器人到目标点的最优路径

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.MotionApi()
body = swagger_client.V1SearchPathBody() # V1SearchPathBody | 

try:
    # 搜索路径
    api_response = api_instance.search_path(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling MotionApi->search_path: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**V1SearchPathBody**](V1SearchPathBody.md)|  | 

### Return type

[**InlineResponse2007**](InlineResponse2007.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **set_current_strategy**
> bool set_current_strategy(body)

设置运动策略

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.MotionApi()
body = swagger_client.StrategiesCurrentBody() # StrategiesCurrentBody | 

try:
    # 设置运动策略
    api_response = api_instance.set_current_strategy(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling MotionApi->set_current_strategy: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**StrategiesCurrentBody**](StrategiesCurrentBody.md)|  | 

### Return type

**bool**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

