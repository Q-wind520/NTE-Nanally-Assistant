from __future__ import annotations

import logging

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenu,
    QPushButton,
    QSpinBox,
    QStackedWidget,
    QStatusBar,
    QSystemTrayIcon,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QMessageBox,
)

from core.packages.constants import (
    DEFAULT_PROCESS_NAME, DEFAULT_TITLE, DEFAULT_AUTHOR,
    TARGET_ASPECT_RATIO, ASPECT_RATIO_TOLERANCE,
    GITHUB_AUTHOR_URL, GITHUB_REPO_URL, GITHUB_ISSUES_URL,
    get_asset_path as gap, get_version,
)
from core.packages.process import is_process_running
from core.packages.window import get_hwnd, get_window, WindowNotFoundError, WindowInvalidError
from core.packages.menu import register_all_scripts, get_registry

from gui.script_worker import ScriptWorker
from gui.log_handler import get_log_signal
from core.settings import load as load_settings, save as save_settings
import gui.theme as theme

logger = logging.getLogger(__name__)


def _icon_path() -> str:
    icon = gap('docs', 'img', 'icon.ico')
    if icon.exists():
        return str(icon)
    png = gap('docs', 'img', 'icon.png')
    if png.exists():
        return str(png)
    return ""


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(f"{DEFAULT_TITLE} {get_version()}")
        self.resize(960, 580)

        icon = _icon_path()
        if icon:
            self.setWindowIcon(QIcon(icon))

        self._worker: ScriptWorker | None = None

        _cfg = load_settings()
        if _cfg.get("accent_color"):
            theme.set_accent_color(_cfg["accent_color"])
        theme.set_theme_override(_cfg.get("theme_override"))

        self._build_ui()
        self._setup_tray()
        self._connect_global_signals()
        self._populate_scripts()
        self._start_status_poll()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # --- 侧边栏 ---
        self._sidebar = QWidget()
        self._sidebar.setFixedWidth(160)
        sidebar_layout = QVBoxLayout(self._sidebar)
        sidebar_layout.setContentsMargins(0, 8, 0, 8)
        sidebar_layout.setSpacing(2)

        self._nav_group = QButtonGroup(self)
        self._nav_group.setExclusive(True)

        self._nav_home = QPushButton("  主页")
        self._nav_home.setCheckable(True)
        self._nav_home.setChecked(True)
        self._nav_home.setCursor(Qt.CursorShape.PointingHandCursor)

        self._nav_settings = QPushButton("  设置")
        self._nav_settings.setCheckable(True)
        self._nav_settings.setCursor(Qt.CursorShape.PointingHandCursor)

        self._nav_about = QPushButton("  关于")
        self._nav_about.setCheckable(True)
        self._nav_about.setCursor(Qt.CursorShape.PointingHandCursor)

        self._nav_group.addButton(self._nav_home, 0)
        self._nav_group.addButton(self._nav_settings, 1)
        self._nav_group.addButton(self._nav_about, 2)

        sidebar_layout.addWidget(self._nav_home)
        sidebar_layout.addWidget(self._nav_settings)
        sidebar_layout.addWidget(self._nav_about)
        sidebar_layout.addStretch()

        root.addWidget(self._sidebar)

        # --- 页面容器 ---
        self._pages = QStackedWidget()
        self._pages.addWidget(self._build_home_page())
        self._pages.addWidget(self._build_settings_page())
        self._pages.addWidget(self._build_about_page())

        self._nav_group.idClicked.connect(self._pages.setCurrentIndex)

        root.addWidget(self._pages, 1)

        self._connect_page_signals()

        # --- 状态栏 ---
        self._status_bar = QStatusBar()
        self.setStatusBar(self._status_bar)
        self._status_bar.showMessage("就绪")

        # --- 全局主题 ---
        QApplication.instance().setStyleSheet(theme._global_qss())
        self._update_sidebar_theme()

    def _build_home_page(self) -> QWidget:
        page = QWidget()
        page.setStyleSheet(f"background: {theme._page_bg()};")
        layout = QVBoxLayout(page)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 16, 20, 16)

        status_widget = QWidget()
        status_widget.setStyleSheet(f"background: {theme._card_bg()}; border-radius: 6px; padding: 12px;")
        status_layout = QVBoxLayout(status_widget)
        status_layout.setSpacing(6)
        title_label = QLabel("游戏状态")
        title_label.setStyleSheet(f"font-size: 15px; font-weight: bold; color: {theme._text_color()};")
        status_layout.addWidget(title_label)
        status_row = QHBoxLayout()
        self._process_label = QLabel("等待检测...")
        self._resolution_label = QLabel("等待检测...")
        status_row.addWidget(self._process_label)
        status_row.addWidget(self._resolution_label)
        status_row.addStretch()
        status_layout.addLayout(status_row)
        layout.addWidget(status_widget)

        # 左右分栏：实时日志 | 脚本控制
        split_layout = QHBoxLayout()
        split_layout.setSpacing(12)

        # ---- 左侧：实时日志 ----
        log_widget = QWidget()
        log_widget.setStyleSheet(f"background: {theme._card_bg()}; border-radius: 6px; padding: 12px;")
        log_layout = QVBoxLayout(log_widget)
        log_layout.setSpacing(8)

        log_header = QHBoxLayout()
        log_title = QLabel("实时日志")
        log_title.setStyleSheet(f"font-size: 15px; font-weight: bold; color: {theme._text_color()};")
        log_header.addWidget(log_title)
        log_header.addStretch()
        self._clear_btn = QPushButton("清空日志")
        log_header.addWidget(self._clear_btn)
        log_layout.addLayout(log_header)

        self._log_output = QTextEdit()
        self._log_output.setReadOnly(True)
        self._log_output.setFont(QFont("Consolas", 10))
        self._log_output.document().setMaximumBlockCount(5000)
        log_layout.addWidget(self._log_output)

        split_layout.addWidget(log_widget, 1)

        # ---- 右侧：脚本控制 ----
        control_widget = QWidget()
        control_widget.setStyleSheet(f"background: {theme._card_bg()}; border-radius: 6px; padding: 12px;")
        control_layout = QVBoxLayout(control_widget)
        control_layout.setSpacing(10)

        control_header = QHBoxLayout()
        control_title = QLabel("脚本控制")
        control_title.setStyleSheet(f"font-size: 15px; font-weight: bold; color: {theme._text_color()};")
        control_header.addWidget(control_title)
        control_header.addStretch()
        self._reload_btn = QPushButton("重载脚本")
        control_header.addWidget(self._reload_btn)
        control_layout.addLayout(control_header)

        script_row = QHBoxLayout()
        script_row.addWidget(QLabel("脚本:"))
        self._script_combo = QComboBox()
        self._script_combo.setMinimumWidth(200)
        script_row.addWidget(self._script_combo, 1)
        control_layout.addLayout(script_row)

        self._script_intro = QLabel()
        self._script_intro.setWordWrap(True)
        self._script_intro.setStyleSheet(f"font-size: 12px; color: {theme._text_color()};")
        control_layout.addWidget(self._script_intro)

        times_row = QHBoxLayout()
        times_row.addWidget(QLabel("执行次数:"))
        self._times_spin = QSpinBox()
        self._times_spin.setRange(1, 9999)
        self._times_spin.setValue(1)
        times_row.addWidget(self._times_spin)
        times_row.addStretch()
        control_layout.addLayout(times_row)

        control_layout.addStretch()

        self._toggle_btn = QPushButton("▶ 开始执行")
        self._style_toggle_btn()
        control_layout.addWidget(self._toggle_btn)

        split_layout.addWidget(control_widget)

        layout.addLayout(split_layout)
        return page

    def _build_settings_page(self) -> QWidget:
        page = QWidget()
        page.setStyleSheet(f"background: {theme._page_bg()};")
        layout = QVBoxLayout(page)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 16, 20, 16)

        title_label = QLabel("设置")
        title_label.setStyleSheet(f"font-size: 15px; font-weight: bold; color: {theme._text_color()};")
        layout.addWidget(title_label)

        # 外观设置
        appearance_widget = QWidget()
        appearance_widget.setStyleSheet(f"background: {theme._card_bg()}; border-radius: 6px; padding: 16px;")
        appearance_layout = QVBoxLayout(appearance_widget)
        appearance_layout.setSpacing(12)

        appearance_title = QLabel("外观设置")
        appearance_title.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {theme._text_color()};")
        appearance_layout.addWidget(appearance_title)

        theme_row = QHBoxLayout()
        theme_row.addWidget(QLabel("主题模式:"))
        self._theme_combo = QComboBox()
        self._theme_combo.addItem("跟随系统", "system")
        self._theme_combo.addItem("浅色", "light")
        self._theme_combo.addItem("深色", "dark")
        if theme._theme_override is None:
            self._theme_combo.setCurrentIndex(0)
        elif theme._theme_override == "light":
            self._theme_combo.setCurrentIndex(1)
        else:
            self._theme_combo.setCurrentIndex(2)
        self._theme_combo.currentIndexChanged.connect(self._on_theme_changed)
        theme_row.addWidget(self._theme_combo)
        theme_row.addStretch()
        appearance_layout.addLayout(theme_row)

        # 主题色
        accent_row = QHBoxLayout()
        accent_row.addWidget(QLabel("主题色:"))

        self._preset_colors = ["#6b9fed", "#ff6b9d", "#ff4444", "#44bb44", "#ff8844"]
        self._accent_presets = []
        for c in self._preset_colors:
            btn = QPushButton()
            btn.setFixedSize(24, 24)
            selected = "border: 2px solid #000000;" if c == theme._accent_color else "border: 2px solid #888888;"
            btn.setStyleSheet(
                f"QPushButton {{ background-color: {c}; {selected} border-radius: 4px; }}"
                f"QPushButton:hover {{ border: 2px solid #000000; }}"
            )
            btn.clicked.connect(lambda checked, color=c: self._on_accent_picked(color))
            self._accent_presets.append(btn)
            accent_row.addWidget(btn)

        accent_row.addStretch()
        accent_row.addWidget(QLabel("自定义:"))
        self._accent_input = QLineEdit()
        self._accent_input.setMaxLength(7)
        self._accent_input.setPlaceholderText("#RRGGBB")
        self._accent_input.setText(theme._accent_color)
        self._accent_input.textChanged.connect(self._on_accent_input_changed)
        accent_row.addWidget(self._accent_input)
        appearance_layout.addLayout(accent_row)

        layout.addWidget(appearance_widget)
        layout.addStretch()
        return page

    def _build_about_page(self) -> QWidget:
        page = QWidget()
        page.setStyleSheet(f"background: {theme._page_bg()};")
        layout = QVBoxLayout(page)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 16, 20, 16)

        title_label = QLabel("关于")
        title_label.setStyleSheet(f"font-size: 15px; font-weight: bold; color: {theme._text_color()};")
        layout.addWidget(title_label)

        info_widget = QWidget()
        info_widget.setStyleSheet(f"background: {theme._card_bg()}; border-radius: 6px; padding: 16px;")
        info_layout = QVBoxLayout(info_widget)
        info_layout.setSpacing(12)

        # 版本
        ver_label = QLabel(f"版本: {get_version()}")
        ver_label.setStyleSheet("font-size: 13px;")
        info_layout.addWidget(ver_label)

        # 作者
        author_label = QLabel(
            f'作者: <a href="{GITHUB_AUTHOR_URL}" style="color: #6b9fed;">{DEFAULT_AUTHOR}</a>'
        )
        author_label.setOpenExternalLinks(True)
        author_label.setStyleSheet("font-size: 13px;")
        info_layout.addWidget(author_label)

        # 仓库
        repo_label = QLabel(
            f'仓库: <a href="{GITHUB_REPO_URL}" style="color: #6b9fed;">{GITHUB_REPO_URL}</a>'
        )
        repo_label.setOpenExternalLinks(True)
        repo_label.setStyleSheet("font-size: 13px;")
        info_layout.addWidget(repo_label)

        # Issues
        issues_label = QLabel(
            f'反馈: <a href="{GITHUB_ISSUES_URL}" style="color: #6b9fed;">提交 Issue</a>'
        )
        issues_label.setOpenExternalLinks(True)
        issues_label.setStyleSheet("font-size: 13px;")
        info_layout.addWidget(issues_label)

        info_layout.addSpacing(8)

        # 开源协议
        license_label = QLabel(
            '开源协议: <a href="https://www.gnu.org/licenses/gpl-3.0.html" '
            'style="color: #6b9fed;">GPLv3</a>'
        )
        license_label.setOpenExternalLinks(True)
        license_label.setStyleSheet("font-size: 13px;")
        info_layout.addWidget(license_label)

        license_desc = QLabel(
            "本软件为自由软件，您可以自由使用、修改和重新发布，"
            "但必须保留相同的许可证并公开源代码。"
        )
        license_desc.setWordWrap(True)
        license_desc.setStyleSheet(f"font-size: 12px; color: {theme._text_color()}; opacity: 0.7;")
        info_layout.addWidget(license_desc)

        layout.addWidget(info_widget)
        layout.addStretch()
        return page

    # ------------------------------------------------------------------
    # 脚本列表
    # ------------------------------------------------------------------

    def _populate_scripts(self) -> None:
        register_all_scripts()
        all_scripts = get_registry().get_all()
        self._script_combo.clear()
        for key, info in all_scripts.items():
            if key == "0":
                continue
            self._script_combo.addItem(info.name, info)
        self._on_script_changed(0)

    def _reload_scripts(self) -> None:
        """重新扫描并加载外置脚本"""
        self._populate_scripts()
        count = self._script_combo.count()
        self._status_bar.showMessage(f"已重载 {count} 个脚本")
        self._append_log(f"[INFO] 已重载 {count} 个外置脚本")

    # ------------------------------------------------------------------
    # 信号连接
    # ------------------------------------------------------------------

    def _connect_global_signals(self) -> None:
        """只连接一次的非页面信号"""
        get_log_signal().message.connect(self._append_log)

    def _connect_page_signals(self) -> None:
        """页面重建后需要重新连接的信号"""
        self._script_combo.currentIndexChanged.connect(self._on_script_changed)
        self._toggle_btn.clicked.connect(self._toggle_script)
        self._reload_btn.clicked.connect(self._reload_scripts)
        self._clear_btn.clicked.connect(self._log_output.clear)

    # ------------------------------------------------------------------
    # 主题
    # ------------------------------------------------------------------

    def _on_theme_changed(self, index: int) -> None:
        mode = self._theme_combo.itemData(index)
        theme.set_theme_override(None if mode == "system" else mode)
        save_settings(theme_override=theme._theme_override)
        self._apply_theme()

    def _apply_theme(self) -> None:
        idx = self._pages.currentIndex()

        while self._pages.count():
            w = self._pages.widget(0)
            self._pages.removeWidget(w)
            w.deleteLater()

        self._pages.addWidget(self._build_home_page())
        self._pages.addWidget(self._build_settings_page())
        self._pages.addWidget(self._build_about_page())

        if idx < self._pages.count():
            self._pages.setCurrentIndex(idx)
        else:
            self._pages.setCurrentIndex(0)

        self._connect_page_signals()
        self._populate_scripts()
        QApplication.instance().setStyleSheet(theme._global_qss())
        self._update_sidebar_theme()
        self._append_log(f"[INFO] 主题已切换")

    def _update_sidebar_theme(self) -> None:
        dark = theme._is_dark_mode()
        self._sidebar.setStyleSheet(f"background: {'#2b2b2b' if dark else '#e0e0e0'};")
        for btn in (self._nav_home, self._nav_settings, self._nav_about):
            btn.setStyleSheet(theme._sidebar_style())

    def _on_accent_picked(self, color: str) -> None:
        theme.set_accent_color(color)
        save_settings(accent_color=color)
        self._accent_input.setText(color)
        self._apply_accent()

    def _on_accent_input_changed(self, text: str) -> None:
        if len(text) == 7 and text.startswith("#"):
            theme.set_accent_color(text)
            save_settings(accent_color=text)
            self._apply_accent()

    def _apply_accent(self) -> None:
        for i, btn in enumerate(self._accent_presets):
            c = self._preset_colors[i]
            selected = "border: 2px solid #000000;" if c == theme._accent_color else "border: 2px solid #888888;"
            btn.setStyleSheet(
                f"QPushButton {{ background-color: {c}; {selected} border-radius: 4px; }}"
                f"QPushButton:hover {{ border: 2px solid #000000; }}"
            )
        QApplication.instance().setStyleSheet(theme._global_qss())
        self._update_sidebar_theme()
        self._style_toggle_btn()
        self._append_log(f"[INFO] 主题色已切换")

    # ------------------------------------------------------------------
    # 脚本启停
    # ------------------------------------------------------------------

    def _on_script_changed(self, _index: int) -> None:
        info = self._script_combo.currentData()
        if info is not None:
            self._times_spin.setEnabled(info.need_times_param)
            self._script_intro.setText(info.description)
        else:
            self._script_intro.setText("")

    def _toggle_script(self) -> None:
        if self._toggle_btn.text() == "▶ 开始执行":
            self._start_script()
        else:
            self._stop_script()

    def _start_script(self) -> None:
        info = self._script_combo.currentData()
        if info is None:
            self._append_log("[WARN] 没有可用的脚本")
            return

        if self._worker is not None and self._worker.isRunning():
            self._append_log("[WARN] 已有脚本正在运行，请先停止")
            return

        # 检查窗口宽高比是否为16:9
        try:
            hwnd = get_hwnd(DEFAULT_PROCESS_NAME)
            win = get_window(hwnd)
            actual_ratio = win.width / win.height
            if abs(actual_ratio - TARGET_ASPECT_RATIO) >= ASPECT_RATIO_TOLERANCE:
                QMessageBox.warning(
                    self, "宽高比不适配",
                    f"当前窗口宽高比不适配（{win.width}×{win.height}），\n"
                    "请将游戏窗口调整为16:9宽高比后再执行脚本。"
                )
                return
        except (WindowNotFoundError, WindowInvalidError):
            QMessageBox.warning(
                self, "未检测到游戏窗口",
                "请先启动游戏并确保窗口可见后再执行脚本。"
            )
            return

        times = self._times_spin.value() if info.need_times_param else None
        self._worker = ScriptWorker(info, times)
        self._worker.started_signal.connect(self._on_worker_started)
        self._worker.finished_signal.connect(self._on_worker_finished)
        self._worker.error_signal.connect(self._on_worker_error)
        self._worker.finished.connect(self._on_worker_done)
        self._worker.start()

    def _stop_script(self) -> None:
        if self._worker is None or not self._worker.isRunning():
            return
        self._append_log("[WARN] 正在强制终止脚本...")
        self._worker.finished.disconnect(self._on_worker_done)
        self._worker.terminate()
        self._worker.wait(3000)
        self._on_worker_done()

    # --- worker callbacks ---

    def _style_toggle_btn(self) -> None:
        is_start = self._toggle_btn.text() == "▶ 开始执行"
        bg = "#6b9fed" if is_start else "#ff4444"
        self._toggle_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                color: #ffffff;
                font-weight: bold;
                font-size: 14px;
                border: 1px solid {theme._accent_color};
                padding: 8px 16px;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {bg}cc;
            }}
            QPushButton:disabled {{
                background-color: #666666;
                color: #999999;
            }}
        """)

    def _on_worker_started(self, name: str) -> None:
        self._toggle_btn.setText("■ 停止")
        self._style_toggle_btn()
        self._script_combo.setEnabled(False)
        self._reload_btn.setEnabled(False)
        self._status_bar.showMessage(f"运行中: {name}")

    def _on_worker_finished(self) -> None:
        self._append_log("[INFO] 脚本执行完成")

    def _on_worker_error(self, msg: str) -> None:
        self._append_log(f"[ERROR] 脚本异常: {msg}")

    def _on_worker_done(self) -> None:
        self._toggle_btn.setText("▶ 开始执行")
        self._style_toggle_btn()
        self._script_combo.setEnabled(True)
        self._reload_btn.setEnabled(True)
        self._status_bar.showMessage("就绪")

    # ------------------------------------------------------------------
    # 日志
    # ------------------------------------------------------------------

    def _append_log(self, text: str) -> None:
        self._log_output.append(text.rstrip("\n"))

    # ------------------------------------------------------------------
    # 状态轮询
    # ------------------------------------------------------------------

    def _start_status_poll(self) -> None:
        self._poll_timer = QTimer(self)
        self._poll_timer.timeout.connect(self._poll_status)
        self._poll_timer.start(2000)
        self._poll_status()

    def _poll_status(self) -> None:
        # 进程
        try:
            running = is_process_running(DEFAULT_PROCESS_NAME)
        except Exception:
            running = False
        if running:
            self._process_label.setText(f"进程: ● {DEFAULT_PROCESS_NAME} 运行中")
            self._process_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            self._process_label.setText(f"进程: ● {DEFAULT_PROCESS_NAME} 未检测到")
            self._process_label.setStyleSheet("color: red; font-weight: bold;")

        # 分辨率
        try:
            hwnd = get_hwnd(DEFAULT_PROCESS_NAME)
            win = get_window(hwnd)
            actual_ratio = win.width / win.height
            is_16_9 = abs(actual_ratio - TARGET_ASPECT_RATIO) < ASPECT_RATIO_TOLERANCE
            if is_16_9:
                self._resolution_label.setText(f"分辨率: {win.width}×{win.height}")
                self._resolution_label.setStyleSheet("color: green; font-weight: bold;")
            else:
                self._resolution_label.setText(
                    f"分辨率: {win.width}×{win.height} - 宽高比不适配，请调整为16:9"
                )
                self._resolution_label.setStyleSheet("color: yellow; font-weight: bold;")
        except (WindowNotFoundError, WindowInvalidError):
            self._resolution_label.setText("分辨率: 未检测到窗口")
            self._resolution_label.setStyleSheet("color: red; font-weight: bold;")
        except Exception:
            self._resolution_label.setText("分辨率: 检测异常")
            self._resolution_label.setStyleSheet("color: orange; font-weight: bold;")

    # ------------------------------------------------------------------
    # 系统托盘
    # ------------------------------------------------------------------

    def _setup_tray(self) -> None:
        icon_path = _icon_path()
        icon = QIcon(icon_path) if icon_path else QApplication.style().standardIcon(
            QApplication.style().StandardPixmap.SP_ComputerIcon
        )
        self._tray = QSystemTrayIcon(icon, self)
        self._tray.setToolTip(f"{DEFAULT_TITLE} v{get_version()}")

        menu = QMenu()
        show_action = menu.addAction("显示/隐藏窗口")
        show_action.triggered.connect(self._toggle_visible)
        menu.addSeparator()
        quit_action = menu.addAction("退出")
        quit_action.triggered.connect(self._quit_app)
        self._tray.setContextMenu(menu)
        self._tray.activated.connect(self._on_tray_activated)
        self._tray.show()

    def _on_tray_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self._toggle_visible()

    def _toggle_visible(self) -> None:
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.raise_()
            self.activateWindow()

    def _quit_app(self) -> None:
        if self._worker is not None and self._worker.isRunning():
            reply = QMessageBox.question(
                self, "确认退出",
                "脚本仍在运行中，确认停止并退出？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
            self._worker.terminate()
            self._worker.wait(3000)
        self._tray.hide()
        QApplication.quit()

    # ------------------------------------------------------------------
    # closeEvent
    # ------------------------------------------------------------------

    def closeEvent(self, _event) -> None:
        self._quit_app()
