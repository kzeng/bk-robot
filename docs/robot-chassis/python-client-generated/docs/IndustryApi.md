# swagger_client.IndustryApi

All URIs are relative to */*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_task_template**](IndustryApi.md#create_task_template) | **POST** /api/industry/v1/tasks/templates | 创建任务模板
[**delete_task_template**](IndustryApi.md#delete_task_template) | **DELETE** /api/industry/v1/tasks/templates/{key_id} | 删除任务模板
[**get_industry_tasks**](IndustryApi.md#get_industry_tasks) | **GET** /api/industry/v1/tasks | 查询任务信息
[**get_task_templates**](IndustryApi.md#get_task_templates) | **GET** /api/industry/v1/tasks/templates | 获取任务模板
[**post_task_event**](IndustryApi.md#post_task_event) | **POST** /api/industry/v1/tasks/events | 推送任务事件

# **create_task_template**
> TaskTemplate create_task_template(body=body)

创建任务模板

创建一个呼叫器任务模板

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.IndustryApi()
body = swagger_client.TaskTemplateRequest() # TaskTemplateRequest |  (optional)

try:
    # 创建任务模板
    api_response = api_instance.create_task_template(body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling IndustryApi->create_task_template: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**TaskTemplateRequest**](TaskTemplateRequest.md)|  | [optional] 

### Return type

[**TaskTemplate**](TaskTemplate.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_task_template**
> InlineResponse20016 delete_task_template(key_id)

删除任务模板

删除一个任务模板

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.IndustryApi()
key_id = '38400000-8cf0-11bd-b23e-10b96e4ef00d' # str | 

try:
    # 删除任务模板
    api_response = api_instance.delete_task_template(key_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling IndustryApi->delete_task_template: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **key_id** | [**str**](.md)|  | 

### Return type

[**InlineResponse20016**](InlineResponse20016.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: text/plain

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_industry_tasks**
> list[IndustryTask] get_industry_tasks(type=type, status=status)

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
api_instance = swagger_client.IndustryApi()
type = 'type_example' # str |  (optional)
status = 'status_example' # str |  (optional)

try:
    # 查询任务信息
    api_response = api_instance.get_industry_tasks(type=type, status=status)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling IndustryApi->get_industry_tasks: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **type** | **str**|  | [optional] 
 **status** | **str**|  | [optional] 

### Return type

[**list[IndustryTask]**](IndustryTask.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_task_templates**
> list[TaskTemplate] get_task_templates()

获取任务模板

获取当前设备所属场景下的所有任务模板

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.IndustryApi()

try:
    # 获取任务模板
    api_response = api_instance.get_task_templates()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling IndustryApi->get_task_templates: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**list[TaskTemplate]**](TaskTemplate.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_task_event**
> post_task_event(body=body)

推送任务事件

上位机执行呼叫器任务时，通过该接口推送任务事件，同时更新任务状态。

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.IndustryApi()
body = swagger_client.TasksEventsBody() # TasksEventsBody |  (optional)

try:
    # 推送任务事件
    api_instance.post_task_event(body=body)
except ApiException as e:
    print("Exception when calling IndustryApi->post_task_event: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**TasksEventsBody**](TasksEventsBody.md)|  | [optional] 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

