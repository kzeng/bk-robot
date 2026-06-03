# swagger_client.FirmwareApi

All URIs are relative to */*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_enable_auto_update**](FirmwareApi.md#get_enable_auto_update) | **GET** /api/core/firmware/v1/autoupdate/:enable | 是否支持自动升级
[**get_firmware_progress**](FirmwareApi.md#get_firmware_progress) | **GET** /api/core/firmware/v1/progress | 获取固件升级进度
[**get_new_version**](FirmwareApi.md#get_new_version) | **GET** /api/core/firmware/v1/newversion | 查询新版本固件
[**set_enable_auto_update**](FirmwareApi.md#set_enable_auto_update) | **PUT** /api/core/firmware/v1/autoupdate/:enable | 开启/关闭自动升级
[**start_update**](FirmwareApi.md#start_update) | **POST** /api/core/firmware/v1/autoupdate/:start | 开始自动固件升级
[**upload_and_start_update**](FirmwareApi.md#upload_and_start_update) | **POST** /api/core/firmware/v1/update/:start | 上传固件升级

# **get_enable_auto_update**
> bool get_enable_auto_update()

是否支持自动升级

上传固件到思岚云并发布给指定设备，如果设备支持自动升级，就会在指定时间段内自动升级固件。

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.FirmwareApi()

try:
    # 是否支持自动升级
    api_response = api_instance.get_enable_auto_update()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling FirmwareApi->get_enable_auto_update: %s\n" % e)
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

# **get_firmware_progress**
> InlineResponse20012 get_firmware_progress()

获取固件升级进度

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.FirmwareApi()

try:
    # 获取固件升级进度
    api_response = api_instance.get_firmware_progress()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling FirmwareApi->get_firmware_progress: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**InlineResponse20012**](InlineResponse20012.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_new_version**
> InlineResponse2009 get_new_version()

查询新版本固件

从云端查询可升级的新版本固件信息，如果没有则返回空数据

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.FirmwareApi()

try:
    # 查询新版本固件
    api_response = api_instance.get_new_version()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling FirmwareApi->get_new_version: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**InlineResponse2009**](InlineResponse2009.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **set_enable_auto_update**
> set_enable_auto_update(body=body)

开启/关闭自动升级

关闭自动升级后将会忽略云端发布的最新固件。

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.FirmwareApi()
body = swagger_client.AutoupdateEnableBody() # AutoupdateEnableBody |  (optional)

try:
    # 开启/关闭自动升级
    api_instance.set_enable_auto_update(body=body)
except ApiException as e:
    print("Exception when calling FirmwareApi->set_enable_auto_update: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**AutoupdateEnableBody**](AutoupdateEnableBody.md)|  | [optional] 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **start_update**
> InlineResponse20010 start_update()

开始自动固件升级

查询思岚云上可升级的最新固件，下载固件并升级。

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.FirmwareApi()

try:
    # 开始自动固件升级
    api_response = api_instance.start_update()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling FirmwareApi->start_update: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**InlineResponse20010**](InlineResponse20010.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **upload_and_start_update**
> InlineResponse20011 upload_and_start_update(body=body)

上传固件升级

将固件包以二进制方式读取作为request body，上传至机器人用于固件升级。<h4>所需最低固件版本：4.6.3</h4>

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.FirmwareApi()
body = swagger_client.Object() # Object |  (optional)

try:
    # 上传固件升级
    api_response = api_instance.upload_and_start_update(body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling FirmwareApi->upload_and_start_update: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | **Object**|  | [optional] 

### Return type

[**InlineResponse20011**](InlineResponse20011.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/octet-stream
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

