# swagger_client.SystemApi

All URIs are relative to */*

Method | HTTP request | Description
------------- | ------------- | -------------
[**clear_robot_health**](SystemApi.md#clear_robot_health) | **DELETE** /api/core/system/v1/robot/health/{error_code} | 清除出错的状态信息
[**get_battery_pack**](SystemApi.md#get_battery_pack) | **GET** /api/core/system/v1/battery/pack | 获取电池包的电流和温度
[**get_capabilities**](SystemApi.md#get_capabilities) | **GET** /api/core/system/v1/capabilities | 获取机器人能力
[**get_cmlink_apn**](SystemApi.md#get_cmlink_apn) | **GET** /api/core/system/v1/network/apn | 获取cmlink apn
[**get_imu_raw_adc_data**](SystemApi.md#get_imu_raw_adc_data) | **GET** /api/core/system/v1/rawadcimu | 获取IMU的ADC原始值
[**get_imu_raw_data**](SystemApi.md#get_imu_raw_data) | **GET** /api/core/system/v1/rawimu | 获取IMU原始值
[**get_jack_status**](SystemApi.md#get_jack_status) | **GET** /api/core/system/v1/jack/status | 获取千斤顶状态
[**get_laser_scan**](SystemApi.md#get_laser_scan) | **GET** /api/core/system/v1/laserscan | 获取当前激光观测帧
[**get_network_route**](SystemApi.md#get_network_route) | **GET** /api/core/system/v1/network/route | 获取路由信息
[**get_network_status**](SystemApi.md#get_network_status) | **GET** /api/core/system/v1/network/status | 获取网络状态
[**get_power_status**](SystemApi.md#get_power_status) | **GET** /api/core/system/v1/power/status | 获取机器人电源状态
[**get_robot_health**](SystemApi.md#get_robot_health) | **GET** /api/core/system/v1/robot/health | 获取设备健康状态信息
[**get_robot_info**](SystemApi.md#get_robot_info) | **GET** /api/core/system/v1/robot/info | 获取设备信息
[**get_system_parameter**](SystemApi.md#get_system_parameter) | **GET** /api/core/system/v1/parameter | 获取系统参数
[**hibernate**](SystemApi.md#hibernate) | **POST** /api/core/system/v1/power/:hibernate | 休眠机器人
[**restart_module**](SystemApi.md#restart_module) | **POST** /api/core/system/v1/power/:restartmodule | 重启模块
[**set_aeb_control**](SystemApi.md#set_aeb_control) | **POST** /api/core/system/v1/aeb/control | 设置AEB控制
[**set_cmlink_apn**](SystemApi.md#set_cmlink_apn) | **PUT** /api/core/system/v1/network/apn | 设置cmlink apn
[**set_cube_config**](SystemApi.md#set_cube_config) | **PUT** /api/core/system/v1/cube/config | 设置Cube配置
[**set_jack_req**](SystemApi.md#set_jack_req) | **POST** /api/core/system/v1/jack/status | 设置千斤顶状态
[**set_light_control**](SystemApi.md#set_light_control) | **POST** /api/core/system/v1/light/control | 设置灯光控制效果
[**set_network_route**](SystemApi.md#set_network_route) | **PUT** /api/core/system/v1/network/route | 设置路由信息
[**set_network_status**](SystemApi.md#set_network_status) | **PUT** /api/core/system/v1/network/status | 设置网络状态
[**set_system_parameter**](SystemApi.md#set_system_parameter) | **PUT** /api/core/system/v1/parameter | 设置系统参数
[**shutdown**](SystemApi.md#shutdown) | **POST** /api/core/system/v1/power/:shutdown | 关闭或重启机器人
[**wakeup**](SystemApi.md#wakeup) | **POST** /api/core/system/v1/power/:wakeup | 唤醒机器人

# **clear_robot_health**
> clear_robot_health(error_code)

清除出错的状态信息

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.SystemApi()
error_code = 56 # int | 错误码

try:
    # 清除出错的状态信息
    api_instance.clear_robot_health(error_code)
except ApiException as e:
    print("Exception when calling SystemApi->clear_robot_health: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **error_code** | **int**| 错误码 | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_battery_pack**
> InlineResponse2003 get_battery_pack()

获取电池包的电流和温度

获取电池包的电流和温度

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.SystemApi()

try:
    # 获取电池包的电流和温度
    api_response = api_instance.get_battery_pack()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SystemApi->get_battery_pack: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**InlineResponse2003**](InlineResponse2003.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_capabilities**
> list[Capability] get_capabilities()

获取机器人能力

该接口用于判断机器人支持哪些功能，以及是否已完成初始化。本文档中的部分接口需要依赖特定的capability才能运行。

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.SystemApi()

try:
    # 获取机器人能力
    api_response = api_instance.get_capabilities()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SystemApi->get_capabilities: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**list[Capability]**](Capability.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_cmlink_apn**
> ApnStatus get_cmlink_apn()

获取cmlink apn

<h4>所需最低固件版本 4.4.0</h4>

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.SystemApi()

try:
    # 获取cmlink apn
    api_response = api_instance.get_cmlink_apn()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SystemApi->get_cmlink_apn: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**ApnStatus**](ApnStatus.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_imu_raw_adc_data**
> InlineResponse2002 get_imu_raw_adc_data()

获取IMU的ADC原始值

获取机器人IMU的ADC原始值

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.SystemApi()

try:
    # 获取IMU的ADC原始值
    api_response = api_instance.get_imu_raw_adc_data()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SystemApi->get_imu_raw_adc_data: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**InlineResponse2002**](InlineResponse2002.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_imu_raw_data**
> InlineResponse2004 get_imu_raw_data()

获取IMU原始值

获取机器人IMU原始值

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.SystemApi()

try:
    # 获取IMU原始值
    api_response = api_instance.get_imu_raw_data()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SystemApi->get_imu_raw_data: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**InlineResponse2004**](InlineResponse2004.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_jack_status**
> InlineResponse2001 get_jack_status()

获取千斤顶状态

获取千斤顶状态。

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.SystemApi()

try:
    # 获取千斤顶状态
    api_response = api_instance.get_jack_status()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SystemApi->get_jack_status: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**InlineResponse2001**](InlineResponse2001.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_laser_scan**
> LaserScan get_laser_scan()

获取当前激光观测帧

<h4>所需最低固件版本 4.2.2</h4>

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.SystemApi()

try:
    # 获取当前激光观测帧
    api_response = api_instance.get_laser_scan()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SystemApi->get_laser_scan: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**LaserScan**](LaserScan.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_network_route**
> RouteStatus get_network_route()

获取路由信息

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.SystemApi()

try:
    # 获取路由信息
    api_response = api_instance.get_network_route()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SystemApi->get_network_route: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**RouteStatus**](RouteStatus.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_network_status**
> InlineResponse200 get_network_status()

获取网络状态

获取机器人当前的网络状态

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.SystemApi()

try:
    # 获取网络状态
    api_response = api_instance.get_network_status()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SystemApi->get_network_status: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**InlineResponse200**](InlineResponse200.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_power_status**
> PowerStatus get_power_status()

获取机器人电源状态

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.SystemApi()

try:
    # 获取机器人电源状态
    api_response = api_instance.get_power_status()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SystemApi->get_power_status: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**PowerStatus**](PowerStatus.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_robot_health**
> BaseHealthInfo get_robot_health()

获取设备健康状态信息

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.SystemApi()

try:
    # 获取设备健康状态信息
    api_response = api_instance.get_robot_health()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SystemApi->get_robot_health: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**BaseHealthInfo**](BaseHealthInfo.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_robot_info**
> DeviceInfo get_robot_info()

获取设备信息

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.SystemApi()

try:
    # 获取设备信息
    api_response = api_instance.get_robot_info()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SystemApi->get_robot_info: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**DeviceInfo**](DeviceInfo.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_system_parameter**
> str get_system_parameter(param)

获取系统参数

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.SystemApi()
param = 'param_example' # str | 系统参数名:  * `base.max_moving_speed` - 最大线速度  * `base.max_angular_speed` - 最大角速度  * `docking.docked_register_strategy` - 充电桩注册策略，`always` 每次回桩都注册，`when_not_exists` 桩不存在时注册 

try:
    # 获取系统参数
    api_response = api_instance.get_system_parameter(param)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SystemApi->get_system_parameter: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **param** | **str**| 系统参数名:  * &#x60;base.max_moving_speed&#x60; - 最大线速度  * &#x60;base.max_angular_speed&#x60; - 最大角速度  * &#x60;docking.docked_register_strategy&#x60; - 充电桩注册策略，&#x60;always&#x60; 每次回桩都注册，&#x60;when_not_exists&#x60; 桩不存在时注册  | 

### Return type

**str**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: text/plain

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **hibernate**
> hibernate()

休眠机器人

休眠时激光雷达暂停工作

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.SystemApi()

try:
    # 休眠机器人
    api_instance.hibernate()
except ApiException as e:
    print("Exception when calling SystemApi->hibernate: %s\n" % e)
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

# **restart_module**
> bool restart_module(body)

重启模块

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.SystemApi()
body = swagger_client.PowerRestartmoduleBody() # PowerRestartmoduleBody | 根据指定的重启模式（默认软复位）执行重启操作。

try:
    # 重启模块
    api_response = api_instance.restart_module(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SystemApi->restart_module: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**PowerRestartmoduleBody**](PowerRestartmoduleBody.md)| 根据指定的重启模式（默认软复位）执行重启操作。 | 

### Return type

**bool**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **set_aeb_control**
> set_aeb_control(body)

设置AEB控制

设置AEB功能打开或者关闭。

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.SystemApi()
body = 'body_example' # str | 

try:
    # 设置AEB控制
    api_instance.set_aeb_control(body)
except ApiException as e:
    print("Exception when calling SystemApi->set_aeb_control: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**str**](str.md)|  | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **set_cmlink_apn**
> set_cmlink_apn(body)

设置cmlink apn

根据地区来设置cmlink apn，设置4g在不同地区的接入点，具体的apn请查阅运营商官网<h4>所需最低固件版本 4.4.0</h4>

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.SystemApi()
body = swagger_client.ApnStatus() # ApnStatus | 

try:
    # 设置cmlink apn
    api_instance.set_cmlink_apn(body)
except ApiException as e:
    print("Exception when calling SystemApi->set_cmlink_apn: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**ApnStatus**](ApnStatus.md)|  | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **set_cube_config**
> set_cube_config(body=body)

设置Cube配置

以二进制方式读取cube_cfg_dat文件作为Request Body. </br>Cube配置文件请用RoboStudio的Cube配置工具导出或联系思岚技术支持获取. <h4>所需最低固件版本  4.2.0</h4>

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.SystemApi()
body = swagger_client.Object() # Object |  (optional)

try:
    # 设置Cube配置
    api_instance.set_cube_config(body=body)
except ApiException as e:
    print("Exception when calling SystemApi->set_cube_config: %s\n" % e)
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

# **set_jack_req**
> set_jack_req(body)

设置千斤顶状态

设置千斤顶状态。

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.SystemApi()
body = 'body_example' # str | 

try:
    # 设置千斤顶状态
    api_instance.set_jack_req(body)
except ApiException as e:
    print("Exception when calling SystemApi->set_jack_req: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**str**](str.md)|  | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **set_light_control**
> set_light_control(body)

设置灯光控制效果

可以设置不同通道，不同部分，不同类型的led灯颜色效果。

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.SystemApi()
body = swagger_client.LightControlData() # LightControlData | 

try:
    # 设置灯光控制效果
    api_instance.set_light_control(body)
except ApiException as e:
    print("Exception when calling SystemApi->set_light_control: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**LightControlData**](LightControlData.md)|  | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **set_network_route**
> set_network_route(body)

设置路由信息

可设置路由优先级，当wifi和4g都可用时，可选择wifi优先或者4g优先。

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.SystemApi()
body = swagger_client.RouteStatus() # RouteStatus | 

try:
    # 设置路由信息
    api_instance.set_network_route(body)
except ApiException as e:
    print("Exception when calling SystemApi->set_network_route: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**RouteStatus**](RouteStatus.md)|  | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **set_network_status**
> bool set_network_status(body)

设置网络状态

当网络由安卓管理时，该接口会返回false

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.SystemApi()
body = swagger_client.NetworkStatusBody() # NetworkStatusBody | 

try:
    # 设置网络状态
    api_response = api_instance.set_network_status(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SystemApi->set_network_status: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**NetworkStatusBody**](NetworkStatusBody.md)|  | 

### Return type

**bool**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **set_system_parameter**
> bool set_system_parameter(body)

设置系统参数

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.SystemApi()
body = swagger_client.V1ParameterBody() # V1ParameterBody | 设置的系统参数仅本次运行有效，重启机器后恢复原值

try:
    # 设置系统参数
    api_response = api_instance.set_system_parameter(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SystemApi->set_system_parameter: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**V1ParameterBody**](V1ParameterBody.md)| 设置的系统参数仅本次运行有效，重启机器后恢复原值 | 

### Return type

**bool**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **shutdown**
> bool shutdown(body)

关闭或重启机器人

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.SystemApi()
body = swagger_client.PowerShutdownBody() # PowerShutdownBody | 通过设置关机时间和重启时间来实现机器人延时重启，单位分钟，如果都为0则表示立即关机且不再重启。

try:
    # 关闭或重启机器人
    api_response = api_instance.shutdown(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling SystemApi->shutdown: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**PowerShutdownBody**](PowerShutdownBody.md)| 通过设置关机时间和重启时间来实现机器人延时重启，单位分钟，如果都为0则表示立即关机且不再重启。 | 

### Return type

**bool**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **wakeup**
> wakeup()

唤醒机器人

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.SystemApi()

try:
    # 唤醒机器人
    api_instance.wakeup()
except ApiException as e:
    print("Exception when calling SystemApi->wakeup: %s\n" % e)
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

