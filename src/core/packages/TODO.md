# TODO - visual

## class VisualLocator

已有：
- 捕获屏幕截图
  - region: 截图区域 (left, top, width, height)，None 则使用窗口区域
  - scale: 缩放比例，None 则使用窗口默认缩放
- 在屏幕上查找单个模板图片
  - template_path: 模板图片路径
  - confidence: 匹配置信度阈值，None 使用默认值
  - region: 搜索区域，None 则使用窗口区域
  - multi_scale: 是否启用多尺度匹配
  - scale_min: 多尺度匹配的最小缩放比例
  - scale_max: 多尺度匹配的最大缩放比例
  - scale_steps: 多尺度匹配的单侧步数
- 在屏幕上查找所有匹配的模板图片
  - template_path: 模板图片路径
  - confidence: 匹配置信度阈值
  - region: 搜索区域
  - max_results: 最大返回结果数
  - multi_scale: 是否启用多尺度匹配
  - scale_min: 多尺度匹配的最小缩放比例
  - scale_max: 多尺度匹配的最大缩放比例
  - scale_steps: 多尺度匹配的单侧步数
- 等待模板图片出现在屏幕上
  - template_path: 模板图片路径
  - timeout: 超时时间（秒）
  - interval: 检查间隔（秒）
  - confidence: 匹配置信度
  - region: 搜索区域
  - multi_scale: 是否启用多尺度匹配
  - scale_min: 多尺度匹配的最小缩放比例
  - scale_max: 多尺度匹配的最大缩放比例
  - scale_steps: 多尺度匹配的单侧步数
- 等待模板图片从屏幕上消失
  - template_path: 模板图片路径
  - timeout: 超时时间（秒）
  - interval: 检查间隔（秒）
  - confidence: 匹配置信度
  - region: 搜索区域
  - multi_scale: 是否启用多尺度匹配
  - scale_min: 多尺度匹配的最小缩放比例
  - scale_max: 多尺度匹配的最大缩放比例
  - scale_steps: 多尺度匹配的单侧步数





## class VisualInteractor

已有：
- 将目标解析为 (x, y) 坐标。模板未找到时返回 None。
- 点击目标位置。支持模板路径、匹配结果或坐标元组。
- 等待并点击模板图片
  - template_path: 模板图片路径
  - timeout: 查找超时时间
  - check_interval: 查找检查间隔
  - click_offset: 点击偏移量
  - confidence: 匹配置信度
  - on_timeout: 超时回调函数
  - multi_scale: 是否启用多尺度匹配
  - scale_min: 多尺度匹配的最小缩放比例
  - scale_max: 多尺度匹配的最大缩放比例
  - scale_steps: 多尺度匹配的单侧步数
- 移动鼠标到目标位置。支持模板路径、匹配结果或坐标元组。

## 便捷函数

已有：
- 在屏幕上查找模板图片并点击其中心位置（向后兼容）
  image_path: 模板图片路径
  timeout: 查找超时时间（秒）
  confidence: 匹配置信度
  timesleep: 点击前的等待时间（默认0.5秒）
  on_failure: 失败时的回调函数
  multi_scale: 是否启用多尺度匹配
  scale_min: 多尺度匹配的最小缩放比例
  scale_max: 多尺度匹配的最大缩放比例
  scale_steps: 多尺度匹配的单侧步数
- 
- 
- 
- 






