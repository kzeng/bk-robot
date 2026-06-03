# MoveOptions

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**mode** | **int** | 0：自由导航， 1：严格轨道模式(遇障碍物停止并等待)，2： 轨道优先模式(遇障碍物下轨绕行) | [default to ModeEnum._0]
**flags** | **list[str]** | * &#x60;precise&#x60; 精确到点模式，使机器人到点时更加精准 * &#x60;with_yaw&#x60; 精确到角模式，只有包含该flag，yaw字段的值才会生效 * &#x60;fail_retry_count&#x60; 指定搜路失败后的重试次数，不指定时采用默认配置 * &#x60;find_path_ignoring_dynamic_obstacles&#x60; 搜路时忽略动态障碍物，适用于人群拥挤、通道狭窄的区域 * &#x60;with_directed_virtual_track&#x60; 有向轨道搜路，当mode为1或2时，使机器人只能按照轨道方向移动 | [optional] 
**yaw** | **float** | 到目标点后机器人的朝向 | [optional] 
**acceptable_precision** | **float** | 可接受的到点范围，当目标点被占据时，机器人离目标点距离在该范围内都算成功， 默认值为0.1米或0.18米，该值不影响机器人到点精度。 | [optional] 
**fail_retry_count** | **int** | 失败重试次数 | [optional] 
**speed_ratio** | **float** | 【所需固件版本 4.5.4】速度比例, 配置的最大移动速度乘以该值为本次运动的最大速度, 最小值为0.1, 大于1的值会导致避障距离变长，在动态障碍物较多的环境中请谨慎使用。 | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

