# Line

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** | 如果是添加线段，id会被忽略，如果是编辑线段，则会修改对应id的线段 | [optional] 
**start** | [**Point**](Point.md) |  | [optional] 
**end** | [**Point**](Point.md) |  | [optional] 
**metadata** | **OneOfLineMetadata** | 如果是直线轨道，metadata为EmptyMetadata，如果是贝塞尔曲线轨道，metadata为BezierCurveMetadata | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

