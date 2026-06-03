# LeaveElevatorOptions

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**elevator_door_flag** | **list[str]** | * &#x60;front_door&#x60; 从电梯前门进入 * &#x60;rear_door&#x60; 从电梯后门进入  | [optional] 
**timeout_in_ms** | **float** | 出电梯的总时长 | [optional] 
**arrive_door_timeout_in_ms** | **float** | 出电梯过程中到达电梯门的超时时间 | [optional] 
**search_path_timeout_in_ms** | **float** | 出电梯的搜路超时时间，超过这个时间仍未搜到路便放弃出电梯 | [optional] 
**on_elevator_door_timeout_in_ms** | **float** | 堵在电梯门槛上的超时时间，到达超时放弃出梯 | [optional] 
**if_need_reach_milestone** | **bool** | true前往出后前往目标点，false表示只到达门口等待点 | [optional] 
**move_options** | [**MoveOptions**](MoveOptions.md) |  | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

