# NTE Nanally Assistant（异环_NA）

<div><center><img src=./docs/img/icon.png alt='icon' title='Nanally Assistant' width='30%'></center></div>

---

## 简述

NTE Nanally Assistant（异环娜娜莉助手）是一个基于计算机视觉、模拟键鼠操作的自动化脚本工具，帮助你在异环中自动完成枯燥的任务。

## 快速开始

### 推荐使用方式

从 Release 下载最新的 `NanallyAssistant_v*_Setup.exe`，安装后双击运行（首次启动会请求管理员权限）。将游戏窗口调整为 16:9 分辨率（如 1280×720、1600×900、1920×1080 等），站到对应位置执行脚本即可。

### 从源码运行

```powershell
# 搭建虚拟环境
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 安装依赖
pip install -e .

# 运行
python src\main.py
```

要求 Python 3.12.8，项目根目录执行。

## 构建

构建配置统一存放在 `builder/` 目录：

| 文件 | 说明 | 命令 |
|------|------|------|
| `build_nuitka.ps1` | Nuitka 原生编译（性能版） | `powershell -File builder/build_nuitka.ps1` |
| `NanallyAssistant.spec` | PyInstaller 打包 | `pyinstaller builder/NanallyAssistant.spec` |
| `setup.iss` | Inno Setup 安装包 | `iscc builder/setup.iss` |

构建产物输出到 `dist/`。

## 架构

```
src/
├── main.py                 # 入口
├── core/
│   ├── settings.py         # 配置持久化 (~/.nanally-assistant/settings.json)
│   ├── packages/           # 框架核心
│   │   ├── constants.py    # 全局常量、版本、资源路径
│   │   ├── window.py       # 窗口管理 (Win32)
│   │   ├── process.py      # 进程检测
│   │   ├── menu.py         # 脚本注册
│   │   └── visual/         # 视觉识别 (OpenCV 模板匹配)
│   ├── scripts/            # 内置 Python 脚本
│   └── toml_runner.py      # TOML 声明式脚本引擎
└── gui/
    ├── __init__.py
    ├── log_handler.py      # 日志信号桥接
    ├── script_worker.py    # 脚本工作线程
    ├── theme.py            # 主题系统 (深/浅色切换、主题色)
    └── main_window.py      # 主窗口
```

## Support

### 屏幕支持

分辨率支持所有 16:9 窗口。模板基于 720P，游戏窗口在 1280×720 下性能最佳。多屏幕下存在未知 Bug，建议单屏使用。

### 操作系统

- Windows 10 / 11

## Functions

- **都市闲趣**
  - 店长特供 — 1-1 速刷方斯
  - 海上钓客 — 自动钓鱼（核心功能待实现）

## Packages

[Opencv-python](https://github.com/opencv/opencv-python) · [MSS](https://github.com/BoboTiG/python-mss) · [PyDirectInput](https://github.com/learncodebygaming/pydirectinput) · [PyWin32](https://github.com/mhammond/pywin32) · [PySide6](https://pypi.org/project/PySide6/)

## Star

如果你认为本项目对你有帮助，请点一点右上角的 Star⭐，谢谢喵~o( =∩ω∩= )m

## Log

详见 [开发日志.md](./docs/CodingLog.md)
