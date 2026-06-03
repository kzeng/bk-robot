# DeliverySettingsLowBatteryLevel

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**level1** | **int** | 达到该电量时机器人自动关机 | [optional] [default to 6]
**level2** | **int** | 达到该电量时机器人取消所有任务并回桩 | [optional] [default to 10]
**level3** | **int** | 预留，通过云端调度机器时，一旦达到该电量应当禁止下发新的任务 | [optional] [default to 20]
**level4** | **int** | 达到该电量时，机器人无法创建外卖配送单 | [optional] [default to 30]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

