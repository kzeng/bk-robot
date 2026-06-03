# swagger_client.ApplicationApi

All URIs are relative to */*

Method | HTTP request | Description
------------- | ------------- | -------------
[**delete_app**](ApplicationApi.md#delete_app) | **DELETE** /api/core/application/v1/apps/{app_name} | 卸载一个APP
[**get_apps**](ApplicationApi.md#get_apps) | **GET** /api/core/application/v1/apps | 获取所有自定义安装的APP
[**install_app**](ApplicationApi.md#install_app) | **POST** /api/core/application/v1/apps | 安装APP

# **delete_app**
> delete_app(app_name)

卸载一个APP

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.ApplicationApi()
app_name = 'app_name_example' # str | 

try:
    # 卸载一个APP
    api_instance.delete_app(app_name)
except ApiException as e:
    print("Exception when calling ApplicationApi->delete_app: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **app_name** | **str**|  | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_apps**
> list[InlineResponse20013] get_apps()

获取所有自定义安装的APP

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.ApplicationApi()

try:
    # 获取所有自定义安装的APP
    api_response = api_instance.get_apps()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ApplicationApi->get_apps: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**list[InlineResponse20013]**](InlineResponse20013.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **install_app**
> install_app(body=body)

安装APP

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.ApplicationApi()
body = NULL # object |  (optional)

try:
    # 安装APP
    api_instance.install_app(body=body)
except ApiException as e:
    print("Exception when calling ApplicationApi->install_app: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**object**](object.md)|  | [optional] 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/octet-stream
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

