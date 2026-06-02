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

logger = logging.getLogger(__name__)

SIDEBAR_STYLE = """
QPushButton {
    background: #2b2b2b;
    color: #cccccc;
    border: none;
    border-left: 3px solid transparent;
    padding: 12px 16px;
    text-align: left;
    font-size: 14px;
}
QPushButton:hover {
    background: #3c3c3c;
    color: #ffffff;
}
QPushButton:checked {
    background: #353535;
    color: #ffffff;
    border-left: 3px solid #6b9fed;
}
"""


def _is_dark_mode() -> bool:
    cs = QApplication.styleHints().colorScheme()
    return cs == Qt.ColorScheme.Dark


def _card_bg() -> str:
    return "#3c3c3c" if _is_dark_mode() else "#f5f5f5"


def _text_color() -> str:
    return "#e0e0e0" if _is_dark_mode() else "#333333"


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

        self._build_ui()
        self._setup_tray()
        self._connect_signals()
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
        sidebar = QWidget()
        sidebar.setFixedWidth(160)
        sidebar.setStyleSheet("background: #2b2b2b;")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 8, 0, 8)
        sidebar_layout.setSpacing(2)

        self._nav_group = QButtonGroup(self)
        self._nav_group.setExclusive(True)

        nav_home = QPushButton("  主页")
        nav_home.setCheckable(True)
        nav_home.setChecked(True)
        nav_home.setStyleSheet(SIDEBAR_STYLE)
        nav_home.setCursor(Qt.CursorShape.PointingHandCursor)

        nav_log = QPushButton("  日志")
        nav_log.setCheckable(True)
        nav_log.setStyleSheet(SIDEBAR_STYLE)
        nav_log.setCursor(Qt.CursorShape.PointingHandCursor)

        nav_about = QPushButton("  关于")
        nav_about.setCheckable(True)
        nav_about.setStyleSheet(SIDEBAR_STYLE)
        nav_about.setCursor(Qt.CursorShape.PointingHandCursor)

        self._nav_group.addButton(nav_home, 0)
        self._nav_group.addButton(nav_log, 1)
        self._nav_group.addButton(nav_about, 2)

        sidebar_layout.addWidget(nav_home)
        sidebar_layout.addWidget(nav_log)
        sidebar_layout.addWidget(nav_about)
        sidebar_layout.addStretch()

        root.addWidget(sidebar)

        # --- 页面容器 ---
        self._pages = QStackedWidget()
        self._pages.addWidget(self._build_home_page())
        self._pages.addWidget(self._build_log_page())
        self._pages.addWidget(self._build_about_page())

        self._nav_group.idClicked.connect(self._pages.setCurrentIndex)

        root.addWidget(self._pages, 1)

        # --- 状态栏 ---
        self._status_bar = QStatusBar()
        self.setStatusBar(self._status_bar)
        self._status_bar.showMessage("就绪")

    def _build_home_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 16, 20, 16)

        # 游戏状态
        title_label = QLabel("游戏状态")
        title_label.setStyleSheet(f"font-size: 15px; font-weight: bold; color: {_text_color()};")
        layout.addWidget(title_label)

        status_widget = QWidget()
        status_widget.setStyleSheet(f"background: {_card_bg()}; border-radius: 6px; padding: 12px;")
        status_layout = QHBoxLayout(status_widget)
        self._process_label = QLabel("等待检测...")
        self._resolution_label = QLabel("等待检测...")
        status_layout.addWidget(self._process_label)
        status_layout.addWidget(self._resolution_label)
        status_layout.addStretch()
        layout.addWidget(status_widget)

        # 脚本控制
        title_label2 = QLabel("脚本控制")
        title_label2.setStyleSheet("font-size: 15px; font-weight: bold; color: #333;")
        layout.addWidget(title_label2)

        control_widget = QWidget()
        control_widget.setStyleSheet(f"background: {_card_bg()}; border-radius: 6px; padding: 12px;")
        control_layout = QHBoxLayout(control_widget)

        control_layout.addWidget(QLabel("脚本:"))
        self._script_combo = QComboBox()
        self._script_combo.setMinimumWidth(200)
        control_layout.addWidget(self._script_combo)

        control_layout.addWidget(QLabel("执行次数:"))
        self._times_spin = QSpinBox()
        self._times_spin.setRange(1, 9999)
        self._times_spin.setValue(1)
        control_layout.addWidget(self._times_spin)

        self._start_btn = QPushButton("▶ 开始执行")
        self._stop_btn = QPushButton("■ 停止")
        self._stop_btn.setEnabled(False)
        self._reload_btn = QPushButton("🔄 重载脚本")

        control_layout.addWidget(self._start_btn)
        control_layout.addWidget(self._stop_btn)
        control_layout.addWidget(self._reload_btn)
        control_layout.addStretch()
        layout.addWidget(control_widget)

        layout.addStretch()
        return page

    def _build_log_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(8)
        layout.setContentsMargins(20, 16, 20, 16)

        header = QHBoxLayout()
        title_label = QLabel("实时日志")
        title_label.setStyleSheet(f"font-size: 15px; font-weight: bold; color: {_text_color()};")
        header.addWidget(title_label)
        header.addStretch()

        self._clear_btn = QPushButton("清空日志")
        header.addWidget(self._clear_btn)
        layout.addLayout(header)

        self._log_output = QTextEdit()
        self._log_output.setReadOnly(True)
        self._log_output.setFont(QFont("Consolas", 10))
        self._log_output.document().setMaximumBlockCount(5000)
        layout.addWidget(self._log_output)

        return page

    def _build_about_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 16, 20, 16)

        title_label = QLabel("关于")
        title_label.setStyleSheet(f"font-size: 15px; font-weight: bold; color: {_text_color()};")
        layout.addWidget(title_label)

        info_widget = QWidget()
        info_widget.setStyleSheet(f"background: {_card_bg()}; border-radius: 6px; padding: 16px;")
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
        license_desc.setStyleSheet(f"font-size: 12px; color: {_text_color()}; opacity: 0.7;")
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
            self._script_combo.addItem(f"{info.name}  -  {info.description}", info)
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

    def _connect_signals(self) -> None:
        self._script_combo.currentIndexChanged.connect(self._on_script_changed)
        self._start_btn.clicked.connect(self._start_script)
        self._stop_btn.clicked.connect(self._stop_script)
        self._reload_btn.clicked.connect(self._reload_scripts)
        self._clear_btn.clicked.connect(self._log_output.clear)
        get_log_signal().message.connect(self._append_log)

    # ------------------------------------------------------------------
    # 脚本启停
    # ------------------------------------------------------------------

    def _on_script_changed(self, _index: int) -> None:
        info = self._script_combo.currentData()
        if info is not None:
            self._times_spin.setEnabled(info.need_times_param)

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

    def _on_worker_started(self, name: str) -> None:
        self._start_btn.setEnabled(False)
        self._stop_btn.setEnabled(True)
        self._script_combo.setEnabled(False)
        self._reload_btn.setEnabled(False)
        self._status_bar.showMessage(f"运行中: {name}")

    def _on_worker_finished(self) -> None:
        self._append_log("[INFO] 脚本执行完成")

    def _on_worker_error(self, msg: str) -> None:
        self._append_log(f"[ERROR] 脚本异常: {msg}")

    def _on_worker_done(self) -> None:
        self._start_btn.setEnabled(True)
        self._stop_btn.setEnabled(False)
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
