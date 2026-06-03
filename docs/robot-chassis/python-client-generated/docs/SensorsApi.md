# swagger_client.SensorsApi

All URIs are relative to */*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_disabled_sensors_mask_data**](SensorsApi.md#get_disabled_sensors_mask_data) | **GET** /api/core/sensors/v1/masks | 获取传感器禁用状态
[**set_depth_sensor_state**](SensorsApi.md#set_depth_sensor_state) | **PUT** /api/core/sensors/v1/depth/:enable | 使能/禁用深度摄像头数据
[**set_sensor_mask**](SensorsApi.md#set_sensor_mask) | **PUT** /api/core/sensors/v1/masks | 使能/禁用传感器

# **get_disabled_sensors_mask_data**
> list[DisabledSensorMaskData] get_disabled_sensors_mask_data()

获取传感器禁用状态

获取禁用状态的传感器掩码信息。

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.SensorsApi()

try:
    # 获取传感器禁用状态
    api_response = api_instance.get_disabled_sensors_mask_data()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SensorsApi->get_disabled_sensors_mask_data: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**list[DisabledSensorMaskData]**](DisabledSensorMaskData.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **set_depth_sensor_state**
> set_depth_sensor_state(body=body)

使能/禁用深度摄像头数据

用户设置是否使用深度摄像头数据

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.SensorsApi()
body = swagger_client.DepthEnableBody() # DepthEnableBody |  (optional)

try:
    # 使能/禁用深度摄像头数据
    api_instance.set_depth_sensor_state(body=body)
except ApiException as e:
    print("Exception when calling SensorsApi->set_depth_sensor_state: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**DepthEnableBody**](DepthEnableBody.md)|  | [optional] 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **set_sensor_mask**
> bool set_sensor_mask(body=body)

使能/禁用传感器

设置传感器掩码。

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.SensorsApi()
body = [swagger_client.SensorMaskCtrlData()] # list[SensorMaskCtrlData] |  (optional)

try:
    # 使能/禁用传感器
    api_response = api_instance.set_sensor_mask(body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SensorsApi->set_sensor_mask: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**list[SensorMaskCtrlData]**](SensorMaskCtrlData.md)|  | [optional] 

### Return type

**bool**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

