# BackOffFromTagActionOptions

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**backup_mode** | **int** | * &#x60;0&#x60; 自由后退 * &#x60;1&#x60; 窄道后退，在后退过程中一直观测二维码并调整角度  | [optional] 
**tag_type** | **int** | 0：二维码视觉标签， 1：激光标签, 2： 激光反光板 | [optional] [default to Tag_typeEnum._0]
**backup_distance** | **float** | 后退的距离, 可选值，默认后退直到机器可以转身 | [optional] 
**backward_docking** | **bool** | 是否向后对接, 如果是向后对接，则调用BackOffFromTagAction时实际是向前移动 | [optional] [default to False]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

