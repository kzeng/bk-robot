# LightControlData

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**channel** | **str** | led控制通道:One通道一，Two通道二 | [optional] 
**control_part** | **str** | led控制部分:Left左半部，Right右半部 | [optional] 
**mode** | **str** | led控制模式:AlwaysBright常亮，Breathe呼吸，Blink闪烁，HorseLamp跑马 | [optional] 
**color** | [**LightControlDataColor**](LightControlDataColor.md) |  | [optional] 
**brightness_end_color** | [**LightControlDataBrightnessEndColor**](LightControlDataBrightnessEndColor.md) |  | [optional] 
**bright_ms** | **int** | 常亮模式可填入任意值；呼吸模式填入亮度单次变化时间（单次变化表示color每次增大1的时间）；闪烁模式填入点亮的持续时间；跑马模式表示点亮下一个灯的时间 | [optional] 
**off_ms** | **int** | 闪烁模式填入熄灭的持续时间；其他模式可填入任意值 | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)

