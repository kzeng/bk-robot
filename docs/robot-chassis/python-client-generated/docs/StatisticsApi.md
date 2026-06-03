# swagger_client.StatisticsApi

All URIs are relative to */*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_odometry**](StatisticsApi.md#get_odometry) | **GET** /api/core/statistics/v1/odometry | 获取运行里程
[**get_runtime**](StatisticsApi.md#get_runtime) | **GET** /api/core/statistics/v1/runtime | 获取运行时间

# **get_odometry**
> float get_odometry()

获取运行里程

机器人总的运行里程，单位米

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.StatisticsApi()

try:
    # 获取运行里程
    api_response = api_instance.get_odometry()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling StatisticsApi->get_odometry: %s\n" % e)
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

# **get_runtime**
> float get_runtime()

获取运行时间

机器人总的运行时间，单位秒

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.StatisticsApi()

try:
    # 获取运行时间
    api_response = api_instance.get_runtime()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling StatisticsApi->get_runtime: %s\n" % e)
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

