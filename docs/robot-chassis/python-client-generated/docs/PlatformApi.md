# swagger_client.PlatformApi

All URIs are relative to */*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_events**](PlatformApi.md#get_events) | **GET** /api/platform/v1/events | 获取事件信息
[**get_timestamp**](PlatformApi.md#get_timestamp) | **GET** /api/platform/v1/timestamp | 获取系统时间戳

# **get_events**
> list[RobotEvent] get_events()

获取事件信息

获取机器人发生的事件，上位机可以播报语音或进行别的交互，启用不同的插件会扩展出不同的事件类型。 

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.PlatformApi()

try:
    # 获取事件信息
    api_response = api_instance.get_events()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling PlatformApi->get_events: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**list[RobotEvent]**](RobotEvent.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_timestamp**
> str get_timestamp()

获取系统时间戳

获取系统启动以来的毫秒数, 返回值为字符串格式的整数。<h4>所需最低固件版本 4.2.4</h4>

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.PlatformApi()

try:
    # 获取系统时间戳
    api_response = api_instance.get_timestamp()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling PlatformApi->get_timestamp: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

**str**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

