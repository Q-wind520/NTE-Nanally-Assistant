# 内置函数一览

本 README 用于概览项目编写的核心函数、内置脚本，方便开发者查找和修改内置函数。

---

# 内置脚本模块（`src/core/scripts`）

内置脚本通过 `@register("name")` 装饰器注册，供 TOML 外置脚本通过 `call` 动作调用。注册表定义在 `_base.py`。

## 注册机制

**文件**: [src/core/scripts/_base.py](../src/core/scripts/_base.py)

```python
@register("name")
def my_func(ctx: BuiltinContext) -> None:
    ...
```

| 函数 | 说明 |
|---|---|
| `register(name)` | 装饰器，将函数注册为内置脚本 |
| `get_builtin(name)` | 按名称查找内置函数 |
| `list_builtins()` | 返回所有已注册的内置函数名列表 |

### `BuiltinContext` 数据类

传递给内置脚本的上下文对象，包含以下字段和方法：

| 字段/方法 | 类型 | 说明 |
|---|---|---|
| `ctx.resolve(path)` | `(str) -> str` | 将相对路径（相对于 TOML 脚本 `base_path`）解析为绝对路径 |
| `ctx.params` | `dict[str, Any]` | TOML 中 `call` 动作的 `params` 参数 |
| `ctx.window_info` | `WindowInfo \| None` | 当前游戏窗口信息 |
| `ctx.press(key)` | `(str) -> None` | 按下并释放按键 |
| `ctx.click(image, **kw)` | `(str, **Any) -> bool` | 查找模板并点击 |
| `ctx.wait(image, **kw)` | `(str, **Any) -> MatchResult \| None` | 等待模板出现 |
| `ctx.wait_disappear(image, **kw)` | `(str, **Any) -> bool` | 等待模板消失 |
| `ctx.scroll(amount)` | `(int) -> None` | 鼠标滚轮滚动 |

---

## 移动类

**文件**: [src/core/scripts/movement.py](../src/core/scripts/movement.py)

### `map_teleport`
打开地图并传送到指定位置（TODO：实现地图选择逻辑）。
- **按键**: `m`

### `dash`
闪避/冲刺，支持连续多次。
- **按键**: `shift`
- **参数**: `count` (int, 默认 1) — 冲刺次数

```toml
# TOML 调用示例
[[loop]]
type = "call"
name = "dash"
params = { count = 3 }
```

---

## 战斗类

**文件**: [src/core/scripts/combat.py](../src/core/scripts/combat.py)

### `support_skill`
释放援护技。
- **按键**: `1`

### `parry`
弹刀 / 极限闪避后的反击。
- **按键**: `j`

### `skill_short_e`
短按 E 技能。
- **按键**: `e`

### `skill_long_e`
长按 E 技能（可配置持续时长）。
- **按键**: `e` (按住)
- **参数**: `hold` (float, 默认 2.0) — 按住时长（秒）

```toml
[[loop]]
type = "call"
name = "skill_long_e"
params = { hold = 3.0 }
```

### `skill_q`
Q 大招 / 终结技。
- **按键**: `q`

---

## 交互类

**文件**: [src/core/scripts/interaction.py](../src/core/scripts/interaction.py)

### `find_interact`
查找屏幕上的交互提示并按下交互键。
- **按键**: `f`
- **参数**:
  - `image` (str, 默认 `"interact.png"`) — 交互提示模板
  - `timeout` (float, 默认 5.0) — 等待超时

### `skip_cutscene`
跳过剧情/对话：先尝试点击跳过按钮，再按 Esc。
- **按键**: `esc` + 点击 skip 模板
- **参数**: `image` (str, 默认 `"skip.png"`) — 跳过按钮模板

---

# 核心框架（`src/core/packages`）

## 计算机视觉与模拟（`visual.py`）

**文件**: [src/core/packages/visual.py](../src/core/packages/visual.py)

核心视觉识别模块，基于 OpenCV 和 MSS 实现模板匹配与键鼠模拟。

### `MatchResult` 数据类（frozen）

| 属性 | 类型 | 说明 |
|---|---|---|
| `left` | int | 匹配区域左上角 X（绝对屏幕坐标） |
| `top` | int | 匹配区域左上角 Y |
| `width` | int | 匹配区域宽度 |
| `height` | int | 匹配区域高度 |
| `confidence` | float | 匹配置信度（-1.0 ~ 1.0） |
| `center` | `(int, int)` | 计算属性 — 匹配区域中心点 |
| `right` | int | 计算属性 — 右边界 |
| `bottom` | int | 计算属性 — 下边界 |
| `box` | `(int, int, int, int)` | 计算属性 — (left, top, width, height) |

### `VisualLocator` 类

主要图像识别引擎。

#### 构造与生命周期

```python
locator = VisualLocator(screen_index=0, confidence=0.8)
with VisualLocator() as loc:   # 支持上下文管理器
    ...
```

#### `capture_screen(region, scale) -> np.ndarray`
截取游戏窗口屏幕。若窗口非 720p，自动缩放到 720p 参考系。

#### `find_template(template_path, confidence, region, multi_scale, scale_min, scale_max, scale_steps) -> MatchResult | None`
在屏幕上查找单个模板图片。

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `template_path` | str | — | 模板图片路径 |
| `confidence` | float | 0.8 | 置信度阈值 |
| `region` | `(int,int,int,int)` | None | 搜索区域，None 则全窗口 |
| `multi_scale` | bool | False | 启用多尺度匹配 |
| `scale_min` | float | 0.95 | 多尺度最小缩放比例 |
| `scale_max` | float | 1.05 | 多尺度最大缩放比例 |
| `scale_steps` | int | 3 | 单侧步数（总尺度数 = 2×steps+1） |

多尺度匹配会在 95%~105% 范围内以 7 个尺度分别匹配模板，选取最高置信度结果。

#### `find_all_templates(template_path, confidence, region, max_results, multi_scale, ...) -> List[MatchResult]`
查找屏幕上所有匹配的模板。结果经 NMS（IoU 阈值 0.3）去重。

#### `wait_for_template(template_path, timeout, interval, confidence, region, multi_scale, ...) -> MatchResult | None`
轮询等待模板出现。默认超时 10s，间隔 0.5s。

#### `wait_for_template_disappear(template_path, timeout, interval, ...) -> bool`
轮询等待模板消失。返回 True 表示已消失，False 表示超时。

### `VisualInteractor` 类

封装基于图像识别的交互操作，内部持有 `VisualLocator` 实例。

| 方法 | 说明 |
|---|---|
| `click(target, offset, button, clicks, interval)` | 点击目标（支持模板路径、MatchResult、坐标元组） |
| `click_when_found(template_path, timeout, check_interval, click_offset, confidence, multi_scale, ...)` | 等待模板出现后点击 |
| `move_to(target, offset)` | 移动鼠标到目标位置 |

### 模块级便捷函数

| 函数 | 说明 |
|---|---|
| `click(image_path, timeout, confidence, timesleep, multi_scale, ...)` | 查找模板并点击中心 |
| `wait_image_appear(image_path, timeout, confidence, multi_scale, ...)` | 等待图片出现 |
| `wait_image_disappear(image_path, timeout, confidence, multi_scale, ...)` | 等待图片消失 |
| `find_all_images(image_path, confidence, max_results, multi_scale, ...)` | 查找所有匹配 |
| `scroll(amount)` | 滚轮滚动（正=上，负=下） |

---

## 窗口管理（`window.py`）

**文件**: [src/core/packages/window.py](../src/core/packages/window.py)

游戏窗口的检测、激活和信息获取。

### `WindowInfo` 数据类

| 字段 | 类型 | 说明 |
|---|---|---|
| `left` | int | 窗口左边界（屏幕坐标） |
| `top` | int | 窗口上边界 |
| `right` | int | 窗口右边界 |
| `bottom` | int | 窗口下边界 |
| `width` | int | 客户端区域宽度 |
| `height` | int | 客户端区域高度 |
| `scale` | float | 缩放比例（相对于 720p），`720 / height` |

### 函数

| 函数 | 说明 |
|---|---|
| `get_hwnd(name="HTGame.exe") -> int` | 根据进程名查找游戏窗口句柄 |
| `get_window(hwnd) -> WindowInfo` | 获取窗口几何信息和缩放比例（自动识别全屏/窗口化） |
| `activate_window(hwnd=None) -> None` | 激活（前台）游戏窗口 |
| `wait_for_target_resolution(timeout=300) -> WindowInfo` | 等待窗口调整为 16:9 宽高比 |

### 异常

| 异常 | 说明 |
|---|---|
| `WindowNotFoundError(RuntimeError)` | 未找到游戏窗口 |
| `WindowInvalidError(ValueError)` | 窗口状态无效 |
| `WindowResolutionTimeoutError(RuntimeError)` | 等待分辨率超时 |

---

## 进程检测（`process.py`）

**文件**: [src/core/packages/process.py](../src/core/packages/process.py)

| 函数 | 说明 |
|---|---|
| `is_process_running(name="HTGame.exe") -> bool` | 检查游戏进程是否在运行 |
| `wait_for_game_process(name, timeout=300, check_interval=2) -> None` | 等待进程启动 |

---

## 脚本注册表（`menu.py`）

**文件**: [src/core/packages/menu.py](../src/core/packages/menu.py)

### `ScriptInfo` 数据类

| 字段 | 类型 | 说明 |
|---|---|---|
| `name` | str | 脚本名称 |
| `description` | str | 脚本描述 |
| `runner` | `Callable[..., None]` | 执行函数 |
| `need_times_param` | bool | 是否需要传入执行次数 |
| `run(times=None)` | method | 执行脚本（自动校验参数） |

### `ScriptRegistry` 类

| 方法 | 说明 |
|---|---|
| `register(key, script)` | 注册脚本 |
| `unregister(key)` | 注销脚本 |
| `get(key) -> ScriptInfo \| None` | 获取脚本 |
| `get_all() -> dict[str, ScriptInfo]` | 获取全部脚本 |
| `has_key(key) -> bool` | 检查键是否存在 |

### 模块级函数

| 函数 | 说明 |
|---|---|
| `get_registry() -> ScriptRegistry` | 获取全局注册表单例 |
| `register_script(key, script)` | 向全局注册表注册 |
| `register_all_scripts()` | 扫描 `scripts/*.toml` 并注册所有外置脚本 |

---

## 全局常量（`constants.py`）

**文件**: [src/core/packages/constants.py](../src/core/packages/constants.py)

所有可配置常量集中管理。

### 进程检测

| 常量 | 默认值 | 说明 |
|---|---|---|
| `DEFAULT_PROCESS_NAME` | `"HTGame.exe"` | 游戏进程名 |
| `DEFAULT_PROCESS_TIMEOUT` | 300 | 等待进程启动超时（秒） |
| `DEFAULT_PROCESS_CHECK_INTERVAL` | 2 | 进程检查间隔（秒） |

### 窗口管理

| 常量 | 默认值 | 说明 |
|---|---|---|
| `WINDOW_BORDER_LEFT` | 8 | 窗口左边框宽度 |
| `WINDOW_BORDER_RIGHT` | 8 | 窗口右边框宽度 |
| `WINDOW_BORDER_TOP` | 30 | 窗口标题栏高度 |
| `WINDOW_BORDER_BOTTOM` | 9 | 窗口下边框高度 |
| `TARGET_ASPECT_RATIO` | 16/9 | 目标宽高比 |
| `TARGET_HEIGHT` | 720 | 模板参考高度（720p） |
| `ASPECT_RATIO_TOLERANCE` | 0.05 | 宽高比容差 |

### 视觉识别

| 常量 | 默认值 | 说明 |
|---|---|---|
| `DEFAULT_CONFIDENCE` | 0.8 | 默认模板匹配置信度 |
| `DEFAULT_TIMEOUT` | 10.0 | 默认查找超时（秒） |
| `DEFAULT_INTERVAL` | 0.5 | 默认轮询间隔（秒） |
| `DEFAULT_SCREEN_INDEX` | 0 | MSS 屏幕索引 |
| `DEFAULT_CLICK_OFFSET` | `(0, 0)` | 点击偏移量 |

### 多尺度模板匹配

| 常量 | 默认值 | 说明 |
|---|---|---|
| `MULTI_SCALE_MIN` | 0.95 | 最小缩放比例 |
| `MULTI_SCALE_MAX` | 1.05 | 最大缩放比例 |
| `MULTI_SCALE_STEPS` | 3 | 单侧步数 |

### 工具函数

| 函数 | 说明 |
|---|---|
| `get_asset_path(*parts) -> Path` | 获取资源路径（兼容 PyInstaller 打包和开发环境） |
| `get_version() -> str` | 从 `pyproject.toml` 读取版本号 |

---

# TOML 外置脚本（`scripts/`）

外置脚本放置于 `scripts/` 目录，为 TOML 格式的声明式脚本。在应用启动时自动扫描注册，也可通过"重载脚本"按钮在运行时刷新。

## 现有脚本

| 文件 | 名称 | 说明 | 资源目录 |
|---|---|---|---|
| `DiaoYu.toml` | 海上钓客 | 半自动钓鱼 | `assets/DY/` |
| `DZTG_1_1.toml` | 店长特供_1-1 | 1-1 速刷方斯 | `assets/DZTG_1-1/` |
| `DZTG_TuiGuanQia.toml` | 店长特供_推关卡 | 娜娜莉+百仓城技能推关 | `assets/DZTG_1-1/` + `assets/DZTG_TuiGuanQia/` |

## TOML 脚本结构

```toml
[meta]
name = "脚本名称"
description = "脚本描述"

[setup]
base_path = "./assets/xxx/"      # 模板图片根目录
activate_window = true            # 是否激活游戏窗口（默认 true）
wait_for_resolution = false       # 是否等待 16:9 分辨率（默认 false）

# 前置步骤（执行一次）
[[enter]]
type = "wait"
image = "start.png"

# 循环体（执行 times 次）
[[loop]]
type = "click"
image = "button.png"

# 后置步骤（执行一次）
[[exit]]
type = "press"
key = "esc"
```

## 支持的动作类型（18 种）

### 基础操作

| 动作 | 必需参数 | 可选参数 | 说明 |
|---|---|---|---|
| `click` | `image` | `timeout` (10.0), `confidence` (0.8), `timesleep` (0.5) | 等待模板出现后点击 |
| `wait` | `image` | `timeout` (10.0), `confidence` (0.8) | 等待模板出现 |
| `wait_disappear` | `image` | `timeout` (10.0), `confidence` (0.8) | 等待模板消失 |
| `wait_forever` | `image` | `confidence` (0.8) | 无限等待模板出现 |
| `press` | `key` | — | 按下并释放按键 |
| `move_to` | — | `x` (0), `y` (0) | 移动鼠标到窗口内相对坐标 |
| `click_at` | — | — | 在当前鼠标位置点击 |
| `sleep` | — | `duration` (1.0) | 等待指定秒数 |
| `scroll` | — | `amount` (1000), `repeat` (1), `interval` (0.0) | 滚轮滚动 |
| `print` | — | `text` ("") | 打印文本到日志 |

### 循环控制

| 动作 | 必需参数 | 可选参数 | 说明 |
|---|---|---|---|
| `break_if` | `image` | `timeout` (1.0), `confidence` (0.8), `message` ("") | 图片出现时跳出循环 |
| `continue_if_not` | `image` | `timeout` (10.0), `confidence` (0.8), `message` ("") | 图片未出现时跳过本轮循环 |

### 复合操作

| 动作 | 必需参数 | 可选参数 | 说明 |
|---|---|---|---|
| `click_until` | `image`, `target` | `confidence` (0.8) | 反复点击直到目标出现 |
| `scroll_until` | `image` | `confidence` (0.8), `scroll` (1000) | 反复滚动直到目标出现 |

### 内置脚本调用

| 动作 | 必需参数 | 可选参数 | 说明 |
|---|---|---|---|
| `call` | `name` | `params` ({}) | 调用已注册的内置 Python 脚本 |

```toml
# 调用内置脚本示例
[[loop]]
type = "call"
name = "skill_long_e"
params = { hold = 2.5 }
```

---

# GUI 模块（`src/gui/`）

## `main_window.py` — 主窗口

**文件**: [src/gui/main_window.py](../src/gui/main_window.py)

`MainWindow(QMainWindow)` — 应用主界面。

### 布局结构

- **侧边栏**（160px）：主页、日志、关于 三个导航按钮
- **页面容器**（QStackedWidget）：
  - **主页**：游戏状态卡片（进程、分辨率）+ 脚本控制卡片（脚本选择、执行次数、开始/停止/重载按钮）
  - **日志页**：只读日志输出（Consolas 字体，5000 行上限）+ 清空按钮
  - **关于页**：版本号、作者（GitHub 链接）、仓库链接、Issues 链接、许可证信息
- **状态栏**：显示当前状态（就绪 / 运行中 / 已重载）
- **系统托盘**：右键菜单（显示/隐藏、退出）+ 双击激活

### 关键方法

| 方法 | 说明 |
|---|---|
| `_populate_scripts()` | 扫描 `scripts/` 并填充脚本下拉列表 |
| `_reload_scripts()` | 重载外置脚本（运行时可用） |
| `_start_script()` | 校验宽高比后启动脚本线程 |
| `_stop_script()` | 强制终止脚本线程 |
| `_poll_status()` | 每 2 秒轮询进程状态和分辨率 |

### 状态轮询

QTimer 每 2 秒触发 `_poll_status()`：
- 检测游戏进程是否运行 → 更新"游戏状态"标签颜色
- 读取窗口分辨率 → 显示当前宽×高

## `script_worker.py` — 脚本工作线程

**文件**: [src/gui/script_worker.py](../src/gui/script_worker.py)

`ScriptWorker(QThread)` — 在后台线程执行脚本，避免阻塞 UI。

### 信号

| 信号 | 参数 | 说明 |
|---|---|---|
| `started_signal` | `str` (脚本名) | 脚本开始执行 |
| `finished_signal` | — | 脚本正常完成 |
| `error_signal` | `str` (错误信息) | 脚本异常 |

## `log_handler.py` — 日志桥接

**文件**: [src/gui/log_handler.py](../src/gui/log_handler.py)

将 Python logging 和 stdout 桥接到 Qt 信号/槽，实现线程安全的 UI 日志更新。

| 类 | 说明 |
|---|---|
| `QtLogHandler(logging.Handler)` | 拦截 Python logging 记录，通过 `_LogSignal.message` 发射到 UI 线程 |
| `QtStreamRedirector(QObject)` | 拦截 `sys.stdout`，将 `print()` 输出转发到 UI 线程 |
| `get_log_signal() -> _LogSignal` | 获取全局日志信号单例 |

---

# 项目入口（`main.py`）

**文件**: [src/main.py](../src/main.py)

1. 设置 Windows DPI 感知为 `PerMonitorV2`
2. 配置日志文件输出（`log/` 目录，带时间戳）
3. 创建 `QApplication`，安装 `QtLogHandler` 和 `QtStreamRedirector`
4. 实例化并显示 `MainWindow`
5. 进入 Qt 事件循环
