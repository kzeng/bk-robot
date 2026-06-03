# PostTaskRequestEntry

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**location** | [**PostTaskRequestEntryLocation**](PostTaskRequestEntryLocation.md) |  | [optional] 
**type** | **str** | * &#x60;TAKEOUT&#x60; 外卖配送任务（仅限有货仓的机型）  * &#x60;GUIDE&#x60; 引领任务，将人带到指定目的地 * &#x60;FOOD_DELIVERY&#x60; 送餐任务 * &#x60;RETURN&#x60; 快速返航，回到取餐点 * &#x60;RECYCLE&#x60; 回收餐盘 * &#x60;TAKEOUT_DISTRIBUTE&#x60; 外卖分发，打开所有舱门由用户自主取物  | [optional] 
**cargos** | [**list[CargoEntry]**](CargoEntry.md) |  | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

