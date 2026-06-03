# MoveToTagActionOptions

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**target** | [**Pose3D**](Pose3D.md) |  | 
**tag_type** | **int** | 0：二维码视觉标签， 1：激光标签, 2：激光反光板, 3：货架(需要6.0或更高版本) | [default to Tag_typeEnum._0]
**target_relative_pose** | [**MoveToTagActionOptionsTargetRelativePose**](MoveToTagActionOptionsTargetRelativePose.md) |  | [optional] 
**backward_docking** | **bool** | 是否向后对接 | [optional] [default to False]
**turn_radian** | **float** | 对接成功后的转向弧度，默认机器是面向或背对Tag，如果需要机器在对接成功后转指定角度，请设置该字段。 | [optional] 
**tag_ids** | **list[int]** | tag_type为0时有效，二维码ID | [optional] 
**reflect_tag_num** | **int** | tag_type为2时有效，对接的反光板个数，默认为1. | [optional] 
**dock_retry_count** | **int** | 对接失败后的重试次数，默认不重试. | [optional] 
**dock_allowance** | **float** | tag_type为3时有效，对接货架时默认机器中心对准货架中心。dock_allowance表示机器人留在货架外的机身长度。 | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

