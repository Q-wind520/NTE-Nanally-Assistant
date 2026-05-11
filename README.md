# <div ><center />NTE Nanally Assistant(异环_NA)</div>

<div ><center /><img src=./docs/img/icon.png alt='icon' title='Nanally Assistant' width='30%'></div>

-----

## 简述

NTE Nanally Assistant（异环娜娜莉助手）是一个基于计算机视觉、模拟键鼠操作的脚本项目，可以帮助你在异环中自动完成一些枯燥的任务。

## Support

### 支持的操作系统 / Systems supported:

- Windows

### 支持的异环服务器 / Supported NTE servers:

- B服 Bilibili Server

## Functions

### 支持的功能:

- 都市闲趣
    - 店长特供
        - 1-1速刷方斯
        - TODO:角色推关

## Star

如果你认为本项目对你有帮助，请点一点右上角的Star⭐，谢谢喵~o( =∩ω∩= )m

## Packages

[Opencv-python](https://github.com/opencv/opencv-python)    
[PyAutoGUI](https://github.com/asweigart/pyautogui)    
[PyDirectInput](https://github.com/learncodebygaming/pydirectinput)

## Log

### Recent

目前处于开发状态

### History

2026年4月26日 立项    
哇哇哇，觉得异环很肝，一时兴起准备写个脚本试试，现在发现写脚本也肝啊。本来想用pyautogui快速解决，然而这貌似对几乎零基础的我来说还是太难了o(╥﹏╥)o。只能是边学边做了。

2026年4月29日 可行性测试    
经过代码小白的不断学习，终于……找到了可行的方法，pydirectinput太强大，开源社区真胃大（

2026年4月30日 完善脚本    
单文件处理了兼容屏幕分辨率问题及脚本bug

2026年5月5日 分辨率兼容失败 | 正式开始写项目    
坐标转换不管用，我准备直接都用截屏识别了。刚学会用多文件串联代码，现在基本都转到main.py里了

2026年5月6日 放弃兼容多分辨率 | 加入截屏识别    
原本想试试用截屏搜索代替坐标转换，然而对于其他分辨率来说依旧毫无卵用，故放弃。今天就写了一个函数。

2026年5月8日 优化视觉模块    
引入视觉模块以后麻烦好多，不会写o(TヘTo)

2026年5月10日 重构项目结构 | 加入自动激活窗口    
使用了pip install -e .命令来管理包，现在直接从项目根开始引用函数。使用win32来获取句柄并激活窗口，体验plusplus( •̀ ω •́ )✧    
两个TODO：把sleep换掉，图像检测到倒计时时点击，不然以后写的难受。把在全屏点击换成获取窗口坐标，按理说这样就能通过游戏窗口化到1080P来兼容更多分辨率显示器了（我试过好多办法了(；′⌒`)）

2026年5月11日 整合视觉模块    
用click把点击和识别合并，增加了timeout。这次试用了Trea CN写代码，这软件过度集成AI了，我感觉难以驾驭。