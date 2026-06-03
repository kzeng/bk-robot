# ImuData

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**acc** | [**Location**](Location.md) |  | [optional] 
**availibility_bit_map** | **int** | * &#x60;1&#x60; 以四元数表示的位姿 * &#x60;2&#x60; 校准后的加速度计 * &#x60;4&#x60; 校准后的陀螺仪 * &#x60;8&#x60; 校准后的罗盘 * &#x60;16&#x60; 加速度计原始值 * &#x60;32&#x60; 陀螺仪原始值 * &#x60;64&#x60; 罗盘原始值 * &#x60;128&#x60; 6自由度的位姿信息 * &#x60;256&#x60; 9自由度的位姿信息 * &#x60;512&#x60; 以欧拉角表示的位姿  | [optional] 
**compass** | [**Location**](Location.md) |  | [optional] 
**euler_angle** | [**Location**](Location.md) |  | [optional] 
**gyro** | [**Location**](Location.md) |  | [optional] 
**quaternion** | [**Quaternion**](Quaternion.md) |  | [optional] 
**raw_acc** | [**Location**](Location.md) |  | [optional] 
**raw_compass** | [**Location**](Location.md) |  | [optional] 
**raw_gyro** | [**Location**](Location.md) |  | [optional] 
**timestamp** | **int** | 底盘启动以来经过的毫秒数 | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

