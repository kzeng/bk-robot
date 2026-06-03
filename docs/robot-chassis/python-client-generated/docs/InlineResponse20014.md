# InlineResponse20014

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**is_in_mapping_mode** | **bool** | 是否处于建图模式 | [optional] 
**map_load_status** | **str** | * &#x60;NOT_LOADED&#x60;本地没有地图文件。 * &#x60;LOADING&#x60; 正在加载地图。 * &#x60;LOADED&#x60;成功加载地图。 * &#x60;LOADING_SKIPPED&#x60; 跳过地图加载步骤，在人为重启单个服务时会进入该状态。 * &#x60;NEED_LOAD&#x60; 执行任务过程中收到同步云端地图的命令，会等回桩后再自动同步地图。 * &#x60;ERROR&#x60; 状态异常，地图文件错误或启动楼层信息不匹配  | [optional] 
**is_managed_by_cloud** | **bool** | 是否由云端管理 | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

