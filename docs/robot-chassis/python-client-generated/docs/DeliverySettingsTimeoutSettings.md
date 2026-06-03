# DeliverySettingsTimeoutSettings

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**takeout_pickup_timeout** | **int** | 配送到达目的地后，等待用户开仓的时间，单位秒 | [optional] [default to 300]
**takeout_open_door_timeout** | **int** | 用户开仓后，自动关仓的等待时间，单位秒 | [optional] [default to 90]
**collect_pickup_timeout** | **int** | 配送失败返回前台时，等待用户取物的时间，单位秒 | [optional] [default to 300]
**brake_released_timeout** | **int** | 按下刹车释放和急停时，任务等待时间，只要在该时间内恢复任务就能继续执行 | [optional] [default to 300]
**food_pickup_timeout** | **int** | 送餐到达目的地后，等待用户取餐的时间，单位秒 | [optional] [default to 120]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

